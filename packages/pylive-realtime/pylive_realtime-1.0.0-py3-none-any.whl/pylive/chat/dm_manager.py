"""
Direct Message Manager - handles private conversations.
"""

import asyncio
import logging
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Set, Any
import threading
import uuid

logger = logging.getLogger("pylive.dm")


@dataclass
class DMMessage:
    """A direct message."""
    id: str
    conversation_id: str
    sender_id: str
    sender_username: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    read: bool = False
    deleted: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "sender_id": self.sender_id,
            "sender_username": self.sender_username,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "read": self.read,
            "deleted": self.deleted,
        }


@dataclass
class Conversation:
    """A DM conversation between users."""
    id: str
    participants: Set[str]  # user IDs
    created_at: datetime = field(default_factory=datetime.now)
    last_message_at: datetime = field(default_factory=datetime.now)
    messages: List[DMMessage] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "participants": list(self.participants),
            "created_at": self.created_at.isoformat(),
            "last_message_at": self.last_message_at.isoformat(),
            "message_count": len(self.messages),
        }


class DMManager:
    """
    Manages direct messages and conversations.

    Features:
    - Create/retrieve conversations
    - Send/receive messages
    - Message history
    - Online presence for DM notifications
    """

    def __init__(self, max_history_per_conversation: int = 100):
        self.max_history = max_history_per_conversation

        # Conversations: conversation_id -> Conversation
        self._conversations: Dict[str, Conversation] = {}

        # User conversations: user_id -> set of conversation_ids
        self._user_conversations: Dict[str, Set[str]] = {}

        # Active listeners: user_id -> list of queues
        self._listeners: Dict[str, List[asyncio.Queue]] = {}

        # Thread safety
        self._lock = threading.RLock()

        logger.info("DMManager initialized")

    def get_or_create_conversation(
        self, user1_id: str, user2_id: str
    ) -> Conversation:
        """
        Get existing conversation between two users or create new one.
        """
        # Create deterministic conversation ID from sorted user IDs
        participants = frozenset([user1_id, user2_id])
        conv_id = self._conversation_id(user1_id, user2_id)

        with self._lock:
            if conv_id in self._conversations:
                return self._conversations[conv_id]

            # Create new conversation
            conversation = Conversation(
                id=conv_id,
                participants=set(participants),
            )
            self._conversations[conv_id] = conversation

            # Index by user
            for user_id in participants:
                if user_id not in self._user_conversations:
                    self._user_conversations[user_id] = set()
                self._user_conversations[user_id].add(conv_id)

            logger.info(f"Created conversation {conv_id} between {user1_id} and {user2_id}")
            return conversation

    def _conversation_id(self, user1_id: str, user2_id: str) -> str:
        """Generate deterministic conversation ID."""
        sorted_ids = sorted([user1_id, user2_id])
        return f"dm:{sorted_ids[0]}:{sorted_ids[1]}"

    async def send_message(
        self,
        sender_id: str,
        sender_username: str,
        recipient_id: str,
        content: str,
    ) -> DMMessage:
        """
        Send a direct message.

        Returns the created message.
        """
        conversation = self.get_or_create_conversation(sender_id, recipient_id)

        message = DMMessage(
            id=f"msg_{uuid.uuid4().hex[:12]}",
            conversation_id=conversation.id,
            sender_id=sender_id,
            sender_username=sender_username,
            content=content,
        )

        with self._lock:
            conversation.messages.append(message)
            conversation.last_message_at = message.timestamp

            # Trim history if needed
            if len(conversation.messages) > self.max_history:
                conversation.messages = conversation.messages[-self.max_history:]

        # Notify listeners
        await self._notify_user(recipient_id, message)
        await self._notify_user(sender_id, message)

        logger.debug(f"Message sent from {sender_id} to {recipient_id}")
        return message

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID."""
        with self._lock:
            return self._conversations.get(conversation_id)

    def get_user_conversations(self, user_id: str) -> List[Conversation]:
        """Get all conversations for a user."""
        with self._lock:
            conv_ids = self._user_conversations.get(user_id, set())
            conversations = [
                self._conversations[cid]
                for cid in conv_ids
                if cid in self._conversations
            ]
            # Sort by last message time
            conversations.sort(key=lambda c: c.last_message_at, reverse=True)
            return conversations

    def get_messages(
        self,
        conversation_id: str,
        limit: int = 50,
        before_id: Optional[str] = None,
    ) -> List[DMMessage]:
        """
        Get messages from a conversation.

        Args:
            conversation_id: Conversation ID
            limit: Maximum messages to return
            before_id: Only return messages before this ID (for pagination)
        """
        with self._lock:
            conversation = self._conversations.get(conversation_id)
            if not conversation:
                return []

            messages = conversation.messages.copy()

        # Filter by before_id if provided
        if before_id:
            idx = None
            for i, msg in enumerate(messages):
                if msg.id == before_id:
                    idx = i
                    break
            if idx is not None:
                messages = messages[:idx]

        # Return last N messages
        return messages[-limit:]

    def mark_as_read(
        self, conversation_id: str, user_id: str, message_id: Optional[str] = None
    ) -> None:
        """Mark messages as read."""
        with self._lock:
            conversation = self._conversations.get(conversation_id)
            if not conversation:
                return

            for msg in conversation.messages:
                # Only mark messages from others
                if msg.sender_id != user_id:
                    if message_id:
                        if msg.id == message_id:
                            msg.read = True
                            break
                    else:
                        msg.read = True

    def get_unread_count(self, user_id: str) -> int:
        """Get total unread message count for a user."""
        count = 0
        with self._lock:
            conv_ids = self._user_conversations.get(user_id, set())
            for conv_id in conv_ids:
                conv = self._conversations.get(conv_id)
                if conv:
                    for msg in conv.messages:
                        if msg.sender_id != user_id and not msg.read:
                            count += 1
        return count

    # Real-time notifications

    def subscribe(self, user_id: str) -> asyncio.Queue:
        """
        Subscribe to DM notifications for a user.

        Returns a queue that will receive new messages.
        """
        queue: asyncio.Queue = asyncio.Queue()
        with self._lock:
            if user_id not in self._listeners:
                self._listeners[user_id] = []
            self._listeners[user_id].append(queue)
        logger.debug(f"User {user_id} subscribed to DM notifications")
        return queue

    def unsubscribe(self, user_id: str, queue: asyncio.Queue) -> None:
        """Unsubscribe from DM notifications."""
        with self._lock:
            if user_id in self._listeners:
                try:
                    self._listeners[user_id].remove(queue)
                except ValueError:
                    pass
                if not self._listeners[user_id]:
                    del self._listeners[user_id]
        logger.debug(f"User {user_id} unsubscribed from DM notifications")

    async def _notify_user(self, user_id: str, message: DMMessage) -> None:
        """Notify a user about a new message."""
        with self._lock:
            queues = self._listeners.get(user_id, []).copy()

        for queue in queues:
            try:
                queue.put_nowait(message)
            except asyncio.QueueFull:
                logger.warning(f"DM notification queue full for user {user_id}")

    # Group DMs

    def create_group(
        self, creator_id: str, participant_ids: List[str], name: str = ""
    ) -> Conversation:
        """Create a group conversation."""
        all_participants = set([creator_id] + participant_ids)
        conv_id = f"group_{uuid.uuid4().hex[:12]}"

        with self._lock:
            conversation = Conversation(
                id=conv_id,
                participants=all_participants,
            )
            self._conversations[conv_id] = conversation

            for user_id in all_participants:
                if user_id not in self._user_conversations:
                    self._user_conversations[user_id] = set()
                self._user_conversations[user_id].add(conv_id)

        logger.info(f"Created group {conv_id} with {len(all_participants)} participants")
        return conversation

    def add_to_group(self, conversation_id: str, user_id: str) -> bool:
        """Add a user to a group conversation."""
        with self._lock:
            conversation = self._conversations.get(conversation_id)
            if not conversation:
                return False

            conversation.participants.add(user_id)

            if user_id not in self._user_conversations:
                self._user_conversations[user_id] = set()
            self._user_conversations[user_id].add(conversation_id)

        return True

    def remove_from_group(self, conversation_id: str, user_id: str) -> bool:
        """Remove a user from a group conversation."""
        with self._lock:
            conversation = self._conversations.get(conversation_id)
            if not conversation:
                return False

            conversation.participants.discard(user_id)

            if user_id in self._user_conversations:
                self._user_conversations[user_id].discard(conversation_id)

        return True

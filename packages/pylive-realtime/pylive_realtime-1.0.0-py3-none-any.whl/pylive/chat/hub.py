"""
Chat Hub - manages chat rooms and messaging.
"""

import asyncio
import json
import logging
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Set, Optional, List, Any
import threading

logger = logging.getLogger("pylive.chat")


class MessageType(str, Enum):
    """Chat message types."""
    MESSAGE = "message"
    SYSTEM = "system"
    EMOTE = "emote"
    COMMAND = "command"
    USER_JOIN = "user_join"
    USER_LEAVE = "user_leave"
    USER_TIMEOUT = "user_timeout"
    USER_BAN = "user_ban"
    CHAT_CLEAR = "chat_clear"


@dataclass
class ChatMessage:
    """A chat message."""
    id: int
    stream_key: str
    type: MessageType
    content: str
    user_id: Optional[str] = None
    username: str = ""
    display_name: str = ""
    user_color: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    emotes: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    is_deleted: bool = False
    is_pinned: bool = False
    reply_to_id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "stream_key": self.stream_key,
            "type": self.type.value if isinstance(self.type, MessageType) else self.type,
            "content": self.content,
            "user_id": self.user_id,
            "username": self.username,
            "display_name": self.display_name,
            "user_color": self.user_color,
            "timestamp": self.timestamp.isoformat(),
            "emotes": self.emotes,
            "mentions": self.mentions,
            "is_deleted": self.is_deleted,
            "is_pinned": self.is_pinned,
            "reply_to_id": self.reply_to_id,
        }


@dataclass
class ChatSettings:
    """Chat room settings."""
    enabled: bool = True
    followers_only: bool = False
    slow_mode: bool = False
    slow_mode_delay: float = 5.0  # seconds
    max_message_length: int = 500
    allow_links: bool = True
    word_filters: List[str] = field(default_factory=list)


class ChatClient:
    """A connected chat client."""

    def __init__(
        self,
        client_id: str,
        websocket: Any,
        user_id: Optional[str] = None,
        username: str = "",
    ):
        self.id = client_id
        self.websocket = websocket
        self.user_id = user_id
        self.username = username
        self.is_streamer = False
        self.is_moderator = False
        self.last_seen = datetime.now()
        self.last_message = datetime.now()
        self._lock = threading.RLock()

    async def send(self, data: bytes) -> bool:
        """Send data to client."""
        try:
            await self.websocket.send_text(data.decode())
            return True
        except Exception as e:
            logger.warning(f"Failed to send to client {self.id}: {e}")
            return False


class ChatHub:
    """
    Chat hub for a stream - manages clients and messages.

    Features:
    - Client registration/unregistration
    - Message broadcasting
    - Settings management
    - Viewer count tracking
    """

    def __init__(self, stream_key: str):
        self.stream_key = stream_key

        # Clients
        self._clients: Set[ChatClient] = set()

        # Message handling
        self._broadcast_queue: asyncio.Queue = asyncio.Queue()

        # Settings
        self._settings = ChatSettings()

        # Message history (in-memory)
        self._history: deque = deque(maxlen=100)
        self._message_id_counter = 0

        # Thread safety
        self._lock = threading.RLock()

        # Running state
        self._running = False
        self._task: Optional[asyncio.Task] = None

        logger.info(f"ChatHub created for stream: {stream_key}")

    async def start(self) -> None:
        """Start the chat hub."""
        self._running = True
        self._task = asyncio.create_task(self._run())
        logger.info(f"ChatHub started: {self.stream_key}")

    async def stop(self) -> None:
        """Stop the chat hub."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        # Close all client connections
        with self._lock:
            for client in self._clients:
                try:
                    await client.websocket.close()
                except Exception:
                    pass
            self._clients.clear()

        logger.info(f"ChatHub stopped: {self.stream_key}")

    async def _run(self) -> None:
        """Main hub loop."""
        while self._running:
            try:
                # Process broadcast queue
                try:
                    data = await asyncio.wait_for(
                        self._broadcast_queue.get(),
                        timeout=1.0
                    )
                    await self._broadcast_data(data)
                except asyncio.TimeoutError:
                    continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in chat hub: {e}")

    def register_client(self, client: ChatClient) -> None:
        """Register a new client."""
        with self._lock:
            self._clients.add(client)

        logger.info(
            f"Client connected to {self.stream_key}: "
            f"{client.id} ({client.username}), total: {len(self._clients)}"
        )

        # Send join message
        if client.username:
            asyncio.create_task(self._send_join_message(client))

    def unregister_client(self, client: ChatClient) -> None:
        """Unregister a client."""
        with self._lock:
            self._clients.discard(client)

        logger.info(
            f"Client disconnected from {self.stream_key}: "
            f"{client.id} ({client.username}), total: {len(self._clients)}"
        )

        # Send leave message
        if client.username:
            asyncio.create_task(self._send_leave_message(client))

    async def _send_join_message(self, client: ChatClient) -> None:
        """Send user join message."""
        msg = ChatMessage(
            id=self._next_id(),
            stream_key=self.stream_key,
            type=MessageType.USER_JOIN,
            content=f"{client.username} joined the chat",
            username=client.username,
            display_name=client.username,
            user_id=client.user_id,
        )
        await self.broadcast_message(msg)

    async def _send_leave_message(self, client: ChatClient) -> None:
        """Send user leave message."""
        msg = ChatMessage(
            id=self._next_id(),
            stream_key=self.stream_key,
            type=MessageType.USER_LEAVE,
            content=f"{client.username} left the chat",
            username=client.username,
            display_name=client.username,
            user_id=client.user_id,
        )
        await self.broadcast_message(msg)

    async def broadcast_message(self, message: ChatMessage) -> None:
        """Broadcast a message to all clients."""
        # Add to history
        with self._lock:
            self._history.append(message)

        # Queue for broadcast
        data = json.dumps(message.to_dict()).encode()
        await self._broadcast_queue.put(data)

    async def _broadcast_data(self, data: bytes) -> None:
        """Broadcast raw data to all clients."""
        with self._lock:
            clients = list(self._clients)

        for client in clients:
            try:
                await client.send(data)
            except Exception:
                # Client disconnected, will be cleaned up
                pass

    def send_system_message(self, content: str) -> None:
        """Send a system message."""
        msg = ChatMessage(
            id=self._next_id(),
            stream_key=self.stream_key,
            type=MessageType.SYSTEM,
            content=content,
            username="System",
            display_name="System",
        )
        asyncio.create_task(self.broadcast_message(msg))

    def process_client_message(
        self,
        client: ChatClient,
        msg_type: MessageType,
        content: str,
    ) -> Optional[ChatMessage]:
        """
        Process an incoming message from a client.

        Returns the message if it should be broadcast, None otherwise.
        """
        # Check settings
        if not self._settings.enabled:
            return None

        # Validate message length
        if len(content) > self._settings.max_message_length:
            return None

        # Check slow mode
        if self._settings.slow_mode:
            time_since_last = (datetime.now() - client.last_message).total_seconds()
            if time_since_last < self._settings.slow_mode_delay:
                return None

        # Apply word filters
        for word in self._settings.word_filters:
            if word.lower() in content.lower():
                return None

        # Update client last message time
        client.last_message = datetime.now()

        # Create message
        msg = ChatMessage(
            id=self._next_id(),
            stream_key=self.stream_key,
            type=msg_type,
            content=content,
            user_id=client.user_id,
            username=client.username,
            display_name=client.username,
        )

        return msg

    def get_client_count(self) -> int:
        """Get number of connected clients."""
        with self._lock:
            return len(self._clients)

    def get_settings(self) -> ChatSettings:
        """Get current chat settings."""
        with self._lock:
            return self._settings

    def update_settings(self, settings: ChatSettings) -> None:
        """Update chat settings."""
        with self._lock:
            self._settings = settings
        self.send_system_message("Chat settings updated")

    def get_history(self) -> List[ChatMessage]:
        """Get message history."""
        with self._lock:
            return list(self._history)

    def _next_id(self) -> int:
        """Generate next message ID."""
        with self._lock:
            self._message_id_counter += 1
            return self._message_id_counter

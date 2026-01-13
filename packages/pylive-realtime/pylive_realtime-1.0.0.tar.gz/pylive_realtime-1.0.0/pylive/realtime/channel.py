"""
Channel management for realtime server.
"""

import asyncio
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Set, Optional, List, Any, TYPE_CHECKING
import threading

if TYPE_CHECKING:
    from pylive.realtime.types import Message, PresenceInfo


@dataclass
class ChannelSettings:
    """Settings for a realtime channel."""
    max_clients: int = 100
    max_history: int = 20
    ttl: timedelta = field(default_factory=lambda: timedelta(hours=1))
    require_auth: bool = True
    allow_publish: bool = False
    allow_presence: bool = False
    private: bool = False
    allowed_roles: List[str] = field(default_factory=list)
    proxy_endpoint: Optional[str] = None


class Channel:
    """
    A realtime channel that clients can subscribe to.

    Channels support:
    - Client subscriptions
    - Message broadcasting
    - Presence tracking
    - Message history
    """

    def __init__(
        self,
        channel_id: str,
        namespace: str,
        settings: Optional[ChannelSettings] = None
    ):
        self.id = channel_id
        self.namespace = namespace
        self.settings = settings or ChannelSettings()
        self.created_at = datetime.now()
        self.last_activity = datetime.now()

        # Client management
        self._clients: Set[Any] = set()
        self._presence: Dict[str, "PresenceInfo"] = {}

        # Message history
        self._history: deque = deque(maxlen=self.settings.max_history)

        # Thread safety
        self._lock = threading.RLock()

    @property
    def client_count(self) -> int:
        """Get number of connected clients."""
        with self._lock:
            return len(self._clients)

    def add_client(self, client: Any) -> bool:
        """
        Add a client to the channel.

        Returns:
            True if client was added, False if channel is full
        """
        with self._lock:
            if len(self._clients) >= self.settings.max_clients:
                return False
            self._clients.add(client)
            self.last_activity = datetime.now()
            return True

    def remove_client(self, client: Any) -> None:
        """Remove a client from the channel."""
        with self._lock:
            self._clients.discard(client)
            self.last_activity = datetime.now()

    def get_clients(self) -> Set[Any]:
        """Get all clients in the channel."""
        with self._lock:
            return self._clients.copy()

    def add_presence(self, user_id: str, presence: "PresenceInfo") -> None:
        """Add or update presence for a user."""
        with self._lock:
            self._presence[user_id] = presence
            self.last_activity = datetime.now()

    def remove_presence(self, user_id: str) -> Optional["PresenceInfo"]:
        """Remove presence for a user."""
        with self._lock:
            self.last_activity = datetime.now()
            return self._presence.pop(user_id, None)

    def get_presence(self) -> Dict[str, "PresenceInfo"]:
        """Get all presence information."""
        with self._lock:
            return self._presence.copy()

    def add_to_history(self, message: "Message") -> None:
        """Add a message to channel history."""
        with self._lock:
            self._history.append(message)
            self.last_activity = datetime.now()

    def get_history(self) -> List["Message"]:
        """Get message history."""
        with self._lock:
            return list(self._history)

    def update_settings(self, settings: ChannelSettings) -> None:
        """Update channel settings."""
        with self._lock:
            self.settings = settings
            # Resize history if needed
            if len(self._history) > settings.max_history:
                self._history = deque(
                    list(self._history)[-settings.max_history:],
                    maxlen=settings.max_history
                )

    def is_expired(self) -> bool:
        """Check if channel has expired based on TTL."""
        return datetime.now() - self.last_activity > self.settings.ttl

    def is_empty(self) -> bool:
        """Check if channel has no clients."""
        with self._lock:
            return len(self._clients) == 0

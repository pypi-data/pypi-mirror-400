"""
Type definitions for realtime module.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class MessageType(str, Enum):
    """Message types for realtime communication."""
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    CHAT = "chat"
    JOIN = "join"
    LEAVE = "leave"
    PRESENCE = "presence"
    RPC = "rpc"
    ERROR = "error"
    SYSTEM = "system"


@dataclass
class UserInfo:
    """User information for realtime clients."""
    id: str
    username: str
    email: str = ""
    role: str = "user"
    avatar: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PresenceInfo:
    """Presence information for users in channels."""
    user: UserInfo
    joined_at: datetime
    last_seen: datetime
    client_id: str
    status: str = "online"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Message:
    """Realtime message."""
    id: str
    type: MessageType
    channel: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    user: Optional[UserInfo] = None
    timestamp: datetime = field(default_factory=datetime.now)
    reply_to: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        result = {
            "id": self.id,
            "type": self.type.value if isinstance(self.type, MessageType) else self.type,
            "channel": self.channel,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
        }
        if self.user:
            result["user"] = {
                "id": self.user.id,
                "username": self.user.username,
                "role": self.user.role,
            }
        if self.reply_to:
            result["reply_to"] = self.reply_to
        return result


@dataclass
class BanInfo:
    """Ban information for moderation."""
    reason: str
    banned_by: str
    banned_at: datetime
    expires_at: Optional[datetime] = None


@dataclass
class TimeoutInfo:
    """Timeout information for moderation."""
    reason: str
    timeout_by: str
    timeout_at: datetime
    expires_at: datetime
    duration_seconds: int = 300

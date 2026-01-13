"""
Realtime server - manages WebSocket connections, channels, and messaging.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Set, Optional, Callable, Any, List
import threading

from pylive.realtime.channel import Channel, ChannelSettings
from pylive.realtime.types import (
    Message, MessageType, UserInfo, PresenceInfo, BanInfo, TimeoutInfo
)
from pylive.core.config import Config

logger = logging.getLogger("pylive.realtime")


class Client:
    """Represents a connected WebSocket client."""

    def __init__(
        self,
        client_id: str,
        websocket: Any,
        user: Optional[UserInfo] = None
    ):
        self.id = client_id
        self.websocket = websocket
        self.user = user or UserInfo(id="", username="anonymous")
        self.channels: Dict[str, Channel] = {}
        self.last_ping = datetime.now()
        self._lock = threading.RLock()

    async def send(self, message: Message) -> bool:
        """Send a message to the client."""
        try:
            data = json.dumps(message.to_dict())
            await self.websocket.send_text(data)
            return True
        except Exception as e:
            logger.warning(f"Failed to send message to client {self.id}: {e}")
            return False

    async def send_json(self, data: Dict[str, Any]) -> bool:
        """Send raw JSON data to the client."""
        try:
            await self.websocket.send_text(json.dumps(data))
            return True
        except Exception as e:
            logger.warning(f"Failed to send data to client {self.id}: {e}")
            return False


RPCHandler = Callable[[Any, UserInfo, Dict[str, Any]], Dict[str, Any]]


class RealtimeServer:
    """
    Main realtime server managing WebSocket connections and channels.

    Features:
    - Channel subscriptions
    - Message broadcasting
    - Presence tracking
    - RPC handlers
    - Ban/timeout moderation
    - SSE support
    """

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()

        # Channel management
        self._channels: Dict[str, Channel] = {}
        self._clients: Dict[str, Client] = {}

        # Moderation
        self._bans: Dict[str, Dict[str, BanInfo]] = {}  # channel -> user_id -> BanInfo
        self._timeouts: Dict[str, Dict[str, TimeoutInfo]] = {}
        self._channel_access: Dict[str, Dict[str, bool]] = {}

        # RPC handlers
        self._rpc_handlers: Dict[str, RPCHandler] = {}

        # SSE clients
        self._sse_clients: Dict[str, Dict[str, asyncio.Queue]] = {}
        self._sse_channel_clients: Dict[str, Dict[str, asyncio.Queue]] = {}

        # Thread safety
        self._lock = threading.RLock()

        # Register default RPC handlers
        self._register_default_handlers()

        logger.info("RealtimeServer initialized")

    def _register_default_handlers(self) -> None:
        """Register default RPC handlers."""

        def ping_handler(ctx: Any, user: UserInfo, params: Dict[str, Any]) -> Dict[str, Any]:
            return {"pong": datetime.now().isoformat()}

        def stats_handler(ctx: Any, user: UserInfo, params: Dict[str, Any]) -> Dict[str, Any]:
            return self.get_stats()

        self.register_rpc_handler("ping", ping_handler)
        self.register_rpc_handler("stats", stats_handler)

    # Channel management

    def get_or_create_channel(self, channel_id: str, namespace: str = "default") -> Channel:
        """Get an existing channel or create a new one."""
        with self._lock:
            if channel_id in self._channels:
                return self._channels[channel_id]

            settings = self._get_default_settings(namespace)
            channel = Channel(channel_id, namespace, settings)
            self._channels[channel_id] = channel

            logger.info(f"Channel created: {channel_id} (namespace: {namespace})")

            # Apply config if available
            self._apply_channel_config(channel_id, namespace, channel)

            return channel

    def _get_default_settings(self, namespace: str) -> ChannelSettings:
        """Get default settings for a namespace."""
        settings = ChannelSettings()

        # Namespace-specific defaults
        if namespace == "chat":
            settings = ChannelSettings(
                max_clients=1000,
                max_history=100,
                ttl=timedelta(hours=24),
                require_auth=False,
                allow_publish=True,
                allow_presence=True,
            )
        elif namespace == "stream":
            settings = ChannelSettings(
                max_clients=10000,
                max_history=50,
                ttl=timedelta(hours=12),
                require_auth=False,
                allow_publish=False,
                allow_presence=True,
            )

        # Apply config overrides
        if self.config and self.config.namespace_config(namespace):
            ns_cfg = self.config.namespace_config(namespace)
            if ns_cfg.max_clients is not None:
                settings.max_clients = ns_cfg.max_clients
            if ns_cfg.max_history is not None:
                settings.max_history = ns_cfg.max_history
            if ns_cfg.require_auth is not None:
                settings.require_auth = ns_cfg.require_auth
            if ns_cfg.allow_publish is not None:
                settings.allow_publish = ns_cfg.allow_publish
            if ns_cfg.allow_presence is not None:
                settings.allow_presence = ns_cfg.allow_presence
            if ns_cfg.private is not None:
                settings.private = ns_cfg.private
            if ns_cfg.allowed_roles:
                settings.allowed_roles = ns_cfg.allowed_roles
            if ns_cfg.proxy_endpoint:
                settings.proxy_endpoint = ns_cfg.proxy_endpoint

        return settings

    def _apply_channel_config(self, channel_id: str, namespace: str, channel: Channel) -> None:
        """Apply configuration to a channel."""
        if not self.config:
            return

        cfg = self.config.channel_config(channel_id, namespace)
        if not cfg:
            return

        settings = channel.settings
        if cfg.max_clients is not None:
            settings.max_clients = cfg.max_clients
        if cfg.max_history is not None:
            settings.max_history = cfg.max_history
        if cfg.require_auth is not None:
            settings.require_auth = cfg.require_auth
        if cfg.allow_publish is not None:
            settings.allow_publish = cfg.allow_publish
        if cfg.allow_presence is not None:
            settings.allow_presence = cfg.allow_presence
        if cfg.private is not None:
            settings.private = cfg.private
        if cfg.allowed_roles:
            settings.allowed_roles = cfg.allowed_roles
        if cfg.proxy_endpoint:
            settings.proxy_endpoint = cfg.proxy_endpoint

        channel.update_settings(settings)

        if cfg.allowed_users:
            self.grant_access(channel_id, cfg.allowed_users)

    # Client management

    def create_client(self, websocket: Any, user: Optional[UserInfo] = None) -> Client:
        """Create a new client."""
        client_id = f"client_{uuid.uuid4().hex[:12]}"
        client = Client(client_id, websocket, user)
        return client

    async def register_client(self, client: Client) -> None:
        """Register a new client connection."""
        with self._lock:
            self._clients[client.id] = client

        logger.info(f"Client connected: {client.id} (user: {client.user.id})")

        # Send welcome message
        welcome = Message(
            id=self._generate_id(),
            type=MessageType.CONNECT,
            data={"status": "connected", "client_id": client.id},
            timestamp=datetime.now(),
        )
        await client.send(welcome)

    async def unregister_client(self, client: Client) -> None:
        """Unregister a client connection."""
        with self._lock:
            self._clients.pop(client.id, None)

            # Unsubscribe from all channels
            for channel_id, channel in list(client.channels.items()):
                await self._unsubscribe_from_channel(client, channel_id, channel)

        logger.info(f"Client disconnected: {client.id}")

    # Subscription management

    async def subscribe(self, client: Client, channel_id: str) -> bool:
        """Subscribe a client to a channel."""
        parts = channel_id.split(":", 1)
        if len(parts) < 2:
            logger.warning(f"Invalid channel ID: {channel_id}")
            return False

        namespace = parts[0]

        # Check permissions
        if not await self._check_join_allowed(channel_id, client.user):
            return False

        channel = self.get_or_create_channel(channel_id, namespace)

        # Check auth requirement
        if channel.settings.require_auth and not client.user.id:
            logger.warning(f"Auth required for channel {channel_id}")
            return False

        # Add client to channel
        if not channel.add_client(client):
            logger.warning(f"Channel {channel_id} is full")
            return False

        client.channels[channel_id] = channel

        # Add presence
        if channel.settings.allow_presence and client.user.id:
            presence = PresenceInfo(
                user=client.user,
                joined_at=datetime.now(),
                last_seen=datetime.now(),
                client_id=client.id,
            )
            channel.add_presence(client.user.id, presence)

            # Broadcast join event
            join_msg = Message(
                id=self._generate_id(),
                type=MessageType.JOIN,
                channel=channel_id,
                user=client.user,
                data={"presence": {"user_id": client.user.id, "username": client.user.username}},
                timestamp=datetime.now(),
            )
            await self.broadcast(join_msg)

        # Send history
        for msg in channel.get_history():
            await client.send(msg)

        # Confirm subscription
        confirm = Message(
            id=self._generate_id(),
            type=MessageType.SUBSCRIBE,
            channel=channel_id,
            data={"subscribed": True, "clients": channel.client_count},
            timestamp=datetime.now(),
        )
        await client.send(confirm)

        logger.info(f"Client {client.id} subscribed to {channel_id}")
        return True

    async def unsubscribe(self, client: Client, channel_id: str) -> None:
        """Unsubscribe a client from a channel."""
        channel = client.channels.get(channel_id)
        if channel:
            await self._unsubscribe_from_channel(client, channel_id, channel)

    async def _unsubscribe_from_channel(
        self, client: Client, channel_id: str, channel: Channel
    ) -> None:
        """Internal unsubscribe logic."""
        channel.remove_client(client)
        client.channels.pop(channel_id, None)

        # Remove presence and broadcast leave
        if channel.settings.allow_presence and client.user.id:
            channel.remove_presence(client.user.id)

            leave_msg = Message(
                id=self._generate_id(),
                type=MessageType.LEAVE,
                channel=channel_id,
                user=client.user,
                timestamp=datetime.now(),
            )
            await self.broadcast(leave_msg)

    # Broadcasting

    async def broadcast(self, message: Message) -> None:
        """Broadcast a message to all clients in a channel."""
        with self._lock:
            channel = self._channels.get(message.channel)

        if not channel:
            return

        # Add to history
        if message.type == MessageType.CHAT:
            channel.add_to_history(message)

        # Send to all clients
        data = json.dumps(message.to_dict()).encode()
        for client in channel.get_clients():
            try:
                await client.websocket.send_text(data.decode())
            except Exception:
                pass

        # Broadcast to SSE clients
        await self._broadcast_to_sse_channel(message.channel, message)

    async def publish(self, message: Message) -> bool:
        """Publish a message to a channel."""
        parts = message.channel.split(":", 1)
        if len(parts) < 2:
            return False

        with self._lock:
            if message.channel not in self._channels:
                self.get_or_create_channel(message.channel, parts[0])

        # Check publish permission
        if message.user:
            if not await self._check_publish_allowed(message.channel, message.user):
                return False

        await self.broadcast(message)
        return True

    # Permission checks

    async def _check_join_allowed(self, channel_id: str, user: UserInfo) -> bool:
        """Check if a user can join a channel."""
        parts = channel_id.split(":", 1)
        if len(parts) < 2:
            return False

        with self._lock:
            channel = self._channels.get(channel_id)

        if channel and channel.settings.private:
            if not user.id:
                return False

            # Check roles
            if channel.settings.allowed_roles:
                if user.role not in channel.settings.allowed_roles:
                    return False

            # Check explicit access
            if channel_id in self._channel_access:
                if user.id not in self._channel_access[channel_id]:
                    return False

        # Check ban
        if self._is_banned(channel_id, user.id):
            return False

        return True

    async def _check_publish_allowed(self, channel_id: str, user: UserInfo) -> bool:
        """Check if a user can publish to a channel."""
        if not await self._check_join_allowed(channel_id, user):
            return False

        # Check timeout
        if self._is_timed_out(channel_id, user.id):
            return False

        return True

    # Moderation

    def _is_banned(self, channel_id: str, user_id: str) -> bool:
        """Check if a user is banned from a channel."""
        if not user_id:
            return False

        with self._lock:
            channel_bans = self._bans.get(channel_id, {})
            return user_id in channel_bans

    def _is_timed_out(self, channel_id: str, user_id: str) -> bool:
        """Check if a user is timed out in a channel."""
        if not user_id:
            return False

        with self._lock:
            channel_timeouts = self._timeouts.get(channel_id, {})
            timeout = channel_timeouts.get(user_id)
            if timeout:
                if datetime.now() > timeout.expires_at:
                    # Timeout expired, remove it
                    del channel_timeouts[user_id]
                    return False
                return True
        return False

    def ban_user(
        self, channel_id: str, user_id: str, reason: str, moderator_id: str
    ) -> None:
        """Ban a user from a channel."""
        with self._lock:
            if channel_id not in self._bans:
                self._bans[channel_id] = {}
            self._bans[channel_id][user_id] = BanInfo(
                reason=reason,
                banned_by=moderator_id,
                banned_at=datetime.now(),
            )
        logger.info(f"User {user_id} banned from {channel_id} by {moderator_id}")

    def unban_user(self, channel_id: str, user_id: str) -> None:
        """Remove a ban for a user."""
        with self._lock:
            if channel_id in self._bans:
                self._bans[channel_id].pop(user_id, None)
        logger.info(f"User {user_id} unbanned from {channel_id}")

    def timeout_user(
        self,
        channel_id: str,
        user_id: str,
        reason: str,
        moderator_id: str,
        duration_seconds: int = 300,
    ) -> None:
        """Timeout a user in a channel."""
        with self._lock:
            if channel_id not in self._timeouts:
                self._timeouts[channel_id] = {}
            self._timeouts[channel_id][user_id] = TimeoutInfo(
                reason=reason,
                timeout_by=moderator_id,
                timeout_at=datetime.now(),
                expires_at=datetime.now() + timedelta(seconds=duration_seconds),
                duration_seconds=duration_seconds,
            )
        logger.info(f"User {user_id} timed out in {channel_id} for {duration_seconds}s")

    # Access control

    def grant_access(self, channel_id: str, user_ids: List[str]) -> None:
        """Grant access to a private channel for users."""
        with self._lock:
            if channel_id not in self._channel_access:
                self._channel_access[channel_id] = {}
            for user_id in user_ids:
                if user_id:
                    self._channel_access[channel_id][user_id] = True

    def revoke_access(self, channel_id: str, user_id: str) -> None:
        """Revoke access to a private channel for a user."""
        with self._lock:
            if channel_id in self._channel_access:
                self._channel_access[channel_id].pop(user_id, None)

    # RPC

    def register_rpc_handler(self, method: str, handler: RPCHandler) -> None:
        """Register an RPC handler."""
        with self._lock:
            self._rpc_handlers[method.lower()] = handler
        logger.info(f"RPC handler registered: {method}")

    async def execute_rpc(
        self, method: str, user: UserInfo, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute an RPC call."""
        with self._lock:
            handler = self._rpc_handlers.get(method.lower())

        if not handler:
            raise ValueError(f"RPC method not found: {method}")

        return handler(None, user, params)

    # SSE support

    def register_sse_client(
        self, user_id: str, client_id: str
    ) -> asyncio.Queue:
        """Register an SSE client."""
        queue: asyncio.Queue = asyncio.Queue()
        with self._lock:
            if user_id not in self._sse_clients:
                self._sse_clients[user_id] = {}
            self._sse_clients[user_id][client_id] = queue
        return queue

    def unregister_sse_client(self, user_id: str, client_id: str) -> None:
        """Unregister an SSE client."""
        with self._lock:
            if user_id in self._sse_clients:
                self._sse_clients[user_id].pop(client_id, None)
                if not self._sse_clients[user_id]:
                    del self._sse_clients[user_id]

    def register_sse_channel_client(
        self, channel_id: str, client_id: str
    ) -> asyncio.Queue:
        """Register an SSE client for a channel."""
        queue: asyncio.Queue = asyncio.Queue()
        with self._lock:
            if channel_id not in self._sse_channel_clients:
                self._sse_channel_clients[channel_id] = {}
            self._sse_channel_clients[channel_id][client_id] = queue
        return queue

    def unregister_sse_channel_client(self, channel_id: str, client_id: str) -> None:
        """Unregister an SSE client from a channel."""
        with self._lock:
            if channel_id in self._sse_channel_clients:
                self._sse_channel_clients[channel_id].pop(client_id, None)
                if not self._sse_channel_clients[channel_id]:
                    del self._sse_channel_clients[channel_id]

    async def _broadcast_to_sse_channel(self, channel_id: str, message: Message) -> None:
        """Broadcast a message to SSE clients in a channel."""
        with self._lock:
            clients = self._sse_channel_clients.get(channel_id, {}).copy()

        for queue in clients.values():
            try:
                queue.put_nowait(message)
            except asyncio.QueueFull:
                pass

    # Stats

    def get_stats(self) -> Dict[str, Any]:
        """Get server statistics."""
        with self._lock:
            return {
                "total_channels": len(self._channels),
                "total_clients": len(self._clients),
                "total_sse_clients": sum(
                    len(clients) for clients in self._sse_clients.values()
                ),
            }

    def _generate_id(self) -> str:
        """Generate a unique message ID."""
        return f"{int(datetime.now().timestamp() * 1000)}_{uuid.uuid4().hex[:8]}"

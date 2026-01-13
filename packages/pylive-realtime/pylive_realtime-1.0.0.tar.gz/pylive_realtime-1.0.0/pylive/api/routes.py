"""
FastAPI routes for PyLive server.

Provides:
- REST API endpoints
- WebSocket connections
- SSE (Server-Sent Events) streams
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Query, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pylive.core.config import Config
from pylive.auth.jwt import sign_token, verify_token, Claims
from pylive.realtime.server import RealtimeServer, Client
from pylive.realtime.types import Message, MessageType, UserInfo
from pylive.chat.hub import ChatHub, ChatClient, ChatMessage, MessageType as ChatMessageType
from pylive.chat.dm_manager import DMManager

logger = logging.getLogger("pylive.api")


# Pydantic models for request/response

class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    user_id: str
    username: str


class PublishRequest(BaseModel):
    channel: str
    data: dict
    type: str = "chat"


class DMRequest(BaseModel):
    recipient_id: str
    content: str


# Dependency injection

def get_realtime_server(request: Request) -> RealtimeServer:
    return request.app.state.realtime_server


def get_dm_manager(request: Request) -> DMManager:
    return request.app.state.dm_manager


def get_config(request: Request) -> Config:
    return request.app.state.config


async def get_current_user(
    request: Request,
    authorization: Optional[str] = None,
) -> Optional[UserInfo]:
    """Extract user from JWT token."""
    config: Config = request.app.state.config

    # Try header
    auth_header = request.headers.get("Authorization", authorization)
    if not auth_header:
        return None

    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
    else:
        token = auth_header

    try:
        claims = verify_token(token, config.jwt.secret)
        return UserInfo(
            id=claims.user_id,
            username=claims.username,
            email=claims.email,
            role=claims.role,
        )
    except Exception:
        return None


def create_app(config: Optional[Config] = None) -> FastAPI:
    """Create and configure the FastAPI application."""

    config = config or Config.load()

    app = FastAPI(
        title="PyLive API",
        description="Realtime streaming platform API with chat",
        version="1.0.0",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize services
    realtime_server = RealtimeServer(config)
    dm_manager = DMManager()

    # Store in app state
    app.state.config = config
    app.state.realtime_server = realtime_server
    app.state.dm_manager = dm_manager

    # Health check
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}

    # Auth endpoints
    @app.post("/api/auth/login", response_model=LoginResponse)
    async def login(request: LoginRequest):
        """Login and get JWT token."""
        # In production, validate credentials against database
        # For demo, accept any username with password "demo"
        if request.password != "demo":
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user_id = f"user_{hash(request.username) % 100000}"
        token = sign_token(
            user_id=user_id,
            username=request.username,
            email=f"{request.username}@example.com",
            secret=config.jwt.secret,
            ttl_hours=config.jwt.ttl_hours,
        )

        return LoginResponse(
            token=token,
            user_id=user_id,
            username=request.username,
        )

    @app.get("/api/auth/me")
    async def get_me(user: Optional[UserInfo] = Depends(get_current_user)):
        """Get current user info."""
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
        }

    # Realtime endpoints
    @app.get("/api/realtime/stats")
    async def get_stats(server: RealtimeServer = Depends(get_realtime_server)):
        """Get realtime server statistics."""
        return server.get_stats()

    @app.post("/api/realtime/publish")
    async def publish_message(
        request: PublishRequest,
        user: Optional[UserInfo] = Depends(get_current_user),
        server: RealtimeServer = Depends(get_realtime_server),
    ):
        """Publish a message to a channel via REST API."""
        message = Message(
            id=f"{int(datetime.now().timestamp() * 1000)}",
            type=MessageType(request.type) if request.type in MessageType.__members__ else MessageType.CHAT,
            channel=request.channel,
            data=request.data,
            user=user,
            timestamp=datetime.now(),
        )

        success = await server.publish(message)
        if not success:
            raise HTTPException(status_code=403, detail="Cannot publish to channel")

        return {"success": True, "message_id": message.id}

    # WebSocket endpoint
    @app.websocket("/ws")
    async def websocket_endpoint(
        websocket: WebSocket,
        token: Optional[str] = Query(None),
        server: RealtimeServer = Depends(get_realtime_server),
    ):
        """WebSocket connection for realtime communication."""
        await websocket.accept()

        # Authenticate
        user = None
        if token:
            try:
                claims = verify_token(token, config.jwt.secret)
                user = UserInfo(
                    id=claims.user_id,
                    username=claims.username,
                    email=claims.email,
                    role=claims.role,
                )
            except Exception:
                pass

        if not user:
            user = UserInfo(id="", username="anonymous")

        # Create and register client
        client = server.create_client(websocket, user)
        await server.register_client(client)

        try:
            while True:
                # Receive message
                data = await websocket.receive_text()
                msg = json.loads(data)

                action = msg.get("action", "")

                if action == "subscribe":
                    channel_id = msg.get("channel", "")
                    await server.subscribe(client, channel_id)

                elif action == "unsubscribe":
                    channel_id = msg.get("channel", "")
                    await server.unsubscribe(client, channel_id)

                elif action == "publish":
                    channel_id = msg.get("channel", "")
                    message = Message(
                        id=f"{int(datetime.now().timestamp() * 1000)}",
                        type=MessageType.CHAT,
                        channel=channel_id,
                        data=msg.get("data", {}),
                        user=user,
                        timestamp=datetime.now(),
                    )
                    await server.publish(message)

                elif action == "rpc":
                    method = msg.get("method", "")
                    params = msg.get("params", {})
                    try:
                        result = await server.execute_rpc(method, user, params)
                        await websocket.send_json({
                            "type": "rpc_response",
                            "method": method,
                            "result": result,
                        })
                    except Exception as e:
                        await websocket.send_json({
                            "type": "rpc_error",
                            "method": method,
                            "error": str(e),
                        })

                elif action == "ping":
                    await websocket.send_json({"type": "pong", "timestamp": datetime.now().isoformat()})

        except WebSocketDisconnect:
            pass
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            await server.unregister_client(client)

    # SSE endpoint
    @app.get("/api/sse/channel/{channel_id}")
    async def sse_channel(
        channel_id: str,
        request: Request,
        token: Optional[str] = Query(None),
        server: RealtimeServer = Depends(get_realtime_server),
    ):
        """SSE stream for a channel."""

        # Authenticate
        user = None
        if token:
            try:
                claims = verify_token(token, config.jwt.secret)
                user = UserInfo(
                    id=claims.user_id,
                    username=claims.username,
                    email=claims.email,
                    role=claims.role,
                )
            except Exception:
                pass

        client_id = f"sse_{int(datetime.now().timestamp() * 1000)}"
        queue = server.register_sse_channel_client(channel_id, client_id)

        async def event_generator():
            try:
                # Send initial connection event
                yield f"event: connected\ndata: {json.dumps({'client_id': client_id})}\n\n"

                while True:
                    # Check if client disconnected
                    if await request.is_disconnected():
                        break

                    try:
                        message = await asyncio.wait_for(queue.get(), timeout=30.0)
                        data = json.dumps(message.to_dict())
                        yield f"event: message\ndata: {data}\n\n"
                    except asyncio.TimeoutError:
                        # Send keepalive
                        yield f"event: ping\ndata: {json.dumps({'timestamp': datetime.now().isoformat()})}\n\n"
            finally:
                server.unregister_sse_channel_client(channel_id, client_id)

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    # DM endpoints
    @app.get("/api/dm/conversations")
    async def get_conversations(
        user: Optional[UserInfo] = Depends(get_current_user),
        dm_manager: DMManager = Depends(get_dm_manager),
    ):
        """Get user's conversations."""
        if not user or not user.id:
            raise HTTPException(status_code=401, detail="Not authenticated")

        conversations = dm_manager.get_user_conversations(user.id)
        return [conv.to_dict() for conv in conversations]

    @app.get("/api/dm/conversations/{conversation_id}/messages")
    async def get_dm_messages(
        conversation_id: str,
        limit: int = 50,
        before_id: Optional[str] = None,
        user: Optional[UserInfo] = Depends(get_current_user),
        dm_manager: DMManager = Depends(get_dm_manager),
    ):
        """Get messages from a conversation."""
        if not user or not user.id:
            raise HTTPException(status_code=401, detail="Not authenticated")

        messages = dm_manager.get_messages(conversation_id, limit, before_id)
        return [msg.to_dict() for msg in messages]

    @app.post("/api/dm/send")
    async def send_dm(
        request: DMRequest,
        user: Optional[UserInfo] = Depends(get_current_user),
        dm_manager: DMManager = Depends(get_dm_manager),
    ):
        """Send a direct message."""
        if not user or not user.id:
            raise HTTPException(status_code=401, detail="Not authenticated")

        message = await dm_manager.send_message(
            sender_id=user.id,
            sender_username=user.username,
            recipient_id=request.recipient_id,
            content=request.content,
        )

        return message.to_dict()

    @app.get("/api/dm/unread")
    async def get_unread_count(
        user: Optional[UserInfo] = Depends(get_current_user),
        dm_manager: DMManager = Depends(get_dm_manager),
    ):
        """Get unread message count."""
        if not user or not user.id:
            raise HTTPException(status_code=401, detail="Not authenticated")

        count = dm_manager.get_unread_count(user.id)
        return {"unread_count": count}

    # SSE for DM notifications
    @app.get("/api/dm/notifications")
    async def dm_notifications(
        request: Request,
        token: Optional[str] = Query(None),
        dm_manager: DMManager = Depends(get_dm_manager),
    ):
        """SSE stream for DM notifications."""

        # Authenticate
        user = None
        if token:
            try:
                claims = verify_token(token, config.jwt.secret)
                user = UserInfo(
                    id=claims.user_id,
                    username=claims.username,
                )
            except Exception:
                pass

        if not user or not user.id:
            raise HTTPException(status_code=401, detail="Not authenticated")

        queue = dm_manager.subscribe(user.id)

        async def event_generator():
            try:
                yield f"event: connected\ndata: {json.dumps({'user_id': user.id})}\n\n"

                while True:
                    if await request.is_disconnected():
                        break

                    try:
                        message = await asyncio.wait_for(queue.get(), timeout=30.0)
                        data = json.dumps(message.to_dict())
                        yield f"event: dm\ndata: {data}\n\n"
                    except asyncio.TimeoutError:
                        yield f"event: ping\ndata: {json.dumps({'timestamp': datetime.now().isoformat()})}\n\n"
            finally:
                dm_manager.unsubscribe(user.id, queue)

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )

    return app

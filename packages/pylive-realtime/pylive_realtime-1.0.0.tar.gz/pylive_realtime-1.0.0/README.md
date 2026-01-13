# PyLive

**Python Realtime Streaming Platform** - A complete realtime platform with WebSocket, SSE, Chat, DM, Groups, and Presence.

Inspired by GoLive architecture, ported to Python with FastAPI and Streamlit.

## Features

- **WebSocket Support** - Real-time bidirectional communication
- **SSE (Server-Sent Events)** - Lightweight unidirectional streaming
- **Channel System** - Subscribe/publish to named channels
- **Chat Rooms** - Full-featured chat with history
- **Direct Messages** - Private conversations between users
- **Presence Tracking** - Know who's online in channels
- **JWT Authentication** - Secure token-based auth
- **Moderation** - Ban/timeout users from channels
- **Streamlit UI** - Web interface included

## Installation

```bash
pip install pylive

# With Streamlit UI
pip install pylive[ui]
```

## Quick Start

### Start the Server

```bash
# Start API server
pylive serve

# With custom port
pylive serve --port 8080

# Development mode with auto-reload
pylive serve --reload
```

### Start the UI

```bash
# Start Streamlit UI (requires pylive[ui])
pylive ui
```

### Generate a Token

```bash
pylive token myusername
```

## API Endpoints

### REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login and get JWT token |
| GET | `/api/auth/me` | Get current user info |
| GET | `/api/realtime/stats` | Get server statistics |
| POST | `/api/realtime/publish` | Publish message to channel |
| GET | `/api/dm/conversations` | Get user's conversations |
| POST | `/api/dm/send` | Send direct message |

### WebSocket

Connect to `/ws?token=YOUR_JWT_TOKEN`

**Actions:**
```json
{"action": "subscribe", "channel": "chat:general"}
{"action": "unsubscribe", "channel": "chat:general"}
{"action": "publish", "channel": "chat:general", "data": {"content": "Hello!"}}
{"action": "ping"}
```

### SSE

- `/api/sse/channel/{channel_id}?token=TOKEN` - Subscribe to channel events
- `/api/dm/notifications?token=TOKEN` - Subscribe to DM notifications

## Python Usage

```python
from pylive import PyLiveServer, Config

# Create server with custom config
config = Config()
config.server.port = 8080
config.jwt.secret = "your-secret-key"

server = PyLiveServer(config)
server.run()
```

### Using the Realtime Server Directly

```python
from pylive.realtime import RealtimeServer, Message, MessageType, UserInfo

server = RealtimeServer()

# Register RPC handler
@server.register_rpc_handler("echo")
def echo_handler(ctx, user, params):
    return {"echo": params.get("message")}

# Publish a message
message = Message(
    id="msg_123",
    type=MessageType.CHAT,
    channel="chat:general",
    data={"content": "Hello!"},
    user=UserInfo(id="user_1", username="alice"),
)
await server.publish(message)
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PYLIVE_HOST` | Server host | `0.0.0.0` |
| `PYLIVE_PORT` | Server port | `8080` |
| `DATABASE_URL` | Database URL | `sqlite:///pylive.db` |
| `JWT_SECRET` | JWT signing secret | `change-me-in-production` |
| `JWT_TTL_HOURS` | Token TTL in hours | `24` |
| `LOG_LEVEL` | Log level | `INFO` |

### Config File

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8080
  },
  "jwt": {
    "secret": "your-secret-key",
    "ttl_hours": 24
  },
  "namespaces": {
    "chat": {
      "max_clients": 1000,
      "allow_publish": true,
      "allow_presence": true
    }
  }
}
```

## Architecture

```
pylive/
├── api/           # FastAPI routes and handlers
├── auth/          # JWT authentication
├── chat/          # Chat hub and DM manager
├── cli/           # CLI entry points
├── core/          # Server and configuration
├── realtime/      # WebSocket/SSE server
└── ui/            # Streamlit web interface
```

## License

MIT License

## Credits

- Inspired by [GoLive](https://github.com/Web3-League/golive) architecture
- Built with [FastAPI](https://fastapi.tiangolo.com/)
- UI powered by [Streamlit](https://streamlit.io/)

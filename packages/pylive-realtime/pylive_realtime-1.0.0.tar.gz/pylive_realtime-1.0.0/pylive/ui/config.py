"""UI Configuration."""

import os

UI_CONFIG = {
    "api_url": os.getenv("PYLIVE_API_URL", "http://localhost:8080"),
    "theme": {
        "background": "#0a0a0a",
        "foreground": "#fafafa",
        "primary": "#0ea5e9",
        "secondary": "#1e293b",
        "accent": "#f97316",
        "destructive": "#ef4444",
    }
}


def get_api_url() -> str:
    """Get API URL from config."""
    return UI_CONFIG["api_url"]


def get_ws_url() -> str:
    """Get WebSocket URL from API URL."""
    api = get_api_url()
    return api.replace("http://", "ws://").replace("https://", "wss://") + "/ws"

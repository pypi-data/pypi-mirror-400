"""API client for UI."""

import requests
from typing import Optional, Dict, Any
import streamlit as st

from pylive.ui.config import get_api_url
from pylive.ui.state import get_token


class APIClient:
    """HTTP client for PyLive API."""

    def __init__(self):
        self.base_url = get_api_url()

    def _headers(self) -> Dict[str, str]:
        """Get request headers with auth token."""
        headers = {"Content-Type": "application/json"}
        token = get_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def get(self, endpoint: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Make GET request."""
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                headers=self._headers(),
                params=params,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"API Error: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {e}")
            return None

    def post(self, endpoint: str, data: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Make POST request."""
        try:
            response = requests.post(
                f"{self.base_url}{endpoint}",
                headers=self._headers(),
                json=data,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"API Error: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {e}")
            return None


# Singleton instance
_client: Optional[APIClient] = None


def get_client() -> APIClient:
    """Get API client instance."""
    global _client
    if _client is None:
        _client = APIClient()
    return _client


# Convenience functions

def login(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Login and get token."""
    return get_client().post("/api/auth/login", {
        "username": username,
        "password": password,
    })


def get_me() -> Optional[Dict[str, Any]]:
    """Get current user info."""
    return get_client().get("/api/auth/me")


def get_stats() -> Optional[Dict[str, Any]]:
    """Get server statistics."""
    return get_client().get("/api/realtime/stats")


def get_health() -> Optional[Dict[str, Any]]:
    """Get server health."""
    return get_client().get("/health")


def publish_message(channel: str, content: str, msg_type: str = "chat") -> Optional[Dict[str, Any]]:
    """Publish message to channel."""
    return get_client().post("/api/realtime/publish", {
        "channel": channel,
        "data": {"content": content},
        "type": msg_type,
    })


def get_conversations() -> Optional[list]:
    """Get user conversations."""
    return get_client().get("/api/dm/conversations")


def get_dm_messages(conversation_id: str, limit: int = 50) -> Optional[list]:
    """Get messages from conversation."""
    return get_client().get(f"/api/dm/conversations/{conversation_id}/messages", {"limit": limit})


def send_dm(recipient_id: str, content: str) -> Optional[Dict[str, Any]]:
    """Send direct message."""
    return get_client().post("/api/dm/send", {
        "recipient_id": recipient_id,
        "content": content,
    })


def get_unread_count() -> Optional[Dict[str, Any]]:
    """Get unread message count."""
    return get_client().get("/api/dm/unread")

"""Session state management."""

import streamlit as st
from typing import Optional, Dict, Any, List


def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        "token": None,
        "user": None,
        "messages": [],
        "current_channel": None,
        "page": "chat",
        "selected_conversation": None,
        "ws_connected": False,
    }

    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default


def get_user() -> Optional[Dict[str, Any]]:
    """Get current user from session."""
    return st.session_state.get("user")


def get_token() -> Optional[str]:
    """Get JWT token from session."""
    return st.session_state.get("token")


def is_authenticated() -> bool:
    """Check if user is authenticated."""
    return st.session_state.get("user") is not None


def set_user(user: Dict[str, Any], token: str):
    """Set user and token in session."""
    st.session_state.user = user
    st.session_state.token = token


def logout():
    """Clear user session."""
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.messages = []
    st.session_state.current_channel = None


def get_messages() -> List[Dict[str, Any]]:
    """Get chat messages from session."""
    return st.session_state.get("messages", [])


def add_message(message: Dict[str, Any]):
    """Add a message to session."""
    st.session_state.messages.append(message)


def clear_messages():
    """Clear all messages."""
    st.session_state.messages = []


def get_current_channel() -> Optional[str]:
    """Get current channel."""
    return st.session_state.get("current_channel")


def set_current_channel(channel: str):
    """Set current channel."""
    st.session_state.current_channel = channel
    clear_messages()


def get_page() -> str:
    """Get current page."""
    return st.session_state.get("page", "chat")


def set_page(page: str):
    """Set current page."""
    st.session_state.page = page

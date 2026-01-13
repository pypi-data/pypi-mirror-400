"""Message display components."""

import streamlit as st
import streamlit_shadcn_ui as ui
from typing import Dict, Any

from pylive.ui.state import get_user


def render_message(msg: Dict[str, Any], index: int):
    """Render a chat message."""
    username = msg.get("user", {}).get("username", "Unknown")
    content = msg.get("data", {}).get("content", str(msg.get("data", "")))
    timestamp = msg.get("timestamp", "")[:19]

    current_user = get_user()
    is_own = msg.get("user", {}).get("id") == (current_user.get("id") if current_user else None)

    with st.container():
        if is_own:
            # Own message - align right
            cols = st.columns([3, 7])
            with cols[1]:
                st.markdown(
                    f"""
                    <div style="
                        background: #1e40af;
                        padding: 0.75rem 1rem;
                        border-radius: 1rem 1rem 0.25rem 1rem;
                        margin-bottom: 0.5rem;
                    ">
                        <div style="font-size: 0.75rem; color: #93c5fd; margin-bottom: 0.25rem;">
                            {username} · {timestamp}
                        </div>
                        <div style="color: #fff;">{content}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            # Other message - align left
            cols = st.columns([7, 3])
            with cols[0]:
                st.markdown(
                    f"""
                    <div style="
                        background: #27272a;
                        padding: 0.75rem 1rem;
                        border-radius: 1rem 1rem 1rem 0.25rem;
                        margin-bottom: 0.5rem;
                    ">
                        <div style="font-size: 0.75rem; color: #a1a1aa; margin-bottom: 0.25rem;">
                            {username} · {timestamp}
                        </div>
                        <div style="color: #fafafa;">{content}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


def render_system_message(msg: Dict[str, Any], index: int):
    """Render a system/join/leave message."""
    username = msg.get("user", {}).get("username", "Unknown")
    msg_type = msg.get("type", "system")

    if msg_type == "join":
        text = f"→ {username} joined the channel"
        color = "#22c55e"
    elif msg_type == "leave":
        text = f"← {username} left the channel"
        color = "#ef4444"
    else:
        text = msg.get("data", {}).get("content", "System message")
        color = "#6b7280"

    st.markdown(
        f"""
        <div style="
            text-align: center;
            color: {color};
            font-size: 0.875rem;
            padding: 0.5rem;
        ">
            {text}
        </div>
        """,
        unsafe_allow_html=True
    )

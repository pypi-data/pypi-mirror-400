"""Chat page."""

import streamlit as st
import streamlit_shadcn_ui as ui
from datetime import datetime

from pylive.ui.api import publish_message
from pylive.ui.state import (
    get_messages,
    add_message,
    get_current_channel,
    set_current_channel,
    get_user,
)
from pylive.ui.components.message import render_message, render_system_message


def render_chat_page():
    """Render the chat page."""
    st.markdown("## 💬 Chat")

    # Channel selection
    col1, col2 = st.columns([5, 1])

    with col1:
        channel = ui.input(
            default_value=get_current_channel() or "chat:general",
            placeholder="Channel (e.g., chat:general)",
            key="channel_input"
        )

    with col2:
        if ui.button("Join", key="join_btn", variant="default"):
            if channel:
                set_current_channel(channel)
                st.rerun()

    current_channel = get_current_channel()

    if not current_channel:
        st.markdown("""
        <div style="
            text-align: center;
            padding: 3rem;
            background: #18181b;
            border-radius: 1rem;
            margin-top: 2rem;
        ">
            <h3>No Channel Selected</h3>
            <p style="color: #a1a1aa;">Enter a channel name and click 'Join' to start chatting.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # Channel header
    st.markdown(f"""
    <div style="
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem 1rem;
        background: #18181b;
        border-radius: 0.5rem;
        margin: 1rem 0;
    ">
        <span style="color: #22c55e;">●</span>
        <span style="font-weight: 600;">{current_channel}</span>
        <span style="color: #6b7280; font-size: 0.875rem;">• Connected</span>
    </div>
    """, unsafe_allow_html=True)

    # Messages container
    messages_container = st.container()

    with messages_container:
        messages = get_messages()

        if not messages:
            st.markdown("""
            <div style="
                text-align: center;
                padding: 2rem;
                color: #6b7280;
            ">
                No messages yet. Start the conversation!
            </div>
            """, unsafe_allow_html=True)
        else:
            for i, msg in enumerate(messages[-50:]):
                msg_type = msg.get("type", "chat")

                if msg_type in ["join", "leave", "system"]:
                    render_system_message(msg, i)
                else:
                    render_message(msg, i)

    st.markdown("---")

    # Message input
    col1, col2 = st.columns([6, 1])

    with col1:
        message = ui.input(
            placeholder="Type a message...",
            key="message_input"
        )

    with col2:
        send_clicked = ui.button("Send", key="send_btn", variant="default")

    if send_clicked and message:
        result = publish_message(current_channel, message)

        if result:
            user = get_user()
            add_message({
                "type": "chat",
                "user": user,
                "data": {"content": message},
                "timestamp": datetime.now().isoformat(),
            })
            st.rerun()

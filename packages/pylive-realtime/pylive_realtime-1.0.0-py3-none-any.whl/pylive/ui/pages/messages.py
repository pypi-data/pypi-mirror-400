"""Direct messages page."""

import streamlit as st
import streamlit_shadcn_ui as ui

from pylive.ui.api import get_conversations, send_dm, get_dm_messages
from pylive.ui.state import get_user


def render_messages_page():
    """Render the direct messages page."""
    st.markdown("## ✉️ Direct Messages")

    col1, col2 = st.columns([1, 2])

    with col1:
        render_conversations_list()

    with col2:
        render_compose_message()


def render_conversations_list():
    """Render the conversations list."""
    st.markdown("### Conversations")

    conversations = get_conversations()
    user = get_user()

    if not conversations:
        st.markdown("""
        <div style="
            padding: 1.5rem;
            background: #18181b;
            border-radius: 0.75rem;
            text-align: center;
        ">
            <p style="color: #6b7280;">No conversations yet</p>
            <p style="color: #4b5563; font-size: 0.875rem;">
                Start a new conversation!
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    for conv in conversations:
        participants = [
            p for p in conv.get("participants", [])
            if p != (user.get("id") if user else None)
        ]
        display_name = ", ".join(participants) if participants else "Self"
        last_msg_time = conv.get("last_message_at", "")[:10]

        st.markdown(f"""
        <div style="
            padding: 0.75rem 1rem;
            background: #27272a;
            border-radius: 0.5rem;
            margin-bottom: 0.5rem;
            cursor: pointer;
            transition: background 0.2s;
        ">
            <div style="font-weight: 500;">{display_name}</div>
            <div style="font-size: 0.75rem; color: #6b7280;">{last_msg_time}</div>
        </div>
        """, unsafe_allow_html=True)


def render_compose_message():
    """Render the compose message form."""
    st.markdown("### New Message")

    st.markdown("""
    <div style="
        padding: 1.5rem;
        background: #18181b;
        border-radius: 0.75rem;
    ">
    """, unsafe_allow_html=True)

    recipient = ui.input(
        placeholder="Recipient User ID",
        key="dm_recipient"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    message = st.text_area(
        "Message",
        key="dm_message",
        height=120,
        placeholder="Write your message here..."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if ui.button("Send Message", key="dm_send_btn", variant="default"):
        if recipient and message:
            result = send_dm(recipient, message)

            if result:
                st.success("Message sent!")
                st.rerun()
        else:
            st.warning("Please enter recipient and message")

    st.markdown("</div>", unsafe_allow_html=True)

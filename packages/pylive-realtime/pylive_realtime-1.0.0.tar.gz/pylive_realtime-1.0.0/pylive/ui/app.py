"""
PyLive Streamlit Application.

Main entry point for the Streamlit UI.
"""

import streamlit as st

from pylive.ui.state import init_session_state, is_authenticated, get_page
from pylive.ui.pages import (
    render_login_page,
    render_chat_page,
    render_messages_page,
    render_stats_page,
)
from pylive.ui.components import render_navbar
from pylive.ui.styles import apply_custom_styles


def main():
    """Main Streamlit application."""
    # Page config
    st.set_page_config(
        page_title="PyLive",
        page_icon="🔴",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # Apply custom styles
    apply_custom_styles()

    # Initialize session state
    init_session_state()

    # Check authentication
    if not is_authenticated():
        render_login_page()
        return

    # Render navbar
    render_navbar()

    st.markdown("---")

    # Route to page
    page = get_page()

    if page == "chat":
        render_chat_page()
    elif page == "messages":
        render_messages_page()
    elif page == "stats":
        render_stats_page()
    else:
        render_chat_page()


if __name__ == "__main__":
    main()

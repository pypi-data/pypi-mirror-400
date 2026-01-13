"""Navigation bar component."""

import streamlit as st
import streamlit_shadcn_ui as ui

from pylive.ui.state import get_user, logout, set_page


def render_navbar():
    """Render the navigation bar."""
    cols = st.columns([2, 6, 2])

    with cols[0]:
        st.markdown("### 🔴 PyLive")

    with cols[1]:
        selected = ui.tabs(
            options=["Chat", "Messages", "Stats"],
            default_value="Chat",
            key="nav_tabs"
        )
        if selected:
            set_page(selected.lower())

    with cols[2]:
        user = get_user()
        if user:
            col1, col2 = st.columns([2, 1])
            with col1:
                ui.badge(
                    text=user["username"],
                    variant="secondary",
                    key="user_badge"
                )
            with col2:
                if ui.button("Logout", key="logout_btn", variant="outline", size="sm"):
                    logout()
                    st.rerun()

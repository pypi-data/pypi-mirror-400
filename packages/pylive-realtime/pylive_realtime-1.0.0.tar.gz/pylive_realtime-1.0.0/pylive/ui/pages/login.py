"""Login page."""

import streamlit as st
import streamlit_shadcn_ui as ui

from pylive.ui.api import login
from pylive.ui.state import set_user


def render_login_page():
    """Render the login page."""
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="font-size: 3rem; margin-bottom: 0.5rem;">🔴 PyLive</h1>
            <p style="color: #a1a1aa;">Realtime Streaming Platform</p>
        </div>
        """, unsafe_allow_html=True)

        # Login form container
        st.markdown("""
        <div style="
            background: #18181b;
            padding: 2rem;
            border-radius: 1rem;
            border: 1px solid #27272a;
        ">
        """, unsafe_allow_html=True)

        st.markdown("### Sign In")

        username = ui.input(
            placeholder="Username",
            key="login_username"
        )

        password = ui.input(
            type="password",
            placeholder="Password",
            key="login_password"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if ui.button("Sign In", key="login_btn", variant="default"):
            if username and password:
                result = login(username, password)

                if result:
                    set_user(
                        user={
                            "id": result["user_id"],
                            "username": result["username"],
                        },
                        token=result["token"]
                    )
                    st.rerun()
            else:
                st.warning("Please enter username and password")

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div style="
            text-align: center;
            margin-top: 1rem;
            padding: 1rem;
            background: #1e293b;
            border-radius: 0.5rem;
            color: #94a3b8;
        ">
            💡 Demo: Use any username with password <code>demo</code>
        </div>
        """, unsafe_allow_html=True)

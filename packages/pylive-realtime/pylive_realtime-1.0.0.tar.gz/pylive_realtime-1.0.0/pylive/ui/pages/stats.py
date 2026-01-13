"""Statistics page."""

import streamlit as st
import streamlit_shadcn_ui as ui

from pylive.ui.api import get_stats, get_health
from pylive.ui.components.cards import render_metric_card, render_status_badge


def render_stats_page():
    """Render the statistics page."""
    st.markdown("## 📊 Server Statistics")

    # Fetch data
    stats = get_stats()
    health = get_health()

    # Metrics
    if stats:
        cols = st.columns(3)

        with cols[0]:
            render_metric_card(
                title="Total Channels",
                value=str(stats.get("total_channels", 0)),
                description="Active channels",
                key="metric_channels"
            )

        with cols[1]:
            render_metric_card(
                title="WebSocket Clients",
                value=str(stats.get("total_clients", 0)),
                description="Connected clients",
                key="metric_clients"
            )

        with cols[2]:
            render_metric_card(
                title="SSE Streams",
                value=str(stats.get("total_sse_clients", 0)),
                description="Active SSE connections",
                key="metric_sse"
            )

    st.markdown("---")

    # Health status
    st.markdown("### Server Health")

    if health:
        status = health.get("status", "unknown")
        timestamp = health.get("timestamp", "")

        col1, col2 = st.columns([1, 3])

        with col1:
            render_status_badge(status, "health_badge")

        with col2:
            st.markdown(f"""
            <div style="
                padding: 1rem;
                background: #18181b;
                border-radius: 0.5rem;
            ">
                <div style="color: #a1a1aa; font-size: 0.875rem;">Last Check</div>
                <div style="font-family: monospace;">{timestamp}</div>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.error("Unable to fetch server health")

    # Connection info
    st.markdown("---")
    st.markdown("### Connection Info")

    from pylive.ui.config import get_api_url, get_ws_url

    st.markdown(f"""
    <div style="
        padding: 1rem;
        background: #18181b;
        border-radius: 0.5rem;
        font-family: monospace;
        font-size: 0.875rem;
    ">
        <div style="margin-bottom: 0.5rem;">
            <span style="color: #6b7280;">API:</span> {get_api_url()}
        </div>
        <div style="margin-bottom: 0.5rem;">
            <span style="color: #6b7280;">WebSocket:</span> {get_ws_url()}
        </div>
        <div>
            <span style="color: #6b7280;">Health:</span> {get_api_url()}/health
        </div>
    </div>
    """, unsafe_allow_html=True)

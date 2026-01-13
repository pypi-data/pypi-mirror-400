"""Card components."""

import streamlit as st
import streamlit_shadcn_ui as ui


def render_metric_card(title: str, value: str, description: str, key: str):
    """Render a metric card."""
    ui.metric_card(
        title=title,
        content=value,
        description=description,
        key=key
    )


def render_info_card(title: str, description: str, key: str):
    """Render an info card."""
    ui.card(
        title=title,
        description=description,
        key=key
    ).render()


def render_status_badge(status: str, key: str):
    """Render a status badge."""
    if status.lower() in ["healthy", "online", "connected"]:
        variant = "default"
    elif status.lower() in ["warning", "degraded"]:
        variant = "secondary"
    else:
        variant = "destructive"

    ui.badge(
        text=status.upper(),
        variant=variant,
        key=key
    )

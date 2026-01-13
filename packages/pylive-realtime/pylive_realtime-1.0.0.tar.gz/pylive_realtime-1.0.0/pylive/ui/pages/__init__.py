"""UI Pages."""

from pylive.ui.pages.login import render_login_page
from pylive.ui.pages.chat import render_chat_page
from pylive.ui.pages.messages import render_messages_page
from pylive.ui.pages.stats import render_stats_page

__all__ = [
    "render_login_page",
    "render_chat_page",
    "render_messages_page",
    "render_stats_page",
]

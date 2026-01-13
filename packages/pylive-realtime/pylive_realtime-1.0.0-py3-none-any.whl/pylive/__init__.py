"""
PyLive - Python Realtime Streaming Platform

A complete realtime platform with WebSocket, SSE, Chat, DM, Groups, and Presence.
Inspired by GoLive architecture.
"""

__version__ = "1.0.0"
__author__ = "nano3"

from pylive.core.server import PyLiveServer
from pylive.core.config import Config

__all__ = ["PyLiveServer", "Config", "__version__"]

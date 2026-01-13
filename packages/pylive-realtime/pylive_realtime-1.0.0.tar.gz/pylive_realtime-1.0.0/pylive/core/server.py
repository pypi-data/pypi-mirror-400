"""
Main PyLive server - combines all components.
"""

import asyncio
import logging
import signal
from typing import Optional

import uvicorn

from pylive.core.config import Config
from pylive.api.routes import create_app

logger = logging.getLogger("pylive")


class PyLiveServer:
    """
    Main PyLive server class.

    Combines FastAPI app with realtime services.
    """

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config.load()
        self.app = create_app(self.config)
        self._server: Optional[uvicorn.Server] = None

    def run(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        reload: bool = False,
        workers: int = 1,
    ) -> None:
        """
        Run the server.

        Args:
            host: Host to bind to (default from config)
            port: Port to bind to (default from config)
            reload: Enable auto-reload for development
            workers: Number of worker processes
        """
        host = host or self.config.server.host
        port = port or self.config.server.port

        # Configure logging
        logging.basicConfig(
            level=getattr(logging, self.config.logging.level.upper()),
            format=self.config.logging.format,
        )

        logger.info(f"Starting PyLive server on {host}:{port}")

        uvicorn_config = uvicorn.Config(
            app=self.app,
            host=host,
            port=port,
            reload=reload,
            workers=workers,
            log_level=self.config.logging.level.lower(),
        )

        self._server = uvicorn.Server(uvicorn_config)

        # Run server
        self._server.run()

    async def start_async(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ) -> None:
        """Start server asynchronously."""
        host = host or self.config.server.host
        port = port or self.config.server.port

        uvicorn_config = uvicorn.Config(
            app=self.app,
            host=host,
            port=port,
            log_level=self.config.logging.level.lower(),
        )

        self._server = uvicorn.Server(uvicorn_config)
        await self._server.serve()

    async def stop(self) -> None:
        """Stop the server."""
        if self._server:
            self._server.should_exit = True
            logger.info("Server shutdown initiated")

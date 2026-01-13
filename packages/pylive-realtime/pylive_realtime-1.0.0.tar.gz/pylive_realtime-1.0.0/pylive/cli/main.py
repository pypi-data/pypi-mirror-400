"""
CLI entry point for PyLive.

Usage:
    pylive serve [--host HOST] [--port PORT] [--reload]
    pylive ui [--port PORT]
    pylive --version
"""

import argparse
import sys
import logging

from pylive import __version__


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="pylive",
        description="PyLive - Realtime Streaming Platform",
    )

    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"pylive {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start the API server")
    serve_parser.add_argument(
        "--host", "-H",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)",
    )
    serve_parser.add_argument(
        "--port", "-p",
        type=int,
        default=8080,
        help="Port to bind to (default: 8080)",
    )
    serve_parser.add_argument(
        "--reload", "-r",
        action="store_true",
        help="Enable auto-reload for development",
    )
    serve_parser.add_argument(
        "--workers", "-w",
        type=int,
        default=1,
        help="Number of worker processes (default: 1)",
    )
    serve_parser.add_argument(
        "--config", "-c",
        type=str,
        help="Path to config file",
    )
    serve_parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Log level (default: INFO)",
    )

    # UI command
    ui_parser = subparsers.add_parser("ui", help="Start the Streamlit UI")
    ui_parser.add_argument(
        "--port", "-p",
        type=int,
        default=8501,
        help="Port for Streamlit (default: 8501)",
    )
    ui_parser.add_argument(
        "--api-url",
        type=str,
        default="http://localhost:8080",
        help="API server URL (default: http://localhost:8080)",
    )

    # Token command
    token_parser = subparsers.add_parser("token", help="Generate a JWT token")
    token_parser.add_argument("username", help="Username for the token")
    token_parser.add_argument(
        "--secret", "-s",
        type=str,
        default="change-me-in-production",
        help="JWT secret",
    )
    token_parser.add_argument(
        "--ttl",
        type=int,
        default=24,
        help="Token TTL in hours (default: 24)",
    )

    args = parser.parse_args()

    if args.command == "serve":
        run_server(args)
    elif args.command == "ui":
        run_ui(args)
    elif args.command == "token":
        generate_token(args)
    else:
        parser.print_help()
        sys.exit(1)


def run_server(args):
    """Run the API server."""
    from pylive.core.config import Config
    from pylive.core.server import PyLiveServer

    # Load config
    config = Config.load(args.config)
    config.server.host = args.host
    config.server.port = args.port
    config.logging.level = args.log_level

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    print(f"""
╔═══════════════════════════════════════════════════════╗
║                    PyLive Server                       ║
║        Realtime Streaming Platform                     ║
╠═══════════════════════════════════════════════════════╣
║  API:        http://{args.host}:{args.port}                    ║
║  WebSocket:  ws://{args.host}:{args.port}/ws                   ║
║  Health:     http://{args.host}:{args.port}/health             ║
║  Docs:       http://{args.host}:{args.port}/docs               ║
╚═══════════════════════════════════════════════════════╝
    """)

    # Start server
    server = PyLiveServer(config)
    server.run(
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers,
    )


def run_ui(args):
    """Run the Streamlit UI."""
    import subprocess
    import os

    # Get path to streamlit app
    ui_path = os.path.join(os.path.dirname(__file__), "..", "ui", "app.py")

    if not os.path.exists(ui_path):
        print("Error: Streamlit UI not found. Make sure pylive is installed correctly.")
        sys.exit(1)

    print(f"""
╔═══════════════════════════════════════════════════════╗
║                    PyLive UI                           ║
║           Streamlit Web Interface                      ║
╠═══════════════════════════════════════════════════════╣
║  URL:      http://localhost:{args.port}                       ║
║  API:      {args.api_url}                       ║
╚═══════════════════════════════════════════════════════╝
    """)

    # Set environment variable for API URL
    os.environ["PYLIVE_API_URL"] = args.api_url

    # Run streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        ui_path,
        "--server.port", str(args.port),
        "--server.headless", "true",
    ])


def generate_token(args):
    """Generate a JWT token."""
    from pylive.auth.jwt import sign_token

    token = sign_token(
        user_id=f"user_{hash(args.username) % 100000}",
        username=args.username,
        email=f"{args.username}@example.com",
        secret=args.secret,
        ttl_hours=args.ttl,
    )

    print(f"""
JWT Token for {args.username}:
────────────────────────────────────────────────────────
{token}
────────────────────────────────────────────────────────
Expires in: {args.ttl} hours
    """)


if __name__ == "__main__":
    main()

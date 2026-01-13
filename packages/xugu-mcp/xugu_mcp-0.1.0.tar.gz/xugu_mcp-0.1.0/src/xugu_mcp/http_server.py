"""
XuguDB MCP Server - HTTP/SSE Entry Point

A Model Context Protocol server for XuguDB (虚谷数据库)
with Chat2SQL support and full DDL/DML operations.
Runs as an HTTP server using Server-Sent Events (SSE) transport.

This module imports the server configuration from main.py to avoid
duplicating tool definitions.
"""
import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import uvicorn
from mcp.server.sse import SseServerTransport

from .config.settings import get_settings
from .utils.logging import get_mcp_logger

# Import the server and tools from main module
# This avoids duplicating all the tool definitions
from .main import server

# Initialize logger
mcp_logger = get_mcp_logger()
logger = mcp_logger.get_logger(__name__)

# Get settings
settings = get_settings()


# =============================================================================
# HTTP Server Setup
# =============================================================================

def create_mcp_asgi_app():
    """Create the ASGI application for MCP SSE transport."""
    # Create SSE transport (shared across all requests)
    sse_transport = SseServerTransport("/messages/")

    # Debug: Check if server has tools registered
    logger.info(f"Creating ASGI app with server: {server.name}")
    logger.info(f"Tool cache has {len(server._tool_cache)} tools")

    async def asgi_app(scope, receive, send):
        """Main ASGI application that routes requests."""
        # Get the path from scope
        path = scope.get("path", "")

        # Route based on path
        if path == "/sse":
            # Handle SSE connection with server.run()
            # connect_sse returns an async context manager that yields (read_stream, write_stream)
            logger.debug("SSE connection requested")
            async with sse_transport.connect_sse(scope, receive, send) as (read_stream, write_stream):
                # Run the MCP server with the streams
                logger.debug("Starting server.run()")
                try:
                    await server.run(
                        read_stream,
                        write_stream,
                        server.create_initialization_options()
                    )
                except Exception as e:
                    logger.error(f"Server.run() error: {e}")
                    import traceback
                    traceback.print_exc()
        elif path == "/messages/":
            # handle_post_message is an async method
            logger.debug("POST message received")
            await sse_transport.handle_post_message(scope, receive, send)
        else:
            # Return 404 for unknown paths
            await send({
                "type": "http.response.start",
                "status": 404,
                "headers": [[b"content-type", b"text/plain"]],
            })
            await send({
                "type": "http.response.body",
                "body": b"Not Found",
            })

    return asgi_app


def main():
    """Main entry point for the HTTP MCP server."""
    # Get HTTP server settings
    http_host = getattr(settings, "http", None)
    if http_host is None:
        # Use default values if HTTP settings not configured
        host = "0.0.0.0"
        port = 8000
    else:
        host = getattr(http_host, "host", "0.0.0.0")
        port = getattr(http_host, "port", 8000)

    logger.info(f"Starting {settings.mcp_server.name} v{settings.mcp_server.version} (HTTP mode)")
    logger.info(f"XuguDB connection: {settings.xugu.host}:{settings.xugu.port}/{settings.xugu.database}")
    logger.info(f"HTTP server will listen on http://{host}:{port}")

    # Test database connection
    try:
        from .db.connection import get_connection_manager
        conn_mgr = get_connection_manager()
        if conn_mgr.ping():
            logger.info("Successfully connected to XuguDB")
        else:
            logger.warning("Database connection test failed")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        logger.warning("Server will start but database operations may fail")

    # Create ASGI app
    app = create_mcp_asgi_app()

    # Run uvicorn server
    try:
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
        )
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    finally:
        from .db.connection import close_connection
        close_connection()
        logger.info("Server shutdown complete")


if __name__ == "__main__":
    main()

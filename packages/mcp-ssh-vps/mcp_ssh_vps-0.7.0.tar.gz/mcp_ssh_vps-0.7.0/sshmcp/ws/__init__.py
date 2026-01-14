"""WebSocket support for real-time shell sessions."""

from sshmcp.ws.shell import ShellWebSocketHandler, create_ws_app

__all__ = ["ShellWebSocketHandler", "create_ws_app"]

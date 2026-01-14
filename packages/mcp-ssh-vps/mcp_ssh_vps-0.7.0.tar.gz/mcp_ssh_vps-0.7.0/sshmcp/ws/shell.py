"""WebSocket handler for real-time SSH shell sessions.

Provides bidirectional real-time communication for interactive shell sessions.
Can be integrated with FastAPI/Starlette applications.

Example usage with FastAPI:
    from fastapi import FastAPI, WebSocket
    from sshmcp.ws import ShellWebSocketHandler

    app = FastAPI()
    handler = ShellWebSocketHandler()

    @app.websocket("/ws/shell/{host}")
    async def websocket_shell(websocket: WebSocket, host: str):
        await handler.handle(websocket, host)
"""

import asyncio
import json
from typing import Any, Protocol

import structlog

from sshmcp.config import get_machine
from sshmcp.ssh.client import SSHClient

logger = structlog.get_logger()


class WebSocketProtocol(Protocol):
    """Protocol for WebSocket connections."""

    async def accept(self) -> None:
        """Accept the connection."""
        ...

    async def receive_text(self) -> str:
        """Receive text message."""
        ...

    async def send_text(self, data: str) -> None:
        """Send text message."""
        ...

    async def send_json(self, data: dict) -> None:
        """Send JSON message."""
        ...

    async def close(self, code: int = 1000) -> None:
        """Close the connection."""
        ...


class ShellWebSocketHandler:
    """
    WebSocket handler for interactive SSH shell sessions.

    Provides real-time bidirectional communication between
    web clients and SSH shell sessions.
    """

    def __init__(self, auth_callback: Any = None) -> None:
        """
        Initialize handler.

        Args:
            auth_callback: Optional async callback(websocket) -> bool for auth.
        """
        self.auth_callback = auth_callback
        self._active_sessions: dict[str, dict] = {}

    async def handle(
        self,
        websocket: WebSocketProtocol,
        host: str,
        term: str = "xterm-256color",
        width: int = 80,
        height: int = 24,
    ) -> None:
        """
        Handle WebSocket connection for shell session.

        Protocol:
        - Client sends JSON: {"type": "input", "data": "command\\n"}
        - Client sends JSON: {"type": "resize", "width": 120, "height": 40}
        - Server sends JSON: {"type": "output", "data": "..."}
        - Server sends JSON: {"type": "error", "message": "..."}
        - Server sends JSON: {"type": "closed"}

        Args:
            websocket: WebSocket connection.
            host: SSH host name.
            term: Terminal type.
            width: Initial terminal width.
            height: Initial terminal height.
        """
        await websocket.accept()
        session_id = f"ws-{id(websocket)}"

        # Optional authentication
        if self.auth_callback:
            try:
                if not await self.auth_callback(websocket):
                    await websocket.send_json(
                        {"type": "error", "message": "Authentication failed"}
                    )
                    await websocket.close(code=4001)
                    return
            except Exception as e:
                logger.error("ws_auth_error", error=str(e))
                await websocket.close(code=4001)
                return

        # Connect to SSH
        try:
            machine = get_machine(host)
            client = SSHClient(machine)
            client.connect()
        except Exception as e:
            await websocket.send_json(
                {"type": "error", "message": f"SSH connection failed: {e}"}
            )
            await websocket.close(code=4002)
            return

        # Open PTY channel
        try:
            transport = client._client.get_transport()
            if not transport:
                raise RuntimeError("No transport")

            channel = transport.open_session()
            channel.get_pty(term=term, width=width, height=height)
            channel.invoke_shell()
            channel.setblocking(0)

            self._active_sessions[session_id] = {
                "client": client,
                "channel": channel,
                "host": host,
            }

            logger.info("ws_shell_started", session_id=session_id, host=host)

            # Run input/output tasks concurrently
            await asyncio.gather(
                self._read_output(websocket, channel),
                self._read_input(websocket, channel),
                return_exceptions=True,
            )

        except Exception as e:
            logger.error("ws_shell_error", error=str(e))
            await websocket.send_json({"type": "error", "message": str(e)})
        finally:
            # Cleanup
            if session_id in self._active_sessions:
                session = self._active_sessions.pop(session_id)
                try:
                    session["channel"].close()
                    session["client"].disconnect()
                except Exception:
                    pass

            logger.info("ws_shell_closed", session_id=session_id)
            try:
                await websocket.send_json({"type": "closed"})
            except Exception:
                pass

    async def _read_output(self, websocket: WebSocketProtocol, channel: Any) -> None:
        """Read output from SSH channel and send to WebSocket."""
        while True:
            try:
                if channel.recv_ready():
                    data = channel.recv(4096).decode("utf-8", errors="replace")
                    if data:
                        await websocket.send_json({"type": "output", "data": data})
                elif channel.exit_status_ready():
                    break
                else:
                    await asyncio.sleep(0.01)
            except Exception:
                break

    async def _read_input(self, websocket: WebSocketProtocol, channel: Any) -> None:
        """Read input from WebSocket and send to SSH channel."""
        while True:
            try:
                text = await websocket.receive_text()
                msg = json.loads(text)

                if msg.get("type") == "input":
                    data = msg.get("data", "")
                    channel.send(data)
                elif msg.get("type") == "resize":
                    width = msg.get("width", 80)
                    height = msg.get("height", 24)
                    channel.resize_pty(width=width, height=height)
                elif msg.get("type") == "close":
                    break

            except Exception:
                break

    def get_active_sessions(self) -> list[dict]:
        """Get list of active WebSocket shell sessions."""
        return [
            {"session_id": sid, "host": info["host"]}
            for sid, info in self._active_sessions.items()
        ]


def create_ws_app(auth_callback: Any = None) -> Any:
    """
    Create a Starlette app with WebSocket shell endpoint.

    Example:
        from starlette.applications import Starlette
        from sshmcp.ws import create_ws_app

        # Mount WebSocket app
        main_app = Starlette(routes=[
            Mount("/ws", app=create_ws_app()),
        ])

    Returns:
        Starlette application with /shell/{host} WebSocket endpoint.
    """
    try:
        from starlette.applications import Starlette
        from starlette.routing import WebSocketRoute
        from starlette.websockets import WebSocket
    except ImportError:
        raise ImportError(
            "starlette is required for WebSocket support. "
            "Install with: pip install starlette"
        )

    handler = ShellWebSocketHandler(auth_callback=auth_callback)

    async def shell_endpoint(websocket: WebSocket) -> None:
        host = websocket.path_params.get("host", "")
        term = websocket.query_params.get("term", "xterm-256color")
        width = int(websocket.query_params.get("width", 80))
        height = int(websocket.query_params.get("height", 24))

        await handler.handle(websocket, host, term, width, height)

    app = Starlette(
        routes=[
            WebSocketRoute("/shell/{host}", shell_endpoint),
        ]
    )

    return app

"""
WebSocket client for real-time Mai-Tai workspace updates (v3 - workspace edition).

Provides automatic reconnection with exponential backoff per v2/runtime-loop.md.
Tracks connection state and re-syncs missed messages on reconnect.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional
from urllib.parse import urlencode

import websockets
from websockets.exceptions import ConnectionClosed, InvalidStatusCode

from .backoff import BackoffState
from .config import MaiTaiConfig
from .errors import FatalRuntimeError, RecoverableError

logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """WebSocket connection states."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"


@dataclass
class WorkspaceSubscription:
    """Tracks subscription state for a workspace."""
    workspace_id: str
    last_message_id: Optional[str] = None
    callback: Optional[Callable[[dict], None]] = None


@dataclass
class WebSocketClient:
    """WebSocket client with automatic reconnection and state tracking.

    Connects to the Mai-Tai backend WebSocket endpoint for real-time updates.
    Automatically reconnects with exponential backoff on disconnection.
    """
    config: MaiTaiConfig
    state: ConnectionState = field(default=ConnectionState.DISCONNECTED)
    backoff: BackoffState = field(default_factory=BackoffState)
    _ws: Optional[websockets.WebSocketClientProtocol] = field(default=None, repr=False)
    _subscriptions: dict[str, WorkspaceSubscription] = field(default_factory=dict)
    _shutdown: bool = field(default=False)
    _receive_task: Optional[asyncio.Task] = field(default=None, repr=False)

    def _get_ws_url(self, workspace_id: str) -> str:
        """Build WebSocket URL for a workspace."""
        # Convert http(s) to ws(s)
        base = self.config.api_url.rstrip("/")
        if base.startswith("https://"):
            ws_base = "wss://" + base[8:]
        elif base.startswith("http://"):
            ws_base = "ws://" + base[7:]
        else:
            ws_base = base

        params = urlencode({"token": self.config.api_key})
        return f"{ws_base}/api/v1/ws/{workspace_id}?{params}"

    async def connect(self, workspace_id: str, on_message: Optional[Callable[[dict], None]] = None) -> bool:
        """Connect to a workspace's WebSocket endpoint.

        Args:
            workspace_id: The workspace to subscribe to
            on_message: Optional callback for new messages

        Returns:
            True if connected successfully

        Raises:
            FatalRuntimeError: For auth failures
            RecoverableError: For transient errors
        """
        if self._shutdown:
            raise RecoverableError("Client is shutting down")

        self.state = ConnectionState.CONNECTING
        url = self._get_ws_url(workspace_id)

        try:
            logger.info(f"Connecting to WebSocket for workspace {workspace_id}")
            self._ws = await websockets.connect(url, ping_interval=20, ping_timeout=10)
            self.state = ConnectionState.CONNECTED
            self.backoff.reset()

            # Store subscription
            self._subscriptions[workspace_id] = WorkspaceSubscription(
                workspace_id=workspace_id,
                callback=on_message,
            )

            logger.info(f"WebSocket connected to workspace {workspace_id}")
            return True

        except InvalidStatusCode as e:
            self.state = ConnectionState.DISCONNECTED
            if e.status_code in (401, 403):
                raise FatalRuntimeError(f"WebSocket auth failed: {e.status_code}")
            elif e.status_code == 404:
                raise FatalRuntimeError(f"Workspace not found: {workspace_id}")
            else:
                self.backoff.record_failure()
                raise RecoverableError(f"WebSocket connection failed: {e.status_code}")

        except Exception as e:
            self.state = ConnectionState.DISCONNECTED
            self.backoff.record_failure()
            raise RecoverableError(f"WebSocket connection error: {e}")

    async def disconnect(self) -> None:
        """Gracefully disconnect from WebSocket."""
        self._shutdown = True

        if self._receive_task and not self._receive_task.done():
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass

        if self._ws:
            try:
                await self._ws.close()
            except Exception:
                pass
            self._ws = None

        self.state = ConnectionState.DISCONNECTED
        self._subscriptions.clear()
        logger.info("WebSocket disconnected")

    async def _receive_loop(self) -> None:
        """Receive and dispatch messages from WebSocket."""
        if not self._ws:
            return

        try:
            async for raw in self._ws:
                try:
                    data = json.loads(raw)
                    await self._handle_message(data)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from WebSocket: {raw[:100]}")
        except ConnectionClosed as e:
            logger.info(f"WebSocket connection closed: {e.code} {e.reason}")
            self.state = ConnectionState.DISCONNECTED
            self.backoff.record_failure()
        except Exception as e:
            logger.error(f"WebSocket receive error: {e}")
            self.state = ConnectionState.DISCONNECTED
            self.backoff.record_failure()

    async def _handle_message(self, data: dict) -> None:
        """Handle an incoming WebSocket message."""
        msg_type = data.get("type")

        if msg_type == "connected":
            workspace_id = data.get("workspace_id")
            logger.debug(f"Connection confirmed for workspace {workspace_id}")

        elif msg_type == "new_message":
            message = data.get("message", {})
            workspace_id = message.get("workspace_id")

            # Update last seen message ID
            if workspace_id in self._subscriptions:
                sub = self._subscriptions[workspace_id]
                sub.last_message_id = message.get("id")

                # Call the callback if registered
                if sub.callback:
                    try:
                        sub.callback(message)
                    except Exception as e:
                        logger.error(f"Message callback error: {e}")

        elif msg_type == "ping":
            # Respond to server pings
            if self._ws:
                await self._ws.send("pong")

        elif msg_type == "error":
            logger.warning(f"WebSocket error message: {data.get('message')}")

    def start_receiving(self) -> asyncio.Task:
        """Start the background receive loop.

        Returns:
            The asyncio Task running the receive loop
        """
        if self._receive_task and not self._receive_task.done():
            return self._receive_task

        self._receive_task = asyncio.create_task(self._receive_loop())
        return self._receive_task

    def get_last_message_id(self, workspace_id: str) -> Optional[str]:
        """Get the last seen message ID for a workspace.

        Used for re-syncing after reconnection.
        """
        if workspace_id in self._subscriptions:
            return self._subscriptions[workspace_id].last_message_id
        return None

    def set_last_message_id(self, workspace_id: str, message_id: str) -> None:
        """Set the last seen message ID for a workspace.

        Used to initialize state before connecting.
        """
        if workspace_id in self._subscriptions:
            self._subscriptions[workspace_id].last_message_id = message_id


async def create_ws_client(config: MaiTaiConfig) -> WebSocketClient:
    """Create a new WebSocket client instance.

    Args:
        config: Mai-Tai configuration

    Returns:
        Configured WebSocketClient ready to connect
    """
    return WebSocketClient(config=config)


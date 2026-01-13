"""
PhyHub Direct Connection Service

Allows direct connection to PhyHub for testing purposes,
bypassing the phyos layer that normally runs on devices.

Usage:
    - Set PHYHUB_DIRECT=true to enable direct connection
    - Provide DEVICE_ID and ACCESS_KEY environment variables
    - Optionally set PHYHUB_URL (defaults to EU region)
"""

import asyncio
import os
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

import socketio


DEFAULT_PHYHUB_URLS: dict[str, str] = {
    "eu": "https://phyhub.eu.omborigrid.net",
    "us": "https://phyhub.us.omborigrid.net",
    "uae": "https://phyhub.uae.omborigrid.net",
    "au": "https://phyhub.au.omborigrid.net",
    "in": "https://phyhub.in.omborigrid.net",
    "qa": "https://phyhub.qa.omborigrid.net",
    "dev": "https://phyhub.dev.omborigrid.net",
    "local": "http://localhost:3000",
}


def is_direct_mode() -> bool:
    """Check if running in direct connection mode (vs PhyOS mode)."""
    return os.environ.get("PHYHUB_DIRECT", "").lower() in ("true", "1")


@dataclass
class DirectConnectionConfig:
    """Configuration for direct PhyHub connection."""

    device_id: str
    access_key: str
    phyhub_url: str = field(default_factory=lambda: DEFAULT_PHYHUB_URLS["eu"])
    instance_id: Optional[str] = None


class PhyHubConnection:
    """Direct connection to PhyHub using Socket.IO."""

    def __init__(self, config: DirectConnectionConfig) -> None:
        self.config = config
        self._sio: Optional[socketio.AsyncClient] = None
        self._connected = False
        self._connect_event: Optional[asyncio.Event] = None
        self._listeners: dict[str, list[Callable[..., Any]]] = {}

    @classmethod
    def from_env(cls) -> "PhyHubConnection":
        """Create a direct connection from environment variables.

        Raises:
            ValueError: If required environment variables are missing.
        """
        device_id = os.environ.get("DEVICE_ID") or os.environ.get("PHYGRID_DEVICE_ID")
        access_key = os.environ.get("ACCESS_KEY") or os.environ.get("PHYGRID_DEVICE_KEY")

        if not device_id:
            raise ValueError(
                "[PhyHubConnection] DEVICE_ID or PHYGRID_DEVICE_ID env var required"
            )
        if not access_key:
            raise ValueError(
                "[PhyHubConnection] ACCESS_KEY or PHYGRID_DEVICE_KEY env var required"
            )

        region = os.environ.get("PHYHUB_REGION", "").lower()
        phyhub_url = os.environ.get("PHYHUB_URL") or DEFAULT_PHYHUB_URLS.get(region)

        if not phyhub_url:
            valid_regions = ", ".join(DEFAULT_PHYHUB_URLS.keys())
            raise ValueError(
                f"[PhyHubConnection] PHYHUB_URL or valid PHYHUB_REGION required. "
                f"Valid regions: {valid_regions}"
            )

        return cls(
            DirectConnectionConfig(
                device_id=device_id,
                access_key=access_key,
                phyhub_url=phyhub_url,
                instance_id=os.environ.get("TWIN_ID") or os.environ.get("INSTANCE_ID"),
            )
        )

    @staticmethod
    def is_enabled() -> bool:
        """Check if direct connection mode is enabled."""
        return os.environ.get("PHYHUB_DIRECT", "").lower() in ("true", "1")

    @property
    def device_id(self) -> str:
        """Get the device ID (also used as the primary twin ID)."""
        return self.config.device_id

    @property
    def instance_id(self) -> str:
        """Get the instance/twin ID to use."""
        return self.config.instance_id or self.config.device_id

    @property
    def is_connected(self) -> bool:
        """Check if currently connected."""
        return self._connected and self._sio is not None

    async def connect(self) -> socketio.AsyncClient:
        """Connect directly to PhyHub.

        Returns:
            The connected Socket.IO client.

        Raises:
            ConnectionError: If connection fails.
        """
        if self._sio and self._connected:
            return self._sio

        print(f"[PhyHubConnection] Connecting to {self.config.phyhub_url}")
        print(f"[PhyHubConnection] Device ID: {self.config.device_id}")

        self._sio = socketio.AsyncClient(
            reconnection=True,
            reconnection_attempts=5,
            reconnection_delay=1,
            logger=False,
            engineio_logger=False,
        )

        self._connect_event = asyncio.Event()

        @self._sio.event
        async def connect() -> None:
            self._connected = True
            print("[PhyHubConnection] Connected successfully")
            if self._connect_event:
                self._connect_event.set()

        @self._sio.event
        async def disconnect() -> None:
            self._connected = False
            print("[PhyHubConnection] Disconnected")

        @self._sio.event
        async def connect_error(data: Any) -> None:
            print(f"[PhyHubConnection] Connection error: {data}")
            if self._connect_event:
                self._connect_event.set()

        try:
            await self._sio.connect(
                self.config.phyhub_url,
                auth={
                    "deviceId": self.config.device_id,
                    "accessKey": self.config.access_key,
                },
                wait_timeout=15,
            )

            # Wait for connection confirmation
            await asyncio.wait_for(self._connect_event.wait(), timeout=15.0)

            if not self._connected:
                raise ConnectionError("Failed to connect to PhyHub")

            return self._sio

        except asyncio.TimeoutError:
            raise ConnectionError("Connection timeout")

    async def disconnect(self) -> None:
        """Disconnect from PhyHub."""
        if self._sio:
            await self._sio.disconnect()
            self._sio = None
            self._connected = False

    def get_socket(self) -> Optional[socketio.AsyncClient]:
        """Get the socket instance."""
        return self._sio

    async def emit(
        self,
        event: str,
        data: Any = None,
        callback: Optional[Callable[..., Any]] = None,
        response_event: Optional[str] = None,
    ) -> Any:
        """Emit an event to the server.

        Args:
            event: Event name.
            data: Data to send.
            callback: Optional callback for acknowledgement.
            response_event: Optional event name to wait for response.

        Returns:
            Response from server if callback pattern is used.
        """
        if not self._sio or not self._connected:
            raise ConnectionError("Not connected to PhyHub")

        if response_event:
            # Wait for a specific response event
            response_future: asyncio.Future[Any] = asyncio.get_event_loop().create_future()

            def on_response(data: Any) -> None:
                if not response_future.done():
                    response_future.set_result(data)

            self._sio.on(response_event, on_response)
            await self._sio.emit(event, data)

            try:
                result = await asyncio.wait_for(response_future, timeout=20)
                return result
            finally:
                # Clean up the listener - use handlers dict directly
                if response_event in self._sio.handlers.get("/", {}):
                    del self._sio.handlers["/"][response_event]
        elif callback:
            # Use callback pattern (ack-based)
            return await self._sio.call(event, data, timeout=20)
        else:
            await self._sio.emit(event, data)
            return None

    def on(self, event: str, handler: Callable[..., Any]) -> None:
        """Register an event handler.

        Args:
            event: Event name to listen for.
            handler: Handler function.
        """
        if self._sio:
            self._sio.on(event, handler)

        # Also store for reconnection
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(handler)

    def off(self, event: str, handler: Optional[Callable[..., Any]] = None) -> None:
        """Remove an event handler.

        Args:
            event: Event name.
            handler: Specific handler to remove, or None to remove all.
        """
        if event in self._listeners:
            if handler:
                self._listeners[event] = [h for h in self._listeners[event] if h != handler]
            else:
                self._listeners[event] = []

    async def __aenter__(self) -> "PhyHubConnection":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.disconnect()

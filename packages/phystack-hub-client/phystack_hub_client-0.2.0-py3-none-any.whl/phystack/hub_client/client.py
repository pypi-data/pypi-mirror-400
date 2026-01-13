"""
PhyHub Client

Main client for connecting to PhyHub and communicating with twins.
Provides events, actions, DataChannel, and MediaStream functionality.
"""

import asyncio
from typing import Any, Callable, Optional, Set

from phystack.hub_client.services.phyhub_connection import (
    PhyHubConnection,
    DirectConnectionConfig,
    is_direct_mode,
)
from phystack.hub_client.twin_messaging import (
    TwinMessaging,
    TwinMessagingContext,
    create_twin_messaging,
)
from phystack.hub_client.types.twin_types import (
    TwinMessageResult,
    TwinMessageResultStatus,
    TwinResponse,
    TwinProperties,
    EventPayload,
)
from phystack.hub_client.services.webrtc.data_channel import (
    DataChannelHandler,
    DataChannelOptions,
    PhygridDataChannel,
    TwinMessagingInterface as DataChannelMessaging,
)
from phystack.hub_client.services.webrtc.media_stream import (
    MediaStreamHandler,
    MediaStreamOptions,
    PhygridMediaStream,
    TwinMessagingInterface as MediaStreamMessaging,
)
from phystack.hub_client.instances.edge_instance import EdgeInstance
from phystack.hub_client.instances.peripheral_instance import PeripheralInstance
from phystack.hub_client.twin_registry import TwinRegistry


class PhyHubClient:
    """Client for connecting to PhyHub.

    Provides:
    - Connection management
    - Twin messaging (events and actions)
    - DataChannel (WebRTC P2P data)
    - MediaStream (WebRTC P2P video/audio)

    Usage:
        async with PhyHubClient.from_env() as client:
            instance = await client.get_instance()
            instance.on("my-event", lambda data, respond: print(data))
    """

    # Socket.IO event names
    class EVENTS:
        CONNECT = "connect"
        DISCONNECT = "disconnect"
        TWIN_MESSAGE = "twinMessage"
        TWIN_SUBSCRIBE = "twinSubscribe"
        TWIN_UPDATED = "twinUpdated"
        GET_TWIN_BY_ID = "getTwinById"
        REPORT_PROPERTIES = "reportPeripheralTwinProperties"

    def __init__(
        self,
        device_id: Optional[str] = None,
        access_key: Optional[str] = None,
        phyhub_url: Optional[str] = None,
        instance_id: Optional[str] = None,
    ) -> None:
        """Initialize PhyHub client.

        Args:
            device_id: Device identifier.
            access_key: Access key for authentication.
            phyhub_url: PhyHub server URL.
            instance_id: Optional specific twin ID to use.
        """
        self._connection: Optional[PhyHubConnection] = None
        self._instance_id: Optional[str] = instance_id
        self._instance: Optional[EdgeInstance] = None
        self._subscribed_twins: Set[str] = set()
        self._twin_message_listeners: dict[str, Set[Callable[[dict[str, Any]], None]]] = {}
        self._twin_update_listeners: dict[str, Set[Callable[[dict[str, Any]], None]]] = {}
        self._settings_update_listeners: Set[Callable[[dict[str, Any]], None]] = set()
        self._twin_data_cache: dict[str, dict[str, Any]] = {}
        self._connected = False
        self._registry: Optional[TwinRegistry] = None

        if device_id and access_key:
            self._connection = PhyHubConnection(
                DirectConnectionConfig(
                    device_id=device_id,
                    access_key=access_key,
                    phyhub_url=phyhub_url or "https://phyhub.eu.omborigrid.net",
                    instance_id=instance_id,
                )
            )

    @classmethod
    def from_env(cls) -> "PhyHubClient":
        """Create client from environment variables.

        Environment variables:
            DEVICE_ID or PHYGRID_DEVICE_ID: Device identifier
            ACCESS_KEY or PHYGRID_DEVICE_KEY: Access key
            PHYHUB_URL or PHYHUB_REGION: Server URL or region (eu, us, etc.)
            TWIN_ID or INSTANCE_ID: Optional specific twin ID

        Returns:
            Configured PhyHubClient instance.
        """
        client = cls()
        client._connection = PhyHubConnection.from_env()
        client._instance_id = client._connection.instance_id
        return client

    @property
    def is_connected(self) -> bool:
        """Check if connected to PhyHub."""
        return self._connected and self._connection is not None

    async def connect(self) -> "PhyHubClient":
        """Connect to PhyHub.

        Returns:
            Self for chaining.

        Raises:
            ConnectionError: If connection fails.
        """
        if not self._connection:
            raise ValueError("No connection configured. Use from_env() or provide credentials.")

        await self._connection.connect()
        self._connected = True

        # Create twin registry
        self._registry = TwinRegistry(self)

        # Set up event handlers
        self._setup_socket_listeners()

        # Authenticate and connect device
        await self._initialize_device_twin()

        return self

    async def disconnect(self) -> None:
        """Disconnect from PhyHub."""
        if self._connection:
            await self._connection.disconnect()
        self._connected = False
        self._instance = None
        if self._registry:
            self._registry.clear()

    def _setup_socket_listeners(self) -> None:
        """Set up Socket.IO event handlers."""
        if not self._connection:
            return

        def on_twin_message(payload: dict[str, Any], callback: Any = None) -> Any:
            """Handle incoming twin messages."""
            twin_id = payload.get("twinId")
            result: Optional[TwinMessageResult] = None

            if twin_id and payload.get("data"):
                listeners = self._twin_message_listeners.get(twin_id)
                if listeners:
                    for listener in listeners:
                        try:
                            listener(payload)
                            result = TwinMessageResult(
                                status=TwinMessageResultStatus.SUCCESS,
                                message="Action completed",
                            )
                        except Exception as e:
                            result = TwinMessageResult(
                                status=TwinMessageResultStatus.ERROR,
                                message=str(e),
                            )
                else:
                    result = TwinMessageResult(
                        status=TwinMessageResultStatus.WARNING,
                        message=f"No listeners found for twin {twin_id}",
                    )

                if callback and result:
                    return {"status": result.status.value, "message": result.message}

            return None

        self._connection.on(self.EVENTS.TWIN_MESSAGE, on_twin_message)

        def on_twin_updated(payload: dict[str, Any]) -> None:
            """Handle twin property update events."""
            twin_data = payload.get("data") or payload
            twin_id = payload.get("twinId") or (twin_data.get("id") if isinstance(twin_data, dict) else None)

            if not twin_id:
                return

            # Notify twin update listeners
            listeners = self._twin_update_listeners.get(twin_id)
            if listeners:
                for callback in listeners:
                    try:
                        callback(twin_data)
                    except Exception as e:
                        print(f"[PhyHubClient] Error in twin update listener: {e}")

            # Check for settings updates on edge instance
            if twin_id == self._instance_id and isinstance(twin_data, dict):
                props = twin_data.get("properties", {})
                desired = props.get("desired", {})
                settings = desired.get("settings", {})
                if settings and self._settings_update_listeners:
                    for callback in self._settings_update_listeners:
                        try:
                            callback(settings)
                        except Exception as e:
                            print(f"[PhyHubClient] Error in settings update listener: {e}")

        self._connection.on(self.EVENTS.TWIN_UPDATED, on_twin_updated)

    async def _initialize_device_twin(self) -> None:
        """Initialize device twin via authentication."""
        if not self._connection:
            return

        # Authenticate - server responds with deviceAuthenticated event
        print("[PhyHubClient] Authenticating...")
        auth_result = await self._connection.emit(
            "authenticate",
            {
                "deviceId": self._connection.device_id,
                "accessKey": self._connection.config.access_key,
            },
            response_event="deviceAuthenticated",
        )

        if auth_result.get("status") != "success":
            raise ConnectionError(f"Authentication failed: {auth_result.get('message')}")

        print(f"[PhyHubClient] Authenticated: {auth_result}")

        # Connect device - server uses callback pattern (no payload needed)
        print("[PhyHubClient] Connecting device...")
        connect_result = await self._connection.emit(
            "connectDevice",
            callback=True,
        )

        if connect_result.get("status") != "success":
            raise ConnectionError(f"Device connection failed: {connect_result.get('message')}")

        # Extract twin info - prefer server response for device twin ID
        twins = connect_result.get("twins", [])
        if twins:
            device_twin = next(
                (t for t in twins if t.get("type") == "Device"),
                twins[0],
            )
            # Use server's twin ID unless user explicitly set a different one
            server_twin_id = device_twin.get("id")
            if server_twin_id:
                self._instance_id = server_twin_id
            print(f"[PhyHubClient] Connected. Twin ID: {self._instance_id}")

    async def get_instance(self) -> Optional[EdgeInstance]:
        """Get or create the edge instance.

        Returns:
            EdgeInstance for messaging, or None if not connected.
        """
        if not self._connected or not self._registry:
            return None

        if self._instance:
            return self._instance

        self._instance = await self._registry.get_edge_instance()
        return self._instance

    async def get_peripheral_instance(self, twin_id: str) -> Optional[PeripheralInstance]:
        """Get a peripheral instance by twin ID.

        Args:
            twin_id: ID of the peripheral twin.

        Returns:
            PeripheralInstance or None if not found.
        """
        if not self._registry:
            return None

        return await self._registry.get_peripheral_instance(twin_id)

    def _send_event(self, target_twin_id: str, payload: dict[str, Any]) -> None:
        """Send event to a twin (fire-and-forget).

        In direct mode: socket.emit('twinMessage', payload)
        In PhyOS mode: socket.emit(instanceId, { method: 'twinMessage', ...payload })
        """
        if not self._connection:
            return

        event_payload = {
            "twinId": target_twin_id,
            "sourceTwinId": self._instance_id,
            "sourceDeviceId": self._connection.device_id if self._connection else None,
            "data": payload,
        }

        # Fire and forget - use asyncio to schedule
        asyncio.create_task(self._emit_to_socket(self.EVENTS.TWIN_MESSAGE, event_payload))

    async def _emit_to_socket(self, method: str, payload: dict[str, Any]) -> None:
        """Emit to socket with proper mode handling.

        In direct mode: socket.emit(method, payload)
        In PhyOS mode: socket.emit(instanceId, { method, ...payload })
        """
        if not self._connection:
            return

        if is_direct_mode():
            # Direct mode: emit to event name directly
            await self._connection.emit(method, payload)
        else:
            # PhyOS mode: emit to instanceId channel with method in payload
            phyos_payload = {"method": method, **payload}
            await self._connection.emit(self._instance_id or "", phyos_payload)

    def on_twin_message(
        self,
        twin_id: str,
        callback: Callable[[dict[str, Any]], None],
    ) -> None:
        """Register a callback for messages to a twin.

        Args:
            twin_id: Twin ID to listen for.
            callback: Handler function.
        """
        if twin_id not in self._twin_message_listeners:
            self._twin_message_listeners[twin_id] = set()
        self._twin_message_listeners[twin_id].add(callback)

    def off_twin_message(
        self,
        twin_id: str,
        callback: Optional[Callable[[dict[str, Any]], None]] = None,
    ) -> bool:
        """Remove a message callback.

        Args:
            twin_id: Twin ID.
            callback: Specific callback to remove, or None for all.

        Returns:
            True if removed, False otherwise.
        """
        if twin_id not in self._twin_message_listeners:
            return False

        if callback:
            self._twin_message_listeners[twin_id].discard(callback)
            if not self._twin_message_listeners[twin_id]:
                del self._twin_message_listeners[twin_id]
            return True
        else:
            del self._twin_message_listeners[twin_id]
            return True

    async def subscribe_twin(self, target_twin_id: str) -> dict[str, Any]:
        """Subscribe to receive messages from a twin.

        Args:
            target_twin_id: Twin ID to subscribe to.

        Returns:
            Subscription response.
        """
        if not self._connection:
            raise ConnectionError("Not connected")

        # Skip if already subscribed
        if target_twin_id in self._subscribed_twins:
            return {"status": "success", "message": "Already subscribed"}

        self._subscribed_twins.add(target_twin_id)

        payload = {
            "twinId": target_twin_id,
            "sourceTwinId": self._instance_id,
            "sourceDeviceId": self._connection.device_id,
        }

        # Fire-and-forget subscription using unified emit
        asyncio.create_task(self._emit_to_socket(self.EVENTS.TWIN_SUBSCRIBE, payload))

        return {"status": "success", "message": "Subscribed"}

    async def get_twin_by_id(self, twin_id: str) -> Optional[dict[str, Any]]:
        """Get twin data by ID.

        Args:
            twin_id: Twin ID to fetch.

        Returns:
            Twin data dictionary.
        """
        if not self._connection:
            return None

        result = await self._connection.emit(
            self.EVENTS.GET_TWIN_BY_ID,
            {"data": {"twinId": twin_id}},
            callback=True,
        )

        return result.get("twin") if result else None

    # =========================================================================
    # Settings API
    # =========================================================================

    async def get_settings(self) -> dict[str, Any]:
        """Get settings from edge instance desired properties.

        Returns:
            Settings dictionary.
        """
        instance = await self.get_instance()
        if instance:
            return instance.get_settings()
        return {}

    async def get_edge_settings(self) -> dict[str, Any]:
        """Alias for get_settings().

        Returns:
            Settings dictionary.
        """
        return await self.get_settings()

    def on_settings_update(
        self, callback: Callable[[dict[str, Any]], None]
    ) -> None:
        """Subscribe to settings changes in edge desired properties.

        Args:
            callback: Handler called with new settings when they change.
        """
        self._settings_update_listeners.add(callback)

        # Subscribe to edge twin updates if connected
        if self._instance_id:
            asyncio.create_task(self.subscribe_twin(self._instance_id))

    def off_settings_update(
        self, callback: Callable[[dict[str, Any]], None]
    ) -> bool:
        """Remove settings update callback.

        Args:
            callback: Callback to remove.

        Returns:
            True if removed, False otherwise.
        """
        if callback in self._settings_update_listeners:
            self._settings_update_listeners.discard(callback)
            return True
        return False

    # =========================================================================
    # Twin Update API
    # =========================================================================

    def on_twin_update(
        self,
        twin_id: str,
        callback: Callable[[dict[str, Any]], None],
    ) -> None:
        """Register callback for twin property updates.

        Args:
            twin_id: Twin ID to listen for updates.
            callback: Handler called with twin data when properties change.
        """
        if twin_id not in self._twin_update_listeners:
            self._twin_update_listeners[twin_id] = set()
        self._twin_update_listeners[twin_id].add(callback)

        # Ensure subscribed
        asyncio.create_task(self.subscribe_twin(twin_id))

    def off_twin_update(
        self,
        twin_id: str,
        callback: Optional[Callable[[dict[str, Any]], None]] = None,
    ) -> bool:
        """Remove twin update callback.

        Args:
            twin_id: Twin ID.
            callback: Specific callback to remove, or None for all.

        Returns:
            True if removed, False otherwise.
        """
        if twin_id not in self._twin_update_listeners:
            return False

        if callback:
            self._twin_update_listeners[twin_id].discard(callback)
            if not self._twin_update_listeners[twin_id]:
                del self._twin_update_listeners[twin_id]
            return True
        else:
            del self._twin_update_listeners[twin_id]
            return True

    # =========================================================================
    # Properties API
    # =========================================================================

    async def update_reported_properties(
        self, twin_id: str, properties: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        """Update reported properties for a twin.

        Args:
            twin_id: Twin ID to update.
            properties: Properties to set.

        Returns:
            Updated twin data.
        """
        if not self._connection:
            return None

        payload = {"twinId": twin_id, "data": properties}
        result = await self._connection.emit(
            self.EVENTS.REPORT_PROPERTIES, payload, callback=True
        )
        return result.get("twin") if result else None

    # =========================================================================
    # WebRTC Helpers
    # =========================================================================

    def _create_twin_messaging_interface(self) -> DataChannelMessaging:
        """Create a twin messaging interface for WebRTC handlers.

        This interface matches the npm TwinMessagingInterface and is used
        for WebRTC signaling (offer/answer/ice exchange).
        """
        async def send_message(target_twin_id: str, payload: dict[str, Any]) -> None:
            """Send a twin message for signaling.

            Unlike _send_event (fire-and-forget), this awaits the emit
            to ensure signaling messages are sent before proceeding.
            """
            if not self._connection:
                return

            event_payload = {
                "twinId": target_twin_id,
                "sourceTwinId": self._instance_id,
                "sourceDeviceId": self._connection.device_id if self._connection else None,
                "data": payload,
            }

            # Use unified emit pattern
            await self._emit_to_socket(self.EVENTS.TWIN_MESSAGE, event_payload)

        async def subscribe(twin_id: str) -> None:
            await self.subscribe_twin(twin_id)

        def get_own_twin_id() -> str:
            if not self._instance_id:
                raise ValueError("Instance ID not set")
            return self._instance_id

        return DataChannelMessaging(
            send_message=send_message,
            subscribe=subscribe,
            on_message=self.on_twin_message,
            off_message=lambda tid, cb: self.off_twin_message(tid, cb),
            get_own_twin_id=get_own_twin_id,
        )

    async def create_data_channel(
        self,
        target_twin_id: str,
        is_initiator: bool = True,
        options: Optional[DataChannelOptions] = None,
        channel_name: str = "default",
        blocking: bool = True,
    ) -> PhygridDataChannel:
        """Create a WebRTC DataChannel connection to another twin.

        Args:
            target_twin_id: ID of the twin to connect to.
            is_initiator: Whether this side initiates the connection.
            options: DataChannel configuration options.
            channel_name: Name for the data channel.
            blocking: If True (default), wait for connection to complete.
                     If False, return immediately and connect in background.

        Returns:
            PhygridDataChannel for sending/receiving data.
        """
        if not self._connected:
            raise ConnectionError("Not connected to PhyHub")

        # Subscribe to target twin
        await self.subscribe_twin(target_twin_id)

        # Create messaging interface
        messaging = self._create_twin_messaging_interface()

        # Create handler
        handler = DataChannelHandler(
            target_twin_id=target_twin_id,
            is_initiator=is_initiator,
            twin_messaging=messaging,
            options=options,
            channel_name=channel_name,
        )

        # Connect and return
        return await handler.connect(blocking=blocking)

    async def create_media_stream(
        self,
        target_twin_id: str,
        is_initiator: bool = True,
        options: Optional[MediaStreamOptions] = None,
        stream_name: str = "default",
        blocking: bool = True,
    ) -> PhygridMediaStream:
        """Create a WebRTC MediaStream connection to another twin.

        Args:
            target_twin_id: ID of the twin to connect to.
            is_initiator: Whether this side initiates the connection.
            options: MediaStream configuration options.
            stream_name: Name for the media stream.
            blocking: If True (default), wait for connection to complete.
                     If False, return immediately and connect in background.

        Returns:
            PhygridMediaStream for video/audio streaming.
        """
        if not self._connected:
            raise ConnectionError("Not connected to PhyHub")

        # Subscribe to target twin
        await self.subscribe_twin(target_twin_id)

        # Create messaging interface (same structure as DataChannel)
        messaging_interface = self._create_twin_messaging_interface()
        media_messaging = MediaStreamMessaging(
            send_message=messaging_interface.send_message,
            subscribe=messaging_interface.subscribe,
            on_message=messaging_interface.on_message,
            off_message=messaging_interface.off_message,
            get_own_twin_id=messaging_interface.get_own_twin_id,
        )

        # Create handler
        handler = MediaStreamHandler(
            target_twin_id=target_twin_id,
            is_initiator=is_initiator,
            twin_messaging=media_messaging,
            options=options,
            stream_name=stream_name,
        )

        # Connect and return
        return await handler.connect(blocking=blocking)

    async def __aenter__(self) -> "PhyHubClient":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.disconnect()

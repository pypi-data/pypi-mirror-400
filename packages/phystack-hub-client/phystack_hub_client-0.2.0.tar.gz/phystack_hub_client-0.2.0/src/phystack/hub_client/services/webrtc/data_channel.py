"""
DataChannelHandler

Manages RTCDataChannel lifecycle including:
- Channel creation (initiator) or reception (responder)
- Message serialization/deserialization
- Persistent channel abstraction across reconnections
"""

import asyncio
import json
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Set

from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate, RTCConfiguration, RTCIceServer


@dataclass
class DataChannelOptions:
    """Options for DataChannel connection."""

    use_stun: bool = True
    stun_servers: list[str] = field(
        default_factory=lambda: ["stun:stun.l.google.com:19302"]
    )
    connection_timeout: float = 15.0
    initial_retry_delay: float = 1.0
    max_retry_delay: float = 30.0


class PhygridDataChannel:
    """High-level DataChannel interface."""

    def __init__(self, handler: "DataChannelHandler") -> None:
        self._handler = handler

    def send(self, data: str | bytes | dict[str, Any]) -> None:
        """Send data through the channel.

        Args:
            data: String, bytes, or dict (will be JSON serialized).
        """
        self._handler.send(data)

    def on_message(self, callback: Callable[[Any], None]) -> None:
        """Register a message handler.

        Args:
            callback: Handler function.
        """
        self._handler.on_message(callback)

    def off_message(self, callback: Callable[[Any], None]) -> None:
        """Remove a message handler."""
        self._handler.off_message(callback)

    def on_close(self, callback: Callable[[], None]) -> None:
        """Register a close handler."""
        self._handler.on_close(callback)

    def off_close(self, callback: Callable[[], None]) -> None:
        """Remove a close handler."""
        self._handler.off_close(callback)

    def close(self) -> None:
        """Close the channel."""
        self._handler.close()

    def is_open(self) -> bool:
        """Check if channel is open."""
        return self._handler.is_open

    def is_connecting(self) -> bool:
        """Check if currently connecting."""
        return self._handler.is_connecting

    @property
    def target_twin_id(self) -> str:
        """Get target twin ID."""
        return self._handler.target_twin_id

    @property
    def channel_name(self) -> str:
        """Get channel name."""
        return self._handler.channel_name


class TwinMessagingInterface:
    """Interface for twin messaging operations."""

    def __init__(
        self,
        send_message: Callable[[str, dict[str, Any]], Any],
        subscribe: Callable[[str], Any],
        on_message: Callable[[str, Callable[[dict[str, Any]], None]], None],
        off_message: Callable[[str, Callable[[dict[str, Any]], None]], None],
        get_own_twin_id: Callable[[], str],
    ) -> None:
        self.send_message = send_message
        self.subscribe = subscribe
        self.on_message = on_message
        self.off_message = off_message
        self.get_own_twin_id = get_own_twin_id


class DataChannelHandler:
    """Handles WebRTC DataChannel connections."""

    def __init__(
        self,
        target_twin_id: str,
        is_initiator: bool,
        twin_messaging: TwinMessagingInterface,
        options: Optional[DataChannelOptions] = None,
        channel_name: str = "default",
    ) -> None:
        self.target_twin_id = target_twin_id
        self.channel_name = channel_name
        self._is_initiator = is_initiator
        self._twin_messaging = twin_messaging
        self._options = options or DataChannelOptions()

        self._pc: Optional[RTCPeerConnection] = None
        self._data_channel: Optional[Any] = None  # aiortc.RTCDataChannel
        self._is_open = False
        self._is_closed = False
        self._is_connecting = False

        self._message_listeners: Set[Callable[[Any], None]] = set()
        self._close_listeners: Set[Callable[[], None]] = set()

        # Callbacks
        self._on_connected: Optional[Callable[[], None]] = None
        self._on_disconnected: Optional[Callable[[], None]] = None
        self._on_error: Optional[Callable[[Exception], None]] = None

        # Message handler reference for cleanup
        self._message_handler: Optional[Callable[[dict[str, Any]], None]] = None

    @property
    def is_open(self) -> bool:
        """Check if channel is open."""
        return self._is_open

    @property
    def is_connecting(self) -> bool:
        """Check if currently connecting."""
        return self._is_connecting

    def set_callbacks(
        self,
        on_connected: Optional[Callable[[], None]] = None,
        on_disconnected: Optional[Callable[[], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
    ) -> None:
        """Set connection callbacks."""
        self._on_connected = on_connected
        self._on_disconnected = on_disconnected
        self._on_error = on_error

    async def connect(self, blocking: bool = True) -> PhygridDataChannel:
        """Connect and return a PhygridDataChannel.

        Args:
            blocking: If True (default), wait for connection to complete.
                     If False, return immediately and connect in background.

        Returns:
            PhygridDataChannel instance.

        Raises:
            RuntimeError: If already closed.
        """
        if self._is_closed:
            raise RuntimeError("DataChannelHandler has been closed")

        self._is_connecting = True
        own_twin_id = self._twin_messaging.get_own_twin_id()

        # Channel prefix for signaling messages - matches npm hub-client format
        # Prefix is just dc-{name}, filter matches dc-{name}-*
        channel_prefix = f"dc-{self.channel_name}"

        # Configure STUN servers
        ice_servers = []
        if self._options.use_stun:
            for server in self._options.stun_servers:
                ice_servers.append(RTCIceServer(urls=server))

        # Create peer connection with proper RTCConfiguration
        config = RTCConfiguration(iceServers=ice_servers) if ice_servers else None
        self._pc = RTCPeerConnection(configuration=config)

        # Set up message handler for signaling
        self._message_handler = self._create_signaling_handler(channel_prefix)
        self._twin_messaging.on_message(own_twin_id, self._message_handler)

        async def do_connect() -> None:
            """Perform the connection in background."""
            try:
                if self._is_initiator:
                    await self._initiate_connection(channel_prefix)
                else:
                    await self._wait_for_connection(channel_prefix)
            except Exception as e:
                self._is_connecting = False
                if self._on_error:
                    self._on_error(e)
                if blocking:
                    raise

        if blocking:
            await do_connect()
        else:
            # Non-blocking: start connection in background
            asyncio.create_task(do_connect())

        return PhygridDataChannel(self)

    def _create_signaling_handler(
        self, channel_prefix: str
    ) -> Callable[[dict[str, Any]], None]:
        """Create signaling message handler."""
        own_twin_id = self._twin_messaging.get_own_twin_id()

        def handler(payload: dict[str, Any]) -> None:
            # Filter by source twin - only process messages FROM the target peer
            source_twin_id = payload.get("sourceTwinId")
            if source_twin_id != self.target_twin_id:
                return

            data = payload.get("data", {})
            msg_type = data.get("type", "")

            # Check if this message is for our channel
            # Format: {channelPrefix}-{twinId}:{signalType}
            prefix_match = f"{channel_prefix}-"
            if not msg_type.startswith(prefix_match):
                return

            signal_type = msg_type.split(":")[-1]
            signal_data = data.get("data", {})
            print(f"[DataChannelHandler] Received signal: {signal_type} from {source_twin_id}")

            asyncio.create_task(self._handle_signal(signal_type, signal_data))

        return handler

    async def _handle_signal(self, signal_type: str, data: dict[str, Any]) -> None:
        """Handle incoming signaling message."""
        if not self._pc:
            return

        try:
            if signal_type == "offer":
                print(f"[DataChannelHandler] Setting remote description (offer)")
                await self._pc.setRemoteDescription(
                    RTCSessionDescription(sdp=data["sdp"], type=data["type"])
                )
                print(f"[DataChannelHandler] Creating answer...")
                answer = await self._pc.createAnswer()
                print(f"[DataChannelHandler] Setting local description (answer)")
                await self._pc.setLocalDescription(answer)
                await self._send_signal("answer", {
                    "sdp": self._pc.localDescription.sdp,
                    "type": self._pc.localDescription.type,
                })
                print(f"[DataChannelHandler] Answer sent")

            elif signal_type == "answer":
                # Ignore duplicate answers if already in stable state
                if self._pc.signalingState == "stable":
                    print(f"[DataChannelHandler] Ignoring duplicate answer (already stable)")
                    return
                print(f"[DataChannelHandler] Setting remote description (answer)")
                await self._pc.setRemoteDescription(
                    RTCSessionDescription(sdp=data["sdp"], type=data["type"])
                )

            elif signal_type == "ice":
                if data:
                    # Parse ICE candidate from signaling data
                    # Data might contain the candidate string or full candidate object
                    candidate_str = data.get("candidate")
                    sdp_mid = data.get("sdpMid")
                    sdp_mline_index = data.get("sdpMLineIndex")

                    if candidate_str:
                        # aiortc expects RTCIceCandidate constructed from string
                        # Parse the candidate string to extract fields
                        candidate = RTCIceCandidate(
                            component=1,  # RTP
                            foundation="",
                            ip="",
                            port=0,
                            priority=0,
                            protocol="udp",
                            type="host",
                            sdpMid=sdp_mid,
                            sdpMLineIndex=sdp_mline_index,
                        )
                        # Set the candidate string for aiortc to parse
                        candidate.candidate = candidate_str
                        await self._pc.addIceCandidate(candidate)

        except Exception as e:
            print(f"[DataChannelHandler] Error handling signal {signal_type}: {e}")
            import traceback
            traceback.print_exc()

    async def _send_signal(self, signal_type: str, data: dict[str, Any]) -> None:
        """Send signaling message."""
        # Message type format: dc-{name}-{targetTwinId}:{signalType}
        # This matches npm hub-client format
        channel_id = f"dc-{self.channel_name}-{self.target_twin_id}"

        await self._twin_messaging.send_message(
            self.target_twin_id,
            {
                "type": f"{channel_id}:{signal_type}",
                "data": data,
            },
        )

    async def _initiate_connection(self, channel_prefix: str) -> None:
        """Initiate WebRTC connection as the caller."""
        if not self._pc:
            return

        # Create data channel before creating offer (like npm)
        channel_id = f"dc-{self.channel_name}-{self.target_twin_id}"
        print(f"[DataChannelHandler] Creating data channel: {channel_id}")
        self._data_channel = self._pc.createDataChannel(channel_id)
        self._attach_channel_handlers()

        # Set up ICE candidate handler
        @self._pc.on("icecandidate")
        async def on_ice_candidate(candidate: Optional[RTCIceCandidate]) -> None:
            if candidate:
                print(f"[DataChannelHandler] Sending ICE candidate")
                # Send in npm format: { candidate, sdpMid, sdpMLineIndex }
                await self._send_signal("ice", {
                    "candidate": candidate.candidate,
                    "sdpMid": candidate.sdpMid,
                    "sdpMLineIndex": candidate.sdpMLineIndex,
                })

        # Create and send offer
        print(f"[DataChannelHandler] Creating offer...")
        offer = await self._pc.createOffer()
        print(f"[DataChannelHandler] Setting local description (offer)")
        await self._pc.setLocalDescription(offer)
        await self._send_signal("offer", {
            "sdp": self._pc.localDescription.sdp,
            "type": self._pc.localDescription.type,
        })
        print(f"[DataChannelHandler] Offer sent")

        # Wait for channel to open
        await self._wait_for_open()

    async def _wait_for_connection(self, channel_prefix: str) -> None:
        """Wait for incoming WebRTC connection as the callee."""
        if not self._pc:
            return

        print(f"[DataChannelHandler] Waiting for connection as responder...")

        # Set up data channel handler for incoming channel BEFORE receiving offer
        @self._pc.on("datachannel")
        def on_datachannel(channel: Any) -> None:
            print(f"[DataChannelHandler] Received data channel: {channel.label}")
            self._data_channel = channel
            self._attach_channel_handlers()

        # Set up ICE candidate handler
        @self._pc.on("icecandidate")
        async def on_ice_candidate(candidate: Optional[RTCIceCandidate]) -> None:
            if candidate:
                print(f"[DataChannelHandler] Sending ICE candidate")
                await self._send_signal("ice", {
                    "candidate": candidate.candidate,
                    "sdpMid": candidate.sdpMid,
                    "sdpMLineIndex": candidate.sdpMLineIndex,
                })

        # Wait for channel to open
        await self._wait_for_open()

    def _attach_channel_handlers(self) -> None:
        """Attach event handlers to data channel."""
        if not self._data_channel:
            return

        # Check if channel is already open (common for responder receiving datachannel)
        if hasattr(self._data_channel, 'readyState') and self._data_channel.readyState == "open":
            print("[DataChannelHandler] Channel already open")
            self._is_open = True
            self._is_connecting = False
            if self._on_connected:
                self._on_connected()

        @self._data_channel.on("open")
        def on_open() -> None:
            print("[DataChannelHandler] Channel opened")
            self._is_open = True
            self._is_connecting = False
            if self._on_connected:
                self._on_connected()

        @self._data_channel.on("close")
        def on_close() -> None:
            print("[DataChannelHandler] Channel closed")
            self._is_open = False
            if not self._is_closed and self._on_disconnected:
                self._on_disconnected()
            self._notify_close_listeners()

        @self._data_channel.on("message")
        def on_message(message: str | bytes) -> None:
            self._handle_message(message)

    async def _wait_for_open(self) -> None:
        """Wait for data channel to open."""
        timeout = self._options.connection_timeout
        start = asyncio.get_event_loop().time()

        while not self._is_open:
            if asyncio.get_event_loop().time() - start > timeout:
                raise TimeoutError(f"Connection timeout after {timeout}s")
            await asyncio.sleep(0.1)

    def _handle_message(self, data: str | bytes) -> None:
        """Handle incoming message."""
        parsed_data: Any = data

        # Try to parse JSON strings
        if isinstance(data, str):
            try:
                parsed_data = json.loads(data)
            except json.JSONDecodeError:
                pass  # Not JSON, use as-is

        for listener in self._message_listeners:
            try:
                listener(parsed_data)
            except Exception as e:
                print(f"[DataChannelHandler] Error in message listener: {e}")

    def send(self, data: str | bytes | dict[str, Any]) -> None:
        """Send data through the channel."""
        if not self._data_channel:
            print("[DataChannelHandler] Cannot send: no data channel")
            return

        # Check actual channel state, not just our flag
        channel_state = getattr(self._data_channel, 'readyState', None)
        if channel_state == "open":
            self._is_open = True  # Sync our flag
        elif not self._is_open:
            print(f"[DataChannelHandler] Cannot send: channel not open (state={channel_state})")
            return

        if isinstance(data, dict):
            message = json.dumps(data)
        else:
            message = data

        try:
            self._data_channel.send(message)
            print(f"[DataChannelHandler] Message sent successfully")
        except Exception as e:
            print(f"[DataChannelHandler] Error sending message: {e}")

    def on_message(self, callback: Callable[[Any], None]) -> None:
        """Register a message handler."""
        self._message_listeners.add(callback)

    def off_message(self, callback: Callable[[Any], None]) -> None:
        """Remove a message handler."""
        self._message_listeners.discard(callback)

    def on_close(self, callback: Callable[[], None]) -> None:
        """Register a close handler."""
        self._close_listeners.add(callback)

    def off_close(self, callback: Callable[[], None]) -> None:
        """Remove a close handler."""
        self._close_listeners.discard(callback)

    def _notify_close_listeners(self) -> None:
        """Notify all close listeners."""
        for listener in self._close_listeners:
            try:
                listener()
            except Exception as e:
                print(f"[DataChannelHandler] Error in close listener: {e}")

    def close(self) -> None:
        """Close the channel and clean up."""
        if self._is_closed:
            return

        self._is_closed = True
        self._is_open = False

        # Remove signaling handler
        if self._message_handler:
            own_twin_id = self._twin_messaging.get_own_twin_id()
            self._twin_messaging.off_message(own_twin_id, self._message_handler)

        # Close data channel
        if self._data_channel:
            try:
                self._data_channel.close()
            except Exception as e:
                print(f"[DataChannelHandler] Error closing data channel: {e}")
            self._data_channel = None

        # Close peer connection
        if self._pc:
            asyncio.create_task(self._pc.close())
            self._pc = None

        self._notify_close_listeners()
        self._message_listeners.clear()
        self._close_listeners.clear()

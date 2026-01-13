"""
MediaStreamHandler

Manages WebRTC MediaStream connections including:
- Video/audio track handling
- Webcam capture via OpenCV
- Stream transmission to remote peers
"""

import asyncio
import fractions
import json
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Set

import cv2
import numpy as np
from aiortc import (
    RTCPeerConnection,
    RTCSessionDescription,
    RTCIceCandidate,
    RTCConfiguration,
    RTCIceServer,
    MediaStreamTrack,
    VideoStreamTrack,
)
from aiortc.contrib.media import MediaPlayer, MediaRecorder
from av import VideoFrame


@dataclass
class MediaStreamOptions:
    """Options for MediaStream connection."""

    use_stun: bool = True
    stun_servers: list[str] = field(
        default_factory=lambda: ["stun:stun.l.google.com:19302"]
    )
    connection_timeout: float = 15.0
    initial_retry_delay: float = 1.0
    max_retry_delay: float = 30.0
    video_device: int = 0  # Default webcam index
    video_width: int = 640
    video_height: int = 480
    video_fps: int = 30


class WebcamVideoTrack(VideoStreamTrack):
    """Video track that captures from webcam using OpenCV."""

    kind = "video"

    def __init__(self, device: int = 0, width: int = 640, height: int = 480, fps: int = 30) -> None:
        super().__init__()
        self._device = device
        self._width = width
        self._height = height
        self._fps = fps
        self._cap: Optional[cv2.VideoCapture] = None
        self._started = False
        self._timestamp = 0
        self._time_base = fractions.Fraction(1, 90000)

    def _start_capture(self) -> None:
        """Start video capture."""
        if self._cap is None:
            self._cap = cv2.VideoCapture(self._device)
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)
            self._cap.set(cv2.CAP_PROP_FPS, self._fps)
            self._started = True
            print(f"[WebcamVideoTrack] Started capture from device {self._device}")

    async def recv(self) -> VideoFrame:
        """Receive the next video frame."""
        if not self._started:
            self._start_capture()

        pts, time_base = await self.next_timestamp()

        if self._cap is None or not self._cap.isOpened():
            # Return black frame if capture failed
            frame = VideoFrame(width=self._width, height=self._height, format="rgb24")
            frame.pts = pts
            frame.time_base = time_base
            return frame

        ret, img = self._cap.read()

        if not ret:
            # Return black frame if read failed
            img = np.zeros((self._height, self._width, 3), dtype=np.uint8)

        # Convert BGR to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Create VideoFrame
        frame = VideoFrame.from_ndarray(img, format="rgb24")
        frame.pts = pts
        frame.time_base = time_base

        return frame

    def stop(self) -> None:
        """Stop video capture."""
        super().stop()
        if self._cap is not None:
            self._cap.release()
            self._cap = None
            self._started = False
            print("[WebcamVideoTrack] Stopped capture")


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


class PhygridMediaStream:
    """High-level MediaStream interface."""

    def __init__(self, handler: "MediaStreamHandler") -> None:
        self._handler = handler

    def on_track(self, callback: Callable[[MediaStreamTrack], None]) -> None:
        """Register a track handler for incoming media tracks.

        Args:
            callback: Handler function for incoming tracks.
        """
        self._handler.on_track(callback)

    def off_track(self, callback: Callable[[MediaStreamTrack], None]) -> None:
        """Remove a track handler."""
        self._handler.off_track(callback)

    def on_close(self, callback: Callable[[], None]) -> None:
        """Register a close handler."""
        self._handler.on_close(callback)

    def off_close(self, callback: Callable[[], None]) -> None:
        """Remove a close handler."""
        self._handler.off_close(callback)

    def close(self) -> None:
        """Close the media stream."""
        self._handler.close()

    def is_open(self) -> bool:
        """Check if stream is open."""
        return self._handler.is_open

    def is_connecting(self) -> bool:
        """Check if currently connecting."""
        return self._handler.is_connecting

    @property
    def target_twin_id(self) -> str:
        """Get target twin ID."""
        return self._handler.target_twin_id

    @property
    def stream_name(self) -> str:
        """Get stream name."""
        return self._handler.stream_name

    @property
    def video_track(self) -> Optional[WebcamVideoTrack]:
        """Get the local video track if any."""
        return self._handler.video_track


class MediaStreamHandler:
    """Handles WebRTC MediaStream connections."""

    def __init__(
        self,
        target_twin_id: str,
        is_initiator: bool,
        twin_messaging: TwinMessagingInterface,
        options: Optional[MediaStreamOptions] = None,
        stream_name: str = "default",
    ) -> None:
        self.target_twin_id = target_twin_id
        self.stream_name = stream_name
        self._is_initiator = is_initiator
        self._twin_messaging = twin_messaging
        self._options = options or MediaStreamOptions()

        self._pc: Optional[RTCPeerConnection] = None
        self._video_track: Optional[WebcamVideoTrack] = None
        self._is_open = False
        self._is_closed = False
        self._is_connecting = False

        self._track_listeners: Set[Callable[[MediaStreamTrack], None]] = set()
        self._close_listeners: Set[Callable[[], None]] = set()

        # Callbacks
        self._on_connected: Optional[Callable[[], None]] = None
        self._on_disconnected: Optional[Callable[[], None]] = None
        self._on_error: Optional[Callable[[Exception], None]] = None

        # Message handler reference for cleanup
        self._message_handler: Optional[Callable[[dict[str, Any]], None]] = None

    @property
    def is_open(self) -> bool:
        """Check if stream is open."""
        return self._is_open

    @property
    def is_connecting(self) -> bool:
        """Check if currently connecting."""
        return self._is_connecting

    @property
    def video_track(self) -> Optional[WebcamVideoTrack]:
        """Get the local video track."""
        return self._video_track

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

    async def connect(self, blocking: bool = True) -> PhygridMediaStream:
        """Connect and return a PhygridMediaStream.

        Args:
            blocking: If True (default), wait for connection to complete.
                     If False, return immediately and connect in background.

        Returns:
            PhygridMediaStream instance.

        Raises:
            RuntimeError: If already closed.
        """
        if self._is_closed:
            raise RuntimeError("MediaStreamHandler has been closed")

        self._is_connecting = True
        own_twin_id = self._twin_messaging.get_own_twin_id()

        # Stream prefix for signaling messages - matches npm hub-client format
        # npm uses "media-" prefix, filter matches media-{name}-*
        stream_prefix = f"media-{self.stream_name}"

        # Configure STUN servers
        ice_servers = []
        if self._options.use_stun:
            for server in self._options.stun_servers:
                ice_servers.append(RTCIceServer(urls=server))

        # Create peer connection with proper RTCConfiguration
        config = RTCConfiguration(iceServers=ice_servers) if ice_servers else None
        self._pc = RTCPeerConnection(configuration=config)

        # Set up message handler for signaling
        self._message_handler = self._create_signaling_handler(stream_prefix)
        self._twin_messaging.on_message(own_twin_id, self._message_handler)

        # Set up track handler
        @self._pc.on("track")
        def on_track(track: MediaStreamTrack) -> None:
            print(f"[MediaStreamHandler] Received track: {track.kind}")
            self._notify_track_listeners(track)

        # Set up connection state handler
        @self._pc.on("connectionstatechange")
        async def on_connection_state_change() -> None:
            if self._pc:
                state = self._pc.connectionState
                print(f"[MediaStreamHandler] Connection state: {state}")
                if state == "connected":
                    self._is_open = True
                    self._is_connecting = False
                    if self._on_connected:
                        self._on_connected()
                elif state in ("failed", "closed", "disconnected"):
                    self._is_open = False
                    if not self._is_closed and self._on_disconnected:
                        self._on_disconnected()

        async def do_connect() -> None:
            """Perform the connection in background."""
            try:
                if self._is_initiator:
                    await self._initiate_connection(stream_prefix)
                else:
                    await self._wait_for_connection(stream_prefix)
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

        return PhygridMediaStream(self)

    def _create_signaling_handler(
        self, stream_prefix: str
    ) -> Callable[[dict[str, Any]], None]:
        """Create signaling message handler."""

        def handler(payload: dict[str, Any]) -> None:
            # Filter by source twin - only process messages FROM the target peer
            source_twin_id = payload.get("sourceTwinId")
            if source_twin_id != self.target_twin_id:
                return

            data = payload.get("data", {})
            msg_type = data.get("type", "")

            # Check if this message is for our stream
            # Format: {streamPrefix}-{twinId}:{signalType}
            prefix_match = f"{stream_prefix}-"
            if not msg_type.startswith(prefix_match):
                return

            signal_type = msg_type.split(":")[-1]
            signal_data = data.get("data", {})
            print(f"[MediaStreamHandler] Received signal: {signal_type} from {source_twin_id}")

            asyncio.create_task(self._handle_signal(signal_type, signal_data))

        return handler

    async def _handle_signal(self, signal_type: str, data: dict[str, Any]) -> None:
        """Handle incoming signaling message."""
        if not self._pc:
            return

        try:
            if signal_type == "offer":
                print(f"[MediaStreamHandler] Setting remote description (offer)")
                await self._pc.setRemoteDescription(
                    RTCSessionDescription(sdp=data["sdp"], type=data["type"])
                )

                # Add local video track for responder
                if self._is_initiator is False:
                    self._add_video_track()

                print(f"[MediaStreamHandler] Creating answer...")
                answer = await self._pc.createAnswer()
                print(f"[MediaStreamHandler] Setting local description (answer)")
                await self._pc.setLocalDescription(answer)
                await self._send_signal("answer", {
                    "sdp": self._pc.localDescription.sdp,
                    "type": self._pc.localDescription.type,
                })
                print(f"[MediaStreamHandler] Answer sent")

            elif signal_type == "answer":
                # Ignore duplicate answers if already in stable state
                if self._pc.signalingState == "stable":
                    print(f"[MediaStreamHandler] Ignoring duplicate answer (already stable)")
                    return
                print(f"[MediaStreamHandler] Setting remote description (answer)")
                await self._pc.setRemoteDescription(
                    RTCSessionDescription(sdp=data["sdp"], type=data["type"])
                )

            elif signal_type == "ice":
                if data:
                    # Parse ICE candidate from signaling data (npm format)
                    candidate_str = data.get("candidate")
                    sdp_mid = data.get("sdpMid")
                    sdp_mline_index = data.get("sdpMLineIndex")

                    if candidate_str:
                        candidate = RTCIceCandidate(
                            component=1,
                            foundation="",
                            ip="",
                            port=0,
                            priority=0,
                            protocol="udp",
                            type="host",
                            sdpMid=sdp_mid,
                            sdpMLineIndex=sdp_mline_index,
                        )
                        candidate.candidate = candidate_str
                        await self._pc.addIceCandidate(candidate)

        except Exception as e:
            print(f"[MediaStreamHandler] Error handling signal {signal_type}: {e}")
            import traceback
            traceback.print_exc()

    async def _send_signal(self, signal_type: str, data: dict[str, Any]) -> None:
        """Send signaling message."""
        # Message type format: media-{name}-{targetTwinId}:{signalType}
        # This matches npm hub-client format
        stream_id = f"media-{self.stream_name}-{self.target_twin_id}"

        await self._twin_messaging.send_message(
            self.target_twin_id,
            {
                "type": f"{stream_id}:{signal_type}",
                "data": data,
            },
        )

    def _add_video_track(self) -> None:
        """Add webcam video track to peer connection."""
        if not self._pc or self._video_track:
            return

        self._video_track = WebcamVideoTrack(
            device=self._options.video_device,
            width=self._options.video_width,
            height=self._options.video_height,
            fps=self._options.video_fps,
        )

        self._pc.addTrack(self._video_track)
        print(f"[MediaStreamHandler] Added video track from webcam {self._options.video_device}")

    async def _initiate_connection(self, stream_prefix: str) -> None:
        """Initiate WebRTC connection as the caller."""
        if not self._pc:
            return

        # Add local video track before creating offer
        self._add_video_track()

        # Set up ICE candidate handler
        @self._pc.on("icecandidate")
        async def on_ice_candidate(candidate: Optional[RTCIceCandidate]) -> None:
            if candidate:
                await self._send_signal("ice", {
                    "candidate": candidate.candidate,
                    "sdpMid": candidate.sdpMid,
                    "sdpMLineIndex": candidate.sdpMLineIndex,
                })

        # Create and send offer
        print(f"[MediaStreamHandler] Creating offer...")
        offer = await self._pc.createOffer()
        print(f"[MediaStreamHandler] Setting local description (offer)")
        await self._pc.setLocalDescription(offer)
        await self._send_signal("offer", {
            "sdp": self._pc.localDescription.sdp,
            "type": self._pc.localDescription.type,
        })
        print(f"[MediaStreamHandler] Offer sent")

        # Wait for connection
        await self._wait_for_connected()

    async def _wait_for_connection(self, stream_prefix: str) -> None:
        """Wait for incoming WebRTC connection as the callee."""
        if not self._pc:
            return

        print(f"[MediaStreamHandler] Waiting for connection as responder...")

        # Set up ICE candidate handler
        @self._pc.on("icecandidate")
        async def on_ice_candidate(candidate: Optional[RTCIceCandidate]) -> None:
            if candidate:
                print(f"[MediaStreamHandler] Sending ICE candidate")
                await self._send_signal("ice", {
                    "candidate": candidate.candidate,
                    "sdpMid": candidate.sdpMid,
                    "sdpMLineIndex": candidate.sdpMLineIndex,
                })

        # Wait for connection to be established
        await self._wait_for_connected()

    async def _wait_for_connected(self) -> None:
        """Wait for WebRTC connection to be established."""
        timeout = self._options.connection_timeout
        start = asyncio.get_event_loop().time()

        while not self._is_open:
            if asyncio.get_event_loop().time() - start > timeout:
                raise TimeoutError(f"Connection timeout after {timeout}s")
            await asyncio.sleep(0.1)

    def on_track(self, callback: Callable[[MediaStreamTrack], None]) -> None:
        """Register a track handler."""
        self._track_listeners.add(callback)

    def off_track(self, callback: Callable[[MediaStreamTrack], None]) -> None:
        """Remove a track handler."""
        self._track_listeners.discard(callback)

    def _notify_track_listeners(self, track: MediaStreamTrack) -> None:
        """Notify all track listeners."""
        for listener in self._track_listeners:
            try:
                listener(track)
            except Exception as e:
                print(f"[MediaStreamHandler] Error in track listener: {e}")

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
                print(f"[MediaStreamHandler] Error in close listener: {e}")

    def close(self) -> None:
        """Close the stream and clean up."""
        if self._is_closed:
            return

        self._is_closed = True
        self._is_open = False

        # Remove signaling handler
        if self._message_handler:
            own_twin_id = self._twin_messaging.get_own_twin_id()
            self._twin_messaging.off_message(own_twin_id, self._message_handler)

        # Stop video track
        if self._video_track:
            try:
                self._video_track.stop()
            except Exception as e:
                print(f"[MediaStreamHandler] Error stopping video track: {e}")
            self._video_track = None

        # Close peer connection
        if self._pc:
            asyncio.create_task(self._pc.close())
            self._pc = None

        self._notify_close_listeners()
        self._track_listeners.clear()
        self._close_listeners.clear()

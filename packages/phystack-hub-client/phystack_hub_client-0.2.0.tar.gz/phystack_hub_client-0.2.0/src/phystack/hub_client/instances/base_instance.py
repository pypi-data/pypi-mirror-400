"""Base instance class with common functionality for all twin types."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Optional

from phystack.hub_client.types.twin_types import (
    TwinMessageResult,
    TwinProperties,
    TwinResponse,
)
from phystack.hub_client.twin_messaging import (
    TwinMessaging,
    TargetedEmitter,
)

if TYPE_CHECKING:
    from phystack.hub_client.client import PhyHubClient
    from phystack.hub_client.services.webrtc.data_channel import (
        PhygridDataChannel,
        DataChannelOptions,
    )
    from phystack.hub_client.services.webrtc.media_stream import (
        PhygridMediaStream,
        MediaStreamOptions,
    )


class BaseInstance:
    """Base class for all twin instances with common messaging and WebRTC."""

    def __init__(
        self,
        twin_id: str,
        device_id: str,
        client: "PhyHubClient",
        messaging: TwinMessaging,
        twin_data: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize base instance.

        Args:
            twin_id: ID of this twin.
            device_id: ID of the parent device.
            client: PhyHubClient for API calls.
            messaging: TwinMessaging instance for emit/on/to.
            twin_data: Optional cached twin data.
        """
        self.id = twin_id
        self.device_id = device_id
        self._client = client
        self._messaging = messaging
        self._twin_data = twin_data or {}

    @property
    def properties(self) -> TwinProperties:
        """Access twin properties (desired/reported)."""
        props = self._twin_data.get("properties", {})
        return TwinProperties.from_dict(props)

    @property
    def tenant_id(self) -> str:
        """Get tenant ID."""
        return self._twin_data.get("tenantId", "")

    @property
    def type(self) -> str:
        """Get twin type."""
        return self._twin_data.get("type", "")

    @property
    def status(self) -> str:
        """Get twin status."""
        return self._twin_data.get("status", "")

    @property
    def descriptors(self) -> dict[str, str]:
        """Get twin descriptors."""
        return self._twin_data.get("descriptors", {})

    def _update_twin_data(self, data: dict[str, Any]) -> None:
        """Update cached twin data."""
        self._twin_data = {**self._twin_data, **data}

    # =========================================================================
    # Messaging API (delegated to TwinMessaging)
    # =========================================================================

    def emit(self, event_type: str, payload: Any = None) -> None:
        """Fire-and-forget broadcast to subscribers.

        Args:
            event_type: Type of event to emit.
            payload: Data to send.
        """
        self._messaging.emit(event_type, payload)

    def on(
        self,
        event_type: str,
        callback: Callable[[Any, Optional[Callable[[TwinMessageResult], None]]], None],
    ) -> None:
        """Listen for events, with optional respond callback for request-response.

        Args:
            event_type: Type of event to listen for.
            callback: Handler function (data, respond?) => None
        """
        self._messaging.on(event_type, callback)

    def to(self, target_twin_id: str) -> TargetedEmitter:
        """Target a specific twin for messaging.

        Args:
            target_twin_id: ID of twin to target.

        Returns:
            TargetedEmitter for the specified twin.
        """
        return self._messaging.to(target_twin_id)

    # =========================================================================
    # WebRTC API (delegated to client)
    # =========================================================================

    async def get_data_channel(
        self,
        target_twin_id: str,
        channel_name: str = "default",
        options: Optional["DataChannelOptions"] = None,
    ) -> "PhygridDataChannel":
        """Create a WebRTC DataChannel to another twin.

        Args:
            target_twin_id: ID of the target twin.
            channel_name: Name for the data channel.
            options: Optional DataChannel configuration.

        Returns:
            PhygridDataChannel for sending/receiving data.
        """
        return await self._client.create_data_channel(
            target_twin_id=target_twin_id,
            is_initiator=True,
            options=options,
            channel_name=channel_name,
        )

    async def on_data_channel(
        self,
        target_twin_id: str,
        callback: Callable[["PhygridDataChannel"], None],
        channel_name: str = "default",
    ) -> None:
        """Listen for incoming DataChannel from a twin.

        Args:
            target_twin_id: ID of the twin to listen from.
            callback: Handler for incoming channel.
            channel_name: Name of the channel to listen for.
        """
        channel = await self._client.create_data_channel(
            target_twin_id=target_twin_id,
            is_initiator=False,
            channel_name=channel_name,
            blocking=False,
        )
        # Call callback when channel is opened
        if channel.is_open():
            callback(channel)
        else:
            original_on_open = None

            def on_open() -> None:
                callback(channel)

            channel._handler._on_connected = on_open

    async def get_media_stream(
        self,
        target_twin_id: str,
        stream_name: str = "default",
        options: Optional["MediaStreamOptions"] = None,
    ) -> "PhygridMediaStream":
        """Create a WebRTC MediaStream to another twin.

        Args:
            target_twin_id: ID of the target twin.
            stream_name: Name for the media stream.
            options: Optional MediaStream configuration.

        Returns:
            PhygridMediaStream for video/audio streaming.
        """
        return await self._client.create_media_stream(
            target_twin_id=target_twin_id,
            is_initiator=True,
            options=options,
            stream_name=stream_name,
        )

    async def on_media_stream(
        self,
        target_twin_id: str,
        callback: Callable[["PhygridMediaStream"], None],
        stream_name: str = "default",
    ) -> None:
        """Listen for incoming MediaStream from a twin.

        Args:
            target_twin_id: ID of the twin to listen from.
            callback: Handler for incoming stream.
            stream_name: Name of the stream to listen for.
        """
        stream = await self._client.create_media_stream(
            target_twin_id=target_twin_id,
            is_initiator=False,
            stream_name=stream_name,
            blocking=False,
        )
        # Call callback when stream is opened
        if stream.is_open():
            callback(stream)
        else:
            stream._handler._on_connected = lambda: callback(stream)

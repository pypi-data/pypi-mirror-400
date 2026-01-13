"""
Phystack Hub Client - Python implementation

A Python client for PhyHub that provides:
- Events and Actions via twin messaging
- WebRTC DataChannel for P2P data
- WebRTC MediaStream for P2P video/audio
- Twin instance management (Edge, Peripheral, etc.)
- Properties API (reported/desired)
- Settings API with subscriptions

Usage:
    from phystack.hub_client import PhyHubClient

    async with PhyHubClient.from_env() as client:
        instance = await client.get_instance()

        # Events
        instance.on("my-event", lambda data, respond: print(data))
        instance.to(peer_twin_id).emit("my-event", {"hello": "world"})

        # Actions (request-response)
        instance.to(peer_twin_id).emit("my-action", {"cmd": "process"}, callback=my_callback)

        # Properties
        await instance.update_reported({"status": "ready"})
        instance.on_update_desired(lambda props: print("Desired changed:", props))

        # Settings (for edge apps)
        settings = client.get_settings()
        client.on_settings_update(lambda s: print("Settings updated:", s))

        # DataChannel
        dc = await instance.get_data_channel(peer_twin_id)
        dc.send({"message": "hello"})

        # MediaStream (with webcam)
        stream = await instance.get_media_stream(peer_twin_id)
"""

from phystack.hub_client.client import PhyHubClient
from phystack.hub_client.types.twin_types import (
    TwinMessageResult,
    TwinMessageResultStatus,
    TwinProperties,
    TwinTypeEnum,
    TwinStatusEnum,
)
from phystack.hub_client.instances import (
    BaseInstance,
    EdgeInstance,
    PeripheralInstance,
)
from phystack.hub_client.twin_registry import TwinRegistry
from phystack.hub_client.services.webrtc.data_channel import (
    DataChannelHandler,
    DataChannelOptions,
    PhygridDataChannel,
)
from phystack.hub_client.services.webrtc.media_stream import (
    MediaStreamHandler,
    MediaStreamOptions,
    PhygridMediaStream,
    WebcamVideoTrack,
)

__version__ = "0.1.0"
__all__ = [
    # Client
    "PhyHubClient",
    # Instances
    "BaseInstance",
    "EdgeInstance",
    "PeripheralInstance",
    "TwinRegistry",
    # Types
    "TwinMessageResult",
    "TwinMessageResultStatus",
    "TwinProperties",
    "TwinTypeEnum",
    "TwinStatusEnum",
    # WebRTC
    "DataChannelHandler",
    "DataChannelOptions",
    "PhygridDataChannel",
    "MediaStreamHandler",
    "MediaStreamOptions",
    "PhygridMediaStream",
    "WebcamVideoTrack",
]

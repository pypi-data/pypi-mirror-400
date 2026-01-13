"""Twin type definitions matching the TypeScript implementation."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional


class TwinTypeEnum(str, Enum):
    """Twin type enumeration matching npm hub-client."""

    Device = "Device"
    Screen = "Screen"
    Edge = "Edge"
    Cloud = "Cloud"
    Web = "Web"
    Peripheral = "Peripheral"


class TwinStatusEnum(str, Enum):
    """Twin status enumeration matching npm hub-client."""

    Offline = "Offline"
    Online = "Online"
    Starting = "Starting"
    Exited = "Exited"
    ImageNotFound = "ImageNotFound"


class TwinMessageResultStatus(str, Enum):
    """Status codes for twin message results."""

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


@dataclass
class TwinMessageResult:
    """Result of a twin message operation."""

    status: TwinMessageResultStatus
    message: str
    data: Optional[dict[str, Any]] = None


@dataclass
class TwinProperties:
    """Twin properties structure with desired and reported."""

    desired: dict[str, Any] = field(default_factory=dict)
    reported: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TwinProperties":
        """Create from dictionary."""
        return cls(
            desired=data.get("desired", {}),
            reported=data.get("reported", {}),
        )


@dataclass
class TwinResponse:
    """Response containing twin data."""

    id: str
    device_id: str
    tenant_id: str
    version: int
    status: str
    type: str
    properties: dict[str, Any] = field(default_factory=dict)
    descriptors: dict[str, str] = field(default_factory=dict)
    notes: str = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def get_properties(self) -> TwinProperties:
        """Get typed properties."""
        return TwinProperties.from_dict(self.properties)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TwinResponse":
        """Create from API response dictionary."""
        return cls(
            id=data.get("id", ""),
            device_id=data.get("deviceId", ""),
            tenant_id=data.get("tenantId", ""),
            version=data.get("version", 0),
            status=data.get("status", ""),
            type=data.get("type", ""),
            properties=data.get("properties", {}),
            descriptors=data.get("descriptors", {}),
            notes=data.get("notes", ""),
            created_at=data.get("createdAt"),
            updated_at=data.get("updatedAt"),
        )


@dataclass
class EventPayload:
    """Payload structure for twin events."""

    twin_id: Optional[str] = None
    source_twin_id: Optional[str] = None
    source_device_id: Optional[str] = None
    data: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for Socket.IO transmission."""
        result: dict[str, Any] = {}
        if self.twin_id:
            result["twinId"] = self.twin_id
        if self.source_twin_id:
            result["sourceTwinId"] = self.source_twin_id
        if self.source_device_id:
            result["sourceDeviceId"] = self.source_device_id
        if self.data:
            result["data"] = self.data
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EventPayload":
        """Create from Socket.IO payload dictionary."""
        return cls(
            twin_id=data.get("twinId"),
            source_twin_id=data.get("sourceTwinId"),
            source_device_id=data.get("sourceDeviceId"),
            data=data.get("data"),
        )


# Type aliases for callbacks
MessageCallback = Callable[[dict[str, Any]], None]
RespondCallback = Callable[[TwinMessageResult], None]
EventCallback = Callable[[dict[str, Any], Optional[RespondCallback]], None]

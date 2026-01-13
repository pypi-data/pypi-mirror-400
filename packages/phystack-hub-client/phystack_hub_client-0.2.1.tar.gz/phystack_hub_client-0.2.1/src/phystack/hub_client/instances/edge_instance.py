"""EdgeInstance class for edge twin management."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Callable, Optional, Set

from phystack.hub_client.instances.base_instance import BaseInstance
from phystack.hub_client.types.twin_types import (
    TwinResponse,
    TwinTypeEnum,
)

if TYPE_CHECKING:
    from phystack.hub_client.client import PhyHubClient
    from phystack.hub_client.twin_messaging import TwinMessaging


class EdgeInstance(BaseInstance):
    """Edge twin instance with peripheral and settings management."""

    def __init__(
        self,
        twin_id: str,
        device_id: str,
        client: "PhyHubClient",
        messaging: "TwinMessaging",
        twin_data: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize edge instance.

        Args:
            twin_id: ID of this edge twin.
            device_id: ID of the parent device.
            client: PhyHubClient for API calls.
            messaging: TwinMessaging instance for emit/on/to.
            twin_data: Optional cached twin data.
        """
        super().__init__(twin_id, device_id, client, messaging, twin_data)
        self._update_reported_listeners: Set[Callable[[dict[str, Any]], None]] = set()
        self._update_desired_listeners: Set[Callable[[dict[str, Any]], None]] = set()
        self._previous_reported: Optional[str] = None
        self._previous_desired: Optional[str] = None

    # =========================================================================
    # Properties API
    # =========================================================================

    async def update_reported(self, properties: dict[str, Any]) -> dict[str, Any]:
        """Update reported properties for this edge twin.

        Args:
            properties: Properties to update.

        Returns:
            Updated twin data.
        """
        result = await self._client.update_reported_properties(self.id, properties)
        if result:
            self._update_twin_data(result)
        return result or {}

    def on_update_reported(
        self, callback: Callable[[dict[str, Any]], None]
    ) -> None:
        """Subscribe to reported property changes.

        Args:
            callback: Handler called with new reported properties when they change.
        """
        self._update_reported_listeners.add(callback)

        # Set up twin update listener if not already set
        self._setup_property_listeners()

    def on_update_desired(
        self, callback: Callable[[dict[str, Any]], None]
    ) -> None:
        """Subscribe to desired property changes.

        Args:
            callback: Handler called with new desired properties when they change.
        """
        self._update_desired_listeners.add(callback)

        # Set up twin update listener if not already set
        self._setup_property_listeners()

    def _setup_property_listeners(self) -> None:
        """Set up twin update listener for property change detection."""

        def on_twin_update(twin_data: dict[str, Any]) -> None:
            if twin_data.get("id") != self.id:
                return

            props = twin_data.get("properties", {})

            # Check reported changes
            reported = props.get("reported", {})
            reported_str = json.dumps(reported, sort_keys=True)
            if self._previous_reported is None:
                self._previous_reported = reported_str
                for listener in self._update_reported_listeners:
                    try:
                        listener(reported)
                    except Exception as e:
                        print(f"[EdgeInstance] Error in reported listener: {e}")
            elif reported_str != self._previous_reported:
                self._previous_reported = reported_str
                for listener in self._update_reported_listeners:
                    try:
                        listener(reported)
                    except Exception as e:
                        print(f"[EdgeInstance] Error in reported listener: {e}")

            # Check desired changes
            desired = props.get("desired", {})
            desired_str = json.dumps(desired, sort_keys=True)
            if self._previous_desired is None:
                self._previous_desired = desired_str
                for listener in self._update_desired_listeners:
                    try:
                        listener(desired)
                    except Exception as e:
                        print(f"[EdgeInstance] Error in desired listener: {e}")
            elif desired_str != self._previous_desired:
                self._previous_desired = desired_str
                for listener in self._update_desired_listeners:
                    try:
                        listener(desired)
                    except Exception as e:
                        print(f"[EdgeInstance] Error in desired listener: {e}")

            # Update cached twin data
            self._update_twin_data(twin_data)

        self._client.on_twin_update(self.id, on_twin_update)

    # =========================================================================
    # Peripheral Twin Management
    # =========================================================================

    async def create_peripheral_twin(
        self,
        name: str,
        hardware_id: str,
        desired_properties: Optional[dict[str, Any]] = None,
        descriptors: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """Create a new peripheral twin associated with this edge.

        Args:
            name: Name for the peripheral.
            hardware_id: Unique hardware identifier.
            desired_properties: Optional initial desired properties.
            descriptors: Optional descriptors for the peripheral.

        Returns:
            Created peripheral twin data.

        Raises:
            ValueError: If peripheral with same hardware_id already exists.
        """
        # Check for existing peripheral with same hardware_id
        existing = await self.get_peripheral_twins()
        for twin in existing:
            props = twin.get("properties", {}).get("desired", {})
            if props.get("hardwareId") == hardware_id:
                raise ValueError(
                    f"Peripheral with hardwareId {hardware_id} already exists"
                )

        payload = {
            "data": {
                "deviceId": self.device_id,
                "tenantId": self.tenant_id,
                "instanceId": self.id,
                "peripheralName": name,
                "hardwareId": hardware_id,
                "desiredProperties": desired_properties,
                "descriptors": descriptors,
            }
        }

        result = await self._client._connection.emit(
            "createPeripheralTwin", payload, callback=True
        )
        return result.get("twin", {}) if result else {}

    async def get_peripheral_twins(self) -> list[dict[str, Any]]:
        """Get all peripheral twins for this edge instance.

        Returns:
            List of peripheral twin data.
        """
        payload = {"data": {"instanceId": self.id}}
        result = await self._client._connection.emit(
            "getPeripheralTwins", payload, callback=True
        )
        return result.get("twins", []) if result else []

    # =========================================================================
    # Settings API
    # =========================================================================

    def get_settings(self) -> dict[str, Any]:
        """Get settings from desired properties.

        Returns:
            Settings dictionary.
        """
        return self.properties.desired.get("settings", {})

"""PeripheralInstance class for peripheral twin management."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Callable, Optional, Set

from phystack.hub_client.instances.base_instance import BaseInstance
from phystack.hub_client.types.twin_types import TwinResponse

if TYPE_CHECKING:
    from phystack.hub_client.client import PhyHubClient
    from phystack.hub_client.instances.edge_instance import EdgeInstance
    from phystack.hub_client.twin_messaging import TwinMessaging


class PeripheralInstance(BaseInstance):
    """Peripheral twin instance with full property management."""

    def __init__(
        self,
        twin_id: str,
        device_id: str,
        client: "PhyHubClient",
        messaging: "TwinMessaging",
        edge_instance: "EdgeInstance",
        twin_data: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize peripheral instance.

        Args:
            twin_id: ID of this peripheral twin.
            device_id: ID of the parent device.
            client: PhyHubClient for API calls.
            messaging: TwinMessaging instance for emit/on/to.
            edge_instance: Parent edge instance.
            twin_data: Optional cached twin data.
        """
        super().__init__(twin_id, device_id, client, messaging, twin_data)
        self._edge_instance = edge_instance
        self._update_reported_listeners: Set[Callable[[dict[str, Any]], None]] = set()
        self._update_desired_listeners: Set[Callable[[dict[str, Any]], None]] = set()
        self._previous_reported: Optional[str] = None
        self._previous_desired: Optional[str] = None
        self._listener_setup = False

    # =========================================================================
    # Properties API
    # =========================================================================

    async def update_reported(self, properties: dict[str, Any]) -> dict[str, Any]:
        """Update reported properties for this peripheral twin.

        Args:
            properties: Properties to update.

        Returns:
            Updated twin data.
        """
        result = await self._client.update_reported_properties(self.id, properties)
        if result:
            self._update_twin_data(result)
        return result or {}

    async def update_desired(self, properties: dict[str, Any]) -> dict[str, Any]:
        """Update desired properties for this peripheral twin.

        Peripherals can update their own desired properties unlike edge twins.

        Args:
            properties: Properties to update.

        Returns:
            Updated twin data.
        """
        payload = {
            "twinId": self.id,
            "data": properties,
        }

        result = await self._client._connection.emit(
            "updatePeripheralTwinDesired", payload, callback=True
        )
        twin_data = result.get("twin", {}) if result else {}
        if twin_data:
            self._update_twin_data(twin_data)
        return twin_data

    def on_update_reported(
        self, callback: Callable[[dict[str, Any]], None]
    ) -> None:
        """Subscribe to reported property changes.

        Args:
            callback: Handler called with new reported properties when they change.
        """
        self._update_reported_listeners.add(callback)
        self._setup_property_listeners()

    def on_update_desired(
        self, callback: Callable[[dict[str, Any]], None]
    ) -> None:
        """Subscribe to desired property changes.

        Args:
            callback: Handler called with new desired properties when they change.
        """
        self._update_desired_listeners.add(callback)
        self._setup_property_listeners()

    def _setup_property_listeners(self) -> None:
        """Set up twin update listener for property change detection."""
        if self._listener_setup:
            return
        self._listener_setup = True

        def on_twin_update(twin_data: dict[str, Any]) -> None:
            # Only process updates for this specific peripheral
            if twin_data.get("id") != self.id:
                return

            props = twin_data.get("properties", {})

            # Check reported changes
            reported = props.get("reported", {})
            if reported:
                reported_str = json.dumps(reported, sort_keys=True)
                if self._previous_reported is None:
                    # First update - always trigger
                    self._previous_reported = reported_str
                    for listener in self._update_reported_listeners:
                        try:
                            listener(reported)
                        except Exception as e:
                            print(f"[PeripheralInstance] Error in reported listener: {e}")
                elif reported_str != self._previous_reported:
                    self._previous_reported = reported_str
                    for listener in self._update_reported_listeners:
                        try:
                            listener(reported)
                        except Exception as e:
                            print(f"[PeripheralInstance] Error in reported listener: {e}")

            # Check desired changes
            desired = props.get("desired", {})
            if desired:
                desired_str = json.dumps(desired, sort_keys=True)
                if self._previous_desired is None:
                    # First update - always trigger
                    self._previous_desired = desired_str
                    for listener in self._update_desired_listeners:
                        try:
                            listener(desired)
                        except Exception as e:
                            print(f"[PeripheralInstance] Error in desired listener: {e}")
                elif desired_str != self._previous_desired:
                    self._previous_desired = desired_str
                    for listener in self._update_desired_listeners:
                        try:
                            listener(desired)
                        except Exception as e:
                            print(f"[PeripheralInstance] Error in desired listener: {e}")

            # Update cached twin data
            self._update_twin_data(twin_data)

        self._client.on_twin_update(self.id, on_twin_update)

    # =========================================================================
    # Lifecycle
    # =========================================================================

    async def remove(self) -> Optional[dict[str, Any]]:
        """Delete this peripheral twin.

        Returns:
            Deleted twin data or None.
        """
        payload = {
            "data": {"twinId": self.id}
        }

        result = await self._client._connection.emit(
            "deletePeripheralTwin", payload, callback=True
        )
        return result.get("twin") if result else None

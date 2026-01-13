"""Twin Registry for managing and caching twin instances."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from phystack.hub_client.instances.edge_instance import EdgeInstance
from phystack.hub_client.instances.peripheral_instance import PeripheralInstance
from phystack.hub_client.twin_messaging import (
    TwinMessaging,
    TwinMessagingContext,
    create_twin_messaging,
)
from phystack.hub_client.types.twin_types import TwinTypeEnum

if TYPE_CHECKING:
    from phystack.hub_client.client import PhyHubClient


class TwinRegistry:
    """Registry to create, store, and retrieve twin instances."""

    def __init__(self, client: "PhyHubClient") -> None:
        """Initialize twin registry.

        Args:
            client: PhyHubClient for API calls.
        """
        self._client = client
        self._edge_instance: Optional[EdgeInstance] = None
        self._peripheral_instances: dict[str, PeripheralInstance] = {}

    async def get_edge_instance(self) -> Optional[EdgeInstance]:
        """Get or create the edge instance.

        Returns:
            EdgeInstance or None if not connected.
        """
        if self._edge_instance:
            return self._edge_instance

        instance_id = self._client._instance_id
        if not instance_id:
            return None

        # Fetch twin data
        twin_data = await self._client.get_twin_by_id(instance_id)
        if not twin_data:
            return None

        device_id = self._client._connection.device_id if self._client._connection else ""

        # Create messaging context with edge prefix
        messaging = self._create_messaging(
            twin_id=instance_id,
            device_id=device_id,
            type_prefix="edgeInstance",
        )

        # Subscribe to updates
        await self._client.subscribe_twin(instance_id)

        self._edge_instance = EdgeInstance(
            twin_id=instance_id,
            device_id=device_id,
            client=self._client,
            messaging=messaging,
            twin_data=twin_data,
        )

        return self._edge_instance

    async def get_peripheral_instance(
        self, twin_id: str
    ) -> Optional[PeripheralInstance]:
        """Get or create a peripheral instance by twin ID.

        Args:
            twin_id: ID of the peripheral twin.

        Returns:
            PeripheralInstance or None if not found.

        Raises:
            ValueError: If twin is not a peripheral type.
        """
        # Return cached if exists
        if twin_id in self._peripheral_instances:
            return self._peripheral_instances[twin_id]

        # Need edge instance for peripheral
        edge = await self.get_edge_instance()
        if not edge:
            raise ValueError("Edge instance not available")

        # Fetch twin data
        twin_data = await self._client.get_twin_by_id(twin_id)
        if not twin_data:
            raise ValueError(f"Peripheral twin {twin_id} not found")

        # Validate type
        twin_type = twin_data.get("type")
        if twin_type != TwinTypeEnum.Peripheral.value:
            raise ValueError(
                f"Twin {twin_id} is not a peripheral (type={twin_type})"
            )

        # Create messaging with peripheral prefix
        messaging = self._create_messaging(
            twin_id=twin_id,
            device_id=edge.device_id,
            type_prefix=f"peripheralInstance:{twin_id}",
        )

        # Subscribe to updates
        await self._client.subscribe_twin(twin_id)

        instance = PeripheralInstance(
            twin_id=twin_id,
            device_id=edge.device_id,
            client=self._client,
            messaging=messaging,
            edge_instance=edge,
            twin_data=twin_data,
        )

        self._peripheral_instances[twin_id] = instance
        return instance

    def _create_messaging(
        self,
        twin_id: str,
        device_id: str,
        type_prefix: str,
    ) -> TwinMessaging:
        """Create a TwinMessaging instance for an instance type.

        Args:
            twin_id: ID of the twin.
            device_id: ID of the device.
            type_prefix: Message type prefix (e.g., 'edgeInstance').

        Returns:
            TwinMessaging instance.
        """
        context = TwinMessagingContext(
            send_event=self._client._send_event,
            on_twin_message=self._client.on_twin_message,
            twin_id=twin_id,
            device_id=device_id,
            type_prefix=type_prefix,
        )
        return create_twin_messaging(context)

    def clear(self) -> None:
        """Clear all cached instances."""
        self._edge_instance = None
        self._peripheral_instances.clear()

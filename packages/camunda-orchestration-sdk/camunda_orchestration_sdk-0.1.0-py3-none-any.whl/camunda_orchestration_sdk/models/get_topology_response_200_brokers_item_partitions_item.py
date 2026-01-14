from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.get_topology_response_200_brokers_item_partitions_item_health import (
    GetTopologyResponse200BrokersItemPartitionsItemHealth,
)
from ..models.get_topology_response_200_brokers_item_partitions_item_role import (
    GetTopologyResponse200BrokersItemPartitionsItemRole,
)

T = TypeVar("T", bound="GetTopologyResponse200BrokersItemPartitionsItem")


@_attrs_define
class GetTopologyResponse200BrokersItemPartitionsItem:
    """Provides information on a partition within a broker node.

    Attributes:
        partition_id (int): The unique ID of this partition. Example: 1.
        role (GetTopologyResponse200BrokersItemPartitionsItemRole): Describes the Raft role of the broker for a given
            partition. Example: leader.
        health (GetTopologyResponse200BrokersItemPartitionsItemHealth): Describes the current health of the partition.
            Example: healthy.
    """

    partition_id: int
    role: GetTopologyResponse200BrokersItemPartitionsItemRole
    health: GetTopologyResponse200BrokersItemPartitionsItemHealth
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        partition_id = self.partition_id

        role = self.role.value

        health = self.health.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "partitionId": partition_id,
                "role": role,
                "health": health,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        partition_id = d.pop("partitionId")

        role = GetTopologyResponse200BrokersItemPartitionsItemRole(d.pop("role"))

        health = GetTopologyResponse200BrokersItemPartitionsItemHealth(d.pop("health"))

        get_topology_response_200_brokers_item_partitions_item = cls(
            partition_id=partition_id,
            role=role,
            health=health,
        )

        get_topology_response_200_brokers_item_partitions_item.additional_properties = d
        return get_topology_response_200_brokers_item_partitions_item

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_topology_response_200_brokers_item import (
        GetTopologyResponse200BrokersItem,
    )


T = TypeVar("T", bound="GetTopologyResponse200")


@_attrs_define
class GetTopologyResponse200:
    """The response of a topology request.

    Attributes:
        brokers (list[GetTopologyResponse200BrokersItem]): A list of brokers that are part of this cluster.
        cluster_size (int): The number of brokers in the cluster. Example: 3.
        partitions_count (int): The number of partitions are spread across the cluster. Example: 3.
        replication_factor (int): The configured replication factor for this cluster. Example: 3.
        gateway_version (str): The version of the Zeebe Gateway. Example: 8.8.0.
        last_completed_change_id (str): ID of the last completed change Example: -1.
        cluster_id (None | str | Unset): The cluster Id.
    """

    brokers: list[GetTopologyResponse200BrokersItem]
    cluster_size: int
    partitions_count: int
    replication_factor: int
    gateway_version: str
    last_completed_change_id: str
    cluster_id: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        brokers = []
        for brokers_item_data in self.brokers:
            brokers_item = brokers_item_data.to_dict()
            brokers.append(brokers_item)

        cluster_size = self.cluster_size

        partitions_count = self.partitions_count

        replication_factor = self.replication_factor

        gateway_version = self.gateway_version

        last_completed_change_id = self.last_completed_change_id

        cluster_id: None | str | Unset
        if isinstance(self.cluster_id, Unset):
            cluster_id = UNSET
        else:
            cluster_id = self.cluster_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "brokers": brokers,
                "clusterSize": cluster_size,
                "partitionsCount": partitions_count,
                "replicationFactor": replication_factor,
                "gatewayVersion": gateway_version,
                "lastCompletedChangeId": last_completed_change_id,
            }
        )
        if cluster_id is not UNSET:
            field_dict["clusterId"] = cluster_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_topology_response_200_brokers_item import (
            GetTopologyResponse200BrokersItem,
        )

        d = dict(src_dict)
        brokers = []
        _brokers = d.pop("brokers")
        for brokers_item_data in _brokers:
            brokers_item = GetTopologyResponse200BrokersItem.from_dict(
                brokers_item_data
            )

            brokers.append(brokers_item)

        cluster_size = d.pop("clusterSize")

        partitions_count = d.pop("partitionsCount")

        replication_factor = d.pop("replicationFactor")

        gateway_version = d.pop("gatewayVersion")

        last_completed_change_id = d.pop("lastCompletedChangeId")

        def _parse_cluster_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        cluster_id = _parse_cluster_id(d.pop("clusterId", UNSET))

        get_topology_response_200 = cls(
            brokers=brokers,
            cluster_size=cluster_size,
            partitions_count=partitions_count,
            replication_factor=replication_factor,
            gateway_version=gateway_version,
            last_completed_change_id=last_completed_change_id,
            cluster_id=cluster_id,
        )

        get_topology_response_200.additional_properties = d
        return get_topology_response_200

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

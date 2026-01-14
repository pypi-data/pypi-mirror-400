from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.get_topology_response_200_brokers_item_partitions_item import (
        GetTopologyResponse200BrokersItemPartitionsItem,
    )


T = TypeVar("T", bound="GetTopologyResponse200BrokersItem")


@_attrs_define
class GetTopologyResponse200BrokersItem:
    """Provides information on a broker node.

    Attributes:
        node_id (int): The unique (within a cluster) node ID for the broker.
        host (str): The hostname for reaching the broker. Example: zeebe-0.zeebe-broker-
            service.b7fd7aa3-b973-4128-8789-74cd2318992c-zeebe.svc.cluster.local.
        port (int): The port for reaching the broker. Example: 26501.
        partitions (list[GetTopologyResponse200BrokersItemPartitionsItem]): A list of partitions managed or replicated
            on this broker.
        version (str): The broker version. Example: 8.8.0.
    """

    node_id: int
    host: str
    port: int
    partitions: list[GetTopologyResponse200BrokersItemPartitionsItem]
    version: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        node_id = self.node_id

        host = self.host

        port = self.port

        partitions = []
        for partitions_item_data in self.partitions:
            partitions_item = partitions_item_data.to_dict()
            partitions.append(partitions_item)

        version = self.version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "nodeId": node_id,
                "host": host,
                "port": port,
                "partitions": partitions,
                "version": version,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_topology_response_200_brokers_item_partitions_item import (
            GetTopologyResponse200BrokersItemPartitionsItem,
        )

        d = dict(src_dict)
        node_id = d.pop("nodeId")

        host = d.pop("host")

        port = d.pop("port")

        partitions = []
        _partitions = d.pop("partitions")
        for partitions_item_data in _partitions:
            partitions_item = GetTopologyResponse200BrokersItemPartitionsItem.from_dict(
                partitions_item_data
            )

            partitions.append(partitions_item)

        version = d.pop("version")

        get_topology_response_200_brokers_item = cls(
            node_id=node_id,
            host=host,
            port=port,
            partitions=partitions,
            version=version,
        )

        get_topology_response_200_brokers_item.additional_properties = d
        return get_topology_response_200_brokers_item

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

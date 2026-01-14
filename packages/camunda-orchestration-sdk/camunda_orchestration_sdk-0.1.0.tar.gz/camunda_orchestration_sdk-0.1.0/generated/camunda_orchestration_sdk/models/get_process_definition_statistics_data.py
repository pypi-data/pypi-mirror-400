from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_process_definition_statistics_data_filter import (
        GetProcessDefinitionStatisticsDataFilter,
    )


T = TypeVar("T", bound="GetProcessDefinitionStatisticsData")


@_attrs_define
class GetProcessDefinitionStatisticsData:
    """Process definition element statistics request.

    Attributes:
        filter_ (GetProcessDefinitionStatisticsDataFilter | Unset): The process definition statistics search filters.
    """

    filter_: GetProcessDefinitionStatisticsDataFilter | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        filter_: dict[str, Any] | Unset = UNSET
        if not isinstance(self.filter_, Unset):
            filter_ = self.filter_.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if filter_ is not UNSET:
            field_dict["filter"] = filter_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_process_definition_statistics_data_filter import (
            GetProcessDefinitionStatisticsDataFilter,
        )

        d = dict(src_dict)
        _filter_ = d.pop("filter", UNSET)
        filter_: GetProcessDefinitionStatisticsDataFilter | Unset
        if isinstance(_filter_, Unset):
            filter_ = UNSET
        else:
            filter_ = GetProcessDefinitionStatisticsDataFilter.from_dict(_filter_)

        get_process_definition_statistics_data = cls(
            filter_=filter_,
        )

        return get_process_definition_statistics_data

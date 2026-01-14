from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.actorid_advancedfilter import ActoridAdvancedfilter


T = TypeVar("T", bound="SearchGroupsDataFilter")


@_attrs_define
class SearchGroupsDataFilter:
    """The group search filters.

    Attributes:
        group_id (ActoridAdvancedfilter | str | Unset):
        name (str | Unset): The group name search filters.
    """

    group_id: ActoridAdvancedfilter | str | Unset = UNSET
    name: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.actorid_advancedfilter import ActoridAdvancedfilter

        group_id: dict[str, Any] | str | Unset
        if isinstance(self.group_id, Unset):
            group_id = UNSET
        elif isinstance(self.group_id, ActoridAdvancedfilter):
            group_id = self.group_id.to_dict()
        else:
            group_id = self.group_id

        name = self.name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if group_id is not UNSET:
            field_dict["groupId"] = group_id
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.actorid_advancedfilter import ActoridAdvancedfilter

        d = dict(src_dict)

        def _parse_group_id(data: object) -> ActoridAdvancedfilter | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                group_id_type_1 = ActoridAdvancedfilter.from_dict(data)

                return group_id_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ActoridAdvancedfilter | str | Unset, data)

        group_id = _parse_group_id(d.pop("groupId", UNSET))

        name = d.pop("name", UNSET)

        search_groups_data_filter = cls(
            group_id=group_id,
            name=name,
        )

        search_groups_data_filter.additional_properties = d
        return search_groups_data_filter

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

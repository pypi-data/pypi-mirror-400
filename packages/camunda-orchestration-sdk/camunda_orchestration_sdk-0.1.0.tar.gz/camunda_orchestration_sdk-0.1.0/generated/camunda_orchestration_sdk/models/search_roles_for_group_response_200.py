from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.search_roles_for_group_response_200_page import (
        SearchRolesForGroupResponse200Page,
    )


T = TypeVar("T", bound="SearchRolesForGroupResponse200")


@_attrs_define
class SearchRolesForGroupResponse200:
    """
    Attributes:
        page (SearchRolesForGroupResponse200Page): Pagination information about the search results. Example:
            {'totalItems': 1, 'hasMoreTotalItems': False}.
    """

    page: SearchRolesForGroupResponse200Page
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        page = self.page.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "page": page,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.search_roles_for_group_response_200_page import (
            SearchRolesForGroupResponse200Page,
        )

        d = dict(src_dict)
        page = SearchRolesForGroupResponse200Page.from_dict(d.pop("page"))

        search_roles_for_group_response_200 = cls(
            page=page,
        )

        search_roles_for_group_response_200.additional_properties = d
        return search_roles_for_group_response_200

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

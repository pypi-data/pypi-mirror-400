from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_authentication_response_200_tenants_item import (
        GetAuthenticationResponse200TenantsItem,
    )
    from ..models.get_authentication_response_200c8_links import (
        GetAuthenticationResponse200C8Links,
    )


T = TypeVar("T", bound="GetAuthenticationResponse200")


@_attrs_define
class GetAuthenticationResponse200:
    """
    Attributes:
        tenants (list[GetAuthenticationResponse200TenantsItem]): The tenants the user is a member of.
        groups (list[str]): The groups assigned to the user. Example: ['customer-service'].
        roles (list[str]): The roles assigned to the user. Example: ['frontline-support'].
        sales_plan_type (str): The plan of the user.
        c_8_links (GetAuthenticationResponse200C8Links): The links to the components in the C8 stack.
        can_logout (bool): Flag for understanding if the user is able to perform logout.
        username (None | str | Unset): The username of the user. Example: swillis.
        display_name (None | str | Unset): The display name of the user. Example: Samantha Willis.
        email (None | str | Unset): The email of the user. Example: swillis@acme.com.
        authorized_components (list[str] | Unset): The web components the user is authorized to use. Example: ['*'].
    """

    tenants: list[GetAuthenticationResponse200TenantsItem]
    groups: list[str]
    roles: list[str]
    sales_plan_type: str
    c_8_links: GetAuthenticationResponse200C8Links
    can_logout: bool
    username: None | str | Unset = UNSET
    display_name: None | str | Unset = UNSET
    email: None | str | Unset = UNSET
    authorized_components: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tenants = []
        for tenants_item_data in self.tenants:
            tenants_item = tenants_item_data.to_dict()
            tenants.append(tenants_item)

        groups = self.groups

        roles = self.roles

        sales_plan_type = self.sales_plan_type

        c_8_links = self.c_8_links.to_dict()

        can_logout = self.can_logout

        username: None | str | Unset
        if isinstance(self.username, Unset):
            username = UNSET
        else:
            username = self.username

        display_name: None | str | Unset
        if isinstance(self.display_name, Unset):
            display_name = UNSET
        else:
            display_name = self.display_name

        email: None | str | Unset
        if isinstance(self.email, Unset):
            email = UNSET
        else:
            email = self.email

        authorized_components: list[str] | Unset = UNSET
        if not isinstance(self.authorized_components, Unset):
            authorized_components = self.authorized_components

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "tenants": tenants,
                "groups": groups,
                "roles": roles,
                "salesPlanType": sales_plan_type,
                "c8Links": c_8_links,
                "canLogout": can_logout,
            }
        )
        if username is not UNSET:
            field_dict["username"] = username
        if display_name is not UNSET:
            field_dict["displayName"] = display_name
        if email is not UNSET:
            field_dict["email"] = email
        if authorized_components is not UNSET:
            field_dict["authorizedComponents"] = authorized_components

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_authentication_response_200_tenants_item import (
            GetAuthenticationResponse200TenantsItem,
        )
        from ..models.get_authentication_response_200c8_links import (
            GetAuthenticationResponse200C8Links,
        )

        d = dict(src_dict)
        tenants = []
        _tenants = d.pop("tenants")
        for tenants_item_data in _tenants:
            tenants_item = GetAuthenticationResponse200TenantsItem.from_dict(
                tenants_item_data
            )

            tenants.append(tenants_item)

        groups = cast(list[str], d.pop("groups"))

        roles = cast(list[str], d.pop("roles"))

        sales_plan_type = d.pop("salesPlanType")

        c_8_links = GetAuthenticationResponse200C8Links.from_dict(d.pop("c8Links"))

        can_logout = d.pop("canLogout")

        def _parse_username(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        username = _parse_username(d.pop("username", UNSET))

        def _parse_display_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        display_name = _parse_display_name(d.pop("displayName", UNSET))

        def _parse_email(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        email = _parse_email(d.pop("email", UNSET))

        authorized_components = cast(list[str], d.pop("authorizedComponents", UNSET))

        get_authentication_response_200 = cls(
            tenants=tenants,
            groups=groups,
            roles=roles,
            sales_plan_type=sales_plan_type,
            c_8_links=c_8_links,
            can_logout=can_logout,
            username=username,
            display_name=display_name,
            email=email,
            authorized_components=authorized_components,
        )

        get_authentication_response_200.additional_properties = d
        return get_authentication_response_200

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

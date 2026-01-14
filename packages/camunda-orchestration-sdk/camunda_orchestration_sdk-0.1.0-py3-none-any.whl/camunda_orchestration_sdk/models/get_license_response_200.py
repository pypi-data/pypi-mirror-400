from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetLicenseResponse200")


@_attrs_define
class GetLicenseResponse200:
    """The response of a license request.

    Attributes:
        valid_license (bool): True if the Camunda license is valid, false if otherwise Example: True.
        license_type (str): Will return the license type property of the Camunda license Example: saas.
        is_commercial (bool): Will be false when a license contains a non-commerical=true property
        expires_at (datetime.datetime | None | Unset): The date when the Camunda license expires
    """

    valid_license: bool
    license_type: str
    is_commercial: bool
    expires_at: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        valid_license = self.valid_license

        license_type = self.license_type

        is_commercial = self.is_commercial

        expires_at: None | str | Unset
        if isinstance(self.expires_at, Unset):
            expires_at = UNSET
        elif isinstance(self.expires_at, datetime.datetime):
            expires_at = self.expires_at.isoformat()
        else:
            expires_at = self.expires_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "validLicense": valid_license,
                "licenseType": license_type,
                "isCommercial": is_commercial,
            }
        )
        if expires_at is not UNSET:
            field_dict["expiresAt"] = expires_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        valid_license = d.pop("validLicense")

        license_type = d.pop("licenseType")

        is_commercial = d.pop("isCommercial")

        def _parse_expires_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                expires_at_type_0 = isoparse(data)

                return expires_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        expires_at = _parse_expires_at(d.pop("expiresAt", UNSET))

        get_license_response_200 = cls(
            valid_license=valid_license,
            license_type=license_type,
            is_commercial=is_commercial,
            expires_at=expires_at,
        )

        get_license_response_200.additional_properties = d
        return get_license_response_200

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

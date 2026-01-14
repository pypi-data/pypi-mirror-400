from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateJobDataChangeset")


@_attrs_define
class UpdateJobDataChangeset:
    """JSON object with changed job attribute values. The job cannot be completed or failed with this endpoint, use the
    complete job or fail job endpoints instead.

        Attributes:
            retries (int | None | Unset): The new number of retries for the job.
            timeout (int | None | Unset): The new timeout for the job in milliseconds.
    """

    retries: int | None | Unset = UNSET
    timeout: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        retries: int | None | Unset
        if isinstance(self.retries, Unset):
            retries = UNSET
        else:
            retries = self.retries

        timeout: int | None | Unset
        if isinstance(self.timeout, Unset):
            timeout = UNSET
        else:
            timeout = self.timeout

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if retries is not UNSET:
            field_dict["retries"] = retries
        if timeout is not UNSET:
            field_dict["timeout"] = timeout

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_retries(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        retries = _parse_retries(d.pop("retries", UNSET))

        def _parse_timeout(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        timeout = _parse_timeout(d.pop("timeout", UNSET))

        update_job_data_changeset = cls(
            retries=retries,
            timeout=timeout,
        )

        update_job_data_changeset.additional_properties = d
        return update_job_data_changeset

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

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.activate_jobs_response_200_jobs_item import (
        ActivateJobsResponse200JobsItem,
    )


T = TypeVar("T", bound="ActivateJobsResponse200")


@_attrs_define
class ActivateJobsResponse200:
    """The list of activated jobs

    Attributes:
        jobs (list[ActivateJobsResponse200JobsItem]): The activated jobs.
    """

    jobs: list[ActivateJobsResponse200JobsItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        jobs = []
        for jobs_item_data in self.jobs:
            jobs_item = jobs_item_data.to_dict()
            jobs.append(jobs_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "jobs": jobs,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.activate_jobs_response_200_jobs_item import (
            ActivateJobsResponse200JobsItem,
        )

        d = dict(src_dict)
        jobs = []
        _jobs = d.pop("jobs")
        for jobs_item_data in _jobs:
            jobs_item = ActivateJobsResponse200JobsItem.from_dict(jobs_item_data)

            jobs.append(jobs_item)

        activate_jobs_response_200 = cls(
            jobs=jobs,
        )

        activate_jobs_response_200.additional_properties = d
        return activate_jobs_response_200

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

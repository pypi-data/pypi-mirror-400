from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DeleteGroupResponse500")


@_attrs_define
class DeleteGroupResponse500:
    """A Problem detail object as described in [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457). There may be additional
    properties specific to the problem type.

        Attributes:
            type_ (str | Unset): A URI identifying the problem type. Default: 'about:blank'. Example: about:blank.
            title (str | Unset): A summary of the problem type. Example: Bad Request.
            status (int | Unset): The HTTP status code for this problem. Example: 400.
            detail (str | Unset): An explanation of the problem in more detail. Example: Request property
                [maxJobsToActivates] cannot be parsed.
            instance (str | Unset): A URI path identifying the origin of the problem. Example: /v2/jobs/activation.
    """

    type_: str | Unset = "about:blank"
    title: str | Unset = UNSET
    status: int | Unset = UNSET
    detail: str | Unset = UNSET
    instance: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        title = self.title

        status = self.status

        detail = self.detail

        instance = self.instance

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if type_ is not UNSET:
            field_dict["type"] = type_
        if title is not UNSET:
            field_dict["title"] = title
        if status is not UNSET:
            field_dict["status"] = status
        if detail is not UNSET:
            field_dict["detail"] = detail
        if instance is not UNSET:
            field_dict["instance"] = instance

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = d.pop("type", UNSET)

        title = d.pop("title", UNSET)

        status = d.pop("status", UNSET)

        detail = d.pop("detail", UNSET)

        instance = d.pop("instance", UNSET)

        delete_group_response_500 = cls(
            type_=type_,
            title=title,
            status=status,
            detail=detail,
            instance=instance,
        )

        delete_group_response_500.additional_properties = d
        return delete_group_response_500

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

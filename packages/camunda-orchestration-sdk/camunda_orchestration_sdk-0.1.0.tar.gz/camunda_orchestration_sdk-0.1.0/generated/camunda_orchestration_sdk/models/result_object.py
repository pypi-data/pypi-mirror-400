from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.result_object_corrections import ResultObjectCorrections


T = TypeVar("T", bound="ResultObject")


@_attrs_define
class ResultObject:
    """Job result details for a user task completion, optionally including a denial reason and corrected task properties.

    Attributes:
        denied (bool | None | Unset): Indicates whether the worker denies the work, i.e. explicitly doesn't approve it.
            For example, a user task listener can deny the completion of a task by setting this flag to true. In this
            example, the completion of a task is represented by a job that the worker can complete as denied. As a result,
            the completion request is rejected and the task remains active. Defaults to false.
        denied_reason (None | str | Unset): The reason provided by the user task listener for denying the work.
        corrections (None | ResultObjectCorrections | Unset): JSON object with attributes that were corrected by the
            worker.

            The following attributes can be corrected, additional attributes will be ignored:

            * `assignee` - clear by providing an empty String
            * `dueDate` - clear by providing an empty String
            * `followUpDate` - clear by providing an empty String
            * `candidateGroups` - clear by providing an empty list
            * `candidateUsers` - clear by providing an empty list
            * `priority` - minimum 0, maximum 100, default 50

            Providing any of those attributes with a `null` value or omitting it preserves
            the persisted attribute's value.
        type_ (str | Unset): Used to distinguish between different types of job results. Example: userTask.
    """

    denied: bool | None | Unset = UNSET
    denied_reason: None | str | Unset = UNSET
    corrections: None | ResultObjectCorrections | Unset = UNSET
    type_: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.result_object_corrections import ResultObjectCorrections

        denied: bool | None | Unset
        if isinstance(self.denied, Unset):
            denied = UNSET
        else:
            denied = self.denied

        denied_reason: None | str | Unset
        if isinstance(self.denied_reason, Unset):
            denied_reason = UNSET
        else:
            denied_reason = self.denied_reason

        corrections: dict[str, Any] | None | Unset
        if isinstance(self.corrections, Unset):
            corrections = UNSET
        elif isinstance(self.corrections, ResultObjectCorrections):
            corrections = self.corrections.to_dict()
        else:
            corrections = self.corrections

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if denied is not UNSET:
            field_dict["denied"] = denied
        if denied_reason is not UNSET:
            field_dict["deniedReason"] = denied_reason
        if corrections is not UNSET:
            field_dict["corrections"] = corrections
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.result_object_corrections import ResultObjectCorrections

        d = dict(src_dict)

        def _parse_denied(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        denied = _parse_denied(d.pop("denied", UNSET))

        def _parse_denied_reason(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        denied_reason = _parse_denied_reason(d.pop("deniedReason", UNSET))

        def _parse_corrections(data: object) -> None | ResultObjectCorrections | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_result_object_corrections_type_0 = (
                    ResultObjectCorrections.from_dict(data)
                )

                return componentsschemas_result_object_corrections_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ResultObjectCorrections | Unset, data)

        corrections = _parse_corrections(d.pop("corrections", UNSET))

        type_ = d.pop("type", UNSET)

        result_object = cls(
            denied=denied,
            denied_reason=denied_reason,
            corrections=corrections,
            type_=type_,
        )

        result_object.additional_properties = d
        return result_object

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

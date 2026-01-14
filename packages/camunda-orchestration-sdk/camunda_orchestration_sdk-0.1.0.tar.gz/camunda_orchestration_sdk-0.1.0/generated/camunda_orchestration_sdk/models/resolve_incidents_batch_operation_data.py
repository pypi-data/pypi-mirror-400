from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.resolve_incidents_batch_operation_data_filter import (
        ResolveIncidentsBatchOperationDataFilter,
    )


T = TypeVar("T", bound="ResolveIncidentsBatchOperationData")


@_attrs_define
class ResolveIncidentsBatchOperationData:
    """The process instance filter that defines which process instances should have their incidents resolved.

    Attributes:
        filter_ (ResolveIncidentsBatchOperationDataFilter): The process instance filter.
        operation_reference (int | Unset): A reference key chosen by the user that will be part of all records resulting
            from this operation.
            Must be > 0 if provided.
    """

    filter_: ResolveIncidentsBatchOperationDataFilter
    operation_reference: int | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        filter_ = self.filter_.to_dict()

        operation_reference = self.operation_reference

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "filter": filter_,
            }
        )
        if operation_reference is not UNSET:
            field_dict["operationReference"] = operation_reference

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.resolve_incidents_batch_operation_data_filter import (
            ResolveIncidentsBatchOperationDataFilter,
        )

        d = dict(src_dict)
        filter_ = ResolveIncidentsBatchOperationDataFilter.from_dict(d.pop("filter"))

        operation_reference = d.pop("operationReference", UNSET)

        resolve_incidents_batch_operation_data = cls(
            filter_=filter_,
            operation_reference=operation_reference,
        )

        return resolve_incidents_batch_operation_data

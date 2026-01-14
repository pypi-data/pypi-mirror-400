from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.complete_job_data_variables_type_0 import (
        CompleteJobDataVariablesType0,
    )
    from ..models.result_object import ResultObject
    from ..models.result_object_1 import ResultObject1


T = TypeVar("T", bound="CompleteJobData")


@_attrs_define
class CompleteJobData:
    """
    Attributes:
        variables (CompleteJobDataVariablesType0 | None | Unset): The variables to complete the job with.
        result (None | ResultObject | ResultObject1 | Unset): The result of the completed job as determined by the
            worker.
    """

    variables: CompleteJobDataVariablesType0 | None | Unset = UNSET
    result: None | ResultObject | ResultObject1 | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.complete_job_data_variables_type_0 import (
            CompleteJobDataVariablesType0,
        )
        from ..models.result_object import ResultObject
        from ..models.result_object_1 import ResultObject1

        variables: dict[str, Any] | None | Unset
        if isinstance(self.variables, Unset):
            variables = UNSET
        elif isinstance(self.variables, CompleteJobDataVariablesType0):
            variables = self.variables.to_dict()
        else:
            variables = self.variables

        result: dict[str, Any] | None | Unset
        if isinstance(self.result, Unset):
            result = UNSET
        elif isinstance(self.result, ResultObject):
            result = self.result.to_dict()
        elif isinstance(self.result, ResultObject1):
            result = self.result.to_dict()
        else:
            result = self.result

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if variables is not UNSET:
            field_dict["variables"] = variables
        if result is not UNSET:
            field_dict["result"] = result

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.complete_job_data_variables_type_0 import (
            CompleteJobDataVariablesType0,
        )
        from ..models.result_object import ResultObject
        from ..models.result_object_1 import ResultObject1

        d = dict(src_dict)

        def _parse_variables(
            data: object,
        ) -> CompleteJobDataVariablesType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                variables_type_0 = CompleteJobDataVariablesType0.from_dict(data)

                return variables_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CompleteJobDataVariablesType0 | None | Unset, data)

        variables = _parse_variables(d.pop("variables", UNSET))

        def _parse_result(data: object) -> None | ResultObject | ResultObject1 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_result_object_type_0 = ResultObject.from_dict(data)

                return componentsschemas_result_object_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_result_object_1_type_0 = ResultObject1.from_dict(data)

                return componentsschemas_result_object_1_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ResultObject | ResultObject1 | Unset, data)

        result = _parse_result(d.pop("result", UNSET))

        complete_job_data = cls(
            variables=variables,
            result=result,
        )

        return complete_job_data

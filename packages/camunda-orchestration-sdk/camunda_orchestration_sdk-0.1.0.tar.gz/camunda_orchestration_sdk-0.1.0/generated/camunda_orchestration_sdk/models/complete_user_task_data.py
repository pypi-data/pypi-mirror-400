from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.complete_user_task_data_variables_type_0 import (
        CompleteUserTaskDataVariablesType0,
    )


T = TypeVar("T", bound="CompleteUserTaskData")


@_attrs_define
class CompleteUserTaskData:
    """
    Attributes:
        variables (CompleteUserTaskDataVariablesType0 | None | Unset): The variables to complete the user task with.
        action (None | str | Unset): A custom action value that will be accessible from user task events resulting from
            this endpoint invocation. If not provided, it will default to "complete".
    """

    variables: CompleteUserTaskDataVariablesType0 | None | Unset = UNSET
    action: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.complete_user_task_data_variables_type_0 import (
            CompleteUserTaskDataVariablesType0,
        )

        variables: dict[str, Any] | None | Unset
        if isinstance(self.variables, Unset):
            variables = UNSET
        elif isinstance(self.variables, CompleteUserTaskDataVariablesType0):
            variables = self.variables.to_dict()
        else:
            variables = self.variables

        action: None | str | Unset
        if isinstance(self.action, Unset):
            action = UNSET
        else:
            action = self.action

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if variables is not UNSET:
            field_dict["variables"] = variables
        if action is not UNSET:
            field_dict["action"] = action

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.complete_user_task_data_variables_type_0 import (
            CompleteUserTaskDataVariablesType0,
        )

        d = dict(src_dict)

        def _parse_variables(
            data: object,
        ) -> CompleteUserTaskDataVariablesType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                variables_type_0 = CompleteUserTaskDataVariablesType0.from_dict(data)

                return variables_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CompleteUserTaskDataVariablesType0 | None | Unset, data)

        variables = _parse_variables(d.pop("variables", UNSET))

        def _parse_action(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        action = _parse_action(d.pop("action", UNSET))

        complete_user_task_data = cls(
            variables=variables,
            action=action,
        )

        return complete_user_task_data

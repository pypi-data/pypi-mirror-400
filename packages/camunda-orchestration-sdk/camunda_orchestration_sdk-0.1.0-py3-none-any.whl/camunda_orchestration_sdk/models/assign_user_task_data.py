from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="AssignUserTaskData")


@_attrs_define
class AssignUserTaskData:
    """
    Attributes:
        assignee (str | Unset): The assignee for the user task. The assignee must not be empty or `null`.
        allow_override (bool | None | Unset): By default, the task is reassigned if it was already assigned. Set this to
            `false` to return an error in such cases. The task must then first be unassigned to be assigned again. Use this
            when you have users picking from group task queues to prevent race conditions.
        action (None | str | Unset): A custom action value that will be accessible from user task events resulting from
            this endpoint invocation. If not provided, it will default to "assign".
    """

    assignee: str | Unset = UNSET
    allow_override: bool | None | Unset = UNSET
    action: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        assignee = self.assignee

        allow_override: bool | None | Unset
        if isinstance(self.allow_override, Unset):
            allow_override = UNSET
        else:
            allow_override = self.allow_override

        action: None | str | Unset
        if isinstance(self.action, Unset):
            action = UNSET
        else:
            action = self.action

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if assignee is not UNSET:
            field_dict["assignee"] = assignee
        if allow_override is not UNSET:
            field_dict["allowOverride"] = allow_override
        if action is not UNSET:
            field_dict["action"] = action

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        assignee = d.pop("assignee", UNSET)

        def _parse_allow_override(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        allow_override = _parse_allow_override(d.pop("allowOverride", UNSET))

        def _parse_action(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        action = _parse_action(d.pop("action", UNSET))

        assign_user_task_data = cls(
            assignee=assignee,
            allow_override=allow_override,
            action=action,
        )

        return assign_user_task_data

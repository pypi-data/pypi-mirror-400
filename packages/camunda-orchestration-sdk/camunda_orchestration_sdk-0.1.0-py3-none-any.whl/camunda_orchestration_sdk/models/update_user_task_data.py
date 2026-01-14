from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.update_user_task_data_changeset_type_0 import (
        UpdateUserTaskDataChangesetType0,
    )


T = TypeVar("T", bound="UpdateUserTaskData")


@_attrs_define
class UpdateUserTaskData:
    """
    Attributes:
        changeset (None | Unset | UpdateUserTaskDataChangesetType0): JSON object with changed task attribute values.

            The following attributes can be adjusted with this endpoint, additional attributes
            will be ignored:

            * `candidateGroups` - reset by providing an empty list
            * `candidateUsers` - reset by providing an empty list
            * `dueDate` - reset by providing an empty String
            * `followUpDate` - reset by providing an empty String
            * `priority` - minimum 0, maximum 100, default 50

            Providing any of those attributes with a `null` value or omitting it preserves
            the persisted attribute's value.

            The assignee cannot be adjusted with this endpoint, use the Assign task endpoint.
            This ensures correct event emission for assignee changes.
        action (None | str | Unset): A custom action value that will be accessible from user task events resulting from
            this endpoint invocation. If not provided, it will default to "update".
    """

    changeset: None | Unset | UpdateUserTaskDataChangesetType0 = UNSET
    action: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.update_user_task_data_changeset_type_0 import (
            UpdateUserTaskDataChangesetType0,
        )

        changeset: dict[str, Any] | None | Unset
        if isinstance(self.changeset, Unset):
            changeset = UNSET
        elif isinstance(self.changeset, UpdateUserTaskDataChangesetType0):
            changeset = self.changeset.to_dict()
        else:
            changeset = self.changeset

        action: None | str | Unset
        if isinstance(self.action, Unset):
            action = UNSET
        else:
            action = self.action

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if changeset is not UNSET:
            field_dict["changeset"] = changeset
        if action is not UNSET:
            field_dict["action"] = action

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.update_user_task_data_changeset_type_0 import (
            UpdateUserTaskDataChangesetType0,
        )

        d = dict(src_dict)

        def _parse_changeset(
            data: object,
        ) -> None | Unset | UpdateUserTaskDataChangesetType0:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                changeset_type_0 = UpdateUserTaskDataChangesetType0.from_dict(data)

                return changeset_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UpdateUserTaskDataChangesetType0, data)

        changeset = _parse_changeset(d.pop("changeset", UNSET))

        def _parse_action(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        action = _parse_action(d.pop("action", UNSET))

        update_user_task_data = cls(
            changeset=changeset,
            action=action,
        )

        return update_user_task_data

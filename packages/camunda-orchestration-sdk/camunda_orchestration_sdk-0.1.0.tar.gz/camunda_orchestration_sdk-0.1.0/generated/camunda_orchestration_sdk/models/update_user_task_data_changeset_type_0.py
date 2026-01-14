from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateUserTaskDataChangesetType0")


@_attrs_define
class UpdateUserTaskDataChangesetType0:
    """JSON object with changed task attribute values.

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

        Attributes:
            due_date (datetime.datetime | None | Unset): The due date of the task. Reset by providing an empty String.
            follow_up_date (datetime.datetime | None | Unset): The follow-up date of the task. Reset by providing an empty
                String.
            candidate_users (list[str] | None | Unset): The list of candidate users of the task. Reset by providing an empty
                list.
            candidate_groups (list[str] | None | Unset): The list of candidate groups of the task. Reset by providing an
                empty list.
            priority (int | None | Unset): The priority of the task. Default: 50.
    """

    due_date: datetime.datetime | None | Unset = UNSET
    follow_up_date: datetime.datetime | None | Unset = UNSET
    candidate_users: list[str] | None | Unset = UNSET
    candidate_groups: list[str] | None | Unset = UNSET
    priority: int | None | Unset = 50
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        due_date: None | str | Unset
        if isinstance(self.due_date, Unset):
            due_date = UNSET
        elif isinstance(self.due_date, datetime.datetime):
            due_date = self.due_date.isoformat()
        else:
            due_date = self.due_date

        follow_up_date: None | str | Unset
        if isinstance(self.follow_up_date, Unset):
            follow_up_date = UNSET
        elif isinstance(self.follow_up_date, datetime.datetime):
            follow_up_date = self.follow_up_date.isoformat()
        else:
            follow_up_date = self.follow_up_date

        candidate_users: list[str] | None | Unset
        if isinstance(self.candidate_users, Unset):
            candidate_users = UNSET
        elif isinstance(self.candidate_users, list):
            candidate_users = self.candidate_users

        else:
            candidate_users = self.candidate_users

        candidate_groups: list[str] | None | Unset
        if isinstance(self.candidate_groups, Unset):
            candidate_groups = UNSET
        elif isinstance(self.candidate_groups, list):
            candidate_groups = self.candidate_groups

        else:
            candidate_groups = self.candidate_groups

        priority: int | None | Unset
        if isinstance(self.priority, Unset):
            priority = UNSET
        else:
            priority = self.priority

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if due_date is not UNSET:
            field_dict["dueDate"] = due_date
        if follow_up_date is not UNSET:
            field_dict["followUpDate"] = follow_up_date
        if candidate_users is not UNSET:
            field_dict["candidateUsers"] = candidate_users
        if candidate_groups is not UNSET:
            field_dict["candidateGroups"] = candidate_groups
        if priority is not UNSET:
            field_dict["priority"] = priority

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_due_date(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                due_date_type_0 = isoparse(data)

                return due_date_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        due_date = _parse_due_date(d.pop("dueDate", UNSET))

        def _parse_follow_up_date(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                follow_up_date_type_0 = isoparse(data)

                return follow_up_date_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        follow_up_date = _parse_follow_up_date(d.pop("followUpDate", UNSET))

        def _parse_candidate_users(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                candidate_users_type_0 = cast(list[str], data)

                return candidate_users_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        candidate_users = _parse_candidate_users(d.pop("candidateUsers", UNSET))

        def _parse_candidate_groups(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                candidate_groups_type_0 = cast(list[str], data)

                return candidate_groups_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        candidate_groups = _parse_candidate_groups(d.pop("candidateGroups", UNSET))

        def _parse_priority(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        priority = _parse_priority(d.pop("priority", UNSET))

        update_user_task_data_changeset_type_0 = cls(
            due_date=due_date,
            follow_up_date=follow_up_date,
            candidate_users=candidate_users,
            candidate_groups=candidate_groups,
            priority=priority,
        )

        update_user_task_data_changeset_type_0.additional_properties = d
        return update_user_task_data_changeset_type_0

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

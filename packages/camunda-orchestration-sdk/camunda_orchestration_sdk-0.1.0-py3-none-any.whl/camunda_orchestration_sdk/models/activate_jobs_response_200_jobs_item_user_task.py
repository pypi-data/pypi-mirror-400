from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ActivateJobsResponse200JobsItemUserTask")


@_attrs_define
class ActivateJobsResponse200JobsItemUserTask:
    """Contains properties of a user task.

    Attributes:
        action (str | Unset): The action performed on the user task.
        assignee (None | str | Unset): The user assigned to the task.
        candidate_groups (list[str] | Unset): The groups eligible to claim the task.
        candidate_users (list[str] | Unset): The users eligible to claim the task.
        changed_attributes (list[str] | Unset): The attributes that were changed in the task.
        due_date (None | str | Unset): The due date of the user task in ISO 8601 format.
        follow_up_date (None | str | Unset): The follow-up date of the user task in ISO 8601 format.
        form_key (str | Unset): The key of the form associated with the user task. Example: 2251799813684365.
        priority (int | None | Unset): The priority of the user task.
        user_task_key (None | str | Unset): The unique key identifying the user task.
    """

    action: str | Unset = UNSET
    assignee: None | str | Unset = UNSET
    candidate_groups: list[str] | Unset = UNSET
    candidate_users: list[str] | Unset = UNSET
    changed_attributes: list[str] | Unset = UNSET
    due_date: None | str | Unset = UNSET
    follow_up_date: None | str | Unset = UNSET
    form_key: FormKey | Unset = UNSET
    priority: int | None | Unset = UNSET
    user_task_key: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        action = self.action

        assignee: None | str | Unset
        if isinstance(self.assignee, Unset):
            assignee = UNSET
        else:
            assignee = self.assignee

        candidate_groups: list[str] | Unset = UNSET
        if not isinstance(self.candidate_groups, Unset):
            candidate_groups = self.candidate_groups

        candidate_users: list[str] | Unset = UNSET
        if not isinstance(self.candidate_users, Unset):
            candidate_users = self.candidate_users

        changed_attributes: list[str] | Unset = UNSET
        if not isinstance(self.changed_attributes, Unset):
            changed_attributes = self.changed_attributes

        due_date: None | str | Unset
        if isinstance(self.due_date, Unset):
            due_date = UNSET
        else:
            due_date = self.due_date

        follow_up_date: None | str | Unset
        if isinstance(self.follow_up_date, Unset):
            follow_up_date = UNSET
        else:
            follow_up_date = self.follow_up_date

        form_key = self.form_key

        priority: int | None | Unset
        if isinstance(self.priority, Unset):
            priority = UNSET
        else:
            priority = self.priority

        user_task_key: None | str | Unset
        if isinstance(self.user_task_key, Unset):
            user_task_key = UNSET
        else:
            user_task_key = self.user_task_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if action is not UNSET:
            field_dict["action"] = action
        if assignee is not UNSET:
            field_dict["assignee"] = assignee
        if candidate_groups is not UNSET:
            field_dict["candidateGroups"] = candidate_groups
        if candidate_users is not UNSET:
            field_dict["candidateUsers"] = candidate_users
        if changed_attributes is not UNSET:
            field_dict["changedAttributes"] = changed_attributes
        if due_date is not UNSET:
            field_dict["dueDate"] = due_date
        if follow_up_date is not UNSET:
            field_dict["followUpDate"] = follow_up_date
        if form_key is not UNSET:
            field_dict["formKey"] = form_key
        if priority is not UNSET:
            field_dict["priority"] = priority
        if user_task_key is not UNSET:
            field_dict["userTaskKey"] = user_task_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        action = d.pop("action", UNSET)

        def _parse_assignee(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        assignee = _parse_assignee(d.pop("assignee", UNSET))

        candidate_groups = cast(list[str], d.pop("candidateGroups", UNSET))

        candidate_users = cast(list[str], d.pop("candidateUsers", UNSET))

        changed_attributes = cast(list[str], d.pop("changedAttributes", UNSET))

        def _parse_due_date(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        due_date = _parse_due_date(d.pop("dueDate", UNSET))

        def _parse_follow_up_date(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        follow_up_date = _parse_follow_up_date(d.pop("followUpDate", UNSET))

        form_key = lift_form_key(_val) if (_val := d.pop("formKey", UNSET)) is not UNSET else UNSET

        def _parse_priority(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        priority = _parse_priority(d.pop("priority", UNSET))

        def _parse_user_task_key(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        user_task_key = _parse_user_task_key(d.pop("userTaskKey", UNSET))

        activate_jobs_response_200_jobs_item_user_task = cls(
            action=action,
            assignee=assignee,
            candidate_groups=candidate_groups,
            candidate_users=candidate_users,
            changed_attributes=changed_attributes,
            due_date=due_date,
            follow_up_date=follow_up_date,
            form_key=form_key,
            priority=priority,
            user_task_key=user_task_key,
        )

        activate_jobs_response_200_jobs_item_user_task.additional_properties = d
        return activate_jobs_response_200_jobs_item_user_task

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

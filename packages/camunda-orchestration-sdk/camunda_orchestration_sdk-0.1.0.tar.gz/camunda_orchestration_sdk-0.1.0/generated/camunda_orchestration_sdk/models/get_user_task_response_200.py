from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.get_user_task_response_200_state import GetUserTaskResponse200State
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_user_task_response_200_custom_headers import (
        GetUserTaskResponse200CustomHeaders,
    )


T = TypeVar("T", bound="GetUserTaskResponse200")


@_attrs_define
class GetUserTaskResponse200:
    """
    Attributes:
        name (str | Unset): The name for this user task.
        state (GetUserTaskResponse200State | Unset): The state of the user task.
        assignee (str | Unset): The assignee of the user task.
        element_id (str | Unset): The element ID of the user task. Example: Activity_106kosb.
        candidate_groups (list[str] | Unset): The candidate groups for this user task.
        candidate_users (list[str] | Unset): The candidate users for this user task.
        process_definition_id (str | Unset): The ID of the process definition. Example: new-account-onboarding-workflow.
        creation_date (datetime.datetime | Unset): The creation date of a user task.
        completion_date (datetime.datetime | Unset): The completion date of a user task.
        follow_up_date (datetime.datetime | Unset): The follow date of a user task.
        due_date (datetime.datetime | Unset): The due date of a user task.
        tenant_id (str | Unset): The unique identifier of the tenant. Example: customer-service.
        external_form_reference (str | Unset): The external form reference.
        process_definition_version (int | Unset): The version of the process definition.
        custom_headers (GetUserTaskResponse200CustomHeaders | Unset): Custom headers for the user task.
        priority (int | Unset): The priority of a user task. The higher the value the higher the priority. Default: 50.
        user_task_key (str | Unset): The key of the user task.
        element_instance_key (str | Unset): The key of the element instance. Example: 2251799813686789.
        process_name (str | Unset): The name of the process definition.
        process_definition_key (str | Unset): The key of the process definition. Example: 2251799813686749.
        process_instance_key (str | Unset): The key of the process instance. Example: 2251799813690746.
        form_key (str | Unset): The key of the form. Example: 2251799813684365.
        tags (list[str] | Unset): List of tags. Tags need to start with a letter; then alphanumerics, `_`, `-`, `:`, or
            `.`; length ≤ 100. Example: ['high-touch', 'remediation'].
    """

    name: str | Unset = UNSET
    state: GetUserTaskResponse200State | Unset = UNSET
    assignee: str | Unset = UNSET
    element_id: ElementId | Unset = UNSET
    candidate_groups: list[str] | Unset = UNSET
    candidate_users: list[str] | Unset = UNSET
    process_definition_id: ProcessDefinitionId | Unset = UNSET
    creation_date: datetime.datetime | Unset = UNSET
    completion_date: datetime.datetime | Unset = UNSET
    follow_up_date: datetime.datetime | Unset = UNSET
    due_date: datetime.datetime | Unset = UNSET
    tenant_id: TenantId | Unset = UNSET
    external_form_reference: str | Unset = UNSET
    process_definition_version: int | Unset = UNSET
    custom_headers: GetUserTaskResponse200CustomHeaders | Unset = UNSET
    priority: int | Unset = 50
    user_task_key: UserTaskKey | Unset = UNSET
    element_instance_key: ElementInstanceKey | Unset = UNSET
    process_name: str | Unset = UNSET
    process_definition_key: ProcessDefinitionKey | Unset = UNSET
    process_instance_key: ProcessInstanceKey | Unset = UNSET
    form_key: FormKey | Unset = UNSET
    tags: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        state: str | Unset = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.value

        assignee = self.assignee

        element_id = self.element_id

        candidate_groups: list[str] | Unset = UNSET
        if not isinstance(self.candidate_groups, Unset):
            candidate_groups = self.candidate_groups

        candidate_users: list[str] | Unset = UNSET
        if not isinstance(self.candidate_users, Unset):
            candidate_users = self.candidate_users

        process_definition_id = self.process_definition_id

        creation_date: str | Unset = UNSET
        if not isinstance(self.creation_date, Unset):
            creation_date = self.creation_date.isoformat()

        completion_date: str | Unset = UNSET
        if not isinstance(self.completion_date, Unset):
            completion_date = self.completion_date.isoformat()

        follow_up_date: str | Unset = UNSET
        if not isinstance(self.follow_up_date, Unset):
            follow_up_date = self.follow_up_date.isoformat()

        due_date: str | Unset = UNSET
        if not isinstance(self.due_date, Unset):
            due_date = self.due_date.isoformat()

        tenant_id = self.tenant_id

        external_form_reference = self.external_form_reference

        process_definition_version = self.process_definition_version

        custom_headers: dict[str, Any] | Unset = UNSET
        if not isinstance(self.custom_headers, Unset):
            custom_headers = self.custom_headers.to_dict()

        priority = self.priority

        user_task_key = self.user_task_key

        element_instance_key = self.element_instance_key

        process_name = self.process_name

        process_definition_key = self.process_definition_key

        process_instance_key = self.process_instance_key

        form_key = self.form_key

        tags: list[str] | Unset = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if state is not UNSET:
            field_dict["state"] = state
        if assignee is not UNSET:
            field_dict["assignee"] = assignee
        if element_id is not UNSET:
            field_dict["elementId"] = element_id
        if candidate_groups is not UNSET:
            field_dict["candidateGroups"] = candidate_groups
        if candidate_users is not UNSET:
            field_dict["candidateUsers"] = candidate_users
        if process_definition_id is not UNSET:
            field_dict["processDefinitionId"] = process_definition_id
        if creation_date is not UNSET:
            field_dict["creationDate"] = creation_date
        if completion_date is not UNSET:
            field_dict["completionDate"] = completion_date
        if follow_up_date is not UNSET:
            field_dict["followUpDate"] = follow_up_date
        if due_date is not UNSET:
            field_dict["dueDate"] = due_date
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if external_form_reference is not UNSET:
            field_dict["externalFormReference"] = external_form_reference
        if process_definition_version is not UNSET:
            field_dict["processDefinitionVersion"] = process_definition_version
        if custom_headers is not UNSET:
            field_dict["customHeaders"] = custom_headers
        if priority is not UNSET:
            field_dict["priority"] = priority
        if user_task_key is not UNSET:
            field_dict["userTaskKey"] = user_task_key
        if element_instance_key is not UNSET:
            field_dict["elementInstanceKey"] = element_instance_key
        if process_name is not UNSET:
            field_dict["processName"] = process_name
        if process_definition_key is not UNSET:
            field_dict["processDefinitionKey"] = process_definition_key
        if process_instance_key is not UNSET:
            field_dict["processInstanceKey"] = process_instance_key
        if form_key is not UNSET:
            field_dict["formKey"] = form_key
        if tags is not UNSET:
            field_dict["tags"] = tags

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_user_task_response_200_custom_headers import (
            GetUserTaskResponse200CustomHeaders,
        )

        d = dict(src_dict)
        name = d.pop("name", UNSET)

        _state = d.pop("state", UNSET)
        state: GetUserTaskResponse200State | Unset
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = GetUserTaskResponse200State(_state)

        assignee = d.pop("assignee", UNSET)

        element_id = lift_element_id(_val) if (_val := d.pop("elementId", UNSET)) is not UNSET else UNSET

        candidate_groups = cast(list[str], d.pop("candidateGroups", UNSET))

        candidate_users = cast(list[str], d.pop("candidateUsers", UNSET))

        process_definition_id = lift_process_definition_id(_val) if (_val := d.pop("processDefinitionId", UNSET)) is not UNSET else UNSET

        _creation_date = d.pop("creationDate", UNSET)
        creation_date: datetime.datetime | Unset
        if isinstance(_creation_date, Unset):
            creation_date = UNSET
        else:
            creation_date = isoparse(_creation_date)

        _completion_date = d.pop("completionDate", UNSET)
        completion_date: datetime.datetime | Unset
        if isinstance(_completion_date, Unset):
            completion_date = UNSET
        else:
            completion_date = isoparse(_completion_date)

        _follow_up_date = d.pop("followUpDate", UNSET)
        follow_up_date: datetime.datetime | Unset
        if isinstance(_follow_up_date, Unset):
            follow_up_date = UNSET
        else:
            follow_up_date = isoparse(_follow_up_date)

        _due_date = d.pop("dueDate", UNSET)
        due_date: datetime.datetime | Unset
        if isinstance(_due_date, Unset):
            due_date = UNSET
        else:
            due_date = isoparse(_due_date)

        tenant_id = lift_tenant_id(_val) if (_val := d.pop("tenantId", UNSET)) is not UNSET else UNSET

        external_form_reference = d.pop("externalFormReference", UNSET)

        process_definition_version = d.pop("processDefinitionVersion", UNSET)

        _custom_headers = d.pop("customHeaders", UNSET)
        custom_headers: GetUserTaskResponse200CustomHeaders | Unset
        if isinstance(_custom_headers, Unset):
            custom_headers = UNSET
        else:
            custom_headers = GetUserTaskResponse200CustomHeaders.from_dict(
                _custom_headers
            )

        priority = d.pop("priority", UNSET)

        user_task_key = lift_user_task_key(_val) if (_val := d.pop("userTaskKey", UNSET)) is not UNSET else UNSET

        element_instance_key = lift_element_instance_key(_val) if (_val := d.pop("elementInstanceKey", UNSET)) is not UNSET else UNSET

        process_name = d.pop("processName", UNSET)

        process_definition_key = lift_process_definition_key(_val) if (_val := d.pop("processDefinitionKey", UNSET)) is not UNSET else UNSET

        process_instance_key = lift_process_instance_key(_val) if (_val := d.pop("processInstanceKey", UNSET)) is not UNSET else UNSET

        form_key = lift_form_key(_val) if (_val := d.pop("formKey", UNSET)) is not UNSET else UNSET

        tags = cast(list[str], d.pop("tags", UNSET))

        get_user_task_response_200 = cls(
            name=name,
            state=state,
            assignee=assignee,
            element_id=element_id,
            candidate_groups=candidate_groups,
            candidate_users=candidate_users,
            process_definition_id=process_definition_id,
            creation_date=creation_date,
            completion_date=completion_date,
            follow_up_date=follow_up_date,
            due_date=due_date,
            tenant_id=tenant_id,
            external_form_reference=external_form_reference,
            process_definition_version=process_definition_version,
            custom_headers=custom_headers,
            priority=priority,
            user_task_key=user_task_key,
            element_instance_key=element_instance_key,
            process_name=process_name,
            process_definition_key=process_definition_key,
            process_instance_key=process_instance_key,
            form_key=form_key,
            tags=tags,
        )

        get_user_task_response_200.additional_properties = d
        return get_user_task_response_200

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

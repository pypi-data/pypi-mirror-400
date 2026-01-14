from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.activate_jobs_response_200_jobs_item_kind import (
    ActivateJobsResponse200JobsItemKind,
)
from ..models.activate_jobs_response_200_jobs_item_listener_event_type import (
    ActivateJobsResponse200JobsItemListenerEventType,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.activate_jobs_response_200_jobs_item_custom_headers import (
        ActivateJobsResponse200JobsItemCustomHeaders,
    )
    from ..models.activate_jobs_response_200_jobs_item_user_task import (
        ActivateJobsResponse200JobsItemUserTask,
    )
    from ..models.activate_jobs_response_200_jobs_item_variables import (
        ActivateJobsResponse200JobsItemVariables,
    )


T = TypeVar("T", bound="ActivateJobsResponse200JobsItem")


@_attrs_define
class ActivateJobsResponse200JobsItem:
    """
    Attributes:
        type_ (str): The type of the job (should match what was requested). Example: create-new-user-record.
        process_definition_id (str): The bpmn process ID of the job's process definition. Example: new-account-
            onboarding-workflow.
        process_definition_version (int): The version of the job's process definition. Example: 1.
        element_id (str): The associated task element ID. Example: Activity_106kosb.
        custom_headers (ActivateJobsResponse200JobsItemCustomHeaders): A set of custom headers defined during modelling;
            returned as a serialized JSON document.
        worker (str): The name of the worker which activated this job. Example: worker-324.
        retries (int): The amount of retries left to this job (should always be positive). Example: 3.
        deadline (int): When the job can be activated again, sent as a UNIX epoch timestamp. Example: 1757280974277.
        variables (ActivateJobsResponse200JobsItemVariables): All variables visible to the task scope, computed at
            activation time.
        tenant_id (str): The ID of the tenant that owns the job. Example: customer-service.
        job_key (str): The key, a unique identifier for the job. Example: 2251799813653498.
        process_instance_key (str): The job's process instance key. Example: 2251799813690746.
        process_definition_key (str): The key of the job's process definition. Example: 2251799813686749.
        element_instance_key (str): System-generated key for a element instance. Example: 2251799813686789.
        kind (ActivateJobsResponse200JobsItemKind): The job kind. Example: BPMN_ELEMENT.
        listener_event_type (ActivateJobsResponse200JobsItemListenerEventType): The listener event type of the job.
            Example: UNSPECIFIED.
        user_task (ActivateJobsResponse200JobsItemUserTask | Unset): Contains properties of a user task.
        tags (list[str] | Unset): List of tags. Tags need to start with a letter; then alphanumerics, `_`, `-`, `:`, or
            `.`; length ≤ 100. Example: ['high-touch', 'remediation'].
    """

    type_: str
    process_definition_id: ProcessDefinitionId
    process_definition_version: int
    element_id: ElementId
    custom_headers: ActivateJobsResponse200JobsItemCustomHeaders
    worker: str
    retries: int
    deadline: int
    variables: ActivateJobsResponse200JobsItemVariables
    tenant_id: TenantId
    job_key: JobKey
    process_instance_key: ProcessInstanceKey
    process_definition_key: ProcessDefinitionKey
    element_instance_key: ElementInstanceKey
    kind: ActivateJobsResponse200JobsItemKind
    listener_event_type: ActivateJobsResponse200JobsItemListenerEventType
    user_task: ActivateJobsResponse200JobsItemUserTask | Unset = UNSET
    tags: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        process_definition_id = self.process_definition_id

        process_definition_version = self.process_definition_version

        element_id = self.element_id

        custom_headers = self.custom_headers.to_dict()

        worker = self.worker

        retries = self.retries

        deadline = self.deadline

        variables = self.variables.to_dict()

        tenant_id = self.tenant_id

        job_key = self.job_key

        process_instance_key = self.process_instance_key

        process_definition_key = self.process_definition_key

        element_instance_key = self.element_instance_key

        kind = self.kind.value

        listener_event_type = self.listener_event_type.value

        user_task: dict[str, Any] | Unset = UNSET
        if not isinstance(self.user_task, Unset):
            user_task = self.user_task.to_dict()

        tags: list[str] | Unset = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "processDefinitionId": process_definition_id,
                "processDefinitionVersion": process_definition_version,
                "elementId": element_id,
                "customHeaders": custom_headers,
                "worker": worker,
                "retries": retries,
                "deadline": deadline,
                "variables": variables,
                "tenantId": tenant_id,
                "jobKey": job_key,
                "processInstanceKey": process_instance_key,
                "processDefinitionKey": process_definition_key,
                "elementInstanceKey": element_instance_key,
                "kind": kind,
                "listenerEventType": listener_event_type,
            }
        )
        if user_task is not UNSET:
            field_dict["userTask"] = user_task
        if tags is not UNSET:
            field_dict["tags"] = tags

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.activate_jobs_response_200_jobs_item_custom_headers import (
            ActivateJobsResponse200JobsItemCustomHeaders,
        )
        from ..models.activate_jobs_response_200_jobs_item_user_task import (
            ActivateJobsResponse200JobsItemUserTask,
        )
        from ..models.activate_jobs_response_200_jobs_item_variables import (
            ActivateJobsResponse200JobsItemVariables,
        )

        d = dict(src_dict)
        type_ = d.pop("type")

        process_definition_id = lift_process_definition_id(d.pop("processDefinitionId"))

        process_definition_version = d.pop("processDefinitionVersion")

        element_id = lift_element_id(d.pop("elementId"))

        custom_headers = ActivateJobsResponse200JobsItemCustomHeaders.from_dict(
            d.pop("customHeaders")
        )

        worker = d.pop("worker")

        retries = d.pop("retries")

        deadline = d.pop("deadline")

        variables = ActivateJobsResponse200JobsItemVariables.from_dict(
            d.pop("variables")
        )

        tenant_id = lift_tenant_id(d.pop("tenantId"))

        job_key = lift_job_key(d.pop("jobKey"))

        process_instance_key = lift_process_instance_key(d.pop("processInstanceKey"))

        process_definition_key = lift_process_definition_key(d.pop("processDefinitionKey"))

        element_instance_key = lift_element_instance_key(d.pop("elementInstanceKey"))

        kind = ActivateJobsResponse200JobsItemKind(d.pop("kind"))

        listener_event_type = ActivateJobsResponse200JobsItemListenerEventType(
            d.pop("listenerEventType")
        )

        _user_task = d.pop("userTask", UNSET)
        user_task: ActivateJobsResponse200JobsItemUserTask | Unset
        if isinstance(_user_task, Unset):
            user_task = UNSET
        else:
            user_task = ActivateJobsResponse200JobsItemUserTask.from_dict(_user_task)

        tags = cast(list[str], d.pop("tags", UNSET))

        activate_jobs_response_200_jobs_item = cls(
            type_=type_,
            process_definition_id=process_definition_id,
            process_definition_version=process_definition_version,
            element_id=element_id,
            custom_headers=custom_headers,
            worker=worker,
            retries=retries,
            deadline=deadline,
            variables=variables,
            tenant_id=tenant_id,
            job_key=job_key,
            process_instance_key=process_instance_key,
            process_definition_key=process_definition_key,
            element_instance_key=element_instance_key,
            kind=kind,
            listener_event_type=listener_event_type,
            user_task=user_task,
            tags=tags,
        )

        activate_jobs_response_200_jobs_item.additional_properties = d
        return activate_jobs_response_200_jobs_item

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

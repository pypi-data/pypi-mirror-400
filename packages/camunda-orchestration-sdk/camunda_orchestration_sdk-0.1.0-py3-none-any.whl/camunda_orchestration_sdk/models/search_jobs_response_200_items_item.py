from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.search_jobs_response_200_items_item_kind import (
    SearchJobsResponse200ItemsItemKind,
)
from ..models.search_jobs_response_200_items_item_listener_event_type import (
    SearchJobsResponse200ItemsItemListenerEventType,
)
from ..models.search_jobs_response_200_items_item_state import (
    SearchJobsResponse200ItemsItemState,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.search_jobs_response_200_items_item_custom_headers import (
        SearchJobsResponse200ItemsItemCustomHeaders,
    )


T = TypeVar("T", bound="SearchJobsResponse200ItemsItem")


@_attrs_define
class SearchJobsResponse200ItemsItem:
    """
    Attributes:
        custom_headers (SearchJobsResponse200ItemsItemCustomHeaders): A set of custom headers defined during modelling.
        element_id (str): The element ID associated with the job. Example: Activity_106kosb.
        element_instance_key (str): The element instance key associated with the job. Example: 2251799813686789.
        has_failed_with_retries_left (bool): Indicates whether the job has failed with retries left.
        job_key (str): The key, a unique identifier for the job. Example: 2251799813653498.
        kind (SearchJobsResponse200ItemsItemKind): The job kind. Example: BPMN_ELEMENT.
        listener_event_type (SearchJobsResponse200ItemsItemListenerEventType): The listener event type of the job.
            Example: UNSPECIFIED.
        process_definition_id (str): The process definition ID associated with the job. Example: new-account-onboarding-
            workflow.
        process_definition_key (str): The process definition key associated with the job. Example: 2251799813686749.
        process_instance_key (str): The process instance key associated with the job. Example: 2251799813690746.
        retries (int): The amount of retries left to this job.
        state (SearchJobsResponse200ItemsItemState): The state of the job.
        tenant_id (str): The unique identifier of the tenant. Example: customer-service.
        type_ (str): The type of the job.
        worker (str): The name of the worker of this job.
        deadline (datetime.datetime | None | Unset): If the job has been activated, when it will next be available to be
            activated.
        denied_reason (None | str | Unset): The reason provided by the user task listener for denying the work.
        end_time (datetime.datetime | Unset): When the job ended.
        error_code (None | str | Unset): The error code provided for a failed job.
        error_message (None | str | Unset): The error message that provides additional context for a failed job.
        is_denied (bool | None | Unset): Indicates whether the user task listener denies the work.
        creation_time (datetime.datetime | Unset): When the job was created. Field is present for jobs created after
            8.9.
        last_update_time (datetime.datetime | Unset): When the job was last updated. Field is present for jobs created
            after 8.9.
    """

    custom_headers: SearchJobsResponse200ItemsItemCustomHeaders
    element_id: ElementId
    element_instance_key: ElementInstanceKey
    has_failed_with_retries_left: bool
    job_key: JobKey
    kind: SearchJobsResponse200ItemsItemKind
    listener_event_type: SearchJobsResponse200ItemsItemListenerEventType
    process_definition_id: ProcessDefinitionId
    process_definition_key: ProcessDefinitionKey
    process_instance_key: ProcessInstanceKey
    retries: int
    state: SearchJobsResponse200ItemsItemState
    tenant_id: TenantId
    type_: str
    worker: str
    deadline: datetime.datetime | None | Unset = UNSET
    denied_reason: None | str | Unset = UNSET
    end_time: datetime.datetime | Unset = UNSET
    error_code: None | str | Unset = UNSET
    error_message: None | str | Unset = UNSET
    is_denied: bool | None | Unset = UNSET
    creation_time: datetime.datetime | Unset = UNSET
    last_update_time: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        custom_headers = self.custom_headers.to_dict()

        element_id = self.element_id

        element_instance_key = self.element_instance_key

        has_failed_with_retries_left = self.has_failed_with_retries_left

        job_key = self.job_key

        kind = self.kind.value

        listener_event_type = self.listener_event_type.value

        process_definition_id = self.process_definition_id

        process_definition_key = self.process_definition_key

        process_instance_key = self.process_instance_key

        retries = self.retries

        state = self.state.value

        tenant_id = self.tenant_id

        type_ = self.type_

        worker = self.worker

        deadline: None | str | Unset
        if isinstance(self.deadline, Unset):
            deadline = UNSET
        elif isinstance(self.deadline, datetime.datetime):
            deadline = self.deadline.isoformat()
        else:
            deadline = self.deadline

        denied_reason: None | str | Unset
        if isinstance(self.denied_reason, Unset):
            denied_reason = UNSET
        else:
            denied_reason = self.denied_reason

        end_time: str | Unset = UNSET
        if not isinstance(self.end_time, Unset):
            end_time = self.end_time.isoformat()

        error_code: None | str | Unset
        if isinstance(self.error_code, Unset):
            error_code = UNSET
        else:
            error_code = self.error_code

        error_message: None | str | Unset
        if isinstance(self.error_message, Unset):
            error_message = UNSET
        else:
            error_message = self.error_message

        is_denied: bool | None | Unset
        if isinstance(self.is_denied, Unset):
            is_denied = UNSET
        else:
            is_denied = self.is_denied

        creation_time: str | Unset = UNSET
        if not isinstance(self.creation_time, Unset):
            creation_time = self.creation_time.isoformat()

        last_update_time: str | Unset = UNSET
        if not isinstance(self.last_update_time, Unset):
            last_update_time = self.last_update_time.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "customHeaders": custom_headers,
                "elementId": element_id,
                "elementInstanceKey": element_instance_key,
                "hasFailedWithRetriesLeft": has_failed_with_retries_left,
                "jobKey": job_key,
                "kind": kind,
                "listenerEventType": listener_event_type,
                "processDefinitionId": process_definition_id,
                "processDefinitionKey": process_definition_key,
                "processInstanceKey": process_instance_key,
                "retries": retries,
                "state": state,
                "tenantId": tenant_id,
                "type": type_,
                "worker": worker,
            }
        )
        if deadline is not UNSET:
            field_dict["deadline"] = deadline
        if denied_reason is not UNSET:
            field_dict["deniedReason"] = denied_reason
        if end_time is not UNSET:
            field_dict["endTime"] = end_time
        if error_code is not UNSET:
            field_dict["errorCode"] = error_code
        if error_message is not UNSET:
            field_dict["errorMessage"] = error_message
        if is_denied is not UNSET:
            field_dict["isDenied"] = is_denied
        if creation_time is not UNSET:
            field_dict["creationTime"] = creation_time
        if last_update_time is not UNSET:
            field_dict["lastUpdateTime"] = last_update_time

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.search_jobs_response_200_items_item_custom_headers import (
            SearchJobsResponse200ItemsItemCustomHeaders,
        )

        d = dict(src_dict)
        custom_headers = SearchJobsResponse200ItemsItemCustomHeaders.from_dict(
            d.pop("customHeaders")
        )

        element_id = lift_element_id(d.pop("elementId"))

        element_instance_key = lift_element_instance_key(d.pop("elementInstanceKey"))

        has_failed_with_retries_left = d.pop("hasFailedWithRetriesLeft")

        job_key = lift_job_key(d.pop("jobKey"))

        kind = SearchJobsResponse200ItemsItemKind(d.pop("kind"))

        listener_event_type = SearchJobsResponse200ItemsItemListenerEventType(
            d.pop("listenerEventType")
        )

        process_definition_id = lift_process_definition_id(d.pop("processDefinitionId"))

        process_definition_key = lift_process_definition_key(d.pop("processDefinitionKey"))

        process_instance_key = lift_process_instance_key(d.pop("processInstanceKey"))

        retries = d.pop("retries")

        state = SearchJobsResponse200ItemsItemState(d.pop("state"))

        tenant_id = lift_tenant_id(d.pop("tenantId"))

        type_ = d.pop("type")

        worker = d.pop("worker")

        def _parse_deadline(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                deadline_type_0 = isoparse(data)

                return deadline_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        deadline = _parse_deadline(d.pop("deadline", UNSET))

        def _parse_denied_reason(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        denied_reason = _parse_denied_reason(d.pop("deniedReason", UNSET))

        _end_time = d.pop("endTime", UNSET)
        end_time: datetime.datetime | Unset
        if isinstance(_end_time, Unset):
            end_time = UNSET
        else:
            end_time = isoparse(_end_time)

        def _parse_error_code(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        error_code = _parse_error_code(d.pop("errorCode", UNSET))

        def _parse_error_message(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        error_message = _parse_error_message(d.pop("errorMessage", UNSET))

        def _parse_is_denied(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_denied = _parse_is_denied(d.pop("isDenied", UNSET))

        _creation_time = d.pop("creationTime", UNSET)
        creation_time: datetime.datetime | Unset
        if isinstance(_creation_time, Unset):
            creation_time = UNSET
        else:
            creation_time = isoparse(_creation_time)

        _last_update_time = d.pop("lastUpdateTime", UNSET)
        last_update_time: datetime.datetime | Unset
        if isinstance(_last_update_time, Unset):
            last_update_time = UNSET
        else:
            last_update_time = isoparse(_last_update_time)

        search_jobs_response_200_items_item = cls(
            custom_headers=custom_headers,
            element_id=element_id,
            element_instance_key=element_instance_key,
            has_failed_with_retries_left=has_failed_with_retries_left,
            job_key=job_key,
            kind=kind,
            listener_event_type=listener_event_type,
            process_definition_id=process_definition_id,
            process_definition_key=process_definition_key,
            process_instance_key=process_instance_key,
            retries=retries,
            state=state,
            tenant_id=tenant_id,
            type_=type_,
            worker=worker,
            deadline=deadline,
            denied_reason=denied_reason,
            end_time=end_time,
            error_code=error_code,
            error_message=error_message,
            is_denied=is_denied,
            creation_time=creation_time,
            last_update_time=last_update_time,
        )

        search_jobs_response_200_items_item.additional_properties = d
        return search_jobs_response_200_items_item

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

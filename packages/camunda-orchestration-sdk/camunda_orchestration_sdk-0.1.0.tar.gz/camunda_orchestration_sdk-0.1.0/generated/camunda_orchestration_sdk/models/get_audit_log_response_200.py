from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.get_audit_log_response_200_actor_type import (
    GetAuditLogResponse200ActorType,
)
from ..models.get_audit_log_response_200_batch_operation_type import (
    GetAuditLogResponse200BatchOperationType,
)
from ..models.get_audit_log_response_200_category import GetAuditLogResponse200Category
from ..models.get_audit_log_response_200_entity_type import (
    GetAuditLogResponse200EntityType,
)
from ..models.get_audit_log_response_200_operation_type import (
    GetAuditLogResponse200OperationType,
)
from ..models.get_audit_log_response_200_result import GetAuditLogResponse200Result
from ..types import UNSET, Unset

T = TypeVar("T", bound="GetAuditLogResponse200")


@_attrs_define
class GetAuditLogResponse200:
    """Audit log item.

    Attributes:
        audit_log_key (str | Unset): The unique key of the audit log entry. Example: 22517998136843567.
        entity_key (str | Unset): The key of the entity this audit log refers to.
        entity_type (GetAuditLogResponse200EntityType | Unset): The type of entity affected by the operation.
        operation_type (GetAuditLogResponse200OperationType | Unset): The type of operation performed.
        batch_operation_key (str | Unset): Key of the batch operation. Example: 2251799813684321.
        batch_operation_type (GetAuditLogResponse200BatchOperationType | Unset): The type of batch operation performed,
            if this is part of a batch.
        timestamp (datetime.datetime | Unset): The timestamp when the operation occurred.
        actor_id (str | Unset): The ID of the actor who performed the operation.
        actor_type (GetAuditLogResponse200ActorType | Unset): The type of actor who performed the operation.
        tenant_id (str | Unset): The tenant ID of the audit log. Example: customer-service.
        result (GetAuditLogResponse200Result | Unset): The result status of the operation.
        annotation (str | Unset): Additional notes about the operation.
        category (GetAuditLogResponse200Category | Unset): The category of the audit log operation.
        process_definition_id (str | Unset): The process definition ID. Example: new-account-onboarding-workflow.
        process_definition_key (str | Unset): The key of the process definition. Example: 2251799813686749.
        process_instance_key (str | Unset): The key of the process instance. Example: 2251799813690746.
        element_instance_key (str | Unset): The key of the element instance. Example: 2251799813686789.
        job_key (str | Unset): The key of the job. Example: 2251799813653498.
        user_task_key (str | Unset): The key of the user task.
        decision_requirements_id (str | Unset): The decision requirements ID.
        decision_requirements_key (str | Unset): The assigned key of the decision requirements. Example:
            2251799813683346.
        decision_definition_id (str | Unset): The decision definition ID. Example: new-hire-onboarding-workflow.
        decision_definition_key (str | Unset): The key of the decision definition. Example: 2251799813326547.
        decision_evaluation_key (str | Unset): The key of the decision evaluation. Example: 2251792362345323.
    """

    audit_log_key: AuditLogKey | Unset = UNSET
    entity_key: str | Unset = UNSET
    entity_type: GetAuditLogResponse200EntityType | Unset = UNSET
    operation_type: GetAuditLogResponse200OperationType | Unset = UNSET
    batch_operation_key: BatchOperationKey | Unset = UNSET
    batch_operation_type: GetAuditLogResponse200BatchOperationType | Unset = UNSET
    timestamp: datetime.datetime | Unset = UNSET
    actor_id: str | Unset = UNSET
    actor_type: GetAuditLogResponse200ActorType | Unset = UNSET
    tenant_id: TenantId | Unset = UNSET
    result: GetAuditLogResponse200Result | Unset = UNSET
    annotation: str | Unset = UNSET
    category: GetAuditLogResponse200Category | Unset = UNSET
    process_definition_id: ProcessDefinitionId | Unset = UNSET
    process_definition_key: ProcessDefinitionKey | Unset = UNSET
    process_instance_key: ProcessInstanceKey | Unset = UNSET
    element_instance_key: ElementInstanceKey | Unset = UNSET
    job_key: JobKey | Unset = UNSET
    user_task_key: UserTaskKey | Unset = UNSET
    decision_requirements_id: str | Unset = UNSET
    decision_requirements_key: DecisionRequirementsKey | Unset = UNSET
    decision_definition_id: DecisionDefinitionId | Unset = UNSET
    decision_definition_key: DecisionDefinitionKey | Unset = UNSET
    decision_evaluation_key: DecisionEvaluationKey | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        audit_log_key = self.audit_log_key

        entity_key = self.entity_key

        entity_type: str | Unset = UNSET
        if not isinstance(self.entity_type, Unset):
            entity_type = self.entity_type.value

        operation_type: str | Unset = UNSET
        if not isinstance(self.operation_type, Unset):
            operation_type = self.operation_type.value

        batch_operation_key = self.batch_operation_key

        batch_operation_type: str | Unset = UNSET
        if not isinstance(self.batch_operation_type, Unset):
            batch_operation_type = self.batch_operation_type.value

        timestamp: str | Unset = UNSET
        if not isinstance(self.timestamp, Unset):
            timestamp = self.timestamp.isoformat()

        actor_id = self.actor_id

        actor_type: str | Unset = UNSET
        if not isinstance(self.actor_type, Unset):
            actor_type = self.actor_type.value

        tenant_id = self.tenant_id

        result: str | Unset = UNSET
        if not isinstance(self.result, Unset):
            result = self.result.value

        annotation = self.annotation

        category: str | Unset = UNSET
        if not isinstance(self.category, Unset):
            category = self.category.value

        process_definition_id = self.process_definition_id

        process_definition_key = self.process_definition_key

        process_instance_key = self.process_instance_key

        element_instance_key = self.element_instance_key

        job_key = self.job_key

        user_task_key = self.user_task_key

        decision_requirements_id = self.decision_requirements_id

        decision_requirements_key = self.decision_requirements_key

        decision_definition_id = self.decision_definition_id

        decision_definition_key = self.decision_definition_key

        decision_evaluation_key = self.decision_evaluation_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if audit_log_key is not UNSET:
            field_dict["auditLogKey"] = audit_log_key
        if entity_key is not UNSET:
            field_dict["entityKey"] = entity_key
        if entity_type is not UNSET:
            field_dict["entityType"] = entity_type
        if operation_type is not UNSET:
            field_dict["operationType"] = operation_type
        if batch_operation_key is not UNSET:
            field_dict["batchOperationKey"] = batch_operation_key
        if batch_operation_type is not UNSET:
            field_dict["batchOperationType"] = batch_operation_type
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp
        if actor_id is not UNSET:
            field_dict["actorId"] = actor_id
        if actor_type is not UNSET:
            field_dict["actorType"] = actor_type
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if result is not UNSET:
            field_dict["result"] = result
        if annotation is not UNSET:
            field_dict["annotation"] = annotation
        if category is not UNSET:
            field_dict["category"] = category
        if process_definition_id is not UNSET:
            field_dict["processDefinitionId"] = process_definition_id
        if process_definition_key is not UNSET:
            field_dict["processDefinitionKey"] = process_definition_key
        if process_instance_key is not UNSET:
            field_dict["processInstanceKey"] = process_instance_key
        if element_instance_key is not UNSET:
            field_dict["elementInstanceKey"] = element_instance_key
        if job_key is not UNSET:
            field_dict["jobKey"] = job_key
        if user_task_key is not UNSET:
            field_dict["userTaskKey"] = user_task_key
        if decision_requirements_id is not UNSET:
            field_dict["decisionRequirementsId"] = decision_requirements_id
        if decision_requirements_key is not UNSET:
            field_dict["decisionRequirementsKey"] = decision_requirements_key
        if decision_definition_id is not UNSET:
            field_dict["decisionDefinitionId"] = decision_definition_id
        if decision_definition_key is not UNSET:
            field_dict["decisionDefinitionKey"] = decision_definition_key
        if decision_evaluation_key is not UNSET:
            field_dict["decisionEvaluationKey"] = decision_evaluation_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        audit_log_key = lift_audit_log_key(_val) if (_val := d.pop("auditLogKey", UNSET)) is not UNSET else UNSET

        entity_key = d.pop("entityKey", UNSET)

        _entity_type = d.pop("entityType", UNSET)
        entity_type: GetAuditLogResponse200EntityType | Unset
        if isinstance(_entity_type, Unset):
            entity_type = UNSET
        else:
            entity_type = GetAuditLogResponse200EntityType(_entity_type)

        _operation_type = d.pop("operationType", UNSET)
        operation_type: GetAuditLogResponse200OperationType | Unset
        if isinstance(_operation_type, Unset):
            operation_type = UNSET
        else:
            operation_type = GetAuditLogResponse200OperationType(_operation_type)

        batch_operation_key = lift_batch_operation_key(_val) if (_val := d.pop("batchOperationKey", UNSET)) is not UNSET else UNSET

        _batch_operation_type = d.pop("batchOperationType", UNSET)
        batch_operation_type: GetAuditLogResponse200BatchOperationType | Unset
        if isinstance(_batch_operation_type, Unset):
            batch_operation_type = UNSET
        else:
            batch_operation_type = GetAuditLogResponse200BatchOperationType(
                _batch_operation_type
            )

        _timestamp = d.pop("timestamp", UNSET)
        timestamp: datetime.datetime | Unset
        if isinstance(_timestamp, Unset):
            timestamp = UNSET
        else:
            timestamp = isoparse(_timestamp)

        actor_id = d.pop("actorId", UNSET)

        _actor_type = d.pop("actorType", UNSET)
        actor_type: GetAuditLogResponse200ActorType | Unset
        if isinstance(_actor_type, Unset):
            actor_type = UNSET
        else:
            actor_type = GetAuditLogResponse200ActorType(_actor_type)

        tenant_id = lift_tenant_id(_val) if (_val := d.pop("tenantId", UNSET)) is not UNSET else UNSET

        _result = d.pop("result", UNSET)
        result: GetAuditLogResponse200Result | Unset
        if isinstance(_result, Unset):
            result = UNSET
        else:
            result = GetAuditLogResponse200Result(_result)

        annotation = d.pop("annotation", UNSET)

        _category = d.pop("category", UNSET)
        category: GetAuditLogResponse200Category | Unset
        if isinstance(_category, Unset):
            category = UNSET
        else:
            category = GetAuditLogResponse200Category(_category)

        process_definition_id = lift_process_definition_id(_val) if (_val := d.pop("processDefinitionId", UNSET)) is not UNSET else UNSET

        process_definition_key = lift_process_definition_key(_val) if (_val := d.pop("processDefinitionKey", UNSET)) is not UNSET else UNSET

        process_instance_key = lift_process_instance_key(_val) if (_val := d.pop("processInstanceKey", UNSET)) is not UNSET else UNSET

        element_instance_key = lift_element_instance_key(_val) if (_val := d.pop("elementInstanceKey", UNSET)) is not UNSET else UNSET

        job_key = lift_job_key(_val) if (_val := d.pop("jobKey", UNSET)) is not UNSET else UNSET

        user_task_key = lift_user_task_key(_val) if (_val := d.pop("userTaskKey", UNSET)) is not UNSET else UNSET

        decision_requirements_id = d.pop("decisionRequirementsId", UNSET)

        decision_requirements_key = lift_decision_requirements_key(_val) if (_val := d.pop("decisionRequirementsKey", UNSET)) is not UNSET else UNSET

        decision_definition_id = lift_decision_definition_id(_val) if (_val := d.pop("decisionDefinitionId", UNSET)) is not UNSET else UNSET

        decision_definition_key = lift_decision_definition_key(_val) if (_val := d.pop("decisionDefinitionKey", UNSET)) is not UNSET else UNSET

        decision_evaluation_key = lift_decision_evaluation_key(_val) if (_val := d.pop("decisionEvaluationKey", UNSET)) is not UNSET else UNSET

        get_audit_log_response_200 = cls(
            audit_log_key=audit_log_key,
            entity_key=entity_key,
            entity_type=entity_type,
            operation_type=operation_type,
            batch_operation_key=batch_operation_key,
            batch_operation_type=batch_operation_type,
            timestamp=timestamp,
            actor_id=actor_id,
            actor_type=actor_type,
            tenant_id=tenant_id,
            result=result,
            annotation=annotation,
            category=category,
            process_definition_id=process_definition_id,
            process_definition_key=process_definition_key,
            process_instance_key=process_instance_key,
            element_instance_key=element_instance_key,
            job_key=job_key,
            user_task_key=user_task_key,
            decision_requirements_id=decision_requirements_id,
            decision_requirements_key=decision_requirements_key,
            decision_definition_id=decision_definition_id,
            decision_definition_key=decision_definition_key,
            decision_evaluation_key=decision_evaluation_key,
        )

        get_audit_log_response_200.additional_properties = d
        return get_audit_log_response_200

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

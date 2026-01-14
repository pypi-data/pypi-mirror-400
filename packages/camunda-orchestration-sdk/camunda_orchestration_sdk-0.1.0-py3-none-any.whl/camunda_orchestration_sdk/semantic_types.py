from __future__ import annotations
from typing import NewType, Any, Tuple
import re

AuditLogActorTypeEnum = NewType('AuditLogActorTypeEnum', str)
def lift_audit_log_actor_type_enum(value: Any) -> AuditLogActorTypeEnum:
	if not isinstance(value, str):
		raise TypeError(f"AuditLogActorTypeEnum must be str, got {type(value).__name__}: {value!r}")
	if value not in ['ANONYMOUS', 'CLIENT', 'UNKNOWN', 'USER']:
		raise ValueError(f"AuditLogActorTypeEnum must be one of ['ANONYMOUS', 'CLIENT', 'UNKNOWN', 'USER'], got {value!r}")
	return AuditLogActorTypeEnum(value)

def try_lift_audit_log_actor_type_enum(value: Any) -> Tuple[bool, AuditLogActorTypeEnum | Exception]:
	try:
		return True, lift_audit_log_actor_type_enum(value)
	except Exception as e:
		return False, e

AuditLogCategoryEnum = NewType('AuditLogCategoryEnum', str)
def lift_audit_log_category_enum(value: Any) -> AuditLogCategoryEnum:
	if not isinstance(value, str):
		raise TypeError(f"AuditLogCategoryEnum must be str, got {type(value).__name__}: {value!r}")
	if value not in ['ADMIN', 'DEPLOYED_RESOURCES', 'USER_TASKS']:
		raise ValueError(f"AuditLogCategoryEnum must be one of ['ADMIN', 'DEPLOYED_RESOURCES', 'USER_TASKS'], got {value!r}")
	return AuditLogCategoryEnum(value)

def try_lift_audit_log_category_enum(value: Any) -> Tuple[bool, AuditLogCategoryEnum | Exception]:
	try:
		return True, lift_audit_log_category_enum(value)
	except Exception as e:
		return False, e

AuditLogEntityTypeEnum = NewType('AuditLogEntityTypeEnum', str)
def lift_audit_log_entity_type_enum(value: Any) -> AuditLogEntityTypeEnum:
	if not isinstance(value, str):
		raise TypeError(f"AuditLogEntityTypeEnum must be str, got {type(value).__name__}: {value!r}")
	if value not in ['AUTHORIZATION', 'BATCH', 'DECISION', 'GROUP', 'INCIDENT', 'MAPPING_RULE', 'PROCESS_INSTANCE', 'RESOURCE', 'ROLE', 'TENANT', 'USER', 'USER_TASK', 'VARIABLE']:
		raise ValueError(f"AuditLogEntityTypeEnum must be one of ['AUTHORIZATION', 'BATCH', 'DECISION', 'GROUP', 'INCIDENT', 'MAPPING_RULE', 'PROCESS_INSTANCE', 'RESOURCE', 'ROLE', 'TENANT', 'USER', 'USER_TASK', 'VARIABLE'], got {value!r}")
	return AuditLogEntityTypeEnum(value)

def try_lift_audit_log_entity_type_enum(value: Any) -> Tuple[bool, AuditLogEntityTypeEnum | Exception]:
	try:
		return True, lift_audit_log_entity_type_enum(value)
	except Exception as e:
		return False, e

AuditLogKey = NewType('AuditLogKey', str)
def lift_audit_log_key(value: Any) -> AuditLogKey:
	if not isinstance(value, str):
		raise TypeError(f"AuditLogKey must be str, got {type(value).__name__}: {value!r}")
	if re.fullmatch(r'^-?[0-9]+$', value) is None:
		raise ValueError(f"AuditLogKey does not match pattern '^-?[0-9]+$', got {value!r}")
	if len(value) < 1:
		raise ValueError(f"AuditLogKey shorter than minLength 1, got {value!r}")
	if len(value) > 25:
		raise ValueError(f"AuditLogKey longer than maxLength 25, got {value!r}")
	return AuditLogKey(value)

def try_lift_audit_log_key(value: Any) -> Tuple[bool, AuditLogKey | Exception]:
	try:
		return True, lift_audit_log_key(value)
	except Exception as e:
		return False, e

AuditLogOperationTypeEnum = NewType('AuditLogOperationTypeEnum', str)
def lift_audit_log_operation_type_enum(value: Any) -> AuditLogOperationTypeEnum:
	if not isinstance(value, str):
		raise TypeError(f"AuditLogOperationTypeEnum must be str, got {type(value).__name__}: {value!r}")
	if value not in ['ASSIGN', 'CANCEL', 'COMPLETE', 'CREATE', 'DELETE', 'EVALUATE', 'MIGRATE', 'MODIFY', 'RESOLVE', 'RESUME', 'SUSPEND', 'UNASSIGN', 'UNKNOWN', 'UPDATE']:
		raise ValueError(f"AuditLogOperationTypeEnum must be one of ['ASSIGN', 'CANCEL', 'COMPLETE', 'CREATE', 'DELETE', 'EVALUATE', 'MIGRATE', 'MODIFY', 'RESOLVE', 'RESUME', 'SUSPEND', 'UNASSIGN', 'UNKNOWN', 'UPDATE'], got {value!r}")
	return AuditLogOperationTypeEnum(value)

def try_lift_audit_log_operation_type_enum(value: Any) -> Tuple[bool, AuditLogOperationTypeEnum | Exception]:
	try:
		return True, lift_audit_log_operation_type_enum(value)
	except Exception as e:
		return False, e

AuditLogResultEnum = NewType('AuditLogResultEnum', str)
def lift_audit_log_result_enum(value: Any) -> AuditLogResultEnum:
	if not isinstance(value, str):
		raise TypeError(f"AuditLogResultEnum must be str, got {type(value).__name__}: {value!r}")
	if value not in ['FAIL', 'SUCCESS']:
		raise ValueError(f"AuditLogResultEnum must be one of ['FAIL', 'SUCCESS'], got {value!r}")
	return AuditLogResultEnum(value)

def try_lift_audit_log_result_enum(value: Any) -> Tuple[bool, AuditLogResultEnum | Exception]:
	try:
		return True, lift_audit_log_result_enum(value)
	except Exception as e:
		return False, e

AuthorizationKey = NewType('AuthorizationKey', str)
def lift_authorization_key(value: Any) -> AuthorizationKey:
	if not isinstance(value, str):
		raise TypeError(f"AuthorizationKey must be str, got {type(value).__name__}: {value!r}")
	return AuthorizationKey(value)

def try_lift_authorization_key(value: Any) -> Tuple[bool, AuthorizationKey | Exception]:
	try:
		return True, lift_authorization_key(value)
	except Exception as e:
		return False, e

BatchOperationActorTypeEnum = NewType('BatchOperationActorTypeEnum', str)
def lift_batch_operation_actor_type_enum(value: Any) -> BatchOperationActorTypeEnum:
	if not isinstance(value, str):
		raise TypeError(f"BatchOperationActorTypeEnum must be str, got {type(value).__name__}: {value!r}")
	if value not in ['CLIENT', 'USER']:
		raise ValueError(f"BatchOperationActorTypeEnum must be one of ['CLIENT', 'USER'], got {value!r}")
	return BatchOperationActorTypeEnum(value)

def try_lift_batch_operation_actor_type_enum(value: Any) -> Tuple[bool, BatchOperationActorTypeEnum | Exception]:
	try:
		return True, lift_batch_operation_actor_type_enum(value)
	except Exception as e:
		return False, e

BatchOperationItemStateEnum = NewType('BatchOperationItemStateEnum', str)
def lift_batch_operation_item_state_enum(value: Any) -> BatchOperationItemStateEnum:
	if not isinstance(value, str):
		raise TypeError(f"BatchOperationItemStateEnum must be str, got {type(value).__name__}: {value!r}")
	if value not in ['ACTIVE', 'COMPLETED', 'CANCELED', 'FAILED']:
		raise ValueError(f"BatchOperationItemStateEnum must be one of ['ACTIVE', 'COMPLETED', 'CANCELED', 'FAILED'], got {value!r}")
	return BatchOperationItemStateEnum(value)

def try_lift_batch_operation_item_state_enum(value: Any) -> Tuple[bool, BatchOperationItemStateEnum | Exception]:
	try:
		return True, lift_batch_operation_item_state_enum(value)
	except Exception as e:
		return False, e

BatchOperationKey = NewType('BatchOperationKey', str)
def lift_batch_operation_key(value: Any) -> BatchOperationKey:
	if not isinstance(value, str):
		raise TypeError(f"BatchOperationKey must be str, got {type(value).__name__}: {value!r}")
	return BatchOperationKey(value)

def try_lift_batch_operation_key(value: Any) -> Tuple[bool, BatchOperationKey | Exception]:
	try:
		return True, lift_batch_operation_key(value)
	except Exception as e:
		return False, e

BatchOperationStateEnum = NewType('BatchOperationStateEnum', str)
def lift_batch_operation_state_enum(value: Any) -> BatchOperationStateEnum:
	if not isinstance(value, str):
		raise TypeError(f"BatchOperationStateEnum must be str, got {type(value).__name__}: {value!r}")
	if value not in ['ACTIVE', 'CANCELED', 'COMPLETED', 'CREATED', 'FAILED', 'PARTIALLY_COMPLETED', 'SUSPENDED']:
		raise ValueError(f"BatchOperationStateEnum must be one of ['ACTIVE', 'CANCELED', 'COMPLETED', 'CREATED', 'FAILED', 'PARTIALLY_COMPLETED', 'SUSPENDED'], got {value!r}")
	return BatchOperationStateEnum(value)

def try_lift_batch_operation_state_enum(value: Any) -> Tuple[bool, BatchOperationStateEnum | Exception]:
	try:
		return True, lift_batch_operation_state_enum(value)
	except Exception as e:
		return False, e

BatchOperationTypeEnum = NewType('BatchOperationTypeEnum', str)
def lift_batch_operation_type_enum(value: Any) -> BatchOperationTypeEnum:
	if not isinstance(value, str):
		raise TypeError(f"BatchOperationTypeEnum must be str, got {type(value).__name__}: {value!r}")
	if value not in ['ADD_VARIABLE', 'CANCEL_PROCESS_INSTANCE', 'DELETE_DECISION_DEFINITION', 'DELETE_PROCESS_DEFINITION', 'DELETE_PROCESS_INSTANCE', 'MIGRATE_PROCESS_INSTANCE', 'MODIFY_PROCESS_INSTANCE', 'RESOLVE_INCIDENT', 'UPDATE_VARIABLE']:
		raise ValueError(f"BatchOperationTypeEnum must be one of ['ADD_VARIABLE', 'CANCEL_PROCESS_INSTANCE', 'DELETE_DECISION_DEFINITION', 'DELETE_PROCESS_DEFINITION', 'DELETE_PROCESS_INSTANCE', 'MIGRATE_PROCESS_INSTANCE', 'MODIFY_PROCESS_INSTANCE', 'RESOLVE_INCIDENT', 'UPDATE_VARIABLE'], got {value!r}")
	return BatchOperationTypeEnum(value)

def try_lift_batch_operation_type_enum(value: Any) -> Tuple[bool, BatchOperationTypeEnum | Exception]:
	try:
		return True, lift_batch_operation_type_enum(value)
	except Exception as e:
		return False, e

ClusterVariableScopeEnum = NewType('ClusterVariableScopeEnum', str)
def lift_cluster_variable_scope_enum(value: Any) -> ClusterVariableScopeEnum:
	if not isinstance(value, str):
		raise TypeError(f"ClusterVariableScopeEnum must be str, got {type(value).__name__}: {value!r}")
	if value not in ['GLOBAL', 'TENANT']:
		raise ValueError(f"ClusterVariableScopeEnum must be one of ['GLOBAL', 'TENANT'], got {value!r}")
	return ClusterVariableScopeEnum(value)

def try_lift_cluster_variable_scope_enum(value: Any) -> Tuple[bool, ClusterVariableScopeEnum | Exception]:
	try:
		return True, lift_cluster_variable_scope_enum(value)
	except Exception as e:
		return False, e

DecisionDefinitionId = NewType('DecisionDefinitionId', str)
def lift_decision_definition_id(value: Any) -> DecisionDefinitionId:
	if not isinstance(value, str):
		raise TypeError(f"DecisionDefinitionId must be str, got {type(value).__name__}: {value!r}")
	if re.fullmatch(r'^[A-Za-z0-9_@.+-]+$', value) is None:
		raise ValueError(f"DecisionDefinitionId does not match pattern '^[A-Za-z0-9_@.+-]+$', got {value!r}")
	if len(value) < 1:
		raise ValueError(f"DecisionDefinitionId shorter than minLength 1, got {value!r}")
	if len(value) > 256:
		raise ValueError(f"DecisionDefinitionId longer than maxLength 256, got {value!r}")
	return DecisionDefinitionId(value)

def try_lift_decision_definition_id(value: Any) -> Tuple[bool, DecisionDefinitionId | Exception]:
	try:
		return True, lift_decision_definition_id(value)
	except Exception as e:
		return False, e

DecisionDefinitionKey = NewType('DecisionDefinitionKey', str)
def lift_decision_definition_key(value: Any) -> DecisionDefinitionKey:
	if not isinstance(value, str):
		raise TypeError(f"DecisionDefinitionKey must be str, got {type(value).__name__}: {value!r}")
	if re.fullmatch(r'^-?[0-9]+$', value) is None:
		raise ValueError(f"DecisionDefinitionKey does not match pattern '^-?[0-9]+$', got {value!r}")
	if len(value) < 1:
		raise ValueError(f"DecisionDefinitionKey shorter than minLength 1, got {value!r}")
	if len(value) > 25:
		raise ValueError(f"DecisionDefinitionKey longer than maxLength 25, got {value!r}")
	return DecisionDefinitionKey(value)

def try_lift_decision_definition_key(value: Any) -> Tuple[bool, DecisionDefinitionKey | Exception]:
	try:
		return True, lift_decision_definition_key(value)
	except Exception as e:
		return False, e

DecisionDefinitionTypeEnum = NewType('DecisionDefinitionTypeEnum', str)
def lift_decision_definition_type_enum(value: Any) -> DecisionDefinitionTypeEnum:
	if not isinstance(value, str):
		raise TypeError(f"DecisionDefinitionTypeEnum must be str, got {type(value).__name__}: {value!r}")
	if value not in ['DECISION_TABLE', 'LITERAL_EXPRESSION', 'UNKNOWN']:
		raise ValueError(f"DecisionDefinitionTypeEnum must be one of ['DECISION_TABLE', 'LITERAL_EXPRESSION', 'UNKNOWN'], got {value!r}")
	return DecisionDefinitionTypeEnum(value)

def try_lift_decision_definition_type_enum(value: Any) -> Tuple[bool, DecisionDefinitionTypeEnum | Exception]:
	try:
		return True, lift_decision_definition_type_enum(value)
	except Exception as e:
		return False, e

DecisionEvaluationInstanceKey = NewType('DecisionEvaluationInstanceKey', str)
def lift_decision_evaluation_instance_key(value: Any) -> DecisionEvaluationInstanceKey:
	if not isinstance(value, str):
		raise TypeError(f"DecisionEvaluationInstanceKey must be str, got {type(value).__name__}: {value!r}")
	if re.fullmatch(r'^-?[0-9]+$', value) is None:
		raise ValueError(f"DecisionEvaluationInstanceKey does not match pattern '^-?[0-9]+$', got {value!r}")
	if len(value) < 1:
		raise ValueError(f"DecisionEvaluationInstanceKey shorter than minLength 1, got {value!r}")
	if len(value) > 25:
		raise ValueError(f"DecisionEvaluationInstanceKey longer than maxLength 25, got {value!r}")
	return DecisionEvaluationInstanceKey(value)

def try_lift_decision_evaluation_instance_key(value: Any) -> Tuple[bool, DecisionEvaluationInstanceKey | Exception]:
	try:
		return True, lift_decision_evaluation_instance_key(value)
	except Exception as e:
		return False, e

DecisionEvaluationKey = NewType('DecisionEvaluationKey', str)
def lift_decision_evaluation_key(value: Any) -> DecisionEvaluationKey:
	if not isinstance(value, str):
		raise TypeError(f"DecisionEvaluationKey must be str, got {type(value).__name__}: {value!r}")
	if re.fullmatch(r'^-?[0-9]+$', value) is None:
		raise ValueError(f"DecisionEvaluationKey does not match pattern '^-?[0-9]+$', got {value!r}")
	if len(value) < 1:
		raise ValueError(f"DecisionEvaluationKey shorter than minLength 1, got {value!r}")
	if len(value) > 25:
		raise ValueError(f"DecisionEvaluationKey longer than maxLength 25, got {value!r}")
	return DecisionEvaluationKey(value)

def try_lift_decision_evaluation_key(value: Any) -> Tuple[bool, DecisionEvaluationKey | Exception]:
	try:
		return True, lift_decision_evaluation_key(value)
	except Exception as e:
		return False, e

DecisionInstanceKey = NewType('DecisionInstanceKey', str)
def lift_decision_instance_key(value: Any) -> DecisionInstanceKey:
	if not isinstance(value, str):
		raise TypeError(f"DecisionInstanceKey must be str, got {type(value).__name__}: {value!r}")
	if re.fullmatch(r'^-?[0-9]+$', value) is None:
		raise ValueError(f"DecisionInstanceKey does not match pattern '^-?[0-9]+$', got {value!r}")
	if len(value) < 1:
		raise ValueError(f"DecisionInstanceKey shorter than minLength 1, got {value!r}")
	if len(value) > 25:
		raise ValueError(f"DecisionInstanceKey longer than maxLength 25, got {value!r}")
	return DecisionInstanceKey(value)

def try_lift_decision_instance_key(value: Any) -> Tuple[bool, DecisionInstanceKey | Exception]:
	try:
		return True, lift_decision_instance_key(value)
	except Exception as e:
		return False, e

DecisionInstanceStateEnum = NewType('DecisionInstanceStateEnum', str)
def lift_decision_instance_state_enum(value: Any) -> DecisionInstanceStateEnum:
	if not isinstance(value, str):
		raise TypeError(f"DecisionInstanceStateEnum must be str, got {type(value).__name__}: {value!r}")
	if value not in ['EVALUATED', 'FAILED', 'UNSPECIFIED']:
		raise ValueError(f"DecisionInstanceStateEnum must be one of ['EVALUATED', 'FAILED', 'UNSPECIFIED'], got {value!r}")
	return DecisionInstanceStateEnum(value)

def try_lift_decision_instance_state_enum(value: Any) -> Tuple[bool, DecisionInstanceStateEnum | Exception]:
	try:
		return True, lift_decision_instance_state_enum(value)
	except Exception as e:
		return False, e

DecisionRequirementsKey = NewType('DecisionRequirementsKey', str)
def lift_decision_requirements_key(value: Any) -> DecisionRequirementsKey:
	if not isinstance(value, str):
		raise TypeError(f"DecisionRequirementsKey must be str, got {type(value).__name__}: {value!r}")
	if re.fullmatch(r'^-?[0-9]+$', value) is None:
		raise ValueError(f"DecisionRequirementsKey does not match pattern '^-?[0-9]+$', got {value!r}")
	if len(value) < 1:
		raise ValueError(f"DecisionRequirementsKey shorter than minLength 1, got {value!r}")
	if len(value) > 25:
		raise ValueError(f"DecisionRequirementsKey longer than maxLength 25, got {value!r}")
	return DecisionRequirementsKey(value)

def try_lift_decision_requirements_key(value: Any) -> Tuple[bool, DecisionRequirementsKey | Exception]:
	try:
		return True, lift_decision_requirements_key(value)
	except Exception as e:
		return False, e

DeploymentKey = NewType('DeploymentKey', str)
def lift_deployment_key(value: Any) -> DeploymentKey:
	if not isinstance(value, str):
		raise TypeError(f"DeploymentKey must be str, got {type(value).__name__}: {value!r}")
	return DeploymentKey(value)

def try_lift_deployment_key(value: Any) -> Tuple[bool, DeploymentKey | Exception]:
	try:
		return True, lift_deployment_key(value)
	except Exception as e:
		return False, e

DocumentId = NewType('DocumentId', str)
def lift_document_id(value: Any) -> DocumentId:
	if not isinstance(value, str):
		raise TypeError(f"DocumentId must be str, got {type(value).__name__}: {value!r}")
	return DocumentId(value)

def try_lift_document_id(value: Any) -> Tuple[bool, DocumentId | Exception]:
	try:
		return True, lift_document_id(value)
	except Exception as e:
		return False, e

ElementId = NewType('ElementId', str)
def lift_element_id(value: Any) -> ElementId:
	if not isinstance(value, str):
		raise TypeError(f"ElementId must be str, got {type(value).__name__}: {value!r}")
	return ElementId(value)

def try_lift_element_id(value: Any) -> Tuple[bool, ElementId | Exception]:
	try:
		return True, lift_element_id(value)
	except Exception as e:
		return False, e

ElementInstanceKey = NewType('ElementInstanceKey', str)
def lift_element_instance_key(value: Any) -> ElementInstanceKey:
	if not isinstance(value, str):
		raise TypeError(f"ElementInstanceKey must be str, got {type(value).__name__}: {value!r}")
	if re.fullmatch(r'^-?[0-9]+$', value) is None:
		raise ValueError(f"ElementInstanceKey does not match pattern '^-?[0-9]+$', got {value!r}")
	if len(value) < 1:
		raise ValueError(f"ElementInstanceKey shorter than minLength 1, got {value!r}")
	if len(value) > 25:
		raise ValueError(f"ElementInstanceKey longer than maxLength 25, got {value!r}")
	return ElementInstanceKey(value)

def try_lift_element_instance_key(value: Any) -> Tuple[bool, ElementInstanceKey | Exception]:
	try:
		return True, lift_element_instance_key(value)
	except Exception as e:
		return False, e

ElementInstanceStateEnum = NewType('ElementInstanceStateEnum', str)
def lift_element_instance_state_enum(value: Any) -> ElementInstanceStateEnum:
	if not isinstance(value, str):
		raise TypeError(f"ElementInstanceStateEnum must be str, got {type(value).__name__}: {value!r}")
	if value not in ['ACTIVE', 'COMPLETED', 'TERMINATED']:
		raise ValueError(f"ElementInstanceStateEnum must be one of ['ACTIVE', 'COMPLETED', 'TERMINATED'], got {value!r}")
	return ElementInstanceStateEnum(value)

def try_lift_element_instance_state_enum(value: Any) -> Tuple[bool, ElementInstanceStateEnum | Exception]:
	try:
		return True, lift_element_instance_state_enum(value)
	except Exception as e:
		return False, e

EndCursor = NewType('EndCursor', str)
def lift_end_cursor(value: Any) -> EndCursor:
	if not isinstance(value, str):
		raise TypeError(f"EndCursor must be str, got {type(value).__name__}: {value!r}")
	if re.fullmatch(r'^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}(?:==)?|[A-Za-z0-9+/]{3}=)?$', value) is None:
		raise ValueError(f"EndCursor does not match pattern '^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}(?:==)?|[A-Za-z0-9+/]{3}=)?$', got {value!r}")
	if len(value) < 2:
		raise ValueError(f"EndCursor shorter than minLength 2, got {value!r}")
	if len(value) > 300:
		raise ValueError(f"EndCursor longer than maxLength 300, got {value!r}")
	return EndCursor(value)

def try_lift_end_cursor(value: Any) -> Tuple[bool, EndCursor | Exception]:
	try:
		return True, lift_end_cursor(value)
	except Exception as e:
		return False, e

FormId = NewType('FormId', str)
def lift_form_id(value: Any) -> FormId:
	if not isinstance(value, str):
		raise TypeError(f"FormId must be str, got {type(value).__name__}: {value!r}")
	return FormId(value)

def try_lift_form_id(value: Any) -> Tuple[bool, FormId | Exception]:
	try:
		return True, lift_form_id(value)
	except Exception as e:
		return False, e

FormKey = NewType('FormKey', str)
def lift_form_key(value: Any) -> FormKey:
	if not isinstance(value, str):
		raise TypeError(f"FormKey must be str, got {type(value).__name__}: {value!r}")
	if re.fullmatch(r'^-?[0-9]+$', value) is None:
		raise ValueError(f"FormKey does not match pattern '^-?[0-9]+$', got {value!r}")
	if len(value) < 1:
		raise ValueError(f"FormKey shorter than minLength 1, got {value!r}")
	if len(value) > 25:
		raise ValueError(f"FormKey longer than maxLength 25, got {value!r}")
	return FormKey(value)

def try_lift_form_key(value: Any) -> Tuple[bool, FormKey | Exception]:
	try:
		return True, lift_form_key(value)
	except Exception as e:
		return False, e

IncidentKey = NewType('IncidentKey', str)
def lift_incident_key(value: Any) -> IncidentKey:
	if not isinstance(value, str):
		raise TypeError(f"IncidentKey must be str, got {type(value).__name__}: {value!r}")
	if re.fullmatch(r'^-?[0-9]+$', value) is None:
		raise ValueError(f"IncidentKey does not match pattern '^-?[0-9]+$', got {value!r}")
	if len(value) < 1:
		raise ValueError(f"IncidentKey shorter than minLength 1, got {value!r}")
	if len(value) > 25:
		raise ValueError(f"IncidentKey longer than maxLength 25, got {value!r}")
	return IncidentKey(value)

def try_lift_incident_key(value: Any) -> Tuple[bool, IncidentKey | Exception]:
	try:
		return True, lift_incident_key(value)
	except Exception as e:
		return False, e

JobKey = NewType('JobKey', str)
def lift_job_key(value: Any) -> JobKey:
	if not isinstance(value, str):
		raise TypeError(f"JobKey must be str, got {type(value).__name__}: {value!r}")
	if re.fullmatch(r'^-?[0-9]+$', value) is None:
		raise ValueError(f"JobKey does not match pattern '^-?[0-9]+$', got {value!r}")
	if len(value) < 1:
		raise ValueError(f"JobKey shorter than minLength 1, got {value!r}")
	if len(value) > 25:
		raise ValueError(f"JobKey longer than maxLength 25, got {value!r}")
	return JobKey(value)

def try_lift_job_key(value: Any) -> Tuple[bool, JobKey | Exception]:
	try:
		return True, lift_job_key(value)
	except Exception as e:
		return False, e

JobKindEnum = NewType('JobKindEnum', str)
def lift_job_kind_enum(value: Any) -> JobKindEnum:
	if not isinstance(value, str):
		raise TypeError(f"JobKindEnum must be str, got {type(value).__name__}: {value!r}")
	if value not in ['BPMN_ELEMENT', 'EXECUTION_LISTENER', 'TASK_LISTENER', 'AD_HOC_SUB_PROCESS']:
		raise ValueError(f"JobKindEnum must be one of ['BPMN_ELEMENT', 'EXECUTION_LISTENER', 'TASK_LISTENER', 'AD_HOC_SUB_PROCESS'], got {value!r}")
	return JobKindEnum(value)

def try_lift_job_kind_enum(value: Any) -> Tuple[bool, JobKindEnum | Exception]:
	try:
		return True, lift_job_kind_enum(value)
	except Exception as e:
		return False, e

JobListenerEventTypeEnum = NewType('JobListenerEventTypeEnum', str)
def lift_job_listener_event_type_enum(value: Any) -> JobListenerEventTypeEnum:
	if not isinstance(value, str):
		raise TypeError(f"JobListenerEventTypeEnum must be str, got {type(value).__name__}: {value!r}")
	if value not in ['ASSIGNING', 'CANCELING', 'COMPLETING', 'CREATING', 'END', 'START', 'UNSPECIFIED', 'UPDATING']:
		raise ValueError(f"JobListenerEventTypeEnum must be one of ['ASSIGNING', 'CANCELING', 'COMPLETING', 'CREATING', 'END', 'START', 'UNSPECIFIED', 'UPDATING'], got {value!r}")
	return JobListenerEventTypeEnum(value)

def try_lift_job_listener_event_type_enum(value: Any) -> Tuple[bool, JobListenerEventTypeEnum | Exception]:
	try:
		return True, lift_job_listener_event_type_enum(value)
	except Exception as e:
		return False, e

JobStateEnum = NewType('JobStateEnum', str)
def lift_job_state_enum(value: Any) -> JobStateEnum:
	if not isinstance(value, str):
		raise TypeError(f"JobStateEnum must be str, got {type(value).__name__}: {value!r}")
	if value not in ['CANCELED', 'COMPLETED', 'CREATED', 'ERROR_THROWN', 'FAILED', 'MIGRATED', 'RETRIES_UPDATED', 'TIMED_OUT']:
		raise ValueError(f"JobStateEnum must be one of ['CANCELED', 'COMPLETED', 'CREATED', 'ERROR_THROWN', 'FAILED', 'MIGRATED', 'RETRIES_UPDATED', 'TIMED_OUT'], got {value!r}")
	return JobStateEnum(value)

def try_lift_job_state_enum(value: Any) -> Tuple[bool, JobStateEnum | Exception]:
	try:
		return True, lift_job_state_enum(value)
	except Exception as e:
		return False, e

LikeFilter = NewType('LikeFilter', str)
def lift_like_filter(value: Any) -> LikeFilter:
	if not isinstance(value, str):
		raise TypeError(f"LikeFilter must be str, got {type(value).__name__}: {value!r}")
	return LikeFilter(value)

def try_lift_like_filter(value: Any) -> Tuple[bool, LikeFilter | Exception]:
	try:
		return True, lift_like_filter(value)
	except Exception as e:
		return False, e

LongKey = NewType('LongKey', str)
def lift_long_key(value: Any) -> LongKey:
	if not isinstance(value, str):
		raise TypeError(f"LongKey must be str, got {type(value).__name__}: {value!r}")
	if re.fullmatch(r'^-?[0-9]+$', value) is None:
		raise ValueError(f"LongKey does not match pattern '^-?[0-9]+$', got {value!r}")
	if len(value) < 1:
		raise ValueError(f"LongKey shorter than minLength 1, got {value!r}")
	if len(value) > 25:
		raise ValueError(f"LongKey longer than maxLength 25, got {value!r}")
	return LongKey(value)

def try_lift_long_key(value: Any) -> Tuple[bool, LongKey | Exception]:
	try:
		return True, lift_long_key(value)
	except Exception as e:
		return False, e

MessageCorrelationKey = NewType('MessageCorrelationKey', str)
def lift_message_correlation_key(value: Any) -> MessageCorrelationKey:
	if not isinstance(value, str):
		raise TypeError(f"MessageCorrelationKey must be str, got {type(value).__name__}: {value!r}")
	return MessageCorrelationKey(value)

def try_lift_message_correlation_key(value: Any) -> Tuple[bool, MessageCorrelationKey | Exception]:
	try:
		return True, lift_message_correlation_key(value)
	except Exception as e:
		return False, e

MessageKey = NewType('MessageKey', str)
def lift_message_key(value: Any) -> MessageKey:
	if not isinstance(value, str):
		raise TypeError(f"MessageKey must be str, got {type(value).__name__}: {value!r}")
	return MessageKey(value)

def try_lift_message_key(value: Any) -> Tuple[bool, MessageKey | Exception]:
	try:
		return True, lift_message_key(value)
	except Exception as e:
		return False, e

MessageSubscriptionKey = NewType('MessageSubscriptionKey', str)
def lift_message_subscription_key(value: Any) -> MessageSubscriptionKey:
	if not isinstance(value, str):
		raise TypeError(f"MessageSubscriptionKey must be str, got {type(value).__name__}: {value!r}")
	return MessageSubscriptionKey(value)

def try_lift_message_subscription_key(value: Any) -> Tuple[bool, MessageSubscriptionKey | Exception]:
	try:
		return True, lift_message_subscription_key(value)
	except Exception as e:
		return False, e

MessageSubscriptionStateEnum = NewType('MessageSubscriptionStateEnum', str)
def lift_message_subscription_state_enum(value: Any) -> MessageSubscriptionStateEnum:
	if not isinstance(value, str):
		raise TypeError(f"MessageSubscriptionStateEnum must be str, got {type(value).__name__}: {value!r}")
	if value not in ['CORRELATED', 'CREATED', 'DELETED', 'MIGRATED']:
		raise ValueError(f"MessageSubscriptionStateEnum must be one of ['CORRELATED', 'CREATED', 'DELETED', 'MIGRATED'], got {value!r}")
	return MessageSubscriptionStateEnum(value)

def try_lift_message_subscription_state_enum(value: Any) -> Tuple[bool, MessageSubscriptionStateEnum | Exception]:
	try:
		return True, lift_message_subscription_state_enum(value)
	except Exception as e:
		return False, e

OperationReference = NewType('OperationReference', int)
def lift_operation_reference(value: Any) -> OperationReference:
	if not isinstance(value, int):
		raise TypeError(f"OperationReference must be int, got {type(value).__name__}: {value!r}")
	if value < 1:
		raise ValueError(f"OperationReference smaller than minimum 1, got {value!r}")
	return OperationReference(value)

def try_lift_operation_reference(value: Any) -> Tuple[bool, OperationReference | Exception]:
	try:
		return True, lift_operation_reference(value)
	except Exception as e:
		return False, e

OwnerTypeEnum = NewType('OwnerTypeEnum', str)
def lift_owner_type_enum(value: Any) -> OwnerTypeEnum:
	if not isinstance(value, str):
		raise TypeError(f"OwnerTypeEnum must be str, got {type(value).__name__}: {value!r}")
	if value not in ['USER', 'CLIENT', 'ROLE', 'GROUP', 'MAPPING_RULE', 'UNSPECIFIED']:
		raise ValueError(f"OwnerTypeEnum must be one of ['USER', 'CLIENT', 'ROLE', 'GROUP', 'MAPPING_RULE', 'UNSPECIFIED'], got {value!r}")
	return OwnerTypeEnum(value)

def try_lift_owner_type_enum(value: Any) -> Tuple[bool, OwnerTypeEnum | Exception]:
	try:
		return True, lift_owner_type_enum(value)
	except Exception as e:
		return False, e

PermissionTypeEnum = NewType('PermissionTypeEnum', str)
def lift_permission_type_enum(value: Any) -> PermissionTypeEnum:
	if not isinstance(value, str):
		raise TypeError(f"PermissionTypeEnum must be str, got {type(value).__name__}: {value!r}")
	if value not in ['ACCESS', 'CANCEL_PROCESS_INSTANCE', 'CLAIM', 'COMPLETE', 'CREATE', 'CREATE_BATCH_OPERATION_CANCEL_PROCESS_INSTANCE', 'CREATE_BATCH_OPERATION_DELETE_DECISION_DEFINITION', 'CREATE_BATCH_OPERATION_DELETE_DECISION_INSTANCE', 'CREATE_BATCH_OPERATION_DELETE_PROCESS_DEFINITION', 'CREATE_BATCH_OPERATION_DELETE_PROCESS_INSTANCE', 'CREATE_BATCH_OPERATION_MIGRATE_PROCESS_INSTANCE', 'CREATE_BATCH_OPERATION_MODIFY_PROCESS_INSTANCE', 'CREATE_BATCH_OPERATION_RESOLVE_INCIDENT', 'CREATE_DECISION_INSTANCE', 'CREATE_PROCESS_INSTANCE', 'DELETE', 'DELETE_DECISION_INSTANCE', 'DELETE_DRD', 'DELETE_FORM', 'DELETE_PROCESS', 'DELETE_PROCESS_INSTANCE', 'DELETE_RESOURCE', 'EVALUATE', 'MODIFY_PROCESS_INSTANCE', 'READ', 'READ_DECISION_DEFINITION', 'READ_DECISION_INSTANCE', 'READ_PROCESS_DEFINITION', 'READ_PROCESS_INSTANCE', 'READ_USAGE_METRIC', 'READ_USER_TASK', 'UPDATE', 'UPDATE_PROCESS_INSTANCE', 'UPDATE_USER_TASK']:
		raise ValueError(f"PermissionTypeEnum must be one of ['ACCESS', 'CANCEL_PROCESS_INSTANCE', 'CLAIM', 'COMPLETE', 'CREATE', 'CREATE_BATCH_OPERATION_CANCEL_PROCESS_INSTANCE', 'CREATE_BATCH_OPERATION_DELETE_DECISION_DEFINITION', 'CREATE_BATCH_OPERATION_DELETE_DECISION_INSTANCE', 'CREATE_BATCH_OPERATION_DELETE_PROCESS_DEFINITION', 'CREATE_BATCH_OPERATION_DELETE_PROCESS_INSTANCE', 'CREATE_BATCH_OPERATION_MIGRATE_PROCESS_INSTANCE', 'CREATE_BATCH_OPERATION_MODIFY_PROCESS_INSTANCE', 'CREATE_BATCH_OPERATION_RESOLVE_INCIDENT', 'CREATE_DECISION_INSTANCE', 'CREATE_PROCESS_INSTANCE', 'DELETE', 'DELETE_DECISION_INSTANCE', 'DELETE_DRD', 'DELETE_FORM', 'DELETE_PROCESS', 'DELETE_PROCESS_INSTANCE', 'DELETE_RESOURCE', 'EVALUATE', 'MODIFY_PROCESS_INSTANCE', 'READ', 'READ_DECISION_DEFINITION', 'READ_DECISION_INSTANCE', 'READ_PROCESS_DEFINITION', 'READ_PROCESS_INSTANCE', 'READ_USAGE_METRIC', 'READ_USER_TASK', 'UPDATE', 'UPDATE_PROCESS_INSTANCE', 'UPDATE_USER_TASK'], got {value!r}")
	return PermissionTypeEnum(value)

def try_lift_permission_type_enum(value: Any) -> Tuple[bool, PermissionTypeEnum | Exception]:
	try:
		return True, lift_permission_type_enum(value)
	except Exception as e:
		return False, e

ProcessDefinitionId = NewType('ProcessDefinitionId', str)
def lift_process_definition_id(value: Any) -> ProcessDefinitionId:
	if not isinstance(value, str):
		raise TypeError(f"ProcessDefinitionId must be str, got {type(value).__name__}: {value!r}")
	if re.fullmatch(r'^[a-zA-Z_][a-zA-Z0-9_\\-\\.]*$', value) is None:
		raise ValueError(f"ProcessDefinitionId does not match pattern '^[a-zA-Z_][a-zA-Z0-9_\\-\\.]*$', got {value!r}")
	if len(value) < 1:
		raise ValueError(f"ProcessDefinitionId shorter than minLength 1, got {value!r}")
	return ProcessDefinitionId(value)

def try_lift_process_definition_id(value: Any) -> Tuple[bool, ProcessDefinitionId | Exception]:
	try:
		return True, lift_process_definition_id(value)
	except Exception as e:
		return False, e

ProcessDefinitionKey = NewType('ProcessDefinitionKey', str)
def lift_process_definition_key(value: Any) -> ProcessDefinitionKey:
	if not isinstance(value, str):
		raise TypeError(f"ProcessDefinitionKey must be str, got {type(value).__name__}: {value!r}")
	if re.fullmatch(r'^-?[0-9]+$', value) is None:
		raise ValueError(f"ProcessDefinitionKey does not match pattern '^-?[0-9]+$', got {value!r}")
	if len(value) < 1:
		raise ValueError(f"ProcessDefinitionKey shorter than minLength 1, got {value!r}")
	if len(value) > 25:
		raise ValueError(f"ProcessDefinitionKey longer than maxLength 25, got {value!r}")
	return ProcessDefinitionKey(value)

def try_lift_process_definition_key(value: Any) -> Tuple[bool, ProcessDefinitionKey | Exception]:
	try:
		return True, lift_process_definition_key(value)
	except Exception as e:
		return False, e

ProcessInstanceKey = NewType('ProcessInstanceKey', str)
def lift_process_instance_key(value: Any) -> ProcessInstanceKey:
	if not isinstance(value, str):
		raise TypeError(f"ProcessInstanceKey must be str, got {type(value).__name__}: {value!r}")
	if re.fullmatch(r'^-?[0-9]+$', value) is None:
		raise ValueError(f"ProcessInstanceKey does not match pattern '^-?[0-9]+$', got {value!r}")
	if len(value) < 1:
		raise ValueError(f"ProcessInstanceKey shorter than minLength 1, got {value!r}")
	if len(value) > 25:
		raise ValueError(f"ProcessInstanceKey longer than maxLength 25, got {value!r}")
	return ProcessInstanceKey(value)

def try_lift_process_instance_key(value: Any) -> Tuple[bool, ProcessInstanceKey | Exception]:
	try:
		return True, lift_process_instance_key(value)
	except Exception as e:
		return False, e

ProcessInstanceStateEnum = NewType('ProcessInstanceStateEnum', str)
def lift_process_instance_state_enum(value: Any) -> ProcessInstanceStateEnum:
	if not isinstance(value, str):
		raise TypeError(f"ProcessInstanceStateEnum must be str, got {type(value).__name__}: {value!r}")
	if value not in ['ACTIVE', 'COMPLETED', 'TERMINATED']:
		raise ValueError(f"ProcessInstanceStateEnum must be one of ['ACTIVE', 'COMPLETED', 'TERMINATED'], got {value!r}")
	return ProcessInstanceStateEnum(value)

def try_lift_process_instance_state_enum(value: Any) -> Tuple[bool, ProcessInstanceStateEnum | Exception]:
	try:
		return True, lift_process_instance_state_enum(value)
	except Exception as e:
		return False, e

ResourceKey = NewType('ResourceKey', str)
def lift_resource_key(value: Any) -> ResourceKey:
	if not isinstance(value, str):
		raise TypeError(f"ResourceKey must be str, got {type(value).__name__}: {value!r}")
	return ResourceKey(value)

def try_lift_resource_key(value: Any) -> Tuple[bool, ResourceKey | Exception]:
	try:
		return True, lift_resource_key(value)
	except Exception as e:
		return False, e

ResourceTypeEnum = NewType('ResourceTypeEnum', str)
def lift_resource_type_enum(value: Any) -> ResourceTypeEnum:
	if not isinstance(value, str):
		raise TypeError(f"ResourceTypeEnum must be str, got {type(value).__name__}: {value!r}")
	if value not in ['AUDIT_LOG', 'AUTHORIZATION', 'BATCH', 'CLUSTER_VARIABLE', 'COMPONENT', 'DECISION_DEFINITION', 'DECISION_REQUIREMENTS_DEFINITION', 'DOCUMENT', 'EXPRESSION', 'GROUP', 'MAPPING_RULE', 'MESSAGE', 'PROCESS_DEFINITION', 'RESOURCE', 'ROLE', 'SYSTEM', 'TENANT', 'USER', 'USER_TASK']:
		raise ValueError(f"ResourceTypeEnum must be one of ['AUDIT_LOG', 'AUTHORIZATION', 'BATCH', 'CLUSTER_VARIABLE', 'COMPONENT', 'DECISION_DEFINITION', 'DECISION_REQUIREMENTS_DEFINITION', 'DOCUMENT', 'EXPRESSION', 'GROUP', 'MAPPING_RULE', 'MESSAGE', 'PROCESS_DEFINITION', 'RESOURCE', 'ROLE', 'SYSTEM', 'TENANT', 'USER', 'USER_TASK'], got {value!r}")
	return ResourceTypeEnum(value)

def try_lift_resource_type_enum(value: Any) -> Tuple[bool, ResourceTypeEnum | Exception]:
	try:
		return True, lift_resource_type_enum(value)
	except Exception as e:
		return False, e

ScopeKey = NewType('ScopeKey', str)
def lift_scope_key(value: Any) -> ScopeKey:
	if not isinstance(value, str):
		raise TypeError(f"ScopeKey must be str, got {type(value).__name__}: {value!r}")
	if re.fullmatch(r'^-?[0-9]+$', value) is None:
		raise ValueError(f"ScopeKey does not match pattern '^-?[0-9]+$', got {value!r}")
	if len(value) < 1:
		raise ValueError(f"ScopeKey shorter than minLength 1, got {value!r}")
	if len(value) > 25:
		raise ValueError(f"ScopeKey longer than maxLength 25, got {value!r}")
	return ScopeKey(value)

def try_lift_scope_key(value: Any) -> Tuple[bool, ScopeKey | Exception]:
	try:
		return True, lift_scope_key(value)
	except Exception as e:
		return False, e

SignalKey = NewType('SignalKey', str)
def lift_signal_key(value: Any) -> SignalKey:
	if not isinstance(value, str):
		raise TypeError(f"SignalKey must be str, got {type(value).__name__}: {value!r}")
	return SignalKey(value)

def try_lift_signal_key(value: Any) -> Tuple[bool, SignalKey | Exception]:
	try:
		return True, lift_signal_key(value)
	except Exception as e:
		return False, e

SortOrderEnum = NewType('SortOrderEnum', str)
def lift_sort_order_enum(value: Any) -> SortOrderEnum:
	if not isinstance(value, str):
		raise TypeError(f"SortOrderEnum must be str, got {type(value).__name__}: {value!r}")
	if value not in ['ASC', 'DESC']:
		raise ValueError(f"SortOrderEnum must be one of ['ASC', 'DESC'], got {value!r}")
	return SortOrderEnum(value)

def try_lift_sort_order_enum(value: Any) -> Tuple[bool, SortOrderEnum | Exception]:
	try:
		return True, lift_sort_order_enum(value)
	except Exception as e:
		return False, e

StartCursor = NewType('StartCursor', str)
def lift_start_cursor(value: Any) -> StartCursor:
	if not isinstance(value, str):
		raise TypeError(f"StartCursor must be str, got {type(value).__name__}: {value!r}")
	if re.fullmatch(r'^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}(?:==)?|[A-Za-z0-9+/]{3}=)?$', value) is None:
		raise ValueError(f"StartCursor does not match pattern '^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}(?:==)?|[A-Za-z0-9+/]{3}=)?$', got {value!r}")
	if len(value) < 2:
		raise ValueError(f"StartCursor shorter than minLength 2, got {value!r}")
	if len(value) > 300:
		raise ValueError(f"StartCursor longer than maxLength 300, got {value!r}")
	return StartCursor(value)

def try_lift_start_cursor(value: Any) -> Tuple[bool, StartCursor | Exception]:
	try:
		return True, lift_start_cursor(value)
	except Exception as e:
		return False, e

Tag = NewType('Tag', str)
def lift_tag(value: Any) -> Tag:
	if not isinstance(value, str):
		raise TypeError(f"Tag must be str, got {type(value).__name__}: {value!r}")
	if re.fullmatch(r'^[A-Za-z][A-Za-z0-9_\\-:.]{0,99}$', value) is None:
		raise ValueError(f"Tag does not match pattern '^[A-Za-z][A-Za-z0-9_\\-:.]{0,99}$', got {value!r}")
	if len(value) < 1:
		raise ValueError(f"Tag shorter than minLength 1, got {value!r}")
	if len(value) > 100:
		raise ValueError(f"Tag longer than maxLength 100, got {value!r}")
	return Tag(value)

def try_lift_tag(value: Any) -> Tuple[bool, Tag | Exception]:
	try:
		return True, lift_tag(value)
	except Exception as e:
		return False, e

TenantId = NewType('TenantId', str)
def lift_tenant_id(value: Any) -> TenantId:
	if not isinstance(value, str):
		raise TypeError(f"TenantId must be str, got {type(value).__name__}: {value!r}")
	if re.fullmatch(r'^(<default>|[A-Za-z0-9_@.+-]+)$', value) is None:
		raise ValueError(f"TenantId does not match pattern '^(<default>|[A-Za-z0-9_@.+-]+)$', got {value!r}")
	if len(value) < 1:
		raise ValueError(f"TenantId shorter than minLength 1, got {value!r}")
	if len(value) > 256:
		raise ValueError(f"TenantId longer than maxLength 256, got {value!r}")
	return TenantId(value)

def try_lift_tenant_id(value: Any) -> Tuple[bool, TenantId | Exception]:
	try:
		return True, lift_tenant_id(value)
	except Exception as e:
		return False, e

UserTaskKey = NewType('UserTaskKey', str)
def lift_user_task_key(value: Any) -> UserTaskKey:
	if not isinstance(value, str):
		raise TypeError(f"UserTaskKey must be str, got {type(value).__name__}: {value!r}")
	if re.fullmatch(r'^-?[0-9]+$', value) is None:
		raise ValueError(f"UserTaskKey does not match pattern '^-?[0-9]+$', got {value!r}")
	if len(value) < 1:
		raise ValueError(f"UserTaskKey shorter than minLength 1, got {value!r}")
	if len(value) > 25:
		raise ValueError(f"UserTaskKey longer than maxLength 25, got {value!r}")
	return UserTaskKey(value)

def try_lift_user_task_key(value: Any) -> Tuple[bool, UserTaskKey | Exception]:
	try:
		return True, lift_user_task_key(value)
	except Exception as e:
		return False, e

UserTaskStateEnum = NewType('UserTaskStateEnum', str)
def lift_user_task_state_enum(value: Any) -> UserTaskStateEnum:
	if not isinstance(value, str):
		raise TypeError(f"UserTaskStateEnum must be str, got {type(value).__name__}: {value!r}")
	if value not in ['CREATING', 'CREATED', 'ASSIGNING', 'UPDATING', 'COMPLETING', 'COMPLETED', 'CANCELING', 'CANCELED', 'FAILED']:
		raise ValueError(f"UserTaskStateEnum must be one of ['CREATING', 'CREATED', 'ASSIGNING', 'UPDATING', 'COMPLETING', 'COMPLETED', 'CANCELING', 'CANCELED', 'FAILED'], got {value!r}")
	return UserTaskStateEnum(value)

def try_lift_user_task_state_enum(value: Any) -> Tuple[bool, UserTaskStateEnum | Exception]:
	try:
		return True, lift_user_task_state_enum(value)
	except Exception as e:
		return False, e

Username = NewType('Username', str)
def lift_username(value: Any) -> Username:
	if not isinstance(value, str):
		raise TypeError(f"Username must be str, got {type(value).__name__}: {value!r}")
	if re.fullmatch(r'^(<default>|[A-Za-z0-9_@.+-]+)$', value) is None:
		raise ValueError(f"Username does not match pattern '^(<default>|[A-Za-z0-9_@.+-]+)$', got {value!r}")
	if len(value) < 1:
		raise ValueError(f"Username shorter than minLength 1, got {value!r}")
	if len(value) > 256:
		raise ValueError(f"Username longer than maxLength 256, got {value!r}")
	return Username(value)

def try_lift_username(value: Any) -> Tuple[bool, Username | Exception]:
	try:
		return True, lift_username(value)
	except Exception as e:
		return False, e

VariableKey = NewType('VariableKey', str)
def lift_variable_key(value: Any) -> VariableKey:
	if not isinstance(value, str):
		raise TypeError(f"VariableKey must be str, got {type(value).__name__}: {value!r}")
	if re.fullmatch(r'^-?[0-9]+$', value) is None:
		raise ValueError(f"VariableKey does not match pattern '^-?[0-9]+$', got {value!r}")
	if len(value) < 1:
		raise ValueError(f"VariableKey shorter than minLength 1, got {value!r}")
	if len(value) > 25:
		raise ValueError(f"VariableKey longer than maxLength 25, got {value!r}")
	return VariableKey(value)

def try_lift_variable_key(value: Any) -> Tuple[bool, VariableKey | Exception]:
	try:
		return True, lift_variable_key(value)
	except Exception as e:
		return False, e


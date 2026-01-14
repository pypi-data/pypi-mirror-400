from __future__ import annotations
import ssl
from typing import Any

import httpx
from attrs import define, evolve, field


from .types import UNSET, Unset
from typing import TYPE_CHECKING
import asyncio
from typing import Callable
from .runtime.job_worker import JobWorker, WorkerConfig, JobHandler
from pathlib import Path
from .models.create_deployment_response_200 import CreateDeploymentResponse200
from .models.create_deployment_response_200_deployments_item_process_definition import CreateDeploymentResponse200DeploymentsItemProcessDefinition
from .models.create_deployment_response_200_deployments_item_decision_definition import CreateDeploymentResponse200DeploymentsItemDecisionDefinition
from .models.create_deployment_response_200_deployments_item_decision_requirements import CreateDeploymentResponse200DeploymentsItemDecisionRequirements
from .models.create_deployment_response_200_deployments_item_form import CreateDeploymentResponse200DeploymentsItemForm

if TYPE_CHECKING:
    from . import errors
    from .models.activate_ad_hoc_sub_process_activities_data import ActivateAdHocSubProcessActivitiesData
    from .models.activate_ad_hoc_sub_process_activities_response_400 import ActivateAdHocSubProcessActivitiesResponse400
    from .models.activate_ad_hoc_sub_process_activities_response_401 import ActivateAdHocSubProcessActivitiesResponse401
    from .models.activate_ad_hoc_sub_process_activities_response_403 import ActivateAdHocSubProcessActivitiesResponse403
    from .models.activate_ad_hoc_sub_process_activities_response_404 import ActivateAdHocSubProcessActivitiesResponse404
    from .models.activate_ad_hoc_sub_process_activities_response_500 import ActivateAdHocSubProcessActivitiesResponse500
    from .models.activate_ad_hoc_sub_process_activities_response_503 import ActivateAdHocSubProcessActivitiesResponse503
    from .models.activate_jobs_data import ActivateJobsData
    from .models.activate_jobs_response_200 import ActivateJobsResponse200
    from .models.activate_jobs_response_400 import ActivateJobsResponse400
    from .models.activate_jobs_response_401 import ActivateJobsResponse401
    from .models.activate_jobs_response_500 import ActivateJobsResponse500
    from .models.activate_jobs_response_503 import ActivateJobsResponse503
    from .models.assign_client_to_group_response_400 import AssignClientToGroupResponse400
    from .models.assign_client_to_group_response_403 import AssignClientToGroupResponse403
    from .models.assign_client_to_group_response_404 import AssignClientToGroupResponse404
    from .models.assign_client_to_group_response_409 import AssignClientToGroupResponse409
    from .models.assign_client_to_group_response_500 import AssignClientToGroupResponse500
    from .models.assign_client_to_group_response_503 import AssignClientToGroupResponse503
    from .models.assign_client_to_tenant_response_400 import AssignClientToTenantResponse400
    from .models.assign_client_to_tenant_response_403 import AssignClientToTenantResponse403
    from .models.assign_client_to_tenant_response_404 import AssignClientToTenantResponse404
    from .models.assign_client_to_tenant_response_500 import AssignClientToTenantResponse500
    from .models.assign_client_to_tenant_response_503 import AssignClientToTenantResponse503
    from .models.assign_group_to_tenant_response_400 import AssignGroupToTenantResponse400
    from .models.assign_group_to_tenant_response_403 import AssignGroupToTenantResponse403
    from .models.assign_group_to_tenant_response_404 import AssignGroupToTenantResponse404
    from .models.assign_group_to_tenant_response_500 import AssignGroupToTenantResponse500
    from .models.assign_group_to_tenant_response_503 import AssignGroupToTenantResponse503
    from .models.assign_mapping_rule_to_group_response_400 import AssignMappingRuleToGroupResponse400
    from .models.assign_mapping_rule_to_group_response_403 import AssignMappingRuleToGroupResponse403
    from .models.assign_mapping_rule_to_group_response_404 import AssignMappingRuleToGroupResponse404
    from .models.assign_mapping_rule_to_group_response_409 import AssignMappingRuleToGroupResponse409
    from .models.assign_mapping_rule_to_group_response_500 import AssignMappingRuleToGroupResponse500
    from .models.assign_mapping_rule_to_group_response_503 import AssignMappingRuleToGroupResponse503
    from .models.assign_mapping_rule_to_tenant_response_400 import AssignMappingRuleToTenantResponse400
    from .models.assign_mapping_rule_to_tenant_response_403 import AssignMappingRuleToTenantResponse403
    from .models.assign_mapping_rule_to_tenant_response_404 import AssignMappingRuleToTenantResponse404
    from .models.assign_mapping_rule_to_tenant_response_500 import AssignMappingRuleToTenantResponse500
    from .models.assign_mapping_rule_to_tenant_response_503 import AssignMappingRuleToTenantResponse503
    from .models.assign_role_to_client_response_400 import AssignRoleToClientResponse400
    from .models.assign_role_to_client_response_403 import AssignRoleToClientResponse403
    from .models.assign_role_to_client_response_404 import AssignRoleToClientResponse404
    from .models.assign_role_to_client_response_409 import AssignRoleToClientResponse409
    from .models.assign_role_to_client_response_500 import AssignRoleToClientResponse500
    from .models.assign_role_to_client_response_503 import AssignRoleToClientResponse503
    from .models.assign_role_to_group_response_400 import AssignRoleToGroupResponse400
    from .models.assign_role_to_group_response_403 import AssignRoleToGroupResponse403
    from .models.assign_role_to_group_response_404 import AssignRoleToGroupResponse404
    from .models.assign_role_to_group_response_409 import AssignRoleToGroupResponse409
    from .models.assign_role_to_group_response_500 import AssignRoleToGroupResponse500
    from .models.assign_role_to_group_response_503 import AssignRoleToGroupResponse503
    from .models.assign_role_to_mapping_rule_response_400 import AssignRoleToMappingRuleResponse400
    from .models.assign_role_to_mapping_rule_response_403 import AssignRoleToMappingRuleResponse403
    from .models.assign_role_to_mapping_rule_response_404 import AssignRoleToMappingRuleResponse404
    from .models.assign_role_to_mapping_rule_response_409 import AssignRoleToMappingRuleResponse409
    from .models.assign_role_to_mapping_rule_response_500 import AssignRoleToMappingRuleResponse500
    from .models.assign_role_to_mapping_rule_response_503 import AssignRoleToMappingRuleResponse503
    from .models.assign_role_to_tenant_response_400 import AssignRoleToTenantResponse400
    from .models.assign_role_to_tenant_response_403 import AssignRoleToTenantResponse403
    from .models.assign_role_to_tenant_response_404 import AssignRoleToTenantResponse404
    from .models.assign_role_to_tenant_response_500 import AssignRoleToTenantResponse500
    from .models.assign_role_to_tenant_response_503 import AssignRoleToTenantResponse503
    from .models.assign_role_to_user_response_400 import AssignRoleToUserResponse400
    from .models.assign_role_to_user_response_403 import AssignRoleToUserResponse403
    from .models.assign_role_to_user_response_404 import AssignRoleToUserResponse404
    from .models.assign_role_to_user_response_409 import AssignRoleToUserResponse409
    from .models.assign_role_to_user_response_500 import AssignRoleToUserResponse500
    from .models.assign_role_to_user_response_503 import AssignRoleToUserResponse503
    from .models.assign_user_task_data import AssignUserTaskData
    from .models.assign_user_task_response_400 import AssignUserTaskResponse400
    from .models.assign_user_task_response_404 import AssignUserTaskResponse404
    from .models.assign_user_task_response_409 import AssignUserTaskResponse409
    from .models.assign_user_task_response_500 import AssignUserTaskResponse500
    from .models.assign_user_task_response_503 import AssignUserTaskResponse503
    from .models.assign_user_to_group_response_400 import AssignUserToGroupResponse400
    from .models.assign_user_to_group_response_403 import AssignUserToGroupResponse403
    from .models.assign_user_to_group_response_404 import AssignUserToGroupResponse404
    from .models.assign_user_to_group_response_409 import AssignUserToGroupResponse409
    from .models.assign_user_to_group_response_500 import AssignUserToGroupResponse500
    from .models.assign_user_to_group_response_503 import AssignUserToGroupResponse503
    from .models.assign_user_to_tenant_response_400 import AssignUserToTenantResponse400
    from .models.assign_user_to_tenant_response_403 import AssignUserToTenantResponse403
    from .models.assign_user_to_tenant_response_404 import AssignUserToTenantResponse404
    from .models.assign_user_to_tenant_response_500 import AssignUserToTenantResponse500
    from .models.assign_user_to_tenant_response_503 import AssignUserToTenantResponse503
    from .models.broadcast_signal_data import BroadcastSignalData
    from .models.broadcast_signal_response_200 import BroadcastSignalResponse200
    from .models.broadcast_signal_response_400 import BroadcastSignalResponse400
    from .models.broadcast_signal_response_404 import BroadcastSignalResponse404
    from .models.broadcast_signal_response_500 import BroadcastSignalResponse500
    from .models.broadcast_signal_response_503 import BroadcastSignalResponse503
    from .models.cancel_batch_operation_response_400 import CancelBatchOperationResponse400
    from .models.cancel_batch_operation_response_403 import CancelBatchOperationResponse403
    from .models.cancel_batch_operation_response_404 import CancelBatchOperationResponse404
    from .models.cancel_batch_operation_response_500 import CancelBatchOperationResponse500
    from .models.cancel_process_instance_data_type_0 import CancelProcessInstanceDataType0
    from .models.cancel_process_instance_response_400 import CancelProcessInstanceResponse400
    from .models.cancel_process_instance_response_404 import CancelProcessInstanceResponse404
    from .models.cancel_process_instance_response_500 import CancelProcessInstanceResponse500
    from .models.cancel_process_instance_response_503 import CancelProcessInstanceResponse503
    from .models.cancel_process_instances_batch_operation_data import CancelProcessInstancesBatchOperationData
    from .models.cancel_process_instances_batch_operation_response_200 import CancelProcessInstancesBatchOperationResponse200
    from .models.cancel_process_instances_batch_operation_response_400 import CancelProcessInstancesBatchOperationResponse400
    from .models.cancel_process_instances_batch_operation_response_401 import CancelProcessInstancesBatchOperationResponse401
    from .models.cancel_process_instances_batch_operation_response_403 import CancelProcessInstancesBatchOperationResponse403
    from .models.cancel_process_instances_batch_operation_response_500 import CancelProcessInstancesBatchOperationResponse500
    from .models.complete_job_data import CompleteJobData
    from .models.complete_job_response_400 import CompleteJobResponse400
    from .models.complete_job_response_404 import CompleteJobResponse404
    from .models.complete_job_response_409 import CompleteJobResponse409
    from .models.complete_job_response_500 import CompleteJobResponse500
    from .models.complete_job_response_503 import CompleteJobResponse503
    from .models.complete_user_task_data import CompleteUserTaskData
    from .models.complete_user_task_response_400 import CompleteUserTaskResponse400
    from .models.complete_user_task_response_404 import CompleteUserTaskResponse404
    from .models.complete_user_task_response_409 import CompleteUserTaskResponse409
    from .models.complete_user_task_response_500 import CompleteUserTaskResponse500
    from .models.complete_user_task_response_503 import CompleteUserTaskResponse503
    from .models.correlate_message_data import CorrelateMessageData
    from .models.correlate_message_response_200 import CorrelateMessageResponse200
    from .models.correlate_message_response_400 import CorrelateMessageResponse400
    from .models.correlate_message_response_403 import CorrelateMessageResponse403
    from .models.correlate_message_response_404 import CorrelateMessageResponse404
    from .models.correlate_message_response_500 import CorrelateMessageResponse500
    from .models.correlate_message_response_503 import CorrelateMessageResponse503
    from .models.create_admin_user_data import CreateAdminUserData
    from .models.create_admin_user_response_400 import CreateAdminUserResponse400
    from .models.create_admin_user_response_403 import CreateAdminUserResponse403
    from .models.create_admin_user_response_500 import CreateAdminUserResponse500
    from .models.create_admin_user_response_503 import CreateAdminUserResponse503
    from .models.create_authorization_response_201 import CreateAuthorizationResponse201
    from .models.create_authorization_response_400 import CreateAuthorizationResponse400
    from .models.create_authorization_response_401 import CreateAuthorizationResponse401
    from .models.create_authorization_response_403 import CreateAuthorizationResponse403
    from .models.create_authorization_response_404 import CreateAuthorizationResponse404
    from .models.create_authorization_response_500 import CreateAuthorizationResponse500
    from .models.create_authorization_response_503 import CreateAuthorizationResponse503
    from .models.create_deployment_data import CreateDeploymentData
    from .models.create_deployment_response_200 import CreateDeploymentResponse200
    from .models.create_deployment_response_400 import CreateDeploymentResponse400
    from .models.create_deployment_response_503 import CreateDeploymentResponse503
    from .models.create_document_data import CreateDocumentData
    from .models.create_document_link_data import CreateDocumentLinkData
    from .models.create_document_link_response_201 import CreateDocumentLinkResponse201
    from .models.create_document_link_response_400 import CreateDocumentLinkResponse400
    from .models.create_document_response_201 import CreateDocumentResponse201
    from .models.create_document_response_400 import CreateDocumentResponse400
    from .models.create_document_response_415 import CreateDocumentResponse415
    from .models.create_documents_data import CreateDocumentsData
    from .models.create_documents_response_201 import CreateDocumentsResponse201
    from .models.create_documents_response_207 import CreateDocumentsResponse207
    from .models.create_documents_response_400 import CreateDocumentsResponse400
    from .models.create_documents_response_415 import CreateDocumentsResponse415
    from .models.create_element_instance_variables_data import CreateElementInstanceVariablesData
    from .models.create_element_instance_variables_response_400 import CreateElementInstanceVariablesResponse400
    from .models.create_element_instance_variables_response_500 import CreateElementInstanceVariablesResponse500
    from .models.create_element_instance_variables_response_503 import CreateElementInstanceVariablesResponse503
    from .models.create_global_cluster_variable_data import CreateGlobalClusterVariableData
    from .models.create_global_cluster_variable_response_200 import CreateGlobalClusterVariableResponse200
    from .models.create_global_cluster_variable_response_400 import CreateGlobalClusterVariableResponse400
    from .models.create_global_cluster_variable_response_401 import CreateGlobalClusterVariableResponse401
    from .models.create_global_cluster_variable_response_403 import CreateGlobalClusterVariableResponse403
    from .models.create_global_cluster_variable_response_500 import CreateGlobalClusterVariableResponse500
    from .models.create_group_data import CreateGroupData
    from .models.create_group_response_201 import CreateGroupResponse201
    from .models.create_group_response_400 import CreateGroupResponse400
    from .models.create_group_response_401 import CreateGroupResponse401
    from .models.create_group_response_403 import CreateGroupResponse403
    from .models.create_group_response_500 import CreateGroupResponse500
    from .models.create_group_response_503 import CreateGroupResponse503
    from .models.create_mapping_rule_data import CreateMappingRuleData
    from .models.create_mapping_rule_response_201 import CreateMappingRuleResponse201
    from .models.create_mapping_rule_response_400 import CreateMappingRuleResponse400
    from .models.create_mapping_rule_response_403 import CreateMappingRuleResponse403
    from .models.create_mapping_rule_response_404 import CreateMappingRuleResponse404
    from .models.create_mapping_rule_response_500 import CreateMappingRuleResponse500
    from .models.create_process_instance_response_200 import CreateProcessInstanceResponse200
    from .models.create_process_instance_response_400 import CreateProcessInstanceResponse400
    from .models.create_process_instance_response_500 import CreateProcessInstanceResponse500
    from .models.create_process_instance_response_503 import CreateProcessInstanceResponse503
    from .models.create_process_instance_response_504 import CreateProcessInstanceResponse504
    from .models.create_role_data import CreateRoleData
    from .models.create_role_response_201 import CreateRoleResponse201
    from .models.create_role_response_400 import CreateRoleResponse400
    from .models.create_role_response_401 import CreateRoleResponse401
    from .models.create_role_response_403 import CreateRoleResponse403
    from .models.create_role_response_500 import CreateRoleResponse500
    from .models.create_role_response_503 import CreateRoleResponse503
    from .models.create_tenant_cluster_variable_data import CreateTenantClusterVariableData
    from .models.create_tenant_cluster_variable_response_200 import CreateTenantClusterVariableResponse200
    from .models.create_tenant_cluster_variable_response_400 import CreateTenantClusterVariableResponse400
    from .models.create_tenant_cluster_variable_response_401 import CreateTenantClusterVariableResponse401
    from .models.create_tenant_cluster_variable_response_403 import CreateTenantClusterVariableResponse403
    from .models.create_tenant_cluster_variable_response_500 import CreateTenantClusterVariableResponse500
    from .models.create_tenant_data import CreateTenantData
    from .models.create_tenant_response_201 import CreateTenantResponse201
    from .models.create_tenant_response_400 import CreateTenantResponse400
    from .models.create_tenant_response_403 import CreateTenantResponse403
    from .models.create_tenant_response_404 import CreateTenantResponse404
    from .models.create_tenant_response_500 import CreateTenantResponse500
    from .models.create_tenant_response_503 import CreateTenantResponse503
    from .models.create_user_data import CreateUserData
    from .models.create_user_response_201 import CreateUserResponse201
    from .models.create_user_response_400 import CreateUserResponse400
    from .models.create_user_response_401 import CreateUserResponse401
    from .models.create_user_response_403 import CreateUserResponse403
    from .models.create_user_response_409 import CreateUserResponse409
    from .models.create_user_response_500 import CreateUserResponse500
    from .models.create_user_response_503 import CreateUserResponse503
    from .models.decisionevaluationby_id import DecisionevaluationbyID
    from .models.decisionevaluationbykey import Decisionevaluationbykey
    from .models.delete_authorization_response_401 import DeleteAuthorizationResponse401
    from .models.delete_authorization_response_404 import DeleteAuthorizationResponse404
    from .models.delete_authorization_response_500 import DeleteAuthorizationResponse500
    from .models.delete_authorization_response_503 import DeleteAuthorizationResponse503
    from .models.delete_document_response_404 import DeleteDocumentResponse404
    from .models.delete_document_response_500 import DeleteDocumentResponse500
    from .models.delete_global_cluster_variable_response_400 import DeleteGlobalClusterVariableResponse400
    from .models.delete_global_cluster_variable_response_401 import DeleteGlobalClusterVariableResponse401
    from .models.delete_global_cluster_variable_response_403 import DeleteGlobalClusterVariableResponse403
    from .models.delete_global_cluster_variable_response_404 import DeleteGlobalClusterVariableResponse404
    from .models.delete_global_cluster_variable_response_500 import DeleteGlobalClusterVariableResponse500
    from .models.delete_group_response_401 import DeleteGroupResponse401
    from .models.delete_group_response_404 import DeleteGroupResponse404
    from .models.delete_group_response_500 import DeleteGroupResponse500
    from .models.delete_group_response_503 import DeleteGroupResponse503
    from .models.delete_mapping_rule_response_401 import DeleteMappingRuleResponse401
    from .models.delete_mapping_rule_response_404 import DeleteMappingRuleResponse404
    from .models.delete_mapping_rule_response_500 import DeleteMappingRuleResponse500
    from .models.delete_mapping_rule_response_503 import DeleteMappingRuleResponse503
    from .models.delete_process_instance_data_type_0 import DeleteProcessInstanceDataType0
    from .models.delete_process_instance_response_401 import DeleteProcessInstanceResponse401
    from .models.delete_process_instance_response_403 import DeleteProcessInstanceResponse403
    from .models.delete_process_instance_response_404 import DeleteProcessInstanceResponse404
    from .models.delete_process_instance_response_409 import DeleteProcessInstanceResponse409
    from .models.delete_process_instance_response_500 import DeleteProcessInstanceResponse500
    from .models.delete_process_instance_response_503 import DeleteProcessInstanceResponse503
    from .models.delete_process_instances_batch_operation_data import DeleteProcessInstancesBatchOperationData
    from .models.delete_process_instances_batch_operation_response_200 import DeleteProcessInstancesBatchOperationResponse200
    from .models.delete_process_instances_batch_operation_response_400 import DeleteProcessInstancesBatchOperationResponse400
    from .models.delete_process_instances_batch_operation_response_401 import DeleteProcessInstancesBatchOperationResponse401
    from .models.delete_process_instances_batch_operation_response_403 import DeleteProcessInstancesBatchOperationResponse403
    from .models.delete_process_instances_batch_operation_response_500 import DeleteProcessInstancesBatchOperationResponse500
    from .models.delete_resource_data_type_0 import DeleteResourceDataType0
    from .models.delete_resource_response_400 import DeleteResourceResponse400
    from .models.delete_resource_response_404 import DeleteResourceResponse404
    from .models.delete_resource_response_500 import DeleteResourceResponse500
    from .models.delete_resource_response_503 import DeleteResourceResponse503
    from .models.delete_role_response_401 import DeleteRoleResponse401
    from .models.delete_role_response_404 import DeleteRoleResponse404
    from .models.delete_role_response_500 import DeleteRoleResponse500
    from .models.delete_role_response_503 import DeleteRoleResponse503
    from .models.delete_tenant_cluster_variable_response_400 import DeleteTenantClusterVariableResponse400
    from .models.delete_tenant_cluster_variable_response_401 import DeleteTenantClusterVariableResponse401
    from .models.delete_tenant_cluster_variable_response_403 import DeleteTenantClusterVariableResponse403
    from .models.delete_tenant_cluster_variable_response_404 import DeleteTenantClusterVariableResponse404
    from .models.delete_tenant_cluster_variable_response_500 import DeleteTenantClusterVariableResponse500
    from .models.delete_tenant_response_400 import DeleteTenantResponse400
    from .models.delete_tenant_response_403 import DeleteTenantResponse403
    from .models.delete_tenant_response_404 import DeleteTenantResponse404
    from .models.delete_tenant_response_500 import DeleteTenantResponse500
    from .models.delete_tenant_response_503 import DeleteTenantResponse503
    from .models.delete_user_response_400 import DeleteUserResponse400
    from .models.delete_user_response_404 import DeleteUserResponse404
    from .models.delete_user_response_500 import DeleteUserResponse500
    from .models.delete_user_response_503 import DeleteUserResponse503
    from .models.evaluate_conditionals_data import EvaluateConditionalsData
    from .models.evaluate_conditionals_response_200 import EvaluateConditionalsResponse200
    from .models.evaluate_conditionals_response_400 import EvaluateConditionalsResponse400
    from .models.evaluate_conditionals_response_403 import EvaluateConditionalsResponse403
    from .models.evaluate_conditionals_response_404 import EvaluateConditionalsResponse404
    from .models.evaluate_conditionals_response_500 import EvaluateConditionalsResponse500
    from .models.evaluate_conditionals_response_503 import EvaluateConditionalsResponse503
    from .models.evaluate_decision_response_200 import EvaluateDecisionResponse200
    from .models.evaluate_decision_response_400 import EvaluateDecisionResponse400
    from .models.evaluate_decision_response_500 import EvaluateDecisionResponse500
    from .models.evaluate_decision_response_503 import EvaluateDecisionResponse503
    from .models.evaluate_expression_data import EvaluateExpressionData
    from .models.evaluate_expression_response_200 import EvaluateExpressionResponse200
    from .models.evaluate_expression_response_400 import EvaluateExpressionResponse400
    from .models.evaluate_expression_response_401 import EvaluateExpressionResponse401
    from .models.evaluate_expression_response_403 import EvaluateExpressionResponse403
    from .models.evaluate_expression_response_500 import EvaluateExpressionResponse500
    from .models.fail_job_data import FailJobData
    from .models.fail_job_response_400 import FailJobResponse400
    from .models.fail_job_response_404 import FailJobResponse404
    from .models.fail_job_response_409 import FailJobResponse409
    from .models.fail_job_response_500 import FailJobResponse500
    from .models.fail_job_response_503 import FailJobResponse503
    from .models.get_audit_log_response_200 import GetAuditLogResponse200
    from .models.get_audit_log_response_401 import GetAuditLogResponse401
    from .models.get_audit_log_response_403 import GetAuditLogResponse403
    from .models.get_audit_log_response_404 import GetAuditLogResponse404
    from .models.get_audit_log_response_500 import GetAuditLogResponse500
    from .models.get_authentication_response_200 import GetAuthenticationResponse200
    from .models.get_authentication_response_401 import GetAuthenticationResponse401
    from .models.get_authentication_response_403 import GetAuthenticationResponse403
    from .models.get_authentication_response_500 import GetAuthenticationResponse500
    from .models.get_authorization_response_200 import GetAuthorizationResponse200
    from .models.get_authorization_response_401 import GetAuthorizationResponse401
    from .models.get_authorization_response_403 import GetAuthorizationResponse403
    from .models.get_authorization_response_404 import GetAuthorizationResponse404
    from .models.get_authorization_response_500 import GetAuthorizationResponse500
    from .models.get_batch_operation_response_200 import GetBatchOperationResponse200
    from .models.get_batch_operation_response_400 import GetBatchOperationResponse400
    from .models.get_batch_operation_response_404 import GetBatchOperationResponse404
    from .models.get_batch_operation_response_500 import GetBatchOperationResponse500
    from .models.get_decision_definition_response_200 import GetDecisionDefinitionResponse200
    from .models.get_decision_definition_response_400 import GetDecisionDefinitionResponse400
    from .models.get_decision_definition_response_401 import GetDecisionDefinitionResponse401
    from .models.get_decision_definition_response_403 import GetDecisionDefinitionResponse403
    from .models.get_decision_definition_response_404 import GetDecisionDefinitionResponse404
    from .models.get_decision_definition_response_500 import GetDecisionDefinitionResponse500
    from .models.get_decision_definition_xml_response_400 import GetDecisionDefinitionXMLResponse400
    from .models.get_decision_definition_xml_response_401 import GetDecisionDefinitionXMLResponse401
    from .models.get_decision_definition_xml_response_403 import GetDecisionDefinitionXMLResponse403
    from .models.get_decision_definition_xml_response_404 import GetDecisionDefinitionXMLResponse404
    from .models.get_decision_definition_xml_response_500 import GetDecisionDefinitionXMLResponse500
    from .models.get_decision_instance_response_200 import GetDecisionInstanceResponse200
    from .models.get_decision_instance_response_400 import GetDecisionInstanceResponse400
    from .models.get_decision_instance_response_401 import GetDecisionInstanceResponse401
    from .models.get_decision_instance_response_403 import GetDecisionInstanceResponse403
    from .models.get_decision_instance_response_404 import GetDecisionInstanceResponse404
    from .models.get_decision_instance_response_500 import GetDecisionInstanceResponse500
    from .models.get_decision_requirements_response_200 import GetDecisionRequirementsResponse200
    from .models.get_decision_requirements_response_400 import GetDecisionRequirementsResponse400
    from .models.get_decision_requirements_response_401 import GetDecisionRequirementsResponse401
    from .models.get_decision_requirements_response_403 import GetDecisionRequirementsResponse403
    from .models.get_decision_requirements_response_404 import GetDecisionRequirementsResponse404
    from .models.get_decision_requirements_response_500 import GetDecisionRequirementsResponse500
    from .models.get_decision_requirements_xml_response_400 import GetDecisionRequirementsXMLResponse400
    from .models.get_decision_requirements_xml_response_401 import GetDecisionRequirementsXMLResponse401
    from .models.get_decision_requirements_xml_response_403 import GetDecisionRequirementsXMLResponse403
    from .models.get_decision_requirements_xml_response_404 import GetDecisionRequirementsXMLResponse404
    from .models.get_decision_requirements_xml_response_500 import GetDecisionRequirementsXMLResponse500
    from .models.get_document_response_404 import GetDocumentResponse404
    from .models.get_document_response_500 import GetDocumentResponse500
    from .models.get_element_instance_response_200 import GetElementInstanceResponse200
    from .models.get_element_instance_response_400 import GetElementInstanceResponse400
    from .models.get_element_instance_response_401 import GetElementInstanceResponse401
    from .models.get_element_instance_response_403 import GetElementInstanceResponse403
    from .models.get_element_instance_response_404 import GetElementInstanceResponse404
    from .models.get_element_instance_response_500 import GetElementInstanceResponse500
    from .models.get_global_cluster_variable_response_200 import GetGlobalClusterVariableResponse200
    from .models.get_global_cluster_variable_response_400 import GetGlobalClusterVariableResponse400
    from .models.get_global_cluster_variable_response_401 import GetGlobalClusterVariableResponse401
    from .models.get_global_cluster_variable_response_403 import GetGlobalClusterVariableResponse403
    from .models.get_global_cluster_variable_response_404 import GetGlobalClusterVariableResponse404
    from .models.get_global_cluster_variable_response_500 import GetGlobalClusterVariableResponse500
    from .models.get_group_response_200 import GetGroupResponse200
    from .models.get_group_response_401 import GetGroupResponse401
    from .models.get_group_response_403 import GetGroupResponse403
    from .models.get_group_response_404 import GetGroupResponse404
    from .models.get_group_response_500 import GetGroupResponse500
    from .models.get_incident_response_200 import GetIncidentResponse200
    from .models.get_incident_response_400 import GetIncidentResponse400
    from .models.get_incident_response_401 import GetIncidentResponse401
    from .models.get_incident_response_403 import GetIncidentResponse403
    from .models.get_incident_response_404 import GetIncidentResponse404
    from .models.get_incident_response_500 import GetIncidentResponse500
    from .models.get_license_response_200 import GetLicenseResponse200
    from .models.get_license_response_500 import GetLicenseResponse500
    from .models.get_mapping_rule_response_200 import GetMappingRuleResponse200
    from .models.get_mapping_rule_response_401 import GetMappingRuleResponse401
    from .models.get_mapping_rule_response_404 import GetMappingRuleResponse404
    from .models.get_mapping_rule_response_500 import GetMappingRuleResponse500
    from .models.get_process_definition_instance_statistics_data import GetProcessDefinitionInstanceStatisticsData
    from .models.get_process_definition_instance_statistics_response_200 import GetProcessDefinitionInstanceStatisticsResponse200
    from .models.get_process_definition_instance_statistics_response_400 import GetProcessDefinitionInstanceStatisticsResponse400
    from .models.get_process_definition_instance_statistics_response_401 import GetProcessDefinitionInstanceStatisticsResponse401
    from .models.get_process_definition_instance_statistics_response_403 import GetProcessDefinitionInstanceStatisticsResponse403
    from .models.get_process_definition_instance_statistics_response_500 import GetProcessDefinitionInstanceStatisticsResponse500
    from .models.get_process_definition_instance_version_statistics_data import GetProcessDefinitionInstanceVersionStatisticsData
    from .models.get_process_definition_instance_version_statistics_response_200 import GetProcessDefinitionInstanceVersionStatisticsResponse200
    from .models.get_process_definition_instance_version_statistics_response_400 import GetProcessDefinitionInstanceVersionStatisticsResponse400
    from .models.get_process_definition_instance_version_statistics_response_401 import GetProcessDefinitionInstanceVersionStatisticsResponse401
    from .models.get_process_definition_instance_version_statistics_response_403 import GetProcessDefinitionInstanceVersionStatisticsResponse403
    from .models.get_process_definition_instance_version_statistics_response_500 import GetProcessDefinitionInstanceVersionStatisticsResponse500
    from .models.get_process_definition_message_subscription_statistics_data import GetProcessDefinitionMessageSubscriptionStatisticsData
    from .models.get_process_definition_message_subscription_statistics_response_200 import GetProcessDefinitionMessageSubscriptionStatisticsResponse200
    from .models.get_process_definition_message_subscription_statistics_response_400 import GetProcessDefinitionMessageSubscriptionStatisticsResponse400
    from .models.get_process_definition_message_subscription_statistics_response_401 import GetProcessDefinitionMessageSubscriptionStatisticsResponse401
    from .models.get_process_definition_message_subscription_statistics_response_403 import GetProcessDefinitionMessageSubscriptionStatisticsResponse403
    from .models.get_process_definition_message_subscription_statistics_response_500 import GetProcessDefinitionMessageSubscriptionStatisticsResponse500
    from .models.get_process_definition_response_200 import GetProcessDefinitionResponse200
    from .models.get_process_definition_response_400 import GetProcessDefinitionResponse400
    from .models.get_process_definition_response_401 import GetProcessDefinitionResponse401
    from .models.get_process_definition_response_403 import GetProcessDefinitionResponse403
    from .models.get_process_definition_response_404 import GetProcessDefinitionResponse404
    from .models.get_process_definition_response_500 import GetProcessDefinitionResponse500
    from .models.get_process_definition_statistics_data import GetProcessDefinitionStatisticsData
    from .models.get_process_definition_statistics_response_200 import GetProcessDefinitionStatisticsResponse200
    from .models.get_process_definition_statistics_response_400 import GetProcessDefinitionStatisticsResponse400
    from .models.get_process_definition_statistics_response_401 import GetProcessDefinitionStatisticsResponse401
    from .models.get_process_definition_statistics_response_403 import GetProcessDefinitionStatisticsResponse403
    from .models.get_process_definition_statistics_response_500 import GetProcessDefinitionStatisticsResponse500
    from .models.get_process_definition_xml_response_400 import GetProcessDefinitionXMLResponse400
    from .models.get_process_definition_xml_response_401 import GetProcessDefinitionXMLResponse401
    from .models.get_process_definition_xml_response_403 import GetProcessDefinitionXMLResponse403
    from .models.get_process_definition_xml_response_404 import GetProcessDefinitionXMLResponse404
    from .models.get_process_definition_xml_response_500 import GetProcessDefinitionXMLResponse500
    from .models.get_process_instance_call_hierarchy_response_200_item import GetProcessInstanceCallHierarchyResponse200Item
    from .models.get_process_instance_call_hierarchy_response_400 import GetProcessInstanceCallHierarchyResponse400
    from .models.get_process_instance_call_hierarchy_response_401 import GetProcessInstanceCallHierarchyResponse401
    from .models.get_process_instance_call_hierarchy_response_403 import GetProcessInstanceCallHierarchyResponse403
    from .models.get_process_instance_call_hierarchy_response_404 import GetProcessInstanceCallHierarchyResponse404
    from .models.get_process_instance_call_hierarchy_response_500 import GetProcessInstanceCallHierarchyResponse500
    from .models.get_process_instance_response_200 import GetProcessInstanceResponse200
    from .models.get_process_instance_response_400 import GetProcessInstanceResponse400
    from .models.get_process_instance_response_401 import GetProcessInstanceResponse401
    from .models.get_process_instance_response_403 import GetProcessInstanceResponse403
    from .models.get_process_instance_response_404 import GetProcessInstanceResponse404
    from .models.get_process_instance_response_500 import GetProcessInstanceResponse500
    from .models.get_process_instance_sequence_flows_response_200 import GetProcessInstanceSequenceFlowsResponse200
    from .models.get_process_instance_sequence_flows_response_400 import GetProcessInstanceSequenceFlowsResponse400
    from .models.get_process_instance_sequence_flows_response_401 import GetProcessInstanceSequenceFlowsResponse401
    from .models.get_process_instance_sequence_flows_response_403 import GetProcessInstanceSequenceFlowsResponse403
    from .models.get_process_instance_sequence_flows_response_500 import GetProcessInstanceSequenceFlowsResponse500
    from .models.get_process_instance_statistics_by_definition_data import GetProcessInstanceStatisticsByDefinitionData
    from .models.get_process_instance_statistics_by_definition_response_200 import GetProcessInstanceStatisticsByDefinitionResponse200
    from .models.get_process_instance_statistics_by_definition_response_400 import GetProcessInstanceStatisticsByDefinitionResponse400
    from .models.get_process_instance_statistics_by_definition_response_401 import GetProcessInstanceStatisticsByDefinitionResponse401
    from .models.get_process_instance_statistics_by_definition_response_403 import GetProcessInstanceStatisticsByDefinitionResponse403
    from .models.get_process_instance_statistics_by_definition_response_500 import GetProcessInstanceStatisticsByDefinitionResponse500
    from .models.get_process_instance_statistics_by_error_data import GetProcessInstanceStatisticsByErrorData
    from .models.get_process_instance_statistics_by_error_response_200 import GetProcessInstanceStatisticsByErrorResponse200
    from .models.get_process_instance_statistics_by_error_response_400 import GetProcessInstanceStatisticsByErrorResponse400
    from .models.get_process_instance_statistics_by_error_response_401 import GetProcessInstanceStatisticsByErrorResponse401
    from .models.get_process_instance_statistics_by_error_response_403 import GetProcessInstanceStatisticsByErrorResponse403
    from .models.get_process_instance_statistics_by_error_response_500 import GetProcessInstanceStatisticsByErrorResponse500
    from .models.get_process_instance_statistics_response_200 import GetProcessInstanceStatisticsResponse200
    from .models.get_process_instance_statistics_response_400 import GetProcessInstanceStatisticsResponse400
    from .models.get_process_instance_statistics_response_401 import GetProcessInstanceStatisticsResponse401
    from .models.get_process_instance_statistics_response_403 import GetProcessInstanceStatisticsResponse403
    from .models.get_process_instance_statistics_response_500 import GetProcessInstanceStatisticsResponse500
    from .models.get_resource_content_response_404 import GetResourceContentResponse404
    from .models.get_resource_content_response_500 import GetResourceContentResponse500
    from .models.get_resource_response_200 import GetResourceResponse200
    from .models.get_resource_response_404 import GetResourceResponse404
    from .models.get_resource_response_500 import GetResourceResponse500
    from .models.get_role_response_200 import GetRoleResponse200
    from .models.get_role_response_401 import GetRoleResponse401
    from .models.get_role_response_403 import GetRoleResponse403
    from .models.get_role_response_404 import GetRoleResponse404
    from .models.get_role_response_500 import GetRoleResponse500
    from .models.get_start_process_form_response_200 import GetStartProcessFormResponse200
    from .models.get_start_process_form_response_400 import GetStartProcessFormResponse400
    from .models.get_start_process_form_response_401 import GetStartProcessFormResponse401
    from .models.get_start_process_form_response_403 import GetStartProcessFormResponse403
    from .models.get_start_process_form_response_404 import GetStartProcessFormResponse404
    from .models.get_start_process_form_response_500 import GetStartProcessFormResponse500
    from .models.get_tenant_cluster_variable_response_200 import GetTenantClusterVariableResponse200
    from .models.get_tenant_cluster_variable_response_400 import GetTenantClusterVariableResponse400
    from .models.get_tenant_cluster_variable_response_401 import GetTenantClusterVariableResponse401
    from .models.get_tenant_cluster_variable_response_403 import GetTenantClusterVariableResponse403
    from .models.get_tenant_cluster_variable_response_404 import GetTenantClusterVariableResponse404
    from .models.get_tenant_cluster_variable_response_500 import GetTenantClusterVariableResponse500
    from .models.get_tenant_response_200 import GetTenantResponse200
    from .models.get_tenant_response_400 import GetTenantResponse400
    from .models.get_tenant_response_401 import GetTenantResponse401
    from .models.get_tenant_response_403 import GetTenantResponse403
    from .models.get_tenant_response_404 import GetTenantResponse404
    from .models.get_tenant_response_500 import GetTenantResponse500
    from .models.get_topology_response_200 import GetTopologyResponse200
    from .models.get_topology_response_401 import GetTopologyResponse401
    from .models.get_topology_response_500 import GetTopologyResponse500
    from .models.get_usage_metrics_response_200 import GetUsageMetricsResponse200
    from .models.get_usage_metrics_response_400 import GetUsageMetricsResponse400
    from .models.get_usage_metrics_response_401 import GetUsageMetricsResponse401
    from .models.get_usage_metrics_response_403 import GetUsageMetricsResponse403
    from .models.get_usage_metrics_response_500 import GetUsageMetricsResponse500
    from .models.get_user_response_200 import GetUserResponse200
    from .models.get_user_response_401 import GetUserResponse401
    from .models.get_user_response_403 import GetUserResponse403
    from .models.get_user_response_404 import GetUserResponse404
    from .models.get_user_response_500 import GetUserResponse500
    from .models.get_user_task_form_response_200 import GetUserTaskFormResponse200
    from .models.get_user_task_form_response_400 import GetUserTaskFormResponse400
    from .models.get_user_task_form_response_401 import GetUserTaskFormResponse401
    from .models.get_user_task_form_response_403 import GetUserTaskFormResponse403
    from .models.get_user_task_form_response_404 import GetUserTaskFormResponse404
    from .models.get_user_task_form_response_500 import GetUserTaskFormResponse500
    from .models.get_user_task_response_200 import GetUserTaskResponse200
    from .models.get_user_task_response_400 import GetUserTaskResponse400
    from .models.get_user_task_response_401 import GetUserTaskResponse401
    from .models.get_user_task_response_403 import GetUserTaskResponse403
    from .models.get_user_task_response_404 import GetUserTaskResponse404
    from .models.get_user_task_response_500 import GetUserTaskResponse500
    from .models.get_variable_response_200 import GetVariableResponse200
    from .models.get_variable_response_400 import GetVariableResponse400
    from .models.get_variable_response_401 import GetVariableResponse401
    from .models.get_variable_response_403 import GetVariableResponse403
    from .models.get_variable_response_404 import GetVariableResponse404
    from .models.get_variable_response_500 import GetVariableResponse500
    from .models.migrate_process_instance_data import MigrateProcessInstanceData
    from .models.migrate_process_instance_response_400 import MigrateProcessInstanceResponse400
    from .models.migrate_process_instance_response_404 import MigrateProcessInstanceResponse404
    from .models.migrate_process_instance_response_409 import MigrateProcessInstanceResponse409
    from .models.migrate_process_instance_response_500 import MigrateProcessInstanceResponse500
    from .models.migrate_process_instance_response_503 import MigrateProcessInstanceResponse503
    from .models.migrate_process_instances_batch_operation_data import MigrateProcessInstancesBatchOperationData
    from .models.migrate_process_instances_batch_operation_response_200 import MigrateProcessInstancesBatchOperationResponse200
    from .models.migrate_process_instances_batch_operation_response_400 import MigrateProcessInstancesBatchOperationResponse400
    from .models.migrate_process_instances_batch_operation_response_401 import MigrateProcessInstancesBatchOperationResponse401
    from .models.migrate_process_instances_batch_operation_response_403 import MigrateProcessInstancesBatchOperationResponse403
    from .models.migrate_process_instances_batch_operation_response_500 import MigrateProcessInstancesBatchOperationResponse500
    from .models.modify_process_instance_data import ModifyProcessInstanceData
    from .models.modify_process_instance_response_400 import ModifyProcessInstanceResponse400
    from .models.modify_process_instance_response_404 import ModifyProcessInstanceResponse404
    from .models.modify_process_instance_response_500 import ModifyProcessInstanceResponse500
    from .models.modify_process_instance_response_503 import ModifyProcessInstanceResponse503
    from .models.modify_process_instances_batch_operation_data import ModifyProcessInstancesBatchOperationData
    from .models.modify_process_instances_batch_operation_response_200 import ModifyProcessInstancesBatchOperationResponse200
    from .models.modify_process_instances_batch_operation_response_400 import ModifyProcessInstancesBatchOperationResponse400
    from .models.modify_process_instances_batch_operation_response_401 import ModifyProcessInstancesBatchOperationResponse401
    from .models.modify_process_instances_batch_operation_response_403 import ModifyProcessInstancesBatchOperationResponse403
    from .models.modify_process_instances_batch_operation_response_500 import ModifyProcessInstancesBatchOperationResponse500
    from .models.object_ import Object
    from .models.object_1 import Object1
    from .models.pin_clock_data import PinClockData
    from .models.pin_clock_response_400 import PinClockResponse400
    from .models.pin_clock_response_500 import PinClockResponse500
    from .models.pin_clock_response_503 import PinClockResponse503
    from .models.processcreationbyid import Processcreationbyid
    from .models.processcreationbykey import Processcreationbykey
    from .models.publish_message_data import PublishMessageData
    from .models.publish_message_response_200 import PublishMessageResponse200
    from .models.publish_message_response_400 import PublishMessageResponse400
    from .models.publish_message_response_500 import PublishMessageResponse500
    from .models.publish_message_response_503 import PublishMessageResponse503
    from .models.reset_clock_response_500 import ResetClockResponse500
    from .models.reset_clock_response_503 import ResetClockResponse503
    from .models.resolve_incident_data import ResolveIncidentData
    from .models.resolve_incident_response_400 import ResolveIncidentResponse400
    from .models.resolve_incident_response_404 import ResolveIncidentResponse404
    from .models.resolve_incident_response_500 import ResolveIncidentResponse500
    from .models.resolve_incident_response_503 import ResolveIncidentResponse503
    from .models.resolve_incidents_batch_operation_data import ResolveIncidentsBatchOperationData
    from .models.resolve_incidents_batch_operation_response_200 import ResolveIncidentsBatchOperationResponse200
    from .models.resolve_incidents_batch_operation_response_400 import ResolveIncidentsBatchOperationResponse400
    from .models.resolve_incidents_batch_operation_response_401 import ResolveIncidentsBatchOperationResponse401
    from .models.resolve_incidents_batch_operation_response_403 import ResolveIncidentsBatchOperationResponse403
    from .models.resolve_incidents_batch_operation_response_500 import ResolveIncidentsBatchOperationResponse500
    from .models.resolve_process_instance_incidents_response_200 import ResolveProcessInstanceIncidentsResponse200
    from .models.resolve_process_instance_incidents_response_400 import ResolveProcessInstanceIncidentsResponse400
    from .models.resolve_process_instance_incidents_response_401 import ResolveProcessInstanceIncidentsResponse401
    from .models.resolve_process_instance_incidents_response_404 import ResolveProcessInstanceIncidentsResponse404
    from .models.resolve_process_instance_incidents_response_500 import ResolveProcessInstanceIncidentsResponse500
    from .models.resolve_process_instance_incidents_response_503 import ResolveProcessInstanceIncidentsResponse503
    from .models.resume_batch_operation_response_400 import ResumeBatchOperationResponse400
    from .models.resume_batch_operation_response_403 import ResumeBatchOperationResponse403
    from .models.resume_batch_operation_response_404 import ResumeBatchOperationResponse404
    from .models.resume_batch_operation_response_500 import ResumeBatchOperationResponse500
    from .models.resume_batch_operation_response_503 import ResumeBatchOperationResponse503
    from .models.search_audit_logs_data import SearchAuditLogsData
    from .models.search_audit_logs_response_200 import SearchAuditLogsResponse200
    from .models.search_audit_logs_response_400 import SearchAuditLogsResponse400
    from .models.search_audit_logs_response_401 import SearchAuditLogsResponse401
    from .models.search_audit_logs_response_403 import SearchAuditLogsResponse403
    from .models.search_authorizations_data import SearchAuthorizationsData
    from .models.search_authorizations_response_200 import SearchAuthorizationsResponse200
    from .models.search_authorizations_response_400 import SearchAuthorizationsResponse400
    from .models.search_authorizations_response_401 import SearchAuthorizationsResponse401
    from .models.search_authorizations_response_403 import SearchAuthorizationsResponse403
    from .models.search_authorizations_response_500 import SearchAuthorizationsResponse500
    from .models.search_batch_operation_items_data import SearchBatchOperationItemsData
    from .models.search_batch_operation_items_response_200 import SearchBatchOperationItemsResponse200
    from .models.search_batch_operation_items_response_400 import SearchBatchOperationItemsResponse400
    from .models.search_batch_operation_items_response_500 import SearchBatchOperationItemsResponse500
    from .models.search_batch_operations_data import SearchBatchOperationsData
    from .models.search_batch_operations_response_200 import SearchBatchOperationsResponse200
    from .models.search_batch_operations_response_400 import SearchBatchOperationsResponse400
    from .models.search_batch_operations_response_500 import SearchBatchOperationsResponse500
    from .models.search_clients_for_group_data import SearchClientsForGroupData
    from .models.search_clients_for_group_response_200 import SearchClientsForGroupResponse200
    from .models.search_clients_for_group_response_400 import SearchClientsForGroupResponse400
    from .models.search_clients_for_group_response_401 import SearchClientsForGroupResponse401
    from .models.search_clients_for_group_response_403 import SearchClientsForGroupResponse403
    from .models.search_clients_for_group_response_404 import SearchClientsForGroupResponse404
    from .models.search_clients_for_group_response_500 import SearchClientsForGroupResponse500
    from .models.search_clients_for_role_data import SearchClientsForRoleData
    from .models.search_clients_for_role_response_200 import SearchClientsForRoleResponse200
    from .models.search_clients_for_role_response_400 import SearchClientsForRoleResponse400
    from .models.search_clients_for_role_response_401 import SearchClientsForRoleResponse401
    from .models.search_clients_for_role_response_403 import SearchClientsForRoleResponse403
    from .models.search_clients_for_role_response_404 import SearchClientsForRoleResponse404
    from .models.search_clients_for_role_response_500 import SearchClientsForRoleResponse500
    from .models.search_clients_for_tenant_data import SearchClientsForTenantData
    from .models.search_clients_for_tenant_response_200 import SearchClientsForTenantResponse200
    from .models.search_cluster_variables_data import SearchClusterVariablesData
    from .models.search_cluster_variables_response_200 import SearchClusterVariablesResponse200
    from .models.search_cluster_variables_response_400 import SearchClusterVariablesResponse400
    from .models.search_cluster_variables_response_401 import SearchClusterVariablesResponse401
    from .models.search_cluster_variables_response_403 import SearchClusterVariablesResponse403
    from .models.search_cluster_variables_response_500 import SearchClusterVariablesResponse500
    from .models.search_correlated_message_subscriptions_data import SearchCorrelatedMessageSubscriptionsData
    from .models.search_correlated_message_subscriptions_response_200 import SearchCorrelatedMessageSubscriptionsResponse200
    from .models.search_correlated_message_subscriptions_response_400 import SearchCorrelatedMessageSubscriptionsResponse400
    from .models.search_correlated_message_subscriptions_response_401 import SearchCorrelatedMessageSubscriptionsResponse401
    from .models.search_correlated_message_subscriptions_response_403 import SearchCorrelatedMessageSubscriptionsResponse403
    from .models.search_correlated_message_subscriptions_response_500 import SearchCorrelatedMessageSubscriptionsResponse500
    from .models.search_decision_definitions_data import SearchDecisionDefinitionsData
    from .models.search_decision_definitions_response_200 import SearchDecisionDefinitionsResponse200
    from .models.search_decision_definitions_response_400 import SearchDecisionDefinitionsResponse400
    from .models.search_decision_definitions_response_401 import SearchDecisionDefinitionsResponse401
    from .models.search_decision_definitions_response_403 import SearchDecisionDefinitionsResponse403
    from .models.search_decision_definitions_response_500 import SearchDecisionDefinitionsResponse500
    from .models.search_decision_instances_data import SearchDecisionInstancesData
    from .models.search_decision_instances_response_200 import SearchDecisionInstancesResponse200
    from .models.search_decision_instances_response_400 import SearchDecisionInstancesResponse400
    from .models.search_decision_instances_response_401 import SearchDecisionInstancesResponse401
    from .models.search_decision_instances_response_403 import SearchDecisionInstancesResponse403
    from .models.search_decision_instances_response_500 import SearchDecisionInstancesResponse500
    from .models.search_decision_requirements_data import SearchDecisionRequirementsData
    from .models.search_decision_requirements_response_200 import SearchDecisionRequirementsResponse200
    from .models.search_decision_requirements_response_400 import SearchDecisionRequirementsResponse400
    from .models.search_decision_requirements_response_401 import SearchDecisionRequirementsResponse401
    from .models.search_decision_requirements_response_403 import SearchDecisionRequirementsResponse403
    from .models.search_decision_requirements_response_500 import SearchDecisionRequirementsResponse500
    from .models.search_element_instance_incidents_data import SearchElementInstanceIncidentsData
    from .models.search_element_instance_incidents_response_200 import SearchElementInstanceIncidentsResponse200
    from .models.search_element_instance_incidents_response_400 import SearchElementInstanceIncidentsResponse400
    from .models.search_element_instance_incidents_response_401 import SearchElementInstanceIncidentsResponse401
    from .models.search_element_instance_incidents_response_403 import SearchElementInstanceIncidentsResponse403
    from .models.search_element_instance_incidents_response_404 import SearchElementInstanceIncidentsResponse404
    from .models.search_element_instance_incidents_response_500 import SearchElementInstanceIncidentsResponse500
    from .models.search_element_instances_data import SearchElementInstancesData
    from .models.search_element_instances_response_200 import SearchElementInstancesResponse200
    from .models.search_element_instances_response_400 import SearchElementInstancesResponse400
    from .models.search_element_instances_response_401 import SearchElementInstancesResponse401
    from .models.search_element_instances_response_403 import SearchElementInstancesResponse403
    from .models.search_element_instances_response_500 import SearchElementInstancesResponse500
    from .models.search_group_ids_for_tenant_data import SearchGroupIdsForTenantData
    from .models.search_group_ids_for_tenant_response_200 import SearchGroupIdsForTenantResponse200
    from .models.search_groups_data import SearchGroupsData
    from .models.search_groups_for_role_data import SearchGroupsForRoleData
    from .models.search_groups_for_role_response_200 import SearchGroupsForRoleResponse200
    from .models.search_groups_for_role_response_400 import SearchGroupsForRoleResponse400
    from .models.search_groups_for_role_response_401 import SearchGroupsForRoleResponse401
    from .models.search_groups_for_role_response_403 import SearchGroupsForRoleResponse403
    from .models.search_groups_for_role_response_404 import SearchGroupsForRoleResponse404
    from .models.search_groups_for_role_response_500 import SearchGroupsForRoleResponse500
    from .models.search_groups_response_200 import SearchGroupsResponse200
    from .models.search_groups_response_400 import SearchGroupsResponse400
    from .models.search_groups_response_401 import SearchGroupsResponse401
    from .models.search_groups_response_403 import SearchGroupsResponse403
    from .models.search_incidents_data import SearchIncidentsData
    from .models.search_incidents_response_200 import SearchIncidentsResponse200
    from .models.search_incidents_response_400 import SearchIncidentsResponse400
    from .models.search_incidents_response_401 import SearchIncidentsResponse401
    from .models.search_incidents_response_403 import SearchIncidentsResponse403
    from .models.search_incidents_response_500 import SearchIncidentsResponse500
    from .models.search_jobs_data import SearchJobsData
    from .models.search_jobs_response_200 import SearchJobsResponse200
    from .models.search_jobs_response_400 import SearchJobsResponse400
    from .models.search_jobs_response_401 import SearchJobsResponse401
    from .models.search_jobs_response_403 import SearchJobsResponse403
    from .models.search_jobs_response_500 import SearchJobsResponse500
    from .models.search_mapping_rule_data import SearchMappingRuleData
    from .models.search_mapping_rule_response_200 import SearchMappingRuleResponse200
    from .models.search_mapping_rule_response_400 import SearchMappingRuleResponse400
    from .models.search_mapping_rule_response_401 import SearchMappingRuleResponse401
    from .models.search_mapping_rule_response_403 import SearchMappingRuleResponse403
    from .models.search_mapping_rule_response_500 import SearchMappingRuleResponse500
    from .models.search_mapping_rules_for_group_data import SearchMappingRulesForGroupData
    from .models.search_mapping_rules_for_group_response_200 import SearchMappingRulesForGroupResponse200
    from .models.search_mapping_rules_for_group_response_400 import SearchMappingRulesForGroupResponse400
    from .models.search_mapping_rules_for_group_response_401 import SearchMappingRulesForGroupResponse401
    from .models.search_mapping_rules_for_group_response_403 import SearchMappingRulesForGroupResponse403
    from .models.search_mapping_rules_for_group_response_404 import SearchMappingRulesForGroupResponse404
    from .models.search_mapping_rules_for_group_response_500 import SearchMappingRulesForGroupResponse500
    from .models.search_mapping_rules_for_role_data import SearchMappingRulesForRoleData
    from .models.search_mapping_rules_for_role_response_200 import SearchMappingRulesForRoleResponse200
    from .models.search_mapping_rules_for_role_response_400 import SearchMappingRulesForRoleResponse400
    from .models.search_mapping_rules_for_role_response_401 import SearchMappingRulesForRoleResponse401
    from .models.search_mapping_rules_for_role_response_403 import SearchMappingRulesForRoleResponse403
    from .models.search_mapping_rules_for_role_response_404 import SearchMappingRulesForRoleResponse404
    from .models.search_mapping_rules_for_role_response_500 import SearchMappingRulesForRoleResponse500
    from .models.search_mapping_rules_for_tenant_data import SearchMappingRulesForTenantData
    from .models.search_mapping_rules_for_tenant_response_200 import SearchMappingRulesForTenantResponse200
    from .models.search_message_subscriptions_data import SearchMessageSubscriptionsData
    from .models.search_message_subscriptions_response_200 import SearchMessageSubscriptionsResponse200
    from .models.search_message_subscriptions_response_400 import SearchMessageSubscriptionsResponse400
    from .models.search_message_subscriptions_response_401 import SearchMessageSubscriptionsResponse401
    from .models.search_message_subscriptions_response_403 import SearchMessageSubscriptionsResponse403
    from .models.search_message_subscriptions_response_500 import SearchMessageSubscriptionsResponse500
    from .models.search_process_definitions_data import SearchProcessDefinitionsData
    from .models.search_process_definitions_response_200 import SearchProcessDefinitionsResponse200
    from .models.search_process_definitions_response_400 import SearchProcessDefinitionsResponse400
    from .models.search_process_definitions_response_401 import SearchProcessDefinitionsResponse401
    from .models.search_process_definitions_response_403 import SearchProcessDefinitionsResponse403
    from .models.search_process_definitions_response_500 import SearchProcessDefinitionsResponse500
    from .models.search_process_instance_incidents_data import SearchProcessInstanceIncidentsData
    from .models.search_process_instance_incidents_response_200 import SearchProcessInstanceIncidentsResponse200
    from .models.search_process_instance_incidents_response_400 import SearchProcessInstanceIncidentsResponse400
    from .models.search_process_instance_incidents_response_401 import SearchProcessInstanceIncidentsResponse401
    from .models.search_process_instance_incidents_response_403 import SearchProcessInstanceIncidentsResponse403
    from .models.search_process_instance_incidents_response_404 import SearchProcessInstanceIncidentsResponse404
    from .models.search_process_instance_incidents_response_500 import SearchProcessInstanceIncidentsResponse500
    from .models.search_process_instances_data import SearchProcessInstancesData
    from .models.search_process_instances_response_200 import SearchProcessInstancesResponse200
    from .models.search_process_instances_response_400 import SearchProcessInstancesResponse400
    from .models.search_process_instances_response_401 import SearchProcessInstancesResponse401
    from .models.search_process_instances_response_403 import SearchProcessInstancesResponse403
    from .models.search_process_instances_response_500 import SearchProcessInstancesResponse500
    from .models.search_roles_data import SearchRolesData
    from .models.search_roles_for_group_data import SearchRolesForGroupData
    from .models.search_roles_for_group_response_200 import SearchRolesForGroupResponse200
    from .models.search_roles_for_group_response_400 import SearchRolesForGroupResponse400
    from .models.search_roles_for_group_response_401 import SearchRolesForGroupResponse401
    from .models.search_roles_for_group_response_403 import SearchRolesForGroupResponse403
    from .models.search_roles_for_group_response_404 import SearchRolesForGroupResponse404
    from .models.search_roles_for_group_response_500 import SearchRolesForGroupResponse500
    from .models.search_roles_for_tenant_data import SearchRolesForTenantData
    from .models.search_roles_for_tenant_response_200 import SearchRolesForTenantResponse200
    from .models.search_roles_response_200 import SearchRolesResponse200
    from .models.search_roles_response_400 import SearchRolesResponse400
    from .models.search_roles_response_401 import SearchRolesResponse401
    from .models.search_roles_response_403 import SearchRolesResponse403
    from .models.search_tenants_data import SearchTenantsData
    from .models.search_tenants_response_200 import SearchTenantsResponse200
    from .models.search_tenants_response_400 import SearchTenantsResponse400
    from .models.search_tenants_response_401 import SearchTenantsResponse401
    from .models.search_tenants_response_403 import SearchTenantsResponse403
    from .models.search_tenants_response_500 import SearchTenantsResponse500
    from .models.search_user_task_audit_logs_data import SearchUserTaskAuditLogsData
    from .models.search_user_task_audit_logs_response_200 import SearchUserTaskAuditLogsResponse200
    from .models.search_user_task_audit_logs_response_400 import SearchUserTaskAuditLogsResponse400
    from .models.search_user_task_audit_logs_response_500 import SearchUserTaskAuditLogsResponse500
    from .models.search_user_task_variables_data import SearchUserTaskVariablesData
    from .models.search_user_task_variables_response_200 import SearchUserTaskVariablesResponse200
    from .models.search_user_task_variables_response_400 import SearchUserTaskVariablesResponse400
    from .models.search_user_task_variables_response_500 import SearchUserTaskVariablesResponse500
    from .models.search_user_tasks_data import SearchUserTasksData
    from .models.search_user_tasks_response_200 import SearchUserTasksResponse200
    from .models.search_user_tasks_response_400 import SearchUserTasksResponse400
    from .models.search_user_tasks_response_401 import SearchUserTasksResponse401
    from .models.search_user_tasks_response_403 import SearchUserTasksResponse403
    from .models.search_user_tasks_response_500 import SearchUserTasksResponse500
    from .models.search_users_data import SearchUsersData
    from .models.search_users_for_group_data import SearchUsersForGroupData
    from .models.search_users_for_group_response_200 import SearchUsersForGroupResponse200
    from .models.search_users_for_group_response_400 import SearchUsersForGroupResponse400
    from .models.search_users_for_group_response_401 import SearchUsersForGroupResponse401
    from .models.search_users_for_group_response_403 import SearchUsersForGroupResponse403
    from .models.search_users_for_group_response_404 import SearchUsersForGroupResponse404
    from .models.search_users_for_group_response_500 import SearchUsersForGroupResponse500
    from .models.search_users_for_role_data import SearchUsersForRoleData
    from .models.search_users_for_role_response_200 import SearchUsersForRoleResponse200
    from .models.search_users_for_role_response_400 import SearchUsersForRoleResponse400
    from .models.search_users_for_role_response_401 import SearchUsersForRoleResponse401
    from .models.search_users_for_role_response_403 import SearchUsersForRoleResponse403
    from .models.search_users_for_role_response_404 import SearchUsersForRoleResponse404
    from .models.search_users_for_role_response_500 import SearchUsersForRoleResponse500
    from .models.search_users_for_tenant_data import SearchUsersForTenantData
    from .models.search_users_for_tenant_response_200 import SearchUsersForTenantResponse200
    from .models.search_users_response_200 import SearchUsersResponse200
    from .models.search_users_response_400 import SearchUsersResponse400
    from .models.search_users_response_401 import SearchUsersResponse401
    from .models.search_users_response_403 import SearchUsersResponse403
    from .models.search_users_response_500 import SearchUsersResponse500
    from .models.search_variables_data import SearchVariablesData
    from .models.search_variables_response_200 import SearchVariablesResponse200
    from .models.search_variables_response_400 import SearchVariablesResponse400
    from .models.search_variables_response_401 import SearchVariablesResponse401
    from .models.search_variables_response_403 import SearchVariablesResponse403
    from .models.search_variables_response_500 import SearchVariablesResponse500
    from .models.suspend_batch_operation_response_400 import SuspendBatchOperationResponse400
    from .models.suspend_batch_operation_response_403 import SuspendBatchOperationResponse403
    from .models.suspend_batch_operation_response_404 import SuspendBatchOperationResponse404
    from .models.suspend_batch_operation_response_500 import SuspendBatchOperationResponse500
    from .models.suspend_batch_operation_response_503 import SuspendBatchOperationResponse503
    from .models.throw_job_error_data import ThrowJobErrorData
    from .models.throw_job_error_response_400 import ThrowJobErrorResponse400
    from .models.throw_job_error_response_404 import ThrowJobErrorResponse404
    from .models.throw_job_error_response_409 import ThrowJobErrorResponse409
    from .models.throw_job_error_response_500 import ThrowJobErrorResponse500
    from .models.throw_job_error_response_503 import ThrowJobErrorResponse503
    from .models.unassign_client_from_group_response_400 import UnassignClientFromGroupResponse400
    from .models.unassign_client_from_group_response_403 import UnassignClientFromGroupResponse403
    from .models.unassign_client_from_group_response_404 import UnassignClientFromGroupResponse404
    from .models.unassign_client_from_group_response_500 import UnassignClientFromGroupResponse500
    from .models.unassign_client_from_group_response_503 import UnassignClientFromGroupResponse503
    from .models.unassign_client_from_tenant_response_400 import UnassignClientFromTenantResponse400
    from .models.unassign_client_from_tenant_response_403 import UnassignClientFromTenantResponse403
    from .models.unassign_client_from_tenant_response_404 import UnassignClientFromTenantResponse404
    from .models.unassign_client_from_tenant_response_500 import UnassignClientFromTenantResponse500
    from .models.unassign_client_from_tenant_response_503 import UnassignClientFromTenantResponse503
    from .models.unassign_group_from_tenant_response_400 import UnassignGroupFromTenantResponse400
    from .models.unassign_group_from_tenant_response_403 import UnassignGroupFromTenantResponse403
    from .models.unassign_group_from_tenant_response_404 import UnassignGroupFromTenantResponse404
    from .models.unassign_group_from_tenant_response_500 import UnassignGroupFromTenantResponse500
    from .models.unassign_group_from_tenant_response_503 import UnassignGroupFromTenantResponse503
    from .models.unassign_mapping_rule_from_group_response_400 import UnassignMappingRuleFromGroupResponse400
    from .models.unassign_mapping_rule_from_group_response_403 import UnassignMappingRuleFromGroupResponse403
    from .models.unassign_mapping_rule_from_group_response_404 import UnassignMappingRuleFromGroupResponse404
    from .models.unassign_mapping_rule_from_group_response_500 import UnassignMappingRuleFromGroupResponse500
    from .models.unassign_mapping_rule_from_group_response_503 import UnassignMappingRuleFromGroupResponse503
    from .models.unassign_mapping_rule_from_tenant_response_400 import UnassignMappingRuleFromTenantResponse400
    from .models.unassign_mapping_rule_from_tenant_response_403 import UnassignMappingRuleFromTenantResponse403
    from .models.unassign_mapping_rule_from_tenant_response_404 import UnassignMappingRuleFromTenantResponse404
    from .models.unassign_mapping_rule_from_tenant_response_500 import UnassignMappingRuleFromTenantResponse500
    from .models.unassign_mapping_rule_from_tenant_response_503 import UnassignMappingRuleFromTenantResponse503
    from .models.unassign_role_from_client_response_400 import UnassignRoleFromClientResponse400
    from .models.unassign_role_from_client_response_403 import UnassignRoleFromClientResponse403
    from .models.unassign_role_from_client_response_404 import UnassignRoleFromClientResponse404
    from .models.unassign_role_from_client_response_500 import UnassignRoleFromClientResponse500
    from .models.unassign_role_from_client_response_503 import UnassignRoleFromClientResponse503
    from .models.unassign_role_from_group_response_400 import UnassignRoleFromGroupResponse400
    from .models.unassign_role_from_group_response_403 import UnassignRoleFromGroupResponse403
    from .models.unassign_role_from_group_response_404 import UnassignRoleFromGroupResponse404
    from .models.unassign_role_from_group_response_500 import UnassignRoleFromGroupResponse500
    from .models.unassign_role_from_group_response_503 import UnassignRoleFromGroupResponse503
    from .models.unassign_role_from_mapping_rule_response_400 import UnassignRoleFromMappingRuleResponse400
    from .models.unassign_role_from_mapping_rule_response_403 import UnassignRoleFromMappingRuleResponse403
    from .models.unassign_role_from_mapping_rule_response_404 import UnassignRoleFromMappingRuleResponse404
    from .models.unassign_role_from_mapping_rule_response_500 import UnassignRoleFromMappingRuleResponse500
    from .models.unassign_role_from_mapping_rule_response_503 import UnassignRoleFromMappingRuleResponse503
    from .models.unassign_role_from_tenant_response_400 import UnassignRoleFromTenantResponse400
    from .models.unassign_role_from_tenant_response_403 import UnassignRoleFromTenantResponse403
    from .models.unassign_role_from_tenant_response_404 import UnassignRoleFromTenantResponse404
    from .models.unassign_role_from_tenant_response_500 import UnassignRoleFromTenantResponse500
    from .models.unassign_role_from_tenant_response_503 import UnassignRoleFromTenantResponse503
    from .models.unassign_role_from_user_response_400 import UnassignRoleFromUserResponse400
    from .models.unassign_role_from_user_response_403 import UnassignRoleFromUserResponse403
    from .models.unassign_role_from_user_response_404 import UnassignRoleFromUserResponse404
    from .models.unassign_role_from_user_response_500 import UnassignRoleFromUserResponse500
    from .models.unassign_role_from_user_response_503 import UnassignRoleFromUserResponse503
    from .models.unassign_user_from_group_response_400 import UnassignUserFromGroupResponse400
    from .models.unassign_user_from_group_response_403 import UnassignUserFromGroupResponse403
    from .models.unassign_user_from_group_response_404 import UnassignUserFromGroupResponse404
    from .models.unassign_user_from_group_response_500 import UnassignUserFromGroupResponse500
    from .models.unassign_user_from_group_response_503 import UnassignUserFromGroupResponse503
    from .models.unassign_user_from_tenant_response_400 import UnassignUserFromTenantResponse400
    from .models.unassign_user_from_tenant_response_403 import UnassignUserFromTenantResponse403
    from .models.unassign_user_from_tenant_response_404 import UnassignUserFromTenantResponse404
    from .models.unassign_user_from_tenant_response_500 import UnassignUserFromTenantResponse500
    from .models.unassign_user_from_tenant_response_503 import UnassignUserFromTenantResponse503
    from .models.unassign_user_task_response_400 import UnassignUserTaskResponse400
    from .models.unassign_user_task_response_404 import UnassignUserTaskResponse404
    from .models.unassign_user_task_response_409 import UnassignUserTaskResponse409
    from .models.unassign_user_task_response_500 import UnassignUserTaskResponse500
    from .models.unassign_user_task_response_503 import UnassignUserTaskResponse503
    from .models.update_authorization_response_401 import UpdateAuthorizationResponse401
    from .models.update_authorization_response_404 import UpdateAuthorizationResponse404
    from .models.update_authorization_response_500 import UpdateAuthorizationResponse500
    from .models.update_authorization_response_503 import UpdateAuthorizationResponse503
    from .models.update_group_data import UpdateGroupData
    from .models.update_group_response_200 import UpdateGroupResponse200
    from .models.update_group_response_400 import UpdateGroupResponse400
    from .models.update_group_response_401 import UpdateGroupResponse401
    from .models.update_group_response_404 import UpdateGroupResponse404
    from .models.update_group_response_500 import UpdateGroupResponse500
    from .models.update_group_response_503 import UpdateGroupResponse503
    from .models.update_job_data import UpdateJobData
    from .models.update_job_response_400 import UpdateJobResponse400
    from .models.update_job_response_404 import UpdateJobResponse404
    from .models.update_job_response_409 import UpdateJobResponse409
    from .models.update_job_response_500 import UpdateJobResponse500
    from .models.update_job_response_503 import UpdateJobResponse503
    from .models.update_mapping_rule_data import UpdateMappingRuleData
    from .models.update_mapping_rule_response_200 import UpdateMappingRuleResponse200
    from .models.update_mapping_rule_response_400 import UpdateMappingRuleResponse400
    from .models.update_mapping_rule_response_403 import UpdateMappingRuleResponse403
    from .models.update_mapping_rule_response_404 import UpdateMappingRuleResponse404
    from .models.update_mapping_rule_response_500 import UpdateMappingRuleResponse500
    from .models.update_mapping_rule_response_503 import UpdateMappingRuleResponse503
    from .models.update_role_data import UpdateRoleData
    from .models.update_role_response_200 import UpdateRoleResponse200
    from .models.update_role_response_400 import UpdateRoleResponse400
    from .models.update_role_response_401 import UpdateRoleResponse401
    from .models.update_role_response_404 import UpdateRoleResponse404
    from .models.update_role_response_500 import UpdateRoleResponse500
    from .models.update_role_response_503 import UpdateRoleResponse503
    from .models.update_tenant_data import UpdateTenantData
    from .models.update_tenant_response_200 import UpdateTenantResponse200
    from .models.update_tenant_response_400 import UpdateTenantResponse400
    from .models.update_tenant_response_403 import UpdateTenantResponse403
    from .models.update_tenant_response_404 import UpdateTenantResponse404
    from .models.update_tenant_response_500 import UpdateTenantResponse500
    from .models.update_tenant_response_503 import UpdateTenantResponse503
    from .models.update_user_data import UpdateUserData
    from .models.update_user_response_200 import UpdateUserResponse200
    from .models.update_user_response_400 import UpdateUserResponse400
    from .models.update_user_response_403 import UpdateUserResponse403
    from .models.update_user_response_404 import UpdateUserResponse404
    from .models.update_user_response_500 import UpdateUserResponse500
    from .models.update_user_response_503 import UpdateUserResponse503
    from .models.update_user_task_data import UpdateUserTaskData
    from .models.update_user_task_response_400 import UpdateUserTaskResponse400
    from .models.update_user_task_response_404 import UpdateUserTaskResponse404
    from .models.update_user_task_response_409 import UpdateUserTaskResponse409
    from .models.update_user_task_response_500 import UpdateUserTaskResponse500
    from .models.update_user_task_response_503 import UpdateUserTaskResponse503
    from .types import File, Response
    from .types import Response
    from .types import UNSET, File, Response, Unset
    from .types import UNSET, Response, Unset
    from http import HTTPStatus
    from io import BytesIO
    from typing import Any
    from typing import Any, cast
    import datetime
    import httpx

@define
class Client:
    """A class for keeping track of data related to the API

    The following are accepted as keyword arguments and will be used to construct httpx Clients internally:

        ``base_url``: The base URL for the API, all requests are made to a relative path to this URL

        ``cookies``: A dictionary of cookies to be sent with every request

        ``headers``: A dictionary of headers to be sent with every request

        ``timeout``: The maximum amount of a time a request can take. API functions will raise
        httpx.TimeoutException if this is exceeded.

        ``verify_ssl``: Whether or not to verify the SSL certificate of the API server. This should be True in production,
        but can be set to False for testing purposes.

        ``follow_redirects``: Whether or not to follow redirects. Default value is False.

        ``httpx_args``: A dictionary of additional arguments to be passed to the ``httpx.Client`` and ``httpx.AsyncClient`` constructor.


    Attributes:
        raise_on_unexpected_status: Whether or not to raise an errors.UnexpectedStatus if the API returns a
            status code that was not documented in the source OpenAPI document. Can also be provided as a keyword
            argument to the constructor.
    """

    raise_on_unexpected_status: bool = field(default=False, kw_only=True)
    _base_url: str = field(alias="base_url")
    _cookies: dict[str, str] = field(factory=dict, kw_only=True, alias="cookies")
    _headers: dict[str, str] = field(factory=dict, kw_only=True, alias="headers")
    _timeout: httpx.Timeout | None = field(default=None, kw_only=True, alias="timeout")
    _verify_ssl: str | bool | ssl.SSLContext = field(
        default=True, kw_only=True, alias="verify_ssl"
    )
    _follow_redirects: bool = field(
        default=False, kw_only=True, alias="follow_redirects"
    )
    _httpx_args: dict[str, Any] = field(factory=dict, kw_only=True, alias="httpx_args")
    _client: httpx.Client | None = field(default=None, init=False)
    _async_client: httpx.AsyncClient | None = field(default=None, init=False)

    def with_headers(self, headers: dict[str, str]) -> "Client":
        """Get a new client matching this one with additional headers"""
        if self._client is not None:
            self._client.headers.update(headers)
        if self._async_client is not None:
            self._async_client.headers.update(headers)
        return evolve(self, headers={**self._headers, **headers})

    def with_cookies(self, cookies: dict[str, str]) -> "Client":
        """Get a new client matching this one with additional cookies"""
        if self._client is not None:
            self._client.cookies.update(cookies)
        if self._async_client is not None:
            self._async_client.cookies.update(cookies)
        return evolve(self, cookies={**self._cookies, **cookies})

    def with_timeout(self, timeout: httpx.Timeout) -> "Client":
        """Get a new client matching this one with a new timeout configuration"""
        if self._client is not None:
            self._client.timeout = timeout
        if self._async_client is not None:
            self._async_client.timeout = timeout
        return evolve(self, timeout=timeout)

    def set_httpx_client(self, client: httpx.Client) -> "Client":
        """Manually set the underlying httpx.Client

        **NOTE**: This will override any other settings on the client, including cookies, headers, and timeout.
        """
        self._client = client
        return self

    def get_httpx_client(self) -> httpx.Client:
        """Get the underlying httpx.Client, constructing a new one if not previously set"""
        if self._client is None:
            self._client = httpx.Client(
                base_url=self._base_url,
                cookies=self._cookies,
                headers=self._headers,
                timeout=self._timeout,
                verify=self._verify_ssl,
                follow_redirects=self._follow_redirects,
                **self._httpx_args,
            )
        return self._client

    def __enter__(self) -> "Client":
        """Enter a context manager for self.client—you cannot enter twice (see httpx docs)"""
        self.get_httpx_client().__enter__()
        return self

    def __exit__(self, *args: Any, **kwargs: Any) -> None:
        """Exit a context manager for internal httpx.Client (see httpx docs)"""
        self.get_httpx_client().__exit__(*args, **kwargs)

    def set_async_httpx_client(self, async_client: httpx.AsyncClient) -> "Client":
        """Manually set the underlying httpx.AsyncClient

        **NOTE**: This will override any other settings on the client, including cookies, headers, and timeout.
        """
        self._async_client = async_client
        return self

    def get_async_httpx_client(self) -> httpx.AsyncClient:
        """Get the underlying httpx.AsyncClient, constructing a new one if not previously set"""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(
                base_url=self._base_url,
                cookies=self._cookies,
                headers=self._headers,
                timeout=self._timeout,
                verify=self._verify_ssl,
                follow_redirects=self._follow_redirects,
                **self._httpx_args,
            )
        return self._async_client

    async def __aenter__(self) -> "Client":
        """Enter a context manager for underlying httpx.AsyncClient—you cannot enter twice (see httpx docs)"""
        await self.get_async_httpx_client().__aenter__()
        return self

    async def __aexit__(self, *args: Any, **kwargs: Any) -> None:
        """Exit a context manager for underlying httpx.AsyncClient (see httpx docs)"""
        await self.get_async_httpx_client().__aexit__(*args, **kwargs)


@define
class AuthenticatedClient:
    """A Client which has been authenticated for use on secured endpoints

    The following are accepted as keyword arguments and will be used to construct httpx Clients internally:

        ``base_url``: The base URL for the API, all requests are made to a relative path to this URL

        ``cookies``: A dictionary of cookies to be sent with every request

        ``headers``: A dictionary of headers to be sent with every request

        ``timeout``: The maximum amount of a time a request can take. API functions will raise
        httpx.TimeoutException if this is exceeded.

        ``verify_ssl``: Whether or not to verify the SSL certificate of the API server. This should be True in production,
        but can be set to False for testing purposes.

        ``follow_redirects``: Whether or not to follow redirects. Default value is False.

        ``httpx_args``: A dictionary of additional arguments to be passed to the ``httpx.Client`` and ``httpx.AsyncClient`` constructor.


    Attributes:
        raise_on_unexpected_status: Whether or not to raise an errors.UnexpectedStatus if the API returns a
            status code that was not documented in the source OpenAPI document. Can also be provided as a keyword
            argument to the constructor.
        token: The token to use for authentication
        prefix: The prefix to use for the Authorization header
        auth_header_name: The name of the Authorization header
    """

    raise_on_unexpected_status: bool = field(default=False, kw_only=True)
    _base_url: str = field(alias="base_url")
    _cookies: dict[str, str] = field(factory=dict, kw_only=True, alias="cookies")
    _headers: dict[str, str] = field(factory=dict, kw_only=True, alias="headers")
    _timeout: httpx.Timeout | None = field(default=None, kw_only=True, alias="timeout")
    _verify_ssl: str | bool | ssl.SSLContext = field(
        default=True, kw_only=True, alias="verify_ssl"
    )
    _follow_redirects: bool = field(
        default=False, kw_only=True, alias="follow_redirects"
    )
    _httpx_args: dict[str, Any] = field(factory=dict, kw_only=True, alias="httpx_args")
    _client: httpx.Client | None = field(default=None, init=False)
    _async_client: httpx.AsyncClient | None = field(default=None, init=False)

    token: str
    prefix: str = "Bearer"
    auth_header_name: str = "Authorization"

    def with_headers(self, headers: dict[str, str]) -> "AuthenticatedClient":
        """Get a new client matching this one with additional headers"""
        if self._client is not None:
            self._client.headers.update(headers)
        if self._async_client is not None:
            self._async_client.headers.update(headers)
        return evolve(self, headers={**self._headers, **headers})

    def with_cookies(self, cookies: dict[str, str]) -> "AuthenticatedClient":
        """Get a new client matching this one with additional cookies"""
        if self._client is not None:
            self._client.cookies.update(cookies)
        if self._async_client is not None:
            self._async_client.cookies.update(cookies)
        return evolve(self, cookies={**self._cookies, **cookies})

    def with_timeout(self, timeout: httpx.Timeout) -> "AuthenticatedClient":
        """Get a new client matching this one with a new timeout configuration"""
        if self._client is not None:
            self._client.timeout = timeout
        if self._async_client is not None:
            self._async_client.timeout = timeout
        return evolve(self, timeout=timeout)

    def set_httpx_client(self, client: httpx.Client) -> "AuthenticatedClient":
        """Manually set the underlying httpx.Client

        **NOTE**: This will override any other settings on the client, including cookies, headers, and timeout.
        """
        self._client = client
        return self

    def get_httpx_client(self) -> httpx.Client:
        """Get the underlying httpx.Client, constructing a new one if not previously set"""
        if self._client is None:
            self._headers[self.auth_header_name] = (
                f"{self.prefix} {self.token}" if self.prefix else self.token
            )
            self._client = httpx.Client(
                base_url=self._base_url,
                cookies=self._cookies,
                headers=self._headers,
                timeout=self._timeout,
                verify=self._verify_ssl,
                follow_redirects=self._follow_redirects,
                **self._httpx_args,
            )
        return self._client

    def __enter__(self) -> "AuthenticatedClient":
        """Enter a context manager for self.client—you cannot enter twice (see httpx docs)"""
        self.get_httpx_client().__enter__()
        return self

    def __exit__(self, *args: Any, **kwargs: Any) -> None:
        """Exit a context manager for internal httpx.Client (see httpx docs)"""
        self.get_httpx_client().__exit__(*args, **kwargs)

    def set_async_httpx_client(
        self, async_client: httpx.AsyncClient
    ) -> "AuthenticatedClient":
        """Manually set the underlying httpx.AsyncClient

        **NOTE**: This will override any other settings on the client, including cookies, headers, and timeout.
        """
        self._async_client = async_client
        return self

    def get_async_httpx_client(self) -> httpx.AsyncClient:
        """Get the underlying httpx.AsyncClient, constructing a new one if not previously set"""
        if self._async_client is None:
            self._headers[self.auth_header_name] = (
                f"{self.prefix} {self.token}" if self.prefix else self.token
            )
            self._async_client = httpx.AsyncClient(
                base_url=self._base_url,
                cookies=self._cookies,
                headers=self._headers,
                timeout=self._timeout,
                verify=self._verify_ssl,
                follow_redirects=self._follow_redirects,
                **self._httpx_args,
            )
        return self._async_client

    async def __aenter__(self) -> "AuthenticatedClient":
        """Enter a context manager for underlying httpx.AsyncClient—you cannot enter twice (see httpx docs)"""
        await self.get_async_httpx_client().__aenter__()
        return self

    async def __aexit__(self, *args: Any, **kwargs: Any) -> None:
        """Exit a context manager for underlying httpx.AsyncClient (see httpx docs)"""
        await self.get_async_httpx_client().__aexit__(*args, **kwargs)

class ExtendedDeploymentResult(CreateDeploymentResponse200):
    processes: list[CreateDeploymentResponse200DeploymentsItemProcessDefinition]
    decisions: list[CreateDeploymentResponse200DeploymentsItemDecisionDefinition]
    decision_requirements: list[CreateDeploymentResponse200DeploymentsItemDecisionRequirements]
    forms: list[CreateDeploymentResponse200DeploymentsItemForm]
    
    def __init__(self, response: CreateDeploymentResponse200):
        self.deployment_key = response.deployment_key
        self.tenant_id = response.tenant_id
        self.deployments = response.deployments
        self.additional_properties = response.additional_properties
        
        self.processes = [d.process_definition for d in self.deployments if not isinstance(d.process_definition, Unset)]
        self.decisions = [d.decision_definition for d in self.deployments if not isinstance(d.decision_definition, Unset)]
        self.decision_requirements = [d.decision_requirements for d in self.deployments if not isinstance(d.decision_requirements, Unset)]
        self.forms = [d.form for d in self.deployments if not isinstance(d.form, Unset)]


class CamundaClient:
    client: Client | AuthenticatedClient
    _workers: list[JobWorker]

    def __init__(self, base_url: str = "http://localhost:8080/v2", token: str | None = None, **kwargs):
        if token:
            self.client = AuthenticatedClient(base_url=base_url, token=token, **kwargs)
        else:
            self.client = Client(base_url=base_url, **kwargs)
        self._workers = []

    def __enter__(self):
        self.client.__enter__()
        return self

    def __exit__(self, *args, **kwargs):
        return self.client.__exit__(*args, **kwargs)

    async def __aenter__(self):
        await self.client.__aenter__()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.client.__aexit__(*args, **kwargs)

    def create_job_worker(self, config: WorkerConfig, callback: JobHandler, auto_start: bool = True) -> JobWorker:
        worker = JobWorker(self, callback, config)
        self._workers.append(worker)
        if auto_start:
            worker.start()
        return worker

    async def run_workers(self):
        stop_event = asyncio.Event()
        try:
            await stop_event.wait()
        except asyncio.CancelledError:
            pass
        finally:
            for worker in self._workers:
                worker.stop()

    def deploy_resources_from_files(self, files: list[str | Path], tenant_id: str | None = None) -> ExtendedDeploymentResult:
        from .models.create_deployment_data import CreateDeploymentData
        from .types import File, UNSET
        import os

        resources = []
        for file_path in files:
            file_path = str(file_path)
            with open(file_path, "rb") as f:
                content = f.read()
            resources.append(File(payload=content, file_name=os.path.basename(file_path)))
        
        data = CreateDeploymentData(resources=resources, tenant_id=tenant_id if tenant_id is not None else UNSET)
        return ExtendedDeploymentResult(self.create_deployment(data=data))

    async def deploy_resources_from_files_async(self, files: list[str | Path], tenant_id: str | None = None) -> ExtendedDeploymentResult:
        from .models.create_deployment_data import CreateDeploymentData
        from .types import File, UNSET
        import os

        resources = []
        for file_path in files:
            file_path = str(file_path)
            with open(file_path, "rb") as f:
                content = f.read()
            resources.append(File(payload=content, file_name=os.path.basename(file_path)))
        
        data = CreateDeploymentData(resources=resources, tenant_id=tenant_id if tenant_id is not None else UNSET)
        return ExtendedDeploymentResult(await self.create_deployment_async(data=data))


    def get_audit_log(self, audit_log_key: str, **kwargs: Any) -> GetAuditLogResponse200:
        """Get audit log

 Get an audit log entry by auditLogKey.

Args:
    audit_log_key (str): System-generated key for an audit log entry. Example:
        22517998136843567.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetAuditLogResponse200 | GetAuditLogResponse401 | GetAuditLogResponse403 | GetAuditLogResponse404 | GetAuditLogResponse500]"""
        from .api.audit_log.get_audit_log import sync as get_audit_log_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_audit_log_sync(**_kwargs)


    async def get_audit_log_async(self, audit_log_key: str, **kwargs: Any) -> GetAuditLogResponse200:
        """Get audit log

 Get an audit log entry by auditLogKey.

Args:
    audit_log_key (str): System-generated key for an audit log entry. Example:
        22517998136843567.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetAuditLogResponse200 | GetAuditLogResponse401 | GetAuditLogResponse403 | GetAuditLogResponse404 | GetAuditLogResponse500]"""
        from .api.audit_log.get_audit_log import asyncio as get_audit_log_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_audit_log_asyncio(**_kwargs)


    def search_audit_logs(self, *, data: SearchAuditLogsData, **kwargs: Any) -> Any:
        """Search audit logs

 Search for audit logs based on given criteria.

Args:
    body (SearchAuditLogsData): Audit log search request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | SearchAuditLogsResponse200 | SearchAuditLogsResponse400 | SearchAuditLogsResponse401 | SearchAuditLogsResponse403]"""
        from .api.audit_log.search_audit_logs import sync as search_audit_logs_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_audit_logs_sync(**_kwargs)


    async def search_audit_logs_async(self, *, data: SearchAuditLogsData, **kwargs: Any) -> Any:
        """Search audit logs

 Search for audit logs based on given criteria.

Args:
    body (SearchAuditLogsData): Audit log search request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | SearchAuditLogsResponse200 | SearchAuditLogsResponse400 | SearchAuditLogsResponse401 | SearchAuditLogsResponse403]"""
        from .api.audit_log.search_audit_logs import asyncio as search_audit_logs_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_audit_logs_asyncio(**_kwargs)


    def cancel_batch_operation(self, batch_operation_key: str, *, data: Any, **kwargs: Any) -> Any:
        """Cancel Batch operation

 Cancels a running batch operation.
This is done asynchronously, the progress can be tracked using the batch operation status endpoint
(/batch-operations/{batchOperationKey}).

Args:
    batch_operation_key (str): System-generated key for an batch operation. Example:
        2251799813684321.
    body (Any):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | CancelBatchOperationResponse400 | CancelBatchOperationResponse403 | CancelBatchOperationResponse404 | CancelBatchOperationResponse500]"""
        from .api.batch_operation.cancel_batch_operation import sync as cancel_batch_operation_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return cancel_batch_operation_sync(**_kwargs)


    async def cancel_batch_operation_async(self, batch_operation_key: str, *, data: Any, **kwargs: Any) -> Any:
        """Cancel Batch operation

 Cancels a running batch operation.
This is done asynchronously, the progress can be tracked using the batch operation status endpoint
(/batch-operations/{batchOperationKey}).

Args:
    batch_operation_key (str): System-generated key for an batch operation. Example:
        2251799813684321.
    body (Any):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | CancelBatchOperationResponse400 | CancelBatchOperationResponse403 | CancelBatchOperationResponse404 | CancelBatchOperationResponse500]"""
        from .api.batch_operation.cancel_batch_operation import asyncio as cancel_batch_operation_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await cancel_batch_operation_asyncio(**_kwargs)


    def suspend_batch_operation(self, batch_operation_key: str, *, data: Any, **kwargs: Any) -> Any:
        """Suspend Batch operation

 Suspends a running batch operation.
This is done asynchronously, the progress can be tracked using the batch operation status endpoint
(/batch-operations/{batchOperationKey}).

Args:
    batch_operation_key (str): System-generated key for an batch operation. Example:
        2251799813684321.
    body (Any):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | SuspendBatchOperationResponse400 | SuspendBatchOperationResponse403 | SuspendBatchOperationResponse404 | SuspendBatchOperationResponse500 | SuspendBatchOperationResponse503]"""
        from .api.batch_operation.suspend_batch_operation import sync as suspend_batch_operation_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return suspend_batch_operation_sync(**_kwargs)


    async def suspend_batch_operation_async(self, batch_operation_key: str, *, data: Any, **kwargs: Any) -> Any:
        """Suspend Batch operation

 Suspends a running batch operation.
This is done asynchronously, the progress can be tracked using the batch operation status endpoint
(/batch-operations/{batchOperationKey}).

Args:
    batch_operation_key (str): System-generated key for an batch operation. Example:
        2251799813684321.
    body (Any):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | SuspendBatchOperationResponse400 | SuspendBatchOperationResponse403 | SuspendBatchOperationResponse404 | SuspendBatchOperationResponse500 | SuspendBatchOperationResponse503]"""
        from .api.batch_operation.suspend_batch_operation import asyncio as suspend_batch_operation_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await suspend_batch_operation_asyncio(**_kwargs)


    def search_batch_operations(self, *, data: SearchBatchOperationsData, **kwargs: Any) -> SearchBatchOperationsResponse200:
        """Search batch operations

 Search for batch operations based on given criteria.

Args:
    body (SearchBatchOperationsData): Batch operation search request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchBatchOperationsResponse200 | SearchBatchOperationsResponse400 | SearchBatchOperationsResponse500]"""
        from .api.batch_operation.search_batch_operations import sync as search_batch_operations_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_batch_operations_sync(**_kwargs)


    async def search_batch_operations_async(self, *, data: SearchBatchOperationsData, **kwargs: Any) -> SearchBatchOperationsResponse200:
        """Search batch operations

 Search for batch operations based on given criteria.

Args:
    body (SearchBatchOperationsData): Batch operation search request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchBatchOperationsResponse200 | SearchBatchOperationsResponse400 | SearchBatchOperationsResponse500]"""
        from .api.batch_operation.search_batch_operations import asyncio as search_batch_operations_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_batch_operations_asyncio(**_kwargs)


    def resume_batch_operation(self, batch_operation_key: str, *, data: Any, **kwargs: Any) -> Any:
        """Resume Batch operation

 Resumes a suspended batch operation.
This is done asynchronously, the progress can be tracked using the batch operation status endpoint
(/batch-operations/{batchOperationKey}).

Args:
    batch_operation_key (str): System-generated key for an batch operation. Example:
        2251799813684321.
    body (Any):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | ResumeBatchOperationResponse400 | ResumeBatchOperationResponse403 | ResumeBatchOperationResponse404 | ResumeBatchOperationResponse500 | ResumeBatchOperationResponse503]"""
        from .api.batch_operation.resume_batch_operation import sync as resume_batch_operation_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return resume_batch_operation_sync(**_kwargs)


    async def resume_batch_operation_async(self, batch_operation_key: str, *, data: Any, **kwargs: Any) -> Any:
        """Resume Batch operation

 Resumes a suspended batch operation.
This is done asynchronously, the progress can be tracked using the batch operation status endpoint
(/batch-operations/{batchOperationKey}).

Args:
    batch_operation_key (str): System-generated key for an batch operation. Example:
        2251799813684321.
    body (Any):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | ResumeBatchOperationResponse400 | ResumeBatchOperationResponse403 | ResumeBatchOperationResponse404 | ResumeBatchOperationResponse500 | ResumeBatchOperationResponse503]"""
        from .api.batch_operation.resume_batch_operation import asyncio as resume_batch_operation_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await resume_batch_operation_asyncio(**_kwargs)


    def get_batch_operation(self, batch_operation_key: str, **kwargs: Any) -> GetBatchOperationResponse200:
        """Get batch operation

 Get batch operation by key.

Args:
    batch_operation_key (str): System-generated key for an batch operation. Example:
        2251799813684321.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetBatchOperationResponse200 | GetBatchOperationResponse400 | GetBatchOperationResponse404 | GetBatchOperationResponse500]"""
        from .api.batch_operation.get_batch_operation import sync as get_batch_operation_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_batch_operation_sync(**_kwargs)


    async def get_batch_operation_async(self, batch_operation_key: str, **kwargs: Any) -> GetBatchOperationResponse200:
        """Get batch operation

 Get batch operation by key.

Args:
    batch_operation_key (str): System-generated key for an batch operation. Example:
        2251799813684321.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetBatchOperationResponse200 | GetBatchOperationResponse400 | GetBatchOperationResponse404 | GetBatchOperationResponse500]"""
        from .api.batch_operation.get_batch_operation import asyncio as get_batch_operation_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_batch_operation_asyncio(**_kwargs)


    def search_batch_operation_items(self, *, data: SearchBatchOperationItemsData, **kwargs: Any) -> SearchBatchOperationItemsResponse200:
        """Search batch operation items

 Search for batch operation items based on given criteria.

Args:
    body (SearchBatchOperationItemsData): Batch operation item search request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchBatchOperationItemsResponse200 | SearchBatchOperationItemsResponse400 | SearchBatchOperationItemsResponse500]"""
        from .api.batch_operation.search_batch_operation_items import sync as search_batch_operation_items_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_batch_operation_items_sync(**_kwargs)


    async def search_batch_operation_items_async(self, *, data: SearchBatchOperationItemsData, **kwargs: Any) -> SearchBatchOperationItemsResponse200:
        """Search batch operation items

 Search for batch operation items based on given criteria.

Args:
    body (SearchBatchOperationItemsData): Batch operation item search request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchBatchOperationItemsResponse200 | SearchBatchOperationItemsResponse400 | SearchBatchOperationItemsResponse500]"""
        from .api.batch_operation.search_batch_operation_items import asyncio as search_batch_operation_items_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_batch_operation_items_asyncio(**_kwargs)


    def get_start_process_form(self, process_definition_key: str, **kwargs: Any) -> Any:
        """Get process start form

 Get the start form of a process.
Note that this endpoint will only return linked forms. This endpoint does not support embedded
forms.

Args:
    process_definition_key (str): System-generated key for a deployed process definition.
        Example: 2251799813686749.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | GetStartProcessFormResponse200 | GetStartProcessFormResponse400 | GetStartProcessFormResponse401 | GetStartProcessFormResponse403 | GetStartProcessFormResponse404 | GetStartProcessFormResponse500]"""
        from .api.process_definition.get_start_process_form import sync as get_start_process_form_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_start_process_form_sync(**_kwargs)


    async def get_start_process_form_async(self, process_definition_key: str, **kwargs: Any) -> Any:
        """Get process start form

 Get the start form of a process.
Note that this endpoint will only return linked forms. This endpoint does not support embedded
forms.

Args:
    process_definition_key (str): System-generated key for a deployed process definition.
        Example: 2251799813686749.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | GetStartProcessFormResponse200 | GetStartProcessFormResponse400 | GetStartProcessFormResponse401 | GetStartProcessFormResponse403 | GetStartProcessFormResponse404 | GetStartProcessFormResponse500]"""
        from .api.process_definition.get_start_process_form import asyncio as get_start_process_form_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_start_process_form_asyncio(**_kwargs)


    def search_process_definitions(self, *, data: SearchProcessDefinitionsData, **kwargs: Any) -> SearchProcessDefinitionsResponse200:
        """Search process definitions

 Search for process definitions based on given criteria.

Args:
    body (SearchProcessDefinitionsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchProcessDefinitionsResponse200 | SearchProcessDefinitionsResponse400 | SearchProcessDefinitionsResponse401 | SearchProcessDefinitionsResponse403 | SearchProcessDefinitionsResponse500]"""
        from .api.process_definition.search_process_definitions import sync as search_process_definitions_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_process_definitions_sync(**_kwargs)


    async def search_process_definitions_async(self, *, data: SearchProcessDefinitionsData, **kwargs: Any) -> SearchProcessDefinitionsResponse200:
        """Search process definitions

 Search for process definitions based on given criteria.

Args:
    body (SearchProcessDefinitionsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchProcessDefinitionsResponse200 | SearchProcessDefinitionsResponse400 | SearchProcessDefinitionsResponse401 | SearchProcessDefinitionsResponse403 | SearchProcessDefinitionsResponse500]"""
        from .api.process_definition.search_process_definitions import asyncio as search_process_definitions_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_process_definitions_asyncio(**_kwargs)


    def get_process_definition_statistics(self, process_definition_key: str, *, data: GetProcessDefinitionStatisticsData, **kwargs: Any) -> GetProcessDefinitionStatisticsResponse200:
        """Get process definition statistics

 Get statistics about elements in currently running process instances by process definition key and
search filter.

Args:
    process_definition_key (str): System-generated key for a deployed process definition.
        Example: 2251799813686749.
    body (GetProcessDefinitionStatisticsData): Process definition element statistics request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetProcessDefinitionStatisticsResponse200 | GetProcessDefinitionStatisticsResponse400 | GetProcessDefinitionStatisticsResponse401 | GetProcessDefinitionStatisticsResponse403 | GetProcessDefinitionStatisticsResponse500]"""
        from .api.process_definition.get_process_definition_statistics import sync as get_process_definition_statistics_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_process_definition_statistics_sync(**_kwargs)


    async def get_process_definition_statistics_async(self, process_definition_key: str, *, data: GetProcessDefinitionStatisticsData, **kwargs: Any) -> GetProcessDefinitionStatisticsResponse200:
        """Get process definition statistics

 Get statistics about elements in currently running process instances by process definition key and
search filter.

Args:
    process_definition_key (str): System-generated key for a deployed process definition.
        Example: 2251799813686749.
    body (GetProcessDefinitionStatisticsData): Process definition element statistics request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetProcessDefinitionStatisticsResponse200 | GetProcessDefinitionStatisticsResponse400 | GetProcessDefinitionStatisticsResponse401 | GetProcessDefinitionStatisticsResponse403 | GetProcessDefinitionStatisticsResponse500]"""
        from .api.process_definition.get_process_definition_statistics import asyncio as get_process_definition_statistics_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_process_definition_statistics_asyncio(**_kwargs)


    def get_process_definition_message_subscription_statistics(self, *, data: GetProcessDefinitionMessageSubscriptionStatisticsData, **kwargs: Any) -> GetProcessDefinitionMessageSubscriptionStatisticsResponse200:
        """Get message subscription statistics

 Get message subscription statistics, grouped by process definition.

Args:
    body (GetProcessDefinitionMessageSubscriptionStatisticsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetProcessDefinitionMessageSubscriptionStatisticsResponse200 | GetProcessDefinitionMessageSubscriptionStatisticsResponse400 | GetProcessDefinitionMessageSubscriptionStatisticsResponse401 | GetProcessDefinitionMessageSubscriptionStatisticsResponse403 | GetProcessDefinitionMessageSubscriptionStatisticsResponse500]"""
        from .api.process_definition.get_process_definition_message_subscription_statistics import sync as get_process_definition_message_subscription_statistics_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_process_definition_message_subscription_statistics_sync(**_kwargs)


    async def get_process_definition_message_subscription_statistics_async(self, *, data: GetProcessDefinitionMessageSubscriptionStatisticsData, **kwargs: Any) -> GetProcessDefinitionMessageSubscriptionStatisticsResponse200:
        """Get message subscription statistics

 Get message subscription statistics, grouped by process definition.

Args:
    body (GetProcessDefinitionMessageSubscriptionStatisticsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetProcessDefinitionMessageSubscriptionStatisticsResponse200 | GetProcessDefinitionMessageSubscriptionStatisticsResponse400 | GetProcessDefinitionMessageSubscriptionStatisticsResponse401 | GetProcessDefinitionMessageSubscriptionStatisticsResponse403 | GetProcessDefinitionMessageSubscriptionStatisticsResponse500]"""
        from .api.process_definition.get_process_definition_message_subscription_statistics import asyncio as get_process_definition_message_subscription_statistics_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_process_definition_message_subscription_statistics_asyncio(**_kwargs)


    def get_process_definition_instance_statistics(self, *, data: GetProcessDefinitionInstanceStatisticsData, **kwargs: Any) -> GetProcessDefinitionInstanceStatisticsResponse200:
        """Get process instance statistics

 Get statistics about process instances, grouped by process definition and tenant.

Args:
    body (GetProcessDefinitionInstanceStatisticsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetProcessDefinitionInstanceStatisticsResponse200 | GetProcessDefinitionInstanceStatisticsResponse400 | GetProcessDefinitionInstanceStatisticsResponse401 | GetProcessDefinitionInstanceStatisticsResponse403 | GetProcessDefinitionInstanceStatisticsResponse500]"""
        from .api.process_definition.get_process_definition_instance_statistics import sync as get_process_definition_instance_statistics_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_process_definition_instance_statistics_sync(**_kwargs)


    async def get_process_definition_instance_statistics_async(self, *, data: GetProcessDefinitionInstanceStatisticsData, **kwargs: Any) -> GetProcessDefinitionInstanceStatisticsResponse200:
        """Get process instance statistics

 Get statistics about process instances, grouped by process definition and tenant.

Args:
    body (GetProcessDefinitionInstanceStatisticsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetProcessDefinitionInstanceStatisticsResponse200 | GetProcessDefinitionInstanceStatisticsResponse400 | GetProcessDefinitionInstanceStatisticsResponse401 | GetProcessDefinitionInstanceStatisticsResponse403 | GetProcessDefinitionInstanceStatisticsResponse500]"""
        from .api.process_definition.get_process_definition_instance_statistics import asyncio as get_process_definition_instance_statistics_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_process_definition_instance_statistics_asyncio(**_kwargs)


    def get_process_definition(self, process_definition_key: str, **kwargs: Any) -> GetProcessDefinitionResponse200:
        """Get process definition

 Returns process definition as JSON.

Args:
    process_definition_key (str): System-generated key for a deployed process definition.
        Example: 2251799813686749.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetProcessDefinitionResponse200 | GetProcessDefinitionResponse400 | GetProcessDefinitionResponse401 | GetProcessDefinitionResponse403 | GetProcessDefinitionResponse404 | GetProcessDefinitionResponse500]"""
        from .api.process_definition.get_process_definition import sync as get_process_definition_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_process_definition_sync(**_kwargs)


    async def get_process_definition_async(self, process_definition_key: str, **kwargs: Any) -> GetProcessDefinitionResponse200:
        """Get process definition

 Returns process definition as JSON.

Args:
    process_definition_key (str): System-generated key for a deployed process definition.
        Example: 2251799813686749.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetProcessDefinitionResponse200 | GetProcessDefinitionResponse400 | GetProcessDefinitionResponse401 | GetProcessDefinitionResponse403 | GetProcessDefinitionResponse404 | GetProcessDefinitionResponse500]"""
        from .api.process_definition.get_process_definition import asyncio as get_process_definition_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_process_definition_asyncio(**_kwargs)


    def get_process_definition_instance_version_statistics(self, process_definition_id: str, *, data: GetProcessDefinitionInstanceVersionStatisticsData, **kwargs: Any) -> GetProcessDefinitionInstanceVersionStatisticsResponse200:
        """Get process instance statistics by version

 Get statistics about process instances, grouped by version for a given process definition.

Args:
    process_definition_id (str): Id of a process definition, from the model. Only ids of
        process definitions that are deployed are useful. Example: new-account-onboarding-
        workflow.
    body (GetProcessDefinitionInstanceVersionStatisticsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetProcessDefinitionInstanceVersionStatisticsResponse200 | GetProcessDefinitionInstanceVersionStatisticsResponse400 | GetProcessDefinitionInstanceVersionStatisticsResponse401 | GetProcessDefinitionInstanceVersionStatisticsResponse403 | GetProcessDefinitionInstanceVersionStatisticsResponse500]"""
        from .api.process_definition.get_process_definition_instance_version_statistics import sync as get_process_definition_instance_version_statistics_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_process_definition_instance_version_statistics_sync(**_kwargs)


    async def get_process_definition_instance_version_statistics_async(self, process_definition_id: str, *, data: GetProcessDefinitionInstanceVersionStatisticsData, **kwargs: Any) -> GetProcessDefinitionInstanceVersionStatisticsResponse200:
        """Get process instance statistics by version

 Get statistics about process instances, grouped by version for a given process definition.

Args:
    process_definition_id (str): Id of a process definition, from the model. Only ids of
        process definitions that are deployed are useful. Example: new-account-onboarding-
        workflow.
    body (GetProcessDefinitionInstanceVersionStatisticsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetProcessDefinitionInstanceVersionStatisticsResponse200 | GetProcessDefinitionInstanceVersionStatisticsResponse400 | GetProcessDefinitionInstanceVersionStatisticsResponse401 | GetProcessDefinitionInstanceVersionStatisticsResponse403 | GetProcessDefinitionInstanceVersionStatisticsResponse500]"""
        from .api.process_definition.get_process_definition_instance_version_statistics import asyncio as get_process_definition_instance_version_statistics_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_process_definition_instance_version_statistics_asyncio(**_kwargs)


    def get_process_definition_xml(self, process_definition_key: str, **kwargs: Any) -> GetProcessDefinitionXMLResponse400:
        """Get process definition XML

 Returns process definition as XML.

Args:
    process_definition_key (str): System-generated key for a deployed process definition.
        Example: 2251799813686749.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetProcessDefinitionXMLResponse400 | GetProcessDefinitionXMLResponse401 | GetProcessDefinitionXMLResponse403 | GetProcessDefinitionXMLResponse404 | GetProcessDefinitionXMLResponse500 | str]"""
        from .api.process_definition.get_process_definition_xml import sync as get_process_definition_xml_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_process_definition_xml_sync(**_kwargs)


    async def get_process_definition_xml_async(self, process_definition_key: str, **kwargs: Any) -> GetProcessDefinitionXMLResponse400:
        """Get process definition XML

 Returns process definition as XML.

Args:
    process_definition_key (str): System-generated key for a deployed process definition.
        Example: 2251799813686749.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetProcessDefinitionXMLResponse400 | GetProcessDefinitionXMLResponse401 | GetProcessDefinitionXMLResponse403 | GetProcessDefinitionXMLResponse404 | GetProcessDefinitionXMLResponse500 | str]"""
        from .api.process_definition.get_process_definition_xml import asyncio as get_process_definition_xml_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_process_definition_xml_asyncio(**_kwargs)


    def search_roles_for_group(self, group_id: str, *, data: SearchRolesForGroupData, **kwargs: Any) -> SearchRolesForGroupResponse200:
        """Search group roles

 Search roles assigned to a group.

Args:
    group_id (str):
    body (SearchRolesForGroupData): Role search request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchRolesForGroupResponse200 | SearchRolesForGroupResponse400 | SearchRolesForGroupResponse401 | SearchRolesForGroupResponse403 | SearchRolesForGroupResponse404 | SearchRolesForGroupResponse500]"""
        from .api.group.search_roles_for_group import sync as search_roles_for_group_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_roles_for_group_sync(**_kwargs)


    async def search_roles_for_group_async(self, group_id: str, *, data: SearchRolesForGroupData, **kwargs: Any) -> SearchRolesForGroupResponse200:
        """Search group roles

 Search roles assigned to a group.

Args:
    group_id (str):
    body (SearchRolesForGroupData): Role search request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchRolesForGroupResponse200 | SearchRolesForGroupResponse400 | SearchRolesForGroupResponse401 | SearchRolesForGroupResponse403 | SearchRolesForGroupResponse404 | SearchRolesForGroupResponse500]"""
        from .api.group.search_roles_for_group import asyncio as search_roles_for_group_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_roles_for_group_asyncio(**_kwargs)


    def unassign_user_from_group(self, group_id: str, username: str, **kwargs: Any) -> Any:
        """Unassign a user from a group

 Unassigns a user from a group.
The user is removed as a group member, with associated authorizations, roles, and tenant assignments
no longer applied.

Args:
    group_id (str):
    username (str): The unique name of a user. Example: swillis.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignUserFromGroupResponse400 | UnassignUserFromGroupResponse403 | UnassignUserFromGroupResponse404 | UnassignUserFromGroupResponse500 | UnassignUserFromGroupResponse503]"""
        from .api.group.unassign_user_from_group import sync as unassign_user_from_group_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return unassign_user_from_group_sync(**_kwargs)


    async def unassign_user_from_group_async(self, group_id: str, username: str, **kwargs: Any) -> Any:
        """Unassign a user from a group

 Unassigns a user from a group.
The user is removed as a group member, with associated authorizations, roles, and tenant assignments
no longer applied.

Args:
    group_id (str):
    username (str): The unique name of a user. Example: swillis.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignUserFromGroupResponse400 | UnassignUserFromGroupResponse403 | UnassignUserFromGroupResponse404 | UnassignUserFromGroupResponse500 | UnassignUserFromGroupResponse503]"""
        from .api.group.unassign_user_from_group import asyncio as unassign_user_from_group_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await unassign_user_from_group_asyncio(**_kwargs)


    def search_users_for_group(self, group_id: str, *, data: SearchUsersForGroupData, **kwargs: Any) -> SearchUsersForGroupResponse200:
        """Search group users

 Search users assigned to a group.

Args:
    group_id (str):
    body (SearchUsersForGroupData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchUsersForGroupResponse200 | SearchUsersForGroupResponse400 | SearchUsersForGroupResponse401 | SearchUsersForGroupResponse403 | SearchUsersForGroupResponse404 | SearchUsersForGroupResponse500]"""
        from .api.group.search_users_for_group import sync as search_users_for_group_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_users_for_group_sync(**_kwargs)


    async def search_users_for_group_async(self, group_id: str, *, data: SearchUsersForGroupData, **kwargs: Any) -> SearchUsersForGroupResponse200:
        """Search group users

 Search users assigned to a group.

Args:
    group_id (str):
    body (SearchUsersForGroupData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchUsersForGroupResponse200 | SearchUsersForGroupResponse400 | SearchUsersForGroupResponse401 | SearchUsersForGroupResponse403 | SearchUsersForGroupResponse404 | SearchUsersForGroupResponse500]"""
        from .api.group.search_users_for_group import asyncio as search_users_for_group_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_users_for_group_asyncio(**_kwargs)


    def unassign_client_from_group(self, group_id: str, client_id: str, **kwargs: Any) -> Any:
        """Unassign a client from a group

 Unassigns a client from a group.
The client is removed as a group member, with associated authorizations, roles, and tenant
assignments no longer applied.

Args:
    group_id (str):
    client_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignClientFromGroupResponse400 | UnassignClientFromGroupResponse403 | UnassignClientFromGroupResponse404 | UnassignClientFromGroupResponse500 | UnassignClientFromGroupResponse503]"""
        from .api.group.unassign_client_from_group import sync as unassign_client_from_group_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return unassign_client_from_group_sync(**_kwargs)


    async def unassign_client_from_group_async(self, group_id: str, client_id: str, **kwargs: Any) -> Any:
        """Unassign a client from a group

 Unassigns a client from a group.
The client is removed as a group member, with associated authorizations, roles, and tenant
assignments no longer applied.

Args:
    group_id (str):
    client_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignClientFromGroupResponse400 | UnassignClientFromGroupResponse403 | UnassignClientFromGroupResponse404 | UnassignClientFromGroupResponse500 | UnassignClientFromGroupResponse503]"""
        from .api.group.unassign_client_from_group import asyncio as unassign_client_from_group_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await unassign_client_from_group_asyncio(**_kwargs)


    def assign_user_to_group(self, group_id: str, username: str, **kwargs: Any) -> Any:
        """Assign a user to a group

 Assigns a user to a group, making the user a member of the group.
Group members inherit the group authorizations, roles, and tenant assignments.

Args:
    group_id (str):
    username (str): The unique name of a user. Example: swillis.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignUserToGroupResponse400 | AssignUserToGroupResponse403 | AssignUserToGroupResponse404 | AssignUserToGroupResponse409 | AssignUserToGroupResponse500 | AssignUserToGroupResponse503]"""
        from .api.group.assign_user_to_group import sync as assign_user_to_group_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return assign_user_to_group_sync(**_kwargs)


    async def assign_user_to_group_async(self, group_id: str, username: str, **kwargs: Any) -> Any:
        """Assign a user to a group

 Assigns a user to a group, making the user a member of the group.
Group members inherit the group authorizations, roles, and tenant assignments.

Args:
    group_id (str):
    username (str): The unique name of a user. Example: swillis.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignUserToGroupResponse400 | AssignUserToGroupResponse403 | AssignUserToGroupResponse404 | AssignUserToGroupResponse409 | AssignUserToGroupResponse500 | AssignUserToGroupResponse503]"""
        from .api.group.assign_user_to_group import asyncio as assign_user_to_group_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await assign_user_to_group_asyncio(**_kwargs)


    def search_clients_for_group(self, group_id: str, *, data: SearchClientsForGroupData, **kwargs: Any) -> SearchClientsForGroupResponse200:
        """Search group clients

 Search clients assigned to a group.

Args:
    group_id (str):
    body (SearchClientsForGroupData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchClientsForGroupResponse200 | SearchClientsForGroupResponse400 | SearchClientsForGroupResponse401 | SearchClientsForGroupResponse403 | SearchClientsForGroupResponse404 | SearchClientsForGroupResponse500]"""
        from .api.group.search_clients_for_group import sync as search_clients_for_group_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_clients_for_group_sync(**_kwargs)


    async def search_clients_for_group_async(self, group_id: str, *, data: SearchClientsForGroupData, **kwargs: Any) -> SearchClientsForGroupResponse200:
        """Search group clients

 Search clients assigned to a group.

Args:
    group_id (str):
    body (SearchClientsForGroupData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchClientsForGroupResponse200 | SearchClientsForGroupResponse400 | SearchClientsForGroupResponse401 | SearchClientsForGroupResponse403 | SearchClientsForGroupResponse404 | SearchClientsForGroupResponse500]"""
        from .api.group.search_clients_for_group import asyncio as search_clients_for_group_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_clients_for_group_asyncio(**_kwargs)


    def assign_mapping_rule_to_group(self, group_id: str, mapping_rule_id: str, **kwargs: Any) -> Any:
        """Assign a mapping rule to a group

 Assigns a mapping rule to a group.

Args:
    group_id (str):
    mapping_rule_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignMappingRuleToGroupResponse400 | AssignMappingRuleToGroupResponse403 | AssignMappingRuleToGroupResponse404 | AssignMappingRuleToGroupResponse409 | AssignMappingRuleToGroupResponse500 | AssignMappingRuleToGroupResponse503]"""
        from .api.group.assign_mapping_rule_to_group import sync as assign_mapping_rule_to_group_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return assign_mapping_rule_to_group_sync(**_kwargs)


    async def assign_mapping_rule_to_group_async(self, group_id: str, mapping_rule_id: str, **kwargs: Any) -> Any:
        """Assign a mapping rule to a group

 Assigns a mapping rule to a group.

Args:
    group_id (str):
    mapping_rule_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignMappingRuleToGroupResponse400 | AssignMappingRuleToGroupResponse403 | AssignMappingRuleToGroupResponse404 | AssignMappingRuleToGroupResponse409 | AssignMappingRuleToGroupResponse500 | AssignMappingRuleToGroupResponse503]"""
        from .api.group.assign_mapping_rule_to_group import asyncio as assign_mapping_rule_to_group_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await assign_mapping_rule_to_group_asyncio(**_kwargs)


    def search_mapping_rules_for_group(self, group_id: str, *, data: SearchMappingRulesForGroupData, **kwargs: Any) -> SearchMappingRulesForGroupResponse200:
        """Search group mapping rules

 Search mapping rules assigned to a group.

Args:
    group_id (str):
    body (SearchMappingRulesForGroupData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchMappingRulesForGroupResponse200 | SearchMappingRulesForGroupResponse400 | SearchMappingRulesForGroupResponse401 | SearchMappingRulesForGroupResponse403 | SearchMappingRulesForGroupResponse404 | SearchMappingRulesForGroupResponse500]"""
        from .api.group.search_mapping_rules_for_group import sync as search_mapping_rules_for_group_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_mapping_rules_for_group_sync(**_kwargs)


    async def search_mapping_rules_for_group_async(self, group_id: str, *, data: SearchMappingRulesForGroupData, **kwargs: Any) -> SearchMappingRulesForGroupResponse200:
        """Search group mapping rules

 Search mapping rules assigned to a group.

Args:
    group_id (str):
    body (SearchMappingRulesForGroupData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchMappingRulesForGroupResponse200 | SearchMappingRulesForGroupResponse400 | SearchMappingRulesForGroupResponse401 | SearchMappingRulesForGroupResponse403 | SearchMappingRulesForGroupResponse404 | SearchMappingRulesForGroupResponse500]"""
        from .api.group.search_mapping_rules_for_group import asyncio as search_mapping_rules_for_group_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_mapping_rules_for_group_asyncio(**_kwargs)


    def search_groups(self, *, data: SearchGroupsData, **kwargs: Any) -> Any:
        """Search groups

 Search for groups based on given criteria.

Args:
    body (SearchGroupsData): Group search request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | SearchGroupsResponse200 | SearchGroupsResponse400 | SearchGroupsResponse401 | SearchGroupsResponse403]"""
        from .api.group.search_groups import sync as search_groups_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_groups_sync(**_kwargs)


    async def search_groups_async(self, *, data: SearchGroupsData, **kwargs: Any) -> Any:
        """Search groups

 Search for groups based on given criteria.

Args:
    body (SearchGroupsData): Group search request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | SearchGroupsResponse200 | SearchGroupsResponse400 | SearchGroupsResponse401 | SearchGroupsResponse403]"""
        from .api.group.search_groups import asyncio as search_groups_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_groups_asyncio(**_kwargs)


    def get_group(self, group_id: str, **kwargs: Any) -> GetGroupResponse200:
        """Get group

 Get a group by its ID.

Args:
    group_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetGroupResponse200 | GetGroupResponse401 | GetGroupResponse403 | GetGroupResponse404 | GetGroupResponse500]"""
        from .api.group.get_group import sync as get_group_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_group_sync(**_kwargs)


    async def get_group_async(self, group_id: str, **kwargs: Any) -> GetGroupResponse200:
        """Get group

 Get a group by its ID.

Args:
    group_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetGroupResponse200 | GetGroupResponse401 | GetGroupResponse403 | GetGroupResponse404 | GetGroupResponse500]"""
        from .api.group.get_group import asyncio as get_group_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_group_asyncio(**_kwargs)


    def delete_group(self, group_id: str, **kwargs: Any) -> Any:
        """Delete group

 Deletes the group with the given ID.

Args:
    group_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteGroupResponse401 | DeleteGroupResponse404 | DeleteGroupResponse500 | DeleteGroupResponse503]"""
        from .api.group.delete_group import sync as delete_group_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return delete_group_sync(**_kwargs)


    async def delete_group_async(self, group_id: str, **kwargs: Any) -> Any:
        """Delete group

 Deletes the group with the given ID.

Args:
    group_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteGroupResponse401 | DeleteGroupResponse404 | DeleteGroupResponse500 | DeleteGroupResponse503]"""
        from .api.group.delete_group import asyncio as delete_group_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await delete_group_asyncio(**_kwargs)


    def assign_client_to_group(self, group_id: str, client_id: str, **kwargs: Any) -> Any:
        """Assign a client to a group

 Assigns a client to a group, making it a member of the group.
Members of the group inherit the group authorizations, roles, and tenant assignments.

Args:
    group_id (str):
    client_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignClientToGroupResponse400 | AssignClientToGroupResponse403 | AssignClientToGroupResponse404 | AssignClientToGroupResponse409 | AssignClientToGroupResponse500 | AssignClientToGroupResponse503]"""
        from .api.group.assign_client_to_group import sync as assign_client_to_group_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return assign_client_to_group_sync(**_kwargs)


    async def assign_client_to_group_async(self, group_id: str, client_id: str, **kwargs: Any) -> Any:
        """Assign a client to a group

 Assigns a client to a group, making it a member of the group.
Members of the group inherit the group authorizations, roles, and tenant assignments.

Args:
    group_id (str):
    client_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignClientToGroupResponse400 | AssignClientToGroupResponse403 | AssignClientToGroupResponse404 | AssignClientToGroupResponse409 | AssignClientToGroupResponse500 | AssignClientToGroupResponse503]"""
        from .api.group.assign_client_to_group import asyncio as assign_client_to_group_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await assign_client_to_group_asyncio(**_kwargs)


    def update_group(self, group_id: str, *, data: UpdateGroupData, **kwargs: Any) -> UpdateGroupResponse200:
        """Update group

 Update a group with the given ID.

Args:
    group_id (str):
    body (UpdateGroupData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[UpdateGroupResponse200 | UpdateGroupResponse400 | UpdateGroupResponse401 | UpdateGroupResponse404 | UpdateGroupResponse500 | UpdateGroupResponse503]"""
        from .api.group.update_group import sync as update_group_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return update_group_sync(**_kwargs)


    async def update_group_async(self, group_id: str, *, data: UpdateGroupData, **kwargs: Any) -> UpdateGroupResponse200:
        """Update group

 Update a group with the given ID.

Args:
    group_id (str):
    body (UpdateGroupData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[UpdateGroupResponse200 | UpdateGroupResponse400 | UpdateGroupResponse401 | UpdateGroupResponse404 | UpdateGroupResponse500 | UpdateGroupResponse503]"""
        from .api.group.update_group import asyncio as update_group_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await update_group_asyncio(**_kwargs)


    def unassign_mapping_rule_from_group(self, group_id: str, mapping_rule_id: str, **kwargs: Any) -> Any:
        """Unassign a mapping rule from a group

 Unassigns a mapping rule from a group.

Args:
    group_id (str):
    mapping_rule_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignMappingRuleFromGroupResponse400 | UnassignMappingRuleFromGroupResponse403 | UnassignMappingRuleFromGroupResponse404 | UnassignMappingRuleFromGroupResponse500 | UnassignMappingRuleFromGroupResponse503]"""
        from .api.group.unassign_mapping_rule_from_group import sync as unassign_mapping_rule_from_group_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return unassign_mapping_rule_from_group_sync(**_kwargs)


    async def unassign_mapping_rule_from_group_async(self, group_id: str, mapping_rule_id: str, **kwargs: Any) -> Any:
        """Unassign a mapping rule from a group

 Unassigns a mapping rule from a group.

Args:
    group_id (str):
    mapping_rule_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignMappingRuleFromGroupResponse400 | UnassignMappingRuleFromGroupResponse403 | UnassignMappingRuleFromGroupResponse404 | UnassignMappingRuleFromGroupResponse500 | UnassignMappingRuleFromGroupResponse503]"""
        from .api.group.unassign_mapping_rule_from_group import asyncio as unassign_mapping_rule_from_group_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await unassign_mapping_rule_from_group_asyncio(**_kwargs)


    def create_group(self, *, data: CreateGroupData, **kwargs: Any) -> CreateGroupResponse201:
        """Create group

 Create a new group.

Args:
    body (CreateGroupData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateGroupResponse201 | CreateGroupResponse400 | CreateGroupResponse401 | CreateGroupResponse403 | CreateGroupResponse500 | CreateGroupResponse503]"""
        from .api.group.create_group import sync as create_group_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return create_group_sync(**_kwargs)


    async def create_group_async(self, *, data: CreateGroupData, **kwargs: Any) -> CreateGroupResponse201:
        """Create group

 Create a new group.

Args:
    body (CreateGroupData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateGroupResponse201 | CreateGroupResponse400 | CreateGroupResponse401 | CreateGroupResponse403 | CreateGroupResponse500 | CreateGroupResponse503]"""
        from .api.group.create_group import asyncio as create_group_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await create_group_asyncio(**_kwargs)


    def get_variable(self, variable_key: str, **kwargs: Any) -> GetVariableResponse200:
        """Get variable

 Get the variable by the variable key.

Args:
    variable_key (str): System-generated key for a variable. Example: 2251799813683287.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetVariableResponse200 | GetVariableResponse400 | GetVariableResponse401 | GetVariableResponse403 | GetVariableResponse404 | GetVariableResponse500]"""
        from .api.variable.get_variable import sync as get_variable_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_variable_sync(**_kwargs)


    async def get_variable_async(self, variable_key: str, **kwargs: Any) -> GetVariableResponse200:
        """Get variable

 Get the variable by the variable key.

Args:
    variable_key (str): System-generated key for a variable. Example: 2251799813683287.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetVariableResponse200 | GetVariableResponse400 | GetVariableResponse401 | GetVariableResponse403 | GetVariableResponse404 | GetVariableResponse500]"""
        from .api.variable.get_variable import asyncio as get_variable_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_variable_asyncio(**_kwargs)


    def search_variables(self, *, data: SearchVariablesData, truncate_values: bool | Unset = UNSET, **kwargs: Any) -> SearchVariablesResponse200:
        """Search variables

 Search for process and local variables based on given criteria. By default, long variable values in
the response are truncated.

Args:
    truncate_values (bool | Unset):
    body (SearchVariablesData): Variable search query request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchVariablesResponse200 | SearchVariablesResponse400 | SearchVariablesResponse401 | SearchVariablesResponse403 | SearchVariablesResponse500]"""
        from .api.variable.search_variables import sync as search_variables_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_variables_sync(**_kwargs)


    async def search_variables_async(self, *, data: SearchVariablesData, truncate_values: bool | Unset = UNSET, **kwargs: Any) -> SearchVariablesResponse200:
        """Search variables

 Search for process and local variables based on given criteria. By default, long variable values in
the response are truncated.

Args:
    truncate_values (bool | Unset):
    body (SearchVariablesData): Variable search query request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchVariablesResponse200 | SearchVariablesResponse400 | SearchVariablesResponse401 | SearchVariablesResponse403 | SearchVariablesResponse500]"""
        from .api.variable.search_variables import asyncio as search_variables_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_variables_asyncio(**_kwargs)


    def create_admin_user(self, *, data: CreateAdminUserData, **kwargs: Any) -> Any:
        """Create admin user

 Creates a new user and assigns the admin role to it. This endpoint is only usable when users are
managed in the Orchestration Cluster and while no user is assigned to the admin role.

Args:
    body (CreateAdminUserData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | CreateAdminUserResponse400 | CreateAdminUserResponse403 | CreateAdminUserResponse500 | CreateAdminUserResponse503]"""
        from .api.setup.create_admin_user import sync as create_admin_user_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return create_admin_user_sync(**_kwargs)


    async def create_admin_user_async(self, *, data: CreateAdminUserData, **kwargs: Any) -> Any:
        """Create admin user

 Creates a new user and assigns the admin role to it. This endpoint is only usable when users are
managed in the Orchestration Cluster and while no user is assigned to the admin role.

Args:
    body (CreateAdminUserData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | CreateAdminUserResponse400 | CreateAdminUserResponse403 | CreateAdminUserResponse500 | CreateAdminUserResponse503]"""
        from .api.setup.create_admin_user import asyncio as create_admin_user_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await create_admin_user_asyncio(**_kwargs)


    def get_decision_instance(self, decision_evaluation_instance_key: str, **kwargs: Any) -> GetDecisionInstanceResponse200:
        """Get decision instance

 Returns a decision instance.

Args:
    decision_evaluation_instance_key (str): System-generated key for a deployed decision
        instance. Example: 22517998136843567.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetDecisionInstanceResponse200 | GetDecisionInstanceResponse400 | GetDecisionInstanceResponse401 | GetDecisionInstanceResponse403 | GetDecisionInstanceResponse404 | GetDecisionInstanceResponse500]"""
        from .api.decision_instance.get_decision_instance import sync as get_decision_instance_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_decision_instance_sync(**_kwargs)


    async def get_decision_instance_async(self, decision_evaluation_instance_key: str, **kwargs: Any) -> GetDecisionInstanceResponse200:
        """Get decision instance

 Returns a decision instance.

Args:
    decision_evaluation_instance_key (str): System-generated key for a deployed decision
        instance. Example: 22517998136843567.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetDecisionInstanceResponse200 | GetDecisionInstanceResponse400 | GetDecisionInstanceResponse401 | GetDecisionInstanceResponse403 | GetDecisionInstanceResponse404 | GetDecisionInstanceResponse500]"""
        from .api.decision_instance.get_decision_instance import asyncio as get_decision_instance_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_decision_instance_asyncio(**_kwargs)


    def search_decision_instances(self, *, data: SearchDecisionInstancesData, **kwargs: Any) -> SearchDecisionInstancesResponse200:
        """Search decision instances

 Search for decision instances based on given criteria.

Args:
    body (SearchDecisionInstancesData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchDecisionInstancesResponse200 | SearchDecisionInstancesResponse400 | SearchDecisionInstancesResponse401 | SearchDecisionInstancesResponse403 | SearchDecisionInstancesResponse500]"""
        from .api.decision_instance.search_decision_instances import sync as search_decision_instances_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_decision_instances_sync(**_kwargs)


    async def search_decision_instances_async(self, *, data: SearchDecisionInstancesData, **kwargs: Any) -> SearchDecisionInstancesResponse200:
        """Search decision instances

 Search for decision instances based on given criteria.

Args:
    body (SearchDecisionInstancesData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchDecisionInstancesResponse200 | SearchDecisionInstancesResponse400 | SearchDecisionInstancesResponse401 | SearchDecisionInstancesResponse403 | SearchDecisionInstancesResponse500]"""
        from .api.decision_instance.search_decision_instances import asyncio as search_decision_instances_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_decision_instances_asyncio(**_kwargs)


    def activate_jobs(self, *, data: ActivateJobsData, **kwargs: Any) -> ActivateJobsResponse200:
        """Activate jobs

 Iterate through all known partitions and activate jobs up to the requested maximum.

Args:
    body (ActivateJobsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[ActivateJobsResponse200 | ActivateJobsResponse400 | ActivateJobsResponse401 | ActivateJobsResponse500 | ActivateJobsResponse503]"""
        from .api.job.activate_jobs import sync as activate_jobs_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return activate_jobs_sync(**_kwargs)


    async def activate_jobs_async(self, *, data: ActivateJobsData, **kwargs: Any) -> ActivateJobsResponse200:
        """Activate jobs

 Iterate through all known partitions and activate jobs up to the requested maximum.

Args:
    body (ActivateJobsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[ActivateJobsResponse200 | ActivateJobsResponse400 | ActivateJobsResponse401 | ActivateJobsResponse500 | ActivateJobsResponse503]"""
        from .api.job.activate_jobs import asyncio as activate_jobs_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await activate_jobs_asyncio(**_kwargs)


    def complete_job(self, job_key: str, *, data: CompleteJobData, **kwargs: Any) -> Any:
        """Complete job

 Complete a job with the given payload, which allows completing the associated service task.

Args:
    job_key (str): System-generated key for a job. Example: 2251799813653498.
    body (CompleteJobData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | CompleteJobResponse400 | CompleteJobResponse404 | CompleteJobResponse409 | CompleteJobResponse500 | CompleteJobResponse503]"""
        from .api.job.complete_job import sync as complete_job_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return complete_job_sync(**_kwargs)


    async def complete_job_async(self, job_key: str, *, data: CompleteJobData, **kwargs: Any) -> Any:
        """Complete job

 Complete a job with the given payload, which allows completing the associated service task.

Args:
    job_key (str): System-generated key for a job. Example: 2251799813653498.
    body (CompleteJobData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | CompleteJobResponse400 | CompleteJobResponse404 | CompleteJobResponse409 | CompleteJobResponse500 | CompleteJobResponse503]"""
        from .api.job.complete_job import asyncio as complete_job_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await complete_job_asyncio(**_kwargs)


    def fail_job(self, job_key: str, *, data: FailJobData, **kwargs: Any) -> Any:
        """Fail job

 Mark the job as failed.

Args:
    job_key (str): System-generated key for a job. Example: 2251799813653498.
    body (FailJobData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | FailJobResponse400 | FailJobResponse404 | FailJobResponse409 | FailJobResponse500 | FailJobResponse503]"""
        from .api.job.fail_job import sync as fail_job_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return fail_job_sync(**_kwargs)


    async def fail_job_async(self, job_key: str, *, data: FailJobData, **kwargs: Any) -> Any:
        """Fail job

 Mark the job as failed.

Args:
    job_key (str): System-generated key for a job. Example: 2251799813653498.
    body (FailJobData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | FailJobResponse400 | FailJobResponse404 | FailJobResponse409 | FailJobResponse500 | FailJobResponse503]"""
        from .api.job.fail_job import asyncio as fail_job_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await fail_job_asyncio(**_kwargs)


    def throw_job_error(self, job_key: str, *, data: ThrowJobErrorData, **kwargs: Any) -> Any:
        """Throw error for job

 Reports a business error (i.e. non-technical) that occurs while processing a job.

Args:
    job_key (str): System-generated key for a job. Example: 2251799813653498.
    body (ThrowJobErrorData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | ThrowJobErrorResponse400 | ThrowJobErrorResponse404 | ThrowJobErrorResponse409 | ThrowJobErrorResponse500 | ThrowJobErrorResponse503]"""
        from .api.job.throw_job_error import sync as throw_job_error_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return throw_job_error_sync(**_kwargs)


    async def throw_job_error_async(self, job_key: str, *, data: ThrowJobErrorData, **kwargs: Any) -> Any:
        """Throw error for job

 Reports a business error (i.e. non-technical) that occurs while processing a job.

Args:
    job_key (str): System-generated key for a job. Example: 2251799813653498.
    body (ThrowJobErrorData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | ThrowJobErrorResponse400 | ThrowJobErrorResponse404 | ThrowJobErrorResponse409 | ThrowJobErrorResponse500 | ThrowJobErrorResponse503]"""
        from .api.job.throw_job_error import asyncio as throw_job_error_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await throw_job_error_asyncio(**_kwargs)


    def update_job(self, job_key: str, *, data: UpdateJobData, **kwargs: Any) -> Any:
        """Update job

 Update a job with the given key.

Args:
    job_key (str): System-generated key for a job. Example: 2251799813653498.
    body (UpdateJobData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UpdateJobResponse400 | UpdateJobResponse404 | UpdateJobResponse409 | UpdateJobResponse500 | UpdateJobResponse503]"""
        from .api.job.update_job import sync as update_job_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return update_job_sync(**_kwargs)


    async def update_job_async(self, job_key: str, *, data: UpdateJobData, **kwargs: Any) -> Any:
        """Update job

 Update a job with the given key.

Args:
    job_key (str): System-generated key for a job. Example: 2251799813653498.
    body (UpdateJobData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UpdateJobResponse400 | UpdateJobResponse404 | UpdateJobResponse409 | UpdateJobResponse500 | UpdateJobResponse503]"""
        from .api.job.update_job import asyncio as update_job_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await update_job_asyncio(**_kwargs)


    def search_jobs(self, *, data: SearchJobsData, **kwargs: Any) -> SearchJobsResponse200:
        """Search jobs

 Search for jobs based on given criteria.

Args:
    body (SearchJobsData): Job search request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchJobsResponse200 | SearchJobsResponse400 | SearchJobsResponse401 | SearchJobsResponse403 | SearchJobsResponse500]"""
        from .api.job.search_jobs import sync as search_jobs_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_jobs_sync(**_kwargs)


    async def search_jobs_async(self, *, data: SearchJobsData, **kwargs: Any) -> SearchJobsResponse200:
        """Search jobs

 Search for jobs based on given criteria.

Args:
    body (SearchJobsData): Job search request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchJobsResponse200 | SearchJobsResponse400 | SearchJobsResponse401 | SearchJobsResponse403 | SearchJobsResponse500]"""
        from .api.job.search_jobs import asyncio as search_jobs_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_jobs_asyncio(**_kwargs)


    def get_topology(self, **kwargs: Any) -> GetTopologyResponse200:
        """Get cluster topology

 Obtains the current topology of the cluster the gateway is part of.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetTopologyResponse200 | GetTopologyResponse401 | GetTopologyResponse500]"""
        from .api.cluster.get_topology import sync as get_topology_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_topology_sync(**_kwargs)


    async def get_topology_async(self, **kwargs: Any) -> GetTopologyResponse200:
        """Get cluster topology

 Obtains the current topology of the cluster the gateway is part of.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetTopologyResponse200 | GetTopologyResponse401 | GetTopologyResponse500]"""
        from .api.cluster.get_topology import asyncio as get_topology_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_topology_asyncio(**_kwargs)


    def correlate_message(self, *, data: CorrelateMessageData, **kwargs: Any) -> CorrelateMessageResponse200:
        """Correlate message

 Publishes a message and correlates it to a subscription.
If correlation is successful it will return the first process instance key the message correlated
with.
The message is not buffered.
Use the publish message endpoint to send messages that can be buffered.

Args:
    body (CorrelateMessageData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CorrelateMessageResponse200 | CorrelateMessageResponse400 | CorrelateMessageResponse403 | CorrelateMessageResponse404 | CorrelateMessageResponse500 | CorrelateMessageResponse503]"""
        from .api.message.correlate_message import sync as correlate_message_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return correlate_message_sync(**_kwargs)


    async def correlate_message_async(self, *, data: CorrelateMessageData, **kwargs: Any) -> CorrelateMessageResponse200:
        """Correlate message

 Publishes a message and correlates it to a subscription.
If correlation is successful it will return the first process instance key the message correlated
with.
The message is not buffered.
Use the publish message endpoint to send messages that can be buffered.

Args:
    body (CorrelateMessageData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CorrelateMessageResponse200 | CorrelateMessageResponse400 | CorrelateMessageResponse403 | CorrelateMessageResponse404 | CorrelateMessageResponse500 | CorrelateMessageResponse503]"""
        from .api.message.correlate_message import asyncio as correlate_message_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await correlate_message_asyncio(**_kwargs)


    def publish_message(self, *, data: PublishMessageData, **kwargs: Any) -> PublishMessageResponse200:
        """Publish message

 Publishes a single message.
Messages are published to specific partitions computed from their correlation keys.
Messages can be buffered.
The endpoint does not wait for a correlation result.
Use the message correlation endpoint for such use cases.

Args:
    body (PublishMessageData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[PublishMessageResponse200 | PublishMessageResponse400 | PublishMessageResponse500 | PublishMessageResponse503]"""
        from .api.message.publish_message import sync as publish_message_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return publish_message_sync(**_kwargs)


    async def publish_message_async(self, *, data: PublishMessageData, **kwargs: Any) -> PublishMessageResponse200:
        """Publish message

 Publishes a single message.
Messages are published to specific partitions computed from their correlation keys.
Messages can be buffered.
The endpoint does not wait for a correlation result.
Use the message correlation endpoint for such use cases.

Args:
    body (PublishMessageData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[PublishMessageResponse200 | PublishMessageResponse400 | PublishMessageResponse500 | PublishMessageResponse503]"""
        from .api.message.publish_message import asyncio as publish_message_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await publish_message_asyncio(**_kwargs)


    def delete_process_instances_batch_operation(self, *, data: DeleteProcessInstancesBatchOperationData, **kwargs: Any) -> DeleteProcessInstancesBatchOperationResponse200:
        """Delete process instances (batch)

 Delete multiple process instances. This will delete the historic data from secondary storage.
Only process instances in a final state (COMPLETED or TERMINATED) can be deleted.
This is done asynchronously, the progress can be tracked using the batchOperationKey from the
response and the batch operation status endpoint (/batch-operations/{batchOperationKey}).

Args:
    body (DeleteProcessInstancesBatchOperationData): The process instance filter that defines
        which process instances should be deleted.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[DeleteProcessInstancesBatchOperationResponse200 | DeleteProcessInstancesBatchOperationResponse400 | DeleteProcessInstancesBatchOperationResponse401 | DeleteProcessInstancesBatchOperationResponse403 | DeleteProcessInstancesBatchOperationResponse500]"""
        from .api.process_instance.delete_process_instances_batch_operation import sync as delete_process_instances_batch_operation_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return delete_process_instances_batch_operation_sync(**_kwargs)


    async def delete_process_instances_batch_operation_async(self, *, data: DeleteProcessInstancesBatchOperationData, **kwargs: Any) -> DeleteProcessInstancesBatchOperationResponse200:
        """Delete process instances (batch)

 Delete multiple process instances. This will delete the historic data from secondary storage.
Only process instances in a final state (COMPLETED or TERMINATED) can be deleted.
This is done asynchronously, the progress can be tracked using the batchOperationKey from the
response and the batch operation status endpoint (/batch-operations/{batchOperationKey}).

Args:
    body (DeleteProcessInstancesBatchOperationData): The process instance filter that defines
        which process instances should be deleted.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[DeleteProcessInstancesBatchOperationResponse200 | DeleteProcessInstancesBatchOperationResponse400 | DeleteProcessInstancesBatchOperationResponse401 | DeleteProcessInstancesBatchOperationResponse403 | DeleteProcessInstancesBatchOperationResponse500]"""
        from .api.process_instance.delete_process_instances_batch_operation import asyncio as delete_process_instances_batch_operation_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await delete_process_instances_batch_operation_asyncio(**_kwargs)


    def migrate_process_instances_batch_operation(self, *, data: MigrateProcessInstancesBatchOperationData, **kwargs: Any) -> MigrateProcessInstancesBatchOperationResponse200:
        """Migrate process instances (batch)

 Migrate multiple process instances.
Since only process instances with ACTIVE state can be migrated, any given
filters for state are ignored and overridden during this batch operation.
This is done asynchronously, the progress can be tracked using the batchOperationKey from the
response and the batch operation status endpoint (/batch-operations/{batchOperationKey}).

Args:
    body (MigrateProcessInstancesBatchOperationData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[MigrateProcessInstancesBatchOperationResponse200 | MigrateProcessInstancesBatchOperationResponse400 | MigrateProcessInstancesBatchOperationResponse401 | MigrateProcessInstancesBatchOperationResponse403 | MigrateProcessInstancesBatchOperationResponse500]"""
        from .api.process_instance.migrate_process_instances_batch_operation import sync as migrate_process_instances_batch_operation_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return migrate_process_instances_batch_operation_sync(**_kwargs)


    async def migrate_process_instances_batch_operation_async(self, *, data: MigrateProcessInstancesBatchOperationData, **kwargs: Any) -> MigrateProcessInstancesBatchOperationResponse200:
        """Migrate process instances (batch)

 Migrate multiple process instances.
Since only process instances with ACTIVE state can be migrated, any given
filters for state are ignored and overridden during this batch operation.
This is done asynchronously, the progress can be tracked using the batchOperationKey from the
response and the batch operation status endpoint (/batch-operations/{batchOperationKey}).

Args:
    body (MigrateProcessInstancesBatchOperationData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[MigrateProcessInstancesBatchOperationResponse200 | MigrateProcessInstancesBatchOperationResponse400 | MigrateProcessInstancesBatchOperationResponse401 | MigrateProcessInstancesBatchOperationResponse403 | MigrateProcessInstancesBatchOperationResponse500]"""
        from .api.process_instance.migrate_process_instances_batch_operation import asyncio as migrate_process_instances_batch_operation_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await migrate_process_instances_batch_operation_asyncio(**_kwargs)


    def modify_process_instances_batch_operation(self, *, data: ModifyProcessInstancesBatchOperationData, **kwargs: Any) -> ModifyProcessInstancesBatchOperationResponse200:
        """Modify process instances (batch)

 Modify multiple process instances.
Since only process instances with ACTIVE state can be modified, any given
filters for state are ignored and overridden during this batch operation.
In contrast to single modification operation, it is not possible to add variable instructions or
modify by element key.
It is only possible to use the element id of the source and target.
This is done asynchronously, the progress can be tracked using the batchOperationKey from the
response and the batch operation status endpoint (/batch-operations/{batchOperationKey}).

Args:
    body (ModifyProcessInstancesBatchOperationData): The process instance filter to define on
        which process instances tokens should be moved,
        and new element instances should be activated or terminated.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[ModifyProcessInstancesBatchOperationResponse200 | ModifyProcessInstancesBatchOperationResponse400 | ModifyProcessInstancesBatchOperationResponse401 | ModifyProcessInstancesBatchOperationResponse403 | ModifyProcessInstancesBatchOperationResponse500]"""
        from .api.process_instance.modify_process_instances_batch_operation import sync as modify_process_instances_batch_operation_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return modify_process_instances_batch_operation_sync(**_kwargs)


    async def modify_process_instances_batch_operation_async(self, *, data: ModifyProcessInstancesBatchOperationData, **kwargs: Any) -> ModifyProcessInstancesBatchOperationResponse200:
        """Modify process instances (batch)

 Modify multiple process instances.
Since only process instances with ACTIVE state can be modified, any given
filters for state are ignored and overridden during this batch operation.
In contrast to single modification operation, it is not possible to add variable instructions or
modify by element key.
It is only possible to use the element id of the source and target.
This is done asynchronously, the progress can be tracked using the batchOperationKey from the
response and the batch operation status endpoint (/batch-operations/{batchOperationKey}).

Args:
    body (ModifyProcessInstancesBatchOperationData): The process instance filter to define on
        which process instances tokens should be moved,
        and new element instances should be activated or terminated.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[ModifyProcessInstancesBatchOperationResponse200 | ModifyProcessInstancesBatchOperationResponse400 | ModifyProcessInstancesBatchOperationResponse401 | ModifyProcessInstancesBatchOperationResponse403 | ModifyProcessInstancesBatchOperationResponse500]"""
        from .api.process_instance.modify_process_instances_batch_operation import asyncio as modify_process_instances_batch_operation_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await modify_process_instances_batch_operation_asyncio(**_kwargs)


    def migrate_process_instance(self, process_instance_key: str, *, data: MigrateProcessInstanceData, **kwargs: Any) -> Any:
        """Migrate process instance

 Migrates a process instance to a new process definition.
This request can contain multiple mapping instructions to define mapping between the active
process instance's elements and target process definition elements.

Use this to upgrade a process instance to a new version of a process or to
a different process definition, e.g. to keep your running instances up-to-date with the
latest process improvements.

Args:
    process_instance_key (str): System-generated key for a process instance. Example:
        2251799813690746.
    body (MigrateProcessInstanceData): The migration instructions describe how to migrate a
        process instance from one process definition to another.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | MigrateProcessInstanceResponse400 | MigrateProcessInstanceResponse404 | MigrateProcessInstanceResponse409 | MigrateProcessInstanceResponse500 | MigrateProcessInstanceResponse503]"""
        from .api.process_instance.migrate_process_instance import sync as migrate_process_instance_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return migrate_process_instance_sync(**_kwargs)


    async def migrate_process_instance_async(self, process_instance_key: str, *, data: MigrateProcessInstanceData, **kwargs: Any) -> Any:
        """Migrate process instance

 Migrates a process instance to a new process definition.
This request can contain multiple mapping instructions to define mapping between the active
process instance's elements and target process definition elements.

Use this to upgrade a process instance to a new version of a process or to
a different process definition, e.g. to keep your running instances up-to-date with the
latest process improvements.

Args:
    process_instance_key (str): System-generated key for a process instance. Example:
        2251799813690746.
    body (MigrateProcessInstanceData): The migration instructions describe how to migrate a
        process instance from one process definition to another.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | MigrateProcessInstanceResponse400 | MigrateProcessInstanceResponse404 | MigrateProcessInstanceResponse409 | MigrateProcessInstanceResponse500 | MigrateProcessInstanceResponse503]"""
        from .api.process_instance.migrate_process_instance import asyncio as migrate_process_instance_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await migrate_process_instance_asyncio(**_kwargs)


    def resolve_process_instance_incidents(self, process_instance_key: str, **kwargs: Any) -> ResolveProcessInstanceIncidentsResponse200:
        """Resolve related incidents

 Creates a batch operation to resolve multiple incidents of a process instance.

Args:
    process_instance_key (str): System-generated key for a process instance. Example:
        2251799813690746.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[ResolveProcessInstanceIncidentsResponse200 | ResolveProcessInstanceIncidentsResponse400 | ResolveProcessInstanceIncidentsResponse401 | ResolveProcessInstanceIncidentsResponse404 | ResolveProcessInstanceIncidentsResponse500 | ResolveProcessInstanceIncidentsResponse503]"""
        from .api.process_instance.resolve_process_instance_incidents import sync as resolve_process_instance_incidents_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return resolve_process_instance_incidents_sync(**_kwargs)


    async def resolve_process_instance_incidents_async(self, process_instance_key: str, **kwargs: Any) -> ResolveProcessInstanceIncidentsResponse200:
        """Resolve related incidents

 Creates a batch operation to resolve multiple incidents of a process instance.

Args:
    process_instance_key (str): System-generated key for a process instance. Example:
        2251799813690746.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[ResolveProcessInstanceIncidentsResponse200 | ResolveProcessInstanceIncidentsResponse400 | ResolveProcessInstanceIncidentsResponse401 | ResolveProcessInstanceIncidentsResponse404 | ResolveProcessInstanceIncidentsResponse500 | ResolveProcessInstanceIncidentsResponse503]"""
        from .api.process_instance.resolve_process_instance_incidents import asyncio as resolve_process_instance_incidents_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await resolve_process_instance_incidents_asyncio(**_kwargs)


    def resolve_incidents_batch_operation(self, *, data: ResolveIncidentsBatchOperationData, **kwargs: Any) -> ResolveIncidentsBatchOperationResponse200:
        """Resolve related incidents (batch)

 Resolves multiple instances of process instances.
Since only process instances with ACTIVE state can have unresolved incidents, any given
filters for state are ignored and overridden during this batch operation.
This is done asynchronously, the progress can be tracked using the batchOperationKey from the
response and the batch operation status endpoint (/batch-operations/{batchOperationKey}).

Args:
    body (ResolveIncidentsBatchOperationData): The process instance filter that defines which
        process instances should have their incidents resolved.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[ResolveIncidentsBatchOperationResponse200 | ResolveIncidentsBatchOperationResponse400 | ResolveIncidentsBatchOperationResponse401 | ResolveIncidentsBatchOperationResponse403 | ResolveIncidentsBatchOperationResponse500]"""
        from .api.process_instance.resolve_incidents_batch_operation import sync as resolve_incidents_batch_operation_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return resolve_incidents_batch_operation_sync(**_kwargs)


    async def resolve_incidents_batch_operation_async(self, *, data: ResolveIncidentsBatchOperationData, **kwargs: Any) -> ResolveIncidentsBatchOperationResponse200:
        """Resolve related incidents (batch)

 Resolves multiple instances of process instances.
Since only process instances with ACTIVE state can have unresolved incidents, any given
filters for state are ignored and overridden during this batch operation.
This is done asynchronously, the progress can be tracked using the batchOperationKey from the
response and the batch operation status endpoint (/batch-operations/{batchOperationKey}).

Args:
    body (ResolveIncidentsBatchOperationData): The process instance filter that defines which
        process instances should have their incidents resolved.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[ResolveIncidentsBatchOperationResponse200 | ResolveIncidentsBatchOperationResponse400 | ResolveIncidentsBatchOperationResponse401 | ResolveIncidentsBatchOperationResponse403 | ResolveIncidentsBatchOperationResponse500]"""
        from .api.process_instance.resolve_incidents_batch_operation import asyncio as resolve_incidents_batch_operation_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await resolve_incidents_batch_operation_asyncio(**_kwargs)


    def create_process_instance(self, *, data: Processcreationbyid | Processcreationbykey, **kwargs: Any) -> CreateProcessInstanceResponse200:
        """Create process instance

 Creates and starts an instance of the specified process.
The process definition to use to create the instance can be specified either using its unique key
(as returned by Deploy resources), or using the BPMN process id and a version.

Waits for the completion of the process instance before returning a result
when awaitCompletion is enabled.

Args:
    body (Processcreationbyid | Processcreationbykey): Instructions for creating a process
        instance. The process definition can be specified
        either by id or by key.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateProcessInstanceResponse200 | CreateProcessInstanceResponse400 | CreateProcessInstanceResponse500 | CreateProcessInstanceResponse503 | CreateProcessInstanceResponse504]"""
        from .api.process_instance.create_process_instance import sync as create_process_instance_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return create_process_instance_sync(**_kwargs)


    async def create_process_instance_async(self, *, data: Processcreationbyid | Processcreationbykey, **kwargs: Any) -> CreateProcessInstanceResponse200:
        """Create process instance

 Creates and starts an instance of the specified process.
The process definition to use to create the instance can be specified either using its unique key
(as returned by Deploy resources), or using the BPMN process id and a version.

Waits for the completion of the process instance before returning a result
when awaitCompletion is enabled.

Args:
    body (Processcreationbyid | Processcreationbykey): Instructions for creating a process
        instance. The process definition can be specified
        either by id or by key.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateProcessInstanceResponse200 | CreateProcessInstanceResponse400 | CreateProcessInstanceResponse500 | CreateProcessInstanceResponse503 | CreateProcessInstanceResponse504]"""
        from .api.process_instance.create_process_instance import asyncio as create_process_instance_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await create_process_instance_asyncio(**_kwargs)


    def cancel_process_instance(self, process_instance_key: str, *, data: CancelProcessInstanceDataType0 | None, **kwargs: Any) -> Any:
        """Cancel process instance

 Cancels a running process instance. As a cancellation includes more than just the removal of the
process instance resource, the cancellation resource must be posted.

Args:
    process_instance_key (str): System-generated key for a process instance. Example:
        2251799813690746.
    body (CancelProcessInstanceDataType0 | None):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | CancelProcessInstanceResponse400 | CancelProcessInstanceResponse404 | CancelProcessInstanceResponse500 | CancelProcessInstanceResponse503]"""
        from .api.process_instance.cancel_process_instance import sync as cancel_process_instance_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return cancel_process_instance_sync(**_kwargs)


    async def cancel_process_instance_async(self, process_instance_key: str, *, data: CancelProcessInstanceDataType0 | None, **kwargs: Any) -> Any:
        """Cancel process instance

 Cancels a running process instance. As a cancellation includes more than just the removal of the
process instance resource, the cancellation resource must be posted.

Args:
    process_instance_key (str): System-generated key for a process instance. Example:
        2251799813690746.
    body (CancelProcessInstanceDataType0 | None):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | CancelProcessInstanceResponse400 | CancelProcessInstanceResponse404 | CancelProcessInstanceResponse500 | CancelProcessInstanceResponse503]"""
        from .api.process_instance.cancel_process_instance import asyncio as cancel_process_instance_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await cancel_process_instance_asyncio(**_kwargs)


    def get_process_instance_sequence_flows(self, process_instance_key: str, **kwargs: Any) -> GetProcessInstanceSequenceFlowsResponse200:
        """Get sequence flows

 Get sequence flows taken by the process instance.

Args:
    process_instance_key (str): System-generated key for a process instance. Example:
        2251799813690746.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetProcessInstanceSequenceFlowsResponse200 | GetProcessInstanceSequenceFlowsResponse400 | GetProcessInstanceSequenceFlowsResponse401 | GetProcessInstanceSequenceFlowsResponse403 | GetProcessInstanceSequenceFlowsResponse500]"""
        from .api.process_instance.get_process_instance_sequence_flows import sync as get_process_instance_sequence_flows_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_process_instance_sequence_flows_sync(**_kwargs)


    async def get_process_instance_sequence_flows_async(self, process_instance_key: str, **kwargs: Any) -> GetProcessInstanceSequenceFlowsResponse200:
        """Get sequence flows

 Get sequence flows taken by the process instance.

Args:
    process_instance_key (str): System-generated key for a process instance. Example:
        2251799813690746.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetProcessInstanceSequenceFlowsResponse200 | GetProcessInstanceSequenceFlowsResponse400 | GetProcessInstanceSequenceFlowsResponse401 | GetProcessInstanceSequenceFlowsResponse403 | GetProcessInstanceSequenceFlowsResponse500]"""
        from .api.process_instance.get_process_instance_sequence_flows import asyncio as get_process_instance_sequence_flows_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_process_instance_sequence_flows_asyncio(**_kwargs)


    def delete_process_instance(self, process_instance_key: str, *, data: DeleteProcessInstanceDataType0 | None, **kwargs: Any) -> Any:
        """Delete process instance

 Deletes a process instance. Only instances that are completed or terminated can be deleted.

Args:
    process_instance_key (str): System-generated key for a process instance. Example:
        2251799813690746.
    body (DeleteProcessInstanceDataType0 | None):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteProcessInstanceResponse401 | DeleteProcessInstanceResponse403 | DeleteProcessInstanceResponse404 | DeleteProcessInstanceResponse409 | DeleteProcessInstanceResponse500 | DeleteProcessInstanceResponse503]"""
        from .api.process_instance.delete_process_instance import sync as delete_process_instance_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return delete_process_instance_sync(**_kwargs)


    async def delete_process_instance_async(self, process_instance_key: str, *, data: DeleteProcessInstanceDataType0 | None, **kwargs: Any) -> Any:
        """Delete process instance

 Deletes a process instance. Only instances that are completed or terminated can be deleted.

Args:
    process_instance_key (str): System-generated key for a process instance. Example:
        2251799813690746.
    body (DeleteProcessInstanceDataType0 | None):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteProcessInstanceResponse401 | DeleteProcessInstanceResponse403 | DeleteProcessInstanceResponse404 | DeleteProcessInstanceResponse409 | DeleteProcessInstanceResponse500 | DeleteProcessInstanceResponse503]"""
        from .api.process_instance.delete_process_instance import asyncio as delete_process_instance_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await delete_process_instance_asyncio(**_kwargs)


    def search_process_instance_incidents(self, process_instance_key: str, *, data: SearchProcessInstanceIncidentsData, **kwargs: Any) -> SearchProcessInstanceIncidentsResponse200:
        """Search related incidents

 Search for incidents caused by the process instance or any of its called process or decision
instances.

Although the `processInstanceKey` is provided as a path parameter to indicate the root process
instance,
you may also include a `processInstanceKey` within the filter object to narrow results to specific
child process instances. This is useful, for example, if you want to isolate incidents associated
with
subprocesses or called processes under the root instance while excluding incidents directly tied to
the root.

Args:
    process_instance_key (str): System-generated key for a process instance. Example:
        2251799813690746.
    body (SearchProcessInstanceIncidentsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchProcessInstanceIncidentsResponse200 | SearchProcessInstanceIncidentsResponse400 | SearchProcessInstanceIncidentsResponse401 | SearchProcessInstanceIncidentsResponse403 | SearchProcessInstanceIncidentsResponse404 | SearchProcessInstanceIncidentsResponse500]"""
        from .api.process_instance.search_process_instance_incidents import sync as search_process_instance_incidents_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_process_instance_incidents_sync(**_kwargs)


    async def search_process_instance_incidents_async(self, process_instance_key: str, *, data: SearchProcessInstanceIncidentsData, **kwargs: Any) -> SearchProcessInstanceIncidentsResponse200:
        """Search related incidents

 Search for incidents caused by the process instance or any of its called process or decision
instances.

Although the `processInstanceKey` is provided as a path parameter to indicate the root process
instance,
you may also include a `processInstanceKey` within the filter object to narrow results to specific
child process instances. This is useful, for example, if you want to isolate incidents associated
with
subprocesses or called processes under the root instance while excluding incidents directly tied to
the root.

Args:
    process_instance_key (str): System-generated key for a process instance. Example:
        2251799813690746.
    body (SearchProcessInstanceIncidentsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchProcessInstanceIncidentsResponse200 | SearchProcessInstanceIncidentsResponse400 | SearchProcessInstanceIncidentsResponse401 | SearchProcessInstanceIncidentsResponse403 | SearchProcessInstanceIncidentsResponse404 | SearchProcessInstanceIncidentsResponse500]"""
        from .api.process_instance.search_process_instance_incidents import asyncio as search_process_instance_incidents_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_process_instance_incidents_asyncio(**_kwargs)


    def get_process_instance_statistics(self, process_instance_key: str, **kwargs: Any) -> GetProcessInstanceStatisticsResponse200:
        """Get element instance statistics

 Get statistics about elements by the process instance key.

Args:
    process_instance_key (str): System-generated key for a process instance. Example:
        2251799813690746.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetProcessInstanceStatisticsResponse200 | GetProcessInstanceStatisticsResponse400 | GetProcessInstanceStatisticsResponse401 | GetProcessInstanceStatisticsResponse403 | GetProcessInstanceStatisticsResponse500]"""
        from .api.process_instance.get_process_instance_statistics import sync as get_process_instance_statistics_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_process_instance_statistics_sync(**_kwargs)


    async def get_process_instance_statistics_async(self, process_instance_key: str, **kwargs: Any) -> GetProcessInstanceStatisticsResponse200:
        """Get element instance statistics

 Get statistics about elements by the process instance key.

Args:
    process_instance_key (str): System-generated key for a process instance. Example:
        2251799813690746.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetProcessInstanceStatisticsResponse200 | GetProcessInstanceStatisticsResponse400 | GetProcessInstanceStatisticsResponse401 | GetProcessInstanceStatisticsResponse403 | GetProcessInstanceStatisticsResponse500]"""
        from .api.process_instance.get_process_instance_statistics import asyncio as get_process_instance_statistics_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_process_instance_statistics_asyncio(**_kwargs)


    def search_process_instances(self, *, data: SearchProcessInstancesData, **kwargs: Any) -> SearchProcessInstancesResponse200:
        """Search process instances

 Search for process instances based on given criteria.

Args:
    body (SearchProcessInstancesData): Process instance search request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchProcessInstancesResponse200 | SearchProcessInstancesResponse400 | SearchProcessInstancesResponse401 | SearchProcessInstancesResponse403 | SearchProcessInstancesResponse500]"""
        from .api.process_instance.search_process_instances import sync as search_process_instances_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_process_instances_sync(**_kwargs)


    async def search_process_instances_async(self, *, data: SearchProcessInstancesData, **kwargs: Any) -> SearchProcessInstancesResponse200:
        """Search process instances

 Search for process instances based on given criteria.

Args:
    body (SearchProcessInstancesData): Process instance search request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchProcessInstancesResponse200 | SearchProcessInstancesResponse400 | SearchProcessInstancesResponse401 | SearchProcessInstancesResponse403 | SearchProcessInstancesResponse500]"""
        from .api.process_instance.search_process_instances import asyncio as search_process_instances_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_process_instances_asyncio(**_kwargs)


    def cancel_process_instances_batch_operation(self, *, data: CancelProcessInstancesBatchOperationData, **kwargs: Any) -> CancelProcessInstancesBatchOperationResponse200:
        """Cancel process instances (batch)

 Cancels multiple running process instances.
Since only ACTIVE root instances can be cancelled, any given filters for state and
parentProcessInstanceKey are ignored and overridden during this batch operation.
This is done asynchronously, the progress can be tracked using the batchOperationKey from the
response and the batch operation status endpoint (/batch-operations/{batchOperationKey}).

Args:
    body (CancelProcessInstancesBatchOperationData): The process instance filter that defines
        which process instances should be canceled.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CancelProcessInstancesBatchOperationResponse200 | CancelProcessInstancesBatchOperationResponse400 | CancelProcessInstancesBatchOperationResponse401 | CancelProcessInstancesBatchOperationResponse403 | CancelProcessInstancesBatchOperationResponse500]"""
        from .api.process_instance.cancel_process_instances_batch_operation import sync as cancel_process_instances_batch_operation_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return cancel_process_instances_batch_operation_sync(**_kwargs)


    async def cancel_process_instances_batch_operation_async(self, *, data: CancelProcessInstancesBatchOperationData, **kwargs: Any) -> CancelProcessInstancesBatchOperationResponse200:
        """Cancel process instances (batch)

 Cancels multiple running process instances.
Since only ACTIVE root instances can be cancelled, any given filters for state and
parentProcessInstanceKey are ignored and overridden during this batch operation.
This is done asynchronously, the progress can be tracked using the batchOperationKey from the
response and the batch operation status endpoint (/batch-operations/{batchOperationKey}).

Args:
    body (CancelProcessInstancesBatchOperationData): The process instance filter that defines
        which process instances should be canceled.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CancelProcessInstancesBatchOperationResponse200 | CancelProcessInstancesBatchOperationResponse400 | CancelProcessInstancesBatchOperationResponse401 | CancelProcessInstancesBatchOperationResponse403 | CancelProcessInstancesBatchOperationResponse500]"""
        from .api.process_instance.cancel_process_instances_batch_operation import asyncio as cancel_process_instances_batch_operation_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await cancel_process_instances_batch_operation_asyncio(**_kwargs)


    def get_process_instance(self, process_instance_key: str, **kwargs: Any) -> GetProcessInstanceResponse200:
        """Get process instance

 Get the process instance by the process instance key.

Args:
    process_instance_key (str): System-generated key for a process instance. Example:
        2251799813690746.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetProcessInstanceResponse200 | GetProcessInstanceResponse400 | GetProcessInstanceResponse401 | GetProcessInstanceResponse403 | GetProcessInstanceResponse404 | GetProcessInstanceResponse500]"""
        from .api.process_instance.get_process_instance import sync as get_process_instance_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_process_instance_sync(**_kwargs)


    async def get_process_instance_async(self, process_instance_key: str, **kwargs: Any) -> GetProcessInstanceResponse200:
        """Get process instance

 Get the process instance by the process instance key.

Args:
    process_instance_key (str): System-generated key for a process instance. Example:
        2251799813690746.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetProcessInstanceResponse200 | GetProcessInstanceResponse400 | GetProcessInstanceResponse401 | GetProcessInstanceResponse403 | GetProcessInstanceResponse404 | GetProcessInstanceResponse500]"""
        from .api.process_instance.get_process_instance import asyncio as get_process_instance_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_process_instance_asyncio(**_kwargs)


    def get_process_instance_call_hierarchy(self, process_instance_key: str, **kwargs: Any) -> GetProcessInstanceCallHierarchyResponse400:
        """Get call hierarchy

 Returns the call hierarchy for a given process instance, showing its ancestry up to the root
instance.

Args:
    process_instance_key (str): System-generated key for a process instance. Example:
        2251799813690746.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetProcessInstanceCallHierarchyResponse400 | GetProcessInstanceCallHierarchyResponse401 | GetProcessInstanceCallHierarchyResponse403 | GetProcessInstanceCallHierarchyResponse404 | GetProcessInstanceCallHierarchyResponse500 | list[GetProcessInstanceCallHierarchyResponse200Item]]"""
        from .api.process_instance.get_process_instance_call_hierarchy import sync as get_process_instance_call_hierarchy_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_process_instance_call_hierarchy_sync(**_kwargs)


    async def get_process_instance_call_hierarchy_async(self, process_instance_key: str, **kwargs: Any) -> GetProcessInstanceCallHierarchyResponse400:
        """Get call hierarchy

 Returns the call hierarchy for a given process instance, showing its ancestry up to the root
instance.

Args:
    process_instance_key (str): System-generated key for a process instance. Example:
        2251799813690746.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetProcessInstanceCallHierarchyResponse400 | GetProcessInstanceCallHierarchyResponse401 | GetProcessInstanceCallHierarchyResponse403 | GetProcessInstanceCallHierarchyResponse404 | GetProcessInstanceCallHierarchyResponse500 | list[GetProcessInstanceCallHierarchyResponse200Item]]"""
        from .api.process_instance.get_process_instance_call_hierarchy import asyncio as get_process_instance_call_hierarchy_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_process_instance_call_hierarchy_asyncio(**_kwargs)


    def modify_process_instance(self, process_instance_key: str, *, data: ModifyProcessInstanceData, **kwargs: Any) -> Any:
        """Modify process instance

 Modifies a running process instance.
This request can contain multiple instructions to activate an element of the process or
to terminate an active instance of an element.

Use this to repair a process instance that is stuck on an element or took an unintended path.
For example, because an external system is not available or doesn't respond as expected.

Args:
    process_instance_key (str): System-generated key for a process instance. Example:
        2251799813690746.
    body (ModifyProcessInstanceData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | ModifyProcessInstanceResponse400 | ModifyProcessInstanceResponse404 | ModifyProcessInstanceResponse500 | ModifyProcessInstanceResponse503]"""
        from .api.process_instance.modify_process_instance import sync as modify_process_instance_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return modify_process_instance_sync(**_kwargs)


    async def modify_process_instance_async(self, process_instance_key: str, *, data: ModifyProcessInstanceData, **kwargs: Any) -> Any:
        """Modify process instance

 Modifies a running process instance.
This request can contain multiple instructions to activate an element of the process or
to terminate an active instance of an element.

Use this to repair a process instance that is stuck on an element or took an unintended path.
For example, because an external system is not available or doesn't respond as expected.

Args:
    process_instance_key (str): System-generated key for a process instance. Example:
        2251799813690746.
    body (ModifyProcessInstanceData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | ModifyProcessInstanceResponse400 | ModifyProcessInstanceResponse404 | ModifyProcessInstanceResponse500 | ModifyProcessInstanceResponse503]"""
        from .api.process_instance.modify_process_instance import asyncio as modify_process_instance_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await modify_process_instance_asyncio(**_kwargs)


    def get_authentication(self, **kwargs: Any) -> GetAuthenticationResponse200:
        """Get current user

 Retrieves the current authenticated user.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetAuthenticationResponse200 | GetAuthenticationResponse401 | GetAuthenticationResponse403 | GetAuthenticationResponse500]"""
        from .api.authentication.get_authentication import sync as get_authentication_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_authentication_sync(**_kwargs)


    async def get_authentication_async(self, **kwargs: Any) -> GetAuthenticationResponse200:
        """Get current user

 Retrieves the current authenticated user.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetAuthenticationResponse200 | GetAuthenticationResponse401 | GetAuthenticationResponse403 | GetAuthenticationResponse500]"""
        from .api.authentication.get_authentication import asyncio as get_authentication_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_authentication_asyncio(**_kwargs)


    def assign_group_to_tenant(self, tenant_id: str, group_id: str, **kwargs: Any) -> Any:
        """Assign a group to a tenant

 Assigns a group to a specified tenant.
Group members (users, clients) can then access tenant data and perform authorized actions.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    group_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignGroupToTenantResponse400 | AssignGroupToTenantResponse403 | AssignGroupToTenantResponse404 | AssignGroupToTenantResponse500 | AssignGroupToTenantResponse503]"""
        from .api.tenant.assign_group_to_tenant import sync as assign_group_to_tenant_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return assign_group_to_tenant_sync(**_kwargs)


    async def assign_group_to_tenant_async(self, tenant_id: str, group_id: str, **kwargs: Any) -> Any:
        """Assign a group to a tenant

 Assigns a group to a specified tenant.
Group members (users, clients) can then access tenant data and perform authorized actions.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    group_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignGroupToTenantResponse400 | AssignGroupToTenantResponse403 | AssignGroupToTenantResponse404 | AssignGroupToTenantResponse500 | AssignGroupToTenantResponse503]"""
        from .api.tenant.assign_group_to_tenant import asyncio as assign_group_to_tenant_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await assign_group_to_tenant_asyncio(**_kwargs)


    def search_group_ids_for_tenant(self, tenant_id: str, *, data: SearchGroupIdsForTenantData, **kwargs: Any) -> SearchGroupIdsForTenantResponse200:
        """Search groups for tenant

 Retrieves a filtered and sorted list of groups for a specified tenant.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    body (SearchGroupIdsForTenantData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchGroupIdsForTenantResponse200]"""
        from .api.tenant.search_group_ids_for_tenant import sync as search_group_ids_for_tenant_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_group_ids_for_tenant_sync(**_kwargs)


    async def search_group_ids_for_tenant_async(self, tenant_id: str, *, data: SearchGroupIdsForTenantData, **kwargs: Any) -> SearchGroupIdsForTenantResponse200:
        """Search groups for tenant

 Retrieves a filtered and sorted list of groups for a specified tenant.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    body (SearchGroupIdsForTenantData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchGroupIdsForTenantResponse200]"""
        from .api.tenant.search_group_ids_for_tenant import asyncio as search_group_ids_for_tenant_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_group_ids_for_tenant_asyncio(**_kwargs)


    def unassign_client_from_tenant(self, tenant_id: str, client_id: str, **kwargs: Any) -> Any:
        """Unassign a client from a tenant

 Unassigns the client from the specified tenant.
The client can no longer access tenant data.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    client_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignClientFromTenantResponse400 | UnassignClientFromTenantResponse403 | UnassignClientFromTenantResponse404 | UnassignClientFromTenantResponse500 | UnassignClientFromTenantResponse503]"""
        from .api.tenant.unassign_client_from_tenant import sync as unassign_client_from_tenant_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return unassign_client_from_tenant_sync(**_kwargs)


    async def unassign_client_from_tenant_async(self, tenant_id: str, client_id: str, **kwargs: Any) -> Any:
        """Unassign a client from a tenant

 Unassigns the client from the specified tenant.
The client can no longer access tenant data.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    client_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignClientFromTenantResponse400 | UnassignClientFromTenantResponse403 | UnassignClientFromTenantResponse404 | UnassignClientFromTenantResponse500 | UnassignClientFromTenantResponse503]"""
        from .api.tenant.unassign_client_from_tenant import asyncio as unassign_client_from_tenant_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await unassign_client_from_tenant_asyncio(**_kwargs)


    def get_tenant(self, tenant_id: str, **kwargs: Any) -> GetTenantResponse200:
        """Get tenant

 Retrieves a single tenant by tenant ID.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetTenantResponse200 | GetTenantResponse400 | GetTenantResponse401 | GetTenantResponse403 | GetTenantResponse404 | GetTenantResponse500]"""
        from .api.tenant.get_tenant import sync as get_tenant_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_tenant_sync(**_kwargs)


    async def get_tenant_async(self, tenant_id: str, **kwargs: Any) -> GetTenantResponse200:
        """Get tenant

 Retrieves a single tenant by tenant ID.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetTenantResponse200 | GetTenantResponse400 | GetTenantResponse401 | GetTenantResponse403 | GetTenantResponse404 | GetTenantResponse500]"""
        from .api.tenant.get_tenant import asyncio as get_tenant_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_tenant_asyncio(**_kwargs)


    def assign_mapping_rule_to_tenant(self, tenant_id: str, mapping_rule_id: str, **kwargs: Any) -> Any:
        """Assign a mapping rule to a tenant

 Assign a single mapping rule to a specified tenant.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    mapping_rule_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignMappingRuleToTenantResponse400 | AssignMappingRuleToTenantResponse403 | AssignMappingRuleToTenantResponse404 | AssignMappingRuleToTenantResponse500 | AssignMappingRuleToTenantResponse503]"""
        from .api.tenant.assign_mapping_rule_to_tenant import sync as assign_mapping_rule_to_tenant_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return assign_mapping_rule_to_tenant_sync(**_kwargs)


    async def assign_mapping_rule_to_tenant_async(self, tenant_id: str, mapping_rule_id: str, **kwargs: Any) -> Any:
        """Assign a mapping rule to a tenant

 Assign a single mapping rule to a specified tenant.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    mapping_rule_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignMappingRuleToTenantResponse400 | AssignMappingRuleToTenantResponse403 | AssignMappingRuleToTenantResponse404 | AssignMappingRuleToTenantResponse500 | AssignMappingRuleToTenantResponse503]"""
        from .api.tenant.assign_mapping_rule_to_tenant import asyncio as assign_mapping_rule_to_tenant_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await assign_mapping_rule_to_tenant_asyncio(**_kwargs)


    def search_tenants(self, *, data: SearchTenantsData, **kwargs: Any) -> Any:
        """Search tenants

 Retrieves a filtered and sorted list of tenants.

Args:
    body (SearchTenantsData): Tenant search request

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | SearchTenantsResponse200 | SearchTenantsResponse400 | SearchTenantsResponse401 | SearchTenantsResponse403 | SearchTenantsResponse500]"""
        from .api.tenant.search_tenants import sync as search_tenants_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_tenants_sync(**_kwargs)


    async def search_tenants_async(self, *, data: SearchTenantsData, **kwargs: Any) -> Any:
        """Search tenants

 Retrieves a filtered and sorted list of tenants.

Args:
    body (SearchTenantsData): Tenant search request

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | SearchTenantsResponse200 | SearchTenantsResponse400 | SearchTenantsResponse401 | SearchTenantsResponse403 | SearchTenantsResponse500]"""
        from .api.tenant.search_tenants import asyncio as search_tenants_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_tenants_asyncio(**_kwargs)


    def delete_tenant(self, tenant_id: str, **kwargs: Any) -> Any:
        """Delete tenant

 Deletes an existing tenant.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteTenantResponse400 | DeleteTenantResponse403 | DeleteTenantResponse404 | DeleteTenantResponse500 | DeleteTenantResponse503]"""
        from .api.tenant.delete_tenant import sync as delete_tenant_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return delete_tenant_sync(**_kwargs)


    async def delete_tenant_async(self, tenant_id: str, **kwargs: Any) -> Any:
        """Delete tenant

 Deletes an existing tenant.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteTenantResponse400 | DeleteTenantResponse403 | DeleteTenantResponse404 | DeleteTenantResponse500 | DeleteTenantResponse503]"""
        from .api.tenant.delete_tenant import asyncio as delete_tenant_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await delete_tenant_asyncio(**_kwargs)


    def assign_client_to_tenant(self, tenant_id: str, client_id: str, **kwargs: Any) -> Any:
        """Assign a client to a tenant

 Assign the client to the specified tenant.
The client can then access tenant data and perform authorized actions.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    client_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignClientToTenantResponse400 | AssignClientToTenantResponse403 | AssignClientToTenantResponse404 | AssignClientToTenantResponse500 | AssignClientToTenantResponse503]"""
        from .api.tenant.assign_client_to_tenant import sync as assign_client_to_tenant_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return assign_client_to_tenant_sync(**_kwargs)


    async def assign_client_to_tenant_async(self, tenant_id: str, client_id: str, **kwargs: Any) -> Any:
        """Assign a client to a tenant

 Assign the client to the specified tenant.
The client can then access tenant data and perform authorized actions.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    client_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignClientToTenantResponse400 | AssignClientToTenantResponse403 | AssignClientToTenantResponse404 | AssignClientToTenantResponse500 | AssignClientToTenantResponse503]"""
        from .api.tenant.assign_client_to_tenant import asyncio as assign_client_to_tenant_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await assign_client_to_tenant_asyncio(**_kwargs)


    def search_roles_for_tenant(self, tenant_id: str, *, data: SearchRolesForTenantData, **kwargs: Any) -> SearchRolesForTenantResponse200:
        """Search roles for tenant

 Retrieves a filtered and sorted list of roles for a specified tenant.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    body (SearchRolesForTenantData): Role search request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchRolesForTenantResponse200]"""
        from .api.tenant.search_roles_for_tenant import sync as search_roles_for_tenant_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_roles_for_tenant_sync(**_kwargs)


    async def search_roles_for_tenant_async(self, tenant_id: str, *, data: SearchRolesForTenantData, **kwargs: Any) -> SearchRolesForTenantResponse200:
        """Search roles for tenant

 Retrieves a filtered and sorted list of roles for a specified tenant.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    body (SearchRolesForTenantData): Role search request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchRolesForTenantResponse200]"""
        from .api.tenant.search_roles_for_tenant import asyncio as search_roles_for_tenant_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_roles_for_tenant_asyncio(**_kwargs)


    def unassign_role_from_tenant(self, tenant_id: str, role_id: str, **kwargs: Any) -> Any:
        """Unassign a role from a tenant

 Unassigns a role from a specified tenant.
Users, Clients or Groups, that have the role assigned, will no longer have access to the
tenant's data - unless they are assigned directly to the tenant.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    role_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignRoleFromTenantResponse400 | UnassignRoleFromTenantResponse403 | UnassignRoleFromTenantResponse404 | UnassignRoleFromTenantResponse500 | UnassignRoleFromTenantResponse503]"""
        from .api.tenant.unassign_role_from_tenant import sync as unassign_role_from_tenant_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return unassign_role_from_tenant_sync(**_kwargs)


    async def unassign_role_from_tenant_async(self, tenant_id: str, role_id: str, **kwargs: Any) -> Any:
        """Unassign a role from a tenant

 Unassigns a role from a specified tenant.
Users, Clients or Groups, that have the role assigned, will no longer have access to the
tenant's data - unless they are assigned directly to the tenant.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    role_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignRoleFromTenantResponse400 | UnassignRoleFromTenantResponse403 | UnassignRoleFromTenantResponse404 | UnassignRoleFromTenantResponse500 | UnassignRoleFromTenantResponse503]"""
        from .api.tenant.unassign_role_from_tenant import asyncio as unassign_role_from_tenant_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await unassign_role_from_tenant_asyncio(**_kwargs)


    def unassign_mapping_rule_from_tenant(self, tenant_id: str, mapping_rule_id: str, **kwargs: Any) -> Any:
        """Unassign a mapping rule from a tenant

 Unassigns a single mapping rule from a specified tenant without deleting the rule.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    mapping_rule_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignMappingRuleFromTenantResponse400 | UnassignMappingRuleFromTenantResponse403 | UnassignMappingRuleFromTenantResponse404 | UnassignMappingRuleFromTenantResponse500 | UnassignMappingRuleFromTenantResponse503]"""
        from .api.tenant.unassign_mapping_rule_from_tenant import sync as unassign_mapping_rule_from_tenant_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return unassign_mapping_rule_from_tenant_sync(**_kwargs)


    async def unassign_mapping_rule_from_tenant_async(self, tenant_id: str, mapping_rule_id: str, **kwargs: Any) -> Any:
        """Unassign a mapping rule from a tenant

 Unassigns a single mapping rule from a specified tenant without deleting the rule.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    mapping_rule_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignMappingRuleFromTenantResponse400 | UnassignMappingRuleFromTenantResponse403 | UnassignMappingRuleFromTenantResponse404 | UnassignMappingRuleFromTenantResponse500 | UnassignMappingRuleFromTenantResponse503]"""
        from .api.tenant.unassign_mapping_rule_from_tenant import asyncio as unassign_mapping_rule_from_tenant_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await unassign_mapping_rule_from_tenant_asyncio(**_kwargs)


    def search_users_for_tenant(self, tenant_id: str, *, data: SearchUsersForTenantData, **kwargs: Any) -> SearchUsersForTenantResponse200:
        """Search users for tenant

 Retrieves a filtered and sorted list of users for a specified tenant.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    body (SearchUsersForTenantData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchUsersForTenantResponse200]"""
        from .api.tenant.search_users_for_tenant import sync as search_users_for_tenant_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_users_for_tenant_sync(**_kwargs)


    async def search_users_for_tenant_async(self, tenant_id: str, *, data: SearchUsersForTenantData, **kwargs: Any) -> SearchUsersForTenantResponse200:
        """Search users for tenant

 Retrieves a filtered and sorted list of users for a specified tenant.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    body (SearchUsersForTenantData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchUsersForTenantResponse200]"""
        from .api.tenant.search_users_for_tenant import asyncio as search_users_for_tenant_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_users_for_tenant_asyncio(**_kwargs)


    def assign_user_to_tenant(self, tenant_id: str, username: str, **kwargs: Any) -> Any:
        """Assign a user to a tenant

 Assign a single user to a specified tenant. The user can then access tenant data and perform
authorized actions.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    username (str): The unique name of a user. Example: swillis.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignUserToTenantResponse400 | AssignUserToTenantResponse403 | AssignUserToTenantResponse404 | AssignUserToTenantResponse500 | AssignUserToTenantResponse503]"""
        from .api.tenant.assign_user_to_tenant import sync as assign_user_to_tenant_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return assign_user_to_tenant_sync(**_kwargs)


    async def assign_user_to_tenant_async(self, tenant_id: str, username: str, **kwargs: Any) -> Any:
        """Assign a user to a tenant

 Assign a single user to a specified tenant. The user can then access tenant data and perform
authorized actions.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    username (str): The unique name of a user. Example: swillis.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignUserToTenantResponse400 | AssignUserToTenantResponse403 | AssignUserToTenantResponse404 | AssignUserToTenantResponse500 | AssignUserToTenantResponse503]"""
        from .api.tenant.assign_user_to_tenant import asyncio as assign_user_to_tenant_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await assign_user_to_tenant_asyncio(**_kwargs)


    def assign_role_to_tenant(self, tenant_id: str, role_id: str, **kwargs: Any) -> Any:
        """Assign a role to a tenant

 Assigns a role to a specified tenant.
Users, Clients or Groups, that have the role assigned, will get access to the tenant's data and can
perform actions according to their authorizations.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    role_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignRoleToTenantResponse400 | AssignRoleToTenantResponse403 | AssignRoleToTenantResponse404 | AssignRoleToTenantResponse500 | AssignRoleToTenantResponse503]"""
        from .api.tenant.assign_role_to_tenant import sync as assign_role_to_tenant_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return assign_role_to_tenant_sync(**_kwargs)


    async def assign_role_to_tenant_async(self, tenant_id: str, role_id: str, **kwargs: Any) -> Any:
        """Assign a role to a tenant

 Assigns a role to a specified tenant.
Users, Clients or Groups, that have the role assigned, will get access to the tenant's data and can
perform actions according to their authorizations.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    role_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignRoleToTenantResponse400 | AssignRoleToTenantResponse403 | AssignRoleToTenantResponse404 | AssignRoleToTenantResponse500 | AssignRoleToTenantResponse503]"""
        from .api.tenant.assign_role_to_tenant import asyncio as assign_role_to_tenant_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await assign_role_to_tenant_asyncio(**_kwargs)


    def create_tenant(self, *, data: CreateTenantData, **kwargs: Any) -> Any:
        """Create tenant

 Creates a new tenant.

Args:
    body (CreateTenantData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | CreateTenantResponse201 | CreateTenantResponse400 | CreateTenantResponse403 | CreateTenantResponse404 | CreateTenantResponse500 | CreateTenantResponse503]"""
        from .api.tenant.create_tenant import sync as create_tenant_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return create_tenant_sync(**_kwargs)


    async def create_tenant_async(self, *, data: CreateTenantData, **kwargs: Any) -> Any:
        """Create tenant

 Creates a new tenant.

Args:
    body (CreateTenantData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | CreateTenantResponse201 | CreateTenantResponse400 | CreateTenantResponse403 | CreateTenantResponse404 | CreateTenantResponse500 | CreateTenantResponse503]"""
        from .api.tenant.create_tenant import asyncio as create_tenant_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await create_tenant_asyncio(**_kwargs)


    def unassign_group_from_tenant(self, tenant_id: str, group_id: str, **kwargs: Any) -> Any:
        """Unassign a group from a tenant

 Unassigns a group from a specified tenant.
Members of the group (users, clients) will no longer have access to the tenant's data - except they
are assigned directly to the tenant.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    group_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignGroupFromTenantResponse400 | UnassignGroupFromTenantResponse403 | UnassignGroupFromTenantResponse404 | UnassignGroupFromTenantResponse500 | UnassignGroupFromTenantResponse503]"""
        from .api.tenant.unassign_group_from_tenant import sync as unassign_group_from_tenant_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return unassign_group_from_tenant_sync(**_kwargs)


    async def unassign_group_from_tenant_async(self, tenant_id: str, group_id: str, **kwargs: Any) -> Any:
        """Unassign a group from a tenant

 Unassigns a group from a specified tenant.
Members of the group (users, clients) will no longer have access to the tenant's data - except they
are assigned directly to the tenant.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    group_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignGroupFromTenantResponse400 | UnassignGroupFromTenantResponse403 | UnassignGroupFromTenantResponse404 | UnassignGroupFromTenantResponse500 | UnassignGroupFromTenantResponse503]"""
        from .api.tenant.unassign_group_from_tenant import asyncio as unassign_group_from_tenant_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await unassign_group_from_tenant_asyncio(**_kwargs)


    def search_clients_for_tenant(self, tenant_id: str, *, data: SearchClientsForTenantData, **kwargs: Any) -> SearchClientsForTenantResponse200:
        """Search clients for tenant

 Retrieves a filtered and sorted list of clients for a specified tenant.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    body (SearchClientsForTenantData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchClientsForTenantResponse200]"""
        from .api.tenant.search_clients_for_tenant import sync as search_clients_for_tenant_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_clients_for_tenant_sync(**_kwargs)


    async def search_clients_for_tenant_async(self, tenant_id: str, *, data: SearchClientsForTenantData, **kwargs: Any) -> SearchClientsForTenantResponse200:
        """Search clients for tenant

 Retrieves a filtered and sorted list of clients for a specified tenant.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    body (SearchClientsForTenantData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchClientsForTenantResponse200]"""
        from .api.tenant.search_clients_for_tenant import asyncio as search_clients_for_tenant_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_clients_for_tenant_asyncio(**_kwargs)


    def unassign_user_from_tenant(self, tenant_id: str, username: str, **kwargs: Any) -> Any:
        """Unassign a user from a tenant

 Unassigns the user from the specified tenant.
The user can no longer access tenant data.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    username (str): The unique name of a user. Example: swillis.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignUserFromTenantResponse400 | UnassignUserFromTenantResponse403 | UnassignUserFromTenantResponse404 | UnassignUserFromTenantResponse500 | UnassignUserFromTenantResponse503]"""
        from .api.tenant.unassign_user_from_tenant import sync as unassign_user_from_tenant_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return unassign_user_from_tenant_sync(**_kwargs)


    async def unassign_user_from_tenant_async(self, tenant_id: str, username: str, **kwargs: Any) -> Any:
        """Unassign a user from a tenant

 Unassigns the user from the specified tenant.
The user can no longer access tenant data.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    username (str): The unique name of a user. Example: swillis.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignUserFromTenantResponse400 | UnassignUserFromTenantResponse403 | UnassignUserFromTenantResponse404 | UnassignUserFromTenantResponse500 | UnassignUserFromTenantResponse503]"""
        from .api.tenant.unassign_user_from_tenant import asyncio as unassign_user_from_tenant_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await unassign_user_from_tenant_asyncio(**_kwargs)


    def update_tenant(self, tenant_id: str, *, data: UpdateTenantData, **kwargs: Any) -> UpdateTenantResponse200:
        """Update tenant

 Updates an existing tenant.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    body (UpdateTenantData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[UpdateTenantResponse200 | UpdateTenantResponse400 | UpdateTenantResponse403 | UpdateTenantResponse404 | UpdateTenantResponse500 | UpdateTenantResponse503]"""
        from .api.tenant.update_tenant import sync as update_tenant_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return update_tenant_sync(**_kwargs)


    async def update_tenant_async(self, tenant_id: str, *, data: UpdateTenantData, **kwargs: Any) -> UpdateTenantResponse200:
        """Update tenant

 Updates an existing tenant.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    body (UpdateTenantData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[UpdateTenantResponse200 | UpdateTenantResponse400 | UpdateTenantResponse403 | UpdateTenantResponse404 | UpdateTenantResponse500 | UpdateTenantResponse503]"""
        from .api.tenant.update_tenant import asyncio as update_tenant_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await update_tenant_asyncio(**_kwargs)


    def search_mapping_rules_for_tenant(self, tenant_id: str, *, data: SearchMappingRulesForTenantData, **kwargs: Any) -> SearchMappingRulesForTenantResponse200:
        """Search mapping rules for tenant

 Retrieves a filtered and sorted list of MappingRules for a specified tenant.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    body (SearchMappingRulesForTenantData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchMappingRulesForTenantResponse200]"""
        from .api.tenant.search_mapping_rules_for_tenant import sync as search_mapping_rules_for_tenant_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_mapping_rules_for_tenant_sync(**_kwargs)


    async def search_mapping_rules_for_tenant_async(self, tenant_id: str, *, data: SearchMappingRulesForTenantData, **kwargs: Any) -> SearchMappingRulesForTenantResponse200:
        """Search mapping rules for tenant

 Retrieves a filtered and sorted list of MappingRules for a specified tenant.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    body (SearchMappingRulesForTenantData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchMappingRulesForTenantResponse200]"""
        from .api.tenant.search_mapping_rules_for_tenant import asyncio as search_mapping_rules_for_tenant_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_mapping_rules_for_tenant_asyncio(**_kwargs)


    def get_global_cluster_variable(self, name: str, **kwargs: Any) -> GetGlobalClusterVariableResponse200:
        """Get a global-scoped cluster variable

Args:
    name (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetGlobalClusterVariableResponse200 | GetGlobalClusterVariableResponse400 | GetGlobalClusterVariableResponse401 | GetGlobalClusterVariableResponse403 | GetGlobalClusterVariableResponse404 | GetGlobalClusterVariableResponse500]"""
        from .api.cluster_variable.get_global_cluster_variable import sync as get_global_cluster_variable_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_global_cluster_variable_sync(**_kwargs)


    async def get_global_cluster_variable_async(self, name: str, **kwargs: Any) -> GetGlobalClusterVariableResponse200:
        """Get a global-scoped cluster variable

Args:
    name (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetGlobalClusterVariableResponse200 | GetGlobalClusterVariableResponse400 | GetGlobalClusterVariableResponse401 | GetGlobalClusterVariableResponse403 | GetGlobalClusterVariableResponse404 | GetGlobalClusterVariableResponse500]"""
        from .api.cluster_variable.get_global_cluster_variable import asyncio as get_global_cluster_variable_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_global_cluster_variable_asyncio(**_kwargs)


    def delete_global_cluster_variable(self, name: str, **kwargs: Any) -> Any:
        """Delete a global-scoped cluster variable

Args:
    name (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteGlobalClusterVariableResponse400 | DeleteGlobalClusterVariableResponse401 | DeleteGlobalClusterVariableResponse403 | DeleteGlobalClusterVariableResponse404 | DeleteGlobalClusterVariableResponse500]"""
        from .api.cluster_variable.delete_global_cluster_variable import sync as delete_global_cluster_variable_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return delete_global_cluster_variable_sync(**_kwargs)


    async def delete_global_cluster_variable_async(self, name: str, **kwargs: Any) -> Any:
        """Delete a global-scoped cluster variable

Args:
    name (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteGlobalClusterVariableResponse400 | DeleteGlobalClusterVariableResponse401 | DeleteGlobalClusterVariableResponse403 | DeleteGlobalClusterVariableResponse404 | DeleteGlobalClusterVariableResponse500]"""
        from .api.cluster_variable.delete_global_cluster_variable import asyncio as delete_global_cluster_variable_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await delete_global_cluster_variable_asyncio(**_kwargs)


    def get_tenant_cluster_variable(self, tenant_id: str, name: str, **kwargs: Any) -> GetTenantClusterVariableResponse200:
        """Get a tenant-scoped cluster variable

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    name (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetTenantClusterVariableResponse200 | GetTenantClusterVariableResponse400 | GetTenantClusterVariableResponse401 | GetTenantClusterVariableResponse403 | GetTenantClusterVariableResponse404 | GetTenantClusterVariableResponse500]"""
        from .api.cluster_variable.get_tenant_cluster_variable import sync as get_tenant_cluster_variable_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_tenant_cluster_variable_sync(**_kwargs)


    async def get_tenant_cluster_variable_async(self, tenant_id: str, name: str, **kwargs: Any) -> GetTenantClusterVariableResponse200:
        """Get a tenant-scoped cluster variable

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    name (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetTenantClusterVariableResponse200 | GetTenantClusterVariableResponse400 | GetTenantClusterVariableResponse401 | GetTenantClusterVariableResponse403 | GetTenantClusterVariableResponse404 | GetTenantClusterVariableResponse500]"""
        from .api.cluster_variable.get_tenant_cluster_variable import asyncio as get_tenant_cluster_variable_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_tenant_cluster_variable_asyncio(**_kwargs)


    def create_tenant_cluster_variable(self, tenant_id: str, *, data: CreateTenantClusterVariableData, **kwargs: Any) -> CreateTenantClusterVariableResponse200:
        """Create a tenant-scoped cluster variable

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    body (CreateTenantClusterVariableData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateTenantClusterVariableResponse200 | CreateTenantClusterVariableResponse400 | CreateTenantClusterVariableResponse401 | CreateTenantClusterVariableResponse403 | CreateTenantClusterVariableResponse500]"""
        from .api.cluster_variable.create_tenant_cluster_variable import sync as create_tenant_cluster_variable_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return create_tenant_cluster_variable_sync(**_kwargs)


    async def create_tenant_cluster_variable_async(self, tenant_id: str, *, data: CreateTenantClusterVariableData, **kwargs: Any) -> CreateTenantClusterVariableResponse200:
        """Create a tenant-scoped cluster variable

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    body (CreateTenantClusterVariableData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateTenantClusterVariableResponse200 | CreateTenantClusterVariableResponse400 | CreateTenantClusterVariableResponse401 | CreateTenantClusterVariableResponse403 | CreateTenantClusterVariableResponse500]"""
        from .api.cluster_variable.create_tenant_cluster_variable import asyncio as create_tenant_cluster_variable_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await create_tenant_cluster_variable_asyncio(**_kwargs)


    def delete_tenant_cluster_variable(self, tenant_id: str, name: str, **kwargs: Any) -> Any:
        """Delete a tenant-scoped cluster variable

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    name (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteTenantClusterVariableResponse400 | DeleteTenantClusterVariableResponse401 | DeleteTenantClusterVariableResponse403 | DeleteTenantClusterVariableResponse404 | DeleteTenantClusterVariableResponse500]"""
        from .api.cluster_variable.delete_tenant_cluster_variable import sync as delete_tenant_cluster_variable_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return delete_tenant_cluster_variable_sync(**_kwargs)


    async def delete_tenant_cluster_variable_async(self, tenant_id: str, name: str, **kwargs: Any) -> Any:
        """Delete a tenant-scoped cluster variable

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    name (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteTenantClusterVariableResponse400 | DeleteTenantClusterVariableResponse401 | DeleteTenantClusterVariableResponse403 | DeleteTenantClusterVariableResponse404 | DeleteTenantClusterVariableResponse500]"""
        from .api.cluster_variable.delete_tenant_cluster_variable import asyncio as delete_tenant_cluster_variable_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await delete_tenant_cluster_variable_asyncio(**_kwargs)


    def search_cluster_variables(self, *, data: SearchClusterVariablesData, truncate_values: bool | Unset = UNSET, **kwargs: Any) -> SearchClusterVariablesResponse200:
        """Search for cluster variables based on given criteria. By default, long variable values in the
response are truncated.

Args:
    truncate_values (bool | Unset):
    body (SearchClusterVariablesData): Cluster variable search query request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchClusterVariablesResponse200 | SearchClusterVariablesResponse400 | SearchClusterVariablesResponse401 | SearchClusterVariablesResponse403 | SearchClusterVariablesResponse500]"""
        from .api.cluster_variable.search_cluster_variables import sync as search_cluster_variables_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_cluster_variables_sync(**_kwargs)


    async def search_cluster_variables_async(self, *, data: SearchClusterVariablesData, truncate_values: bool | Unset = UNSET, **kwargs: Any) -> SearchClusterVariablesResponse200:
        """Search for cluster variables based on given criteria. By default, long variable values in the
response are truncated.

Args:
    truncate_values (bool | Unset):
    body (SearchClusterVariablesData): Cluster variable search query request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchClusterVariablesResponse200 | SearchClusterVariablesResponse400 | SearchClusterVariablesResponse401 | SearchClusterVariablesResponse403 | SearchClusterVariablesResponse500]"""
        from .api.cluster_variable.search_cluster_variables import asyncio as search_cluster_variables_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_cluster_variables_asyncio(**_kwargs)


    def create_global_cluster_variable(self, *, data: CreateGlobalClusterVariableData, **kwargs: Any) -> CreateGlobalClusterVariableResponse200:
        """Create a global-scoped cluster variable

Args:
    body (CreateGlobalClusterVariableData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateGlobalClusterVariableResponse200 | CreateGlobalClusterVariableResponse400 | CreateGlobalClusterVariableResponse401 | CreateGlobalClusterVariableResponse403 | CreateGlobalClusterVariableResponse500]"""
        from .api.cluster_variable.create_global_cluster_variable import sync as create_global_cluster_variable_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return create_global_cluster_variable_sync(**_kwargs)


    async def create_global_cluster_variable_async(self, *, data: CreateGlobalClusterVariableData, **kwargs: Any) -> CreateGlobalClusterVariableResponse200:
        """Create a global-scoped cluster variable

Args:
    body (CreateGlobalClusterVariableData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateGlobalClusterVariableResponse200 | CreateGlobalClusterVariableResponse400 | CreateGlobalClusterVariableResponse401 | CreateGlobalClusterVariableResponse403 | CreateGlobalClusterVariableResponse500]"""
        from .api.cluster_variable.create_global_cluster_variable import asyncio as create_global_cluster_variable_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await create_global_cluster_variable_asyncio(**_kwargs)


    def get_document(self, document_id: str, *, store_id: str | Unset = UNSET, content_hash: str | Unset = UNSET, **kwargs: Any) -> File:
        """Download document

 Download a document from the Camunda 8 cluster.

Note that this is currently supported for document stores of type: AWS, GCP, in-memory (non-
production), local (non-production)

Args:
    document_id (str): Document Id that uniquely identifies a document.
    store_id (str | Unset):
    content_hash (str | Unset):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[File | GetDocumentResponse404 | GetDocumentResponse500]"""
        from .api.document.get_document import sync as get_document_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_document_sync(**_kwargs)


    async def get_document_async(self, document_id: str, *, store_id: str | Unset = UNSET, content_hash: str | Unset = UNSET, **kwargs: Any) -> File:
        """Download document

 Download a document from the Camunda 8 cluster.

Note that this is currently supported for document stores of type: AWS, GCP, in-memory (non-
production), local (non-production)

Args:
    document_id (str): Document Id that uniquely identifies a document.
    store_id (str | Unset):
    content_hash (str | Unset):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[File | GetDocumentResponse404 | GetDocumentResponse500]"""
        from .api.document.get_document import asyncio as get_document_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_document_asyncio(**_kwargs)


    def create_documents(self, *, data: CreateDocumentsData, store_id: str | Unset = UNSET, **kwargs: Any) -> CreateDocumentsResponse201:
        """Upload multiple documents

 Upload multiple documents to the Camunda 8 cluster.

The caller must provide a file name for each document, which will be used in case of a multi-status
response
to identify which documents failed to upload. The file name can be provided in the `Content-
Disposition` header
of the file part or in the `fileName` field of the metadata. You can add a parallel array of
metadata objects. These
are matched with the files based on index, and must have the same length as the files array.
To pass homogenous metadata for all files, spread the metadata over the metadata array.
A filename value provided explicitly via the metadata array in the request overrides the `Content-
Disposition` header
of the file part.

In case of a multi-status response, the response body will contain a list of
`DocumentBatchProblemDetail` objects,
each of which contains the file name of the document that failed to upload and the reason for the
failure.
The client can choose to retry the whole batch or individual documents based on the response.

Note that this is currently supported for document stores of type: AWS, GCP, in-memory (non-
production), local (non-production)

Args:
    store_id (str | Unset):
    body (CreateDocumentsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateDocumentsResponse201 | CreateDocumentsResponse207 | CreateDocumentsResponse400 | CreateDocumentsResponse415]"""
        from .api.document.create_documents import sync as create_documents_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return create_documents_sync(**_kwargs)


    async def create_documents_async(self, *, data: CreateDocumentsData, store_id: str | Unset = UNSET, **kwargs: Any) -> CreateDocumentsResponse201:
        """Upload multiple documents

 Upload multiple documents to the Camunda 8 cluster.

The caller must provide a file name for each document, which will be used in case of a multi-status
response
to identify which documents failed to upload. The file name can be provided in the `Content-
Disposition` header
of the file part or in the `fileName` field of the metadata. You can add a parallel array of
metadata objects. These
are matched with the files based on index, and must have the same length as the files array.
To pass homogenous metadata for all files, spread the metadata over the metadata array.
A filename value provided explicitly via the metadata array in the request overrides the `Content-
Disposition` header
of the file part.

In case of a multi-status response, the response body will contain a list of
`DocumentBatchProblemDetail` objects,
each of which contains the file name of the document that failed to upload and the reason for the
failure.
The client can choose to retry the whole batch or individual documents based on the response.

Note that this is currently supported for document stores of type: AWS, GCP, in-memory (non-
production), local (non-production)

Args:
    store_id (str | Unset):
    body (CreateDocumentsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateDocumentsResponse201 | CreateDocumentsResponse207 | CreateDocumentsResponse400 | CreateDocumentsResponse415]"""
        from .api.document.create_documents import asyncio as create_documents_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await create_documents_asyncio(**_kwargs)


    def create_document_link(self, document_id: str, *, data: CreateDocumentLinkData, store_id: str | Unset = UNSET, content_hash: str | Unset = UNSET, **kwargs: Any) -> CreateDocumentLinkResponse201:
        """Create document link

 Create a link to a document in the Camunda 8 cluster.

Note that this is currently supported for document stores of type: AWS, GCP

Args:
    document_id (str): Document Id that uniquely identifies a document.
    store_id (str | Unset):
    content_hash (str | Unset):
    body (CreateDocumentLinkData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateDocumentLinkResponse201 | CreateDocumentLinkResponse400]"""
        from .api.document.create_document_link import sync as create_document_link_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return create_document_link_sync(**_kwargs)


    async def create_document_link_async(self, document_id: str, *, data: CreateDocumentLinkData, store_id: str | Unset = UNSET, content_hash: str | Unset = UNSET, **kwargs: Any) -> CreateDocumentLinkResponse201:
        """Create document link

 Create a link to a document in the Camunda 8 cluster.

Note that this is currently supported for document stores of type: AWS, GCP

Args:
    document_id (str): Document Id that uniquely identifies a document.
    store_id (str | Unset):
    content_hash (str | Unset):
    body (CreateDocumentLinkData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateDocumentLinkResponse201 | CreateDocumentLinkResponse400]"""
        from .api.document.create_document_link import asyncio as create_document_link_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await create_document_link_asyncio(**_kwargs)


    def create_document(self, *, data: CreateDocumentData, store_id: str | Unset = UNSET, document_id: str | Unset = UNSET, **kwargs: Any) -> CreateDocumentResponse201:
        """Upload document

 Upload a document to the Camunda 8 cluster.

Note that this is currently supported for document stores of type: AWS, GCP, in-memory (non-
production), local (non-production)

Args:
    store_id (str | Unset):
    document_id (str | Unset): Document Id that uniquely identifies a document.
    body (CreateDocumentData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateDocumentResponse201 | CreateDocumentResponse400 | CreateDocumentResponse415]"""
        from .api.document.create_document import sync as create_document_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return create_document_sync(**_kwargs)


    async def create_document_async(self, *, data: CreateDocumentData, store_id: str | Unset = UNSET, document_id: str | Unset = UNSET, **kwargs: Any) -> CreateDocumentResponse201:
        """Upload document

 Upload a document to the Camunda 8 cluster.

Note that this is currently supported for document stores of type: AWS, GCP, in-memory (non-
production), local (non-production)

Args:
    store_id (str | Unset):
    document_id (str | Unset): Document Id that uniquely identifies a document.
    body (CreateDocumentData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateDocumentResponse201 | CreateDocumentResponse400 | CreateDocumentResponse415]"""
        from .api.document.create_document import asyncio as create_document_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await create_document_asyncio(**_kwargs)


    def delete_document(self, document_id: str, *, store_id: str | Unset = UNSET, **kwargs: Any) -> Any:
        """Delete document

 Delete a document from the Camunda 8 cluster.

Note that this is currently supported for document stores of type: AWS, GCP, in-memory (non-
production), local (non-production)

Args:
    document_id (str): Document Id that uniquely identifies a document.
    store_id (str | Unset):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteDocumentResponse404 | DeleteDocumentResponse500]"""
        from .api.document.delete_document import sync as delete_document_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return delete_document_sync(**_kwargs)


    async def delete_document_async(self, document_id: str, *, store_id: str | Unset = UNSET, **kwargs: Any) -> Any:
        """Delete document

 Delete a document from the Camunda 8 cluster.

Note that this is currently supported for document stores of type: AWS, GCP, in-memory (non-
production), local (non-production)

Args:
    document_id (str): Document Id that uniquely identifies a document.
    store_id (str | Unset):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteDocumentResponse404 | DeleteDocumentResponse500]"""
        from .api.document.delete_document import asyncio as delete_document_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await delete_document_asyncio(**_kwargs)


    def delete_resource(self, resource_key: str, *, data: DeleteResourceDataType0 | None, **kwargs: Any) -> Any:
        """Delete resource

 Deletes a deployed resource.
This can be a process definition, decision requirements definition, or form definition
deployed using the deploy resources endpoint. Specify the resource you want to delete in the
`resourceKey` parameter.

Args:
    resource_key (str): The system-assigned key for this resource.
    body (DeleteResourceDataType0 | None):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteResourceResponse400 | DeleteResourceResponse404 | DeleteResourceResponse500 | DeleteResourceResponse503]"""
        from .api.resource.delete_resource import sync as delete_resource_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return delete_resource_sync(**_kwargs)


    async def delete_resource_async(self, resource_key: str, *, data: DeleteResourceDataType0 | None, **kwargs: Any) -> Any:
        """Delete resource

 Deletes a deployed resource.
This can be a process definition, decision requirements definition, or form definition
deployed using the deploy resources endpoint. Specify the resource you want to delete in the
`resourceKey` parameter.

Args:
    resource_key (str): The system-assigned key for this resource.
    body (DeleteResourceDataType0 | None):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteResourceResponse400 | DeleteResourceResponse404 | DeleteResourceResponse500 | DeleteResourceResponse503]"""
        from .api.resource.delete_resource import asyncio as delete_resource_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await delete_resource_asyncio(**_kwargs)


    def create_deployment(self, *, data: CreateDeploymentData, **kwargs: Any) -> CreateDeploymentResponse200:
        """Deploy resources

 Deploys one or more resources (e.g. processes, decision models, or forms).
This is an atomic call, i.e. either all resources are deployed or none of them are.

Args:
    body (CreateDeploymentData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateDeploymentResponse200 | CreateDeploymentResponse400 | CreateDeploymentResponse503]"""
        from .api.resource.create_deployment import sync as create_deployment_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return create_deployment_sync(**_kwargs)


    async def create_deployment_async(self, *, data: CreateDeploymentData, **kwargs: Any) -> CreateDeploymentResponse200:
        """Deploy resources

 Deploys one or more resources (e.g. processes, decision models, or forms).
This is an atomic call, i.e. either all resources are deployed or none of them are.

Args:
    body (CreateDeploymentData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateDeploymentResponse200 | CreateDeploymentResponse400 | CreateDeploymentResponse503]"""
        from .api.resource.create_deployment import asyncio as create_deployment_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await create_deployment_asyncio(**_kwargs)


    def get_resource(self, resource_key: str, **kwargs: Any) -> GetResourceResponse200:
        """Get resource

 Returns a deployed resource.
:::info
Currently, this endpoint only supports RPA resources.
:::

Args:
    resource_key (str): The system-assigned key for this resource.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetResourceResponse200 | GetResourceResponse404 | GetResourceResponse500]"""
        from .api.resource.get_resource import sync as get_resource_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_resource_sync(**_kwargs)


    async def get_resource_async(self, resource_key: str, **kwargs: Any) -> GetResourceResponse200:
        """Get resource

 Returns a deployed resource.
:::info
Currently, this endpoint only supports RPA resources.
:::

Args:
    resource_key (str): The system-assigned key for this resource.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetResourceResponse200 | GetResourceResponse404 | GetResourceResponse500]"""
        from .api.resource.get_resource import asyncio as get_resource_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_resource_asyncio(**_kwargs)


    def get_resource_content(self, resource_key: str, **kwargs: Any) -> File:
        """Get resource content

 Returns the content of a deployed resource.
:::info
Currently, this endpoint only supports RPA resources.
:::

Args:
    resource_key (str): The system-assigned key for this resource.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[File | GetResourceContentResponse404 | GetResourceContentResponse500]"""
        from .api.resource.get_resource_content import sync as get_resource_content_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_resource_content_sync(**_kwargs)


    async def get_resource_content_async(self, resource_key: str, **kwargs: Any) -> File:
        """Get resource content

 Returns the content of a deployed resource.
:::info
Currently, this endpoint only supports RPA resources.
:::

Args:
    resource_key (str): The system-assigned key for this resource.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[File | GetResourceContentResponse404 | GetResourceContentResponse500]"""
        from .api.resource.get_resource_content import asyncio as get_resource_content_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_resource_content_asyncio(**_kwargs)


    def pin_clock(self, *, data: PinClockData, **kwargs: Any) -> Any:
        """Pin internal clock (alpha)

 Set a precise, static time for the Zeebe engine's internal clock.
When the clock is pinned, it remains at the specified time and does not advance.
To change the time, the clock must be pinned again with a new timestamp.

This endpoint is an alpha feature and may be subject to change
in future releases.

Args:
    body (PinClockData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | PinClockResponse400 | PinClockResponse500 | PinClockResponse503]"""
        from .api.clock.pin_clock import sync as pin_clock_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return pin_clock_sync(**_kwargs)


    async def pin_clock_async(self, *, data: PinClockData, **kwargs: Any) -> Any:
        """Pin internal clock (alpha)

 Set a precise, static time for the Zeebe engine's internal clock.
When the clock is pinned, it remains at the specified time and does not advance.
To change the time, the clock must be pinned again with a new timestamp.

This endpoint is an alpha feature and may be subject to change
in future releases.

Args:
    body (PinClockData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | PinClockResponse400 | PinClockResponse500 | PinClockResponse503]"""
        from .api.clock.pin_clock import asyncio as pin_clock_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await pin_clock_asyncio(**_kwargs)


    def reset_clock(self, **kwargs: Any) -> Any:
        """Reset internal clock (alpha)

 Resets the Zeebe engine's internal clock to the current system time, enabling it to tick in real-
time.
This operation is useful for returning the clock to
normal behavior after it has been pinned to a specific time.

This endpoint is an alpha feature and may be subject to change
in future releases.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | ResetClockResponse500 | ResetClockResponse503]"""
        from .api.clock.reset_clock import sync as reset_clock_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return reset_clock_sync(**_kwargs)


    async def reset_clock_async(self, **kwargs: Any) -> Any:
        """Reset internal clock (alpha)

 Resets the Zeebe engine's internal clock to the current system time, enabling it to tick in real-
time.
This operation is useful for returning the clock to
normal behavior after it has been pinned to a specific time.

This endpoint is an alpha feature and may be subject to change
in future releases.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | ResetClockResponse500 | ResetClockResponse503]"""
        from .api.clock.reset_clock import asyncio as reset_clock_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await reset_clock_asyncio(**_kwargs)


    def activate_ad_hoc_sub_process_activities(self, ad_hoc_sub_process_instance_key: str, *, data: ActivateAdHocSubProcessActivitiesData, **kwargs: Any) -> ActivateAdHocSubProcessActivitiesResponse400:
        """Activate activities within an ad-hoc sub-process

 Activates selected activities within an ad-hoc sub-process identified by element ID.
The provided element IDs must exist within the ad-hoc sub-process instance identified by the
provided adHocSubProcessInstanceKey.

Args:
    ad_hoc_sub_process_instance_key (str): System-generated key for a element instance.
        Example: 2251799813686789.
    body (ActivateAdHocSubProcessActivitiesData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[ActivateAdHocSubProcessActivitiesResponse400 | ActivateAdHocSubProcessActivitiesResponse401 | ActivateAdHocSubProcessActivitiesResponse403 | ActivateAdHocSubProcessActivitiesResponse404 | ActivateAdHocSubProcessActivitiesResponse500 | ActivateAdHocSubProcessActivitiesResponse503 | Any]"""
        from .api.ad_hoc_sub_process.activate_ad_hoc_sub_process_activities import sync as activate_ad_hoc_sub_process_activities_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return activate_ad_hoc_sub_process_activities_sync(**_kwargs)


    async def activate_ad_hoc_sub_process_activities_async(self, ad_hoc_sub_process_instance_key: str, *, data: ActivateAdHocSubProcessActivitiesData, **kwargs: Any) -> ActivateAdHocSubProcessActivitiesResponse400:
        """Activate activities within an ad-hoc sub-process

 Activates selected activities within an ad-hoc sub-process identified by element ID.
The provided element IDs must exist within the ad-hoc sub-process instance identified by the
provided adHocSubProcessInstanceKey.

Args:
    ad_hoc_sub_process_instance_key (str): System-generated key for a element instance.
        Example: 2251799813686789.
    body (ActivateAdHocSubProcessActivitiesData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[ActivateAdHocSubProcessActivitiesResponse400 | ActivateAdHocSubProcessActivitiesResponse401 | ActivateAdHocSubProcessActivitiesResponse403 | ActivateAdHocSubProcessActivitiesResponse404 | ActivateAdHocSubProcessActivitiesResponse500 | ActivateAdHocSubProcessActivitiesResponse503 | Any]"""
        from .api.ad_hoc_sub_process.activate_ad_hoc_sub_process_activities import asyncio as activate_ad_hoc_sub_process_activities_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await activate_ad_hoc_sub_process_activities_asyncio(**_kwargs)


    def get_decision_requirements_xml(self, decision_requirements_key: str, **kwargs: Any) -> GetDecisionRequirementsXMLResponse400:
        """Get decision requirements XML

 Returns decision requirements as XML.

Args:
    decision_requirements_key (str): System-generated key for a deployed decision requirements
        definition. Example: 2251799813683346.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetDecisionRequirementsXMLResponse400 | GetDecisionRequirementsXMLResponse401 | GetDecisionRequirementsXMLResponse403 | GetDecisionRequirementsXMLResponse404 | GetDecisionRequirementsXMLResponse500 | str]"""
        from .api.decision_requirements.get_decision_requirements_xml import sync as get_decision_requirements_xml_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_decision_requirements_xml_sync(**_kwargs)


    async def get_decision_requirements_xml_async(self, decision_requirements_key: str, **kwargs: Any) -> GetDecisionRequirementsXMLResponse400:
        """Get decision requirements XML

 Returns decision requirements as XML.

Args:
    decision_requirements_key (str): System-generated key for a deployed decision requirements
        definition. Example: 2251799813683346.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetDecisionRequirementsXMLResponse400 | GetDecisionRequirementsXMLResponse401 | GetDecisionRequirementsXMLResponse403 | GetDecisionRequirementsXMLResponse404 | GetDecisionRequirementsXMLResponse500 | str]"""
        from .api.decision_requirements.get_decision_requirements_xml import asyncio as get_decision_requirements_xml_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_decision_requirements_xml_asyncio(**_kwargs)


    def search_decision_requirements(self, *, data: SearchDecisionRequirementsData, **kwargs: Any) -> SearchDecisionRequirementsResponse200:
        """Search decision requirements

 Search for decision requirements based on given criteria.

Args:
    body (SearchDecisionRequirementsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchDecisionRequirementsResponse200 | SearchDecisionRequirementsResponse400 | SearchDecisionRequirementsResponse401 | SearchDecisionRequirementsResponse403 | SearchDecisionRequirementsResponse500]"""
        from .api.decision_requirements.search_decision_requirements import sync as search_decision_requirements_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_decision_requirements_sync(**_kwargs)


    async def search_decision_requirements_async(self, *, data: SearchDecisionRequirementsData, **kwargs: Any) -> SearchDecisionRequirementsResponse200:
        """Search decision requirements

 Search for decision requirements based on given criteria.

Args:
    body (SearchDecisionRequirementsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchDecisionRequirementsResponse200 | SearchDecisionRequirementsResponse400 | SearchDecisionRequirementsResponse401 | SearchDecisionRequirementsResponse403 | SearchDecisionRequirementsResponse500]"""
        from .api.decision_requirements.search_decision_requirements import asyncio as search_decision_requirements_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_decision_requirements_asyncio(**_kwargs)


    def get_decision_requirements(self, decision_requirements_key: str, **kwargs: Any) -> GetDecisionRequirementsResponse200:
        """Get decision requirements

 Returns Decision Requirements as JSON.

Args:
    decision_requirements_key (str): System-generated key for a deployed decision requirements
        definition. Example: 2251799813683346.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetDecisionRequirementsResponse200 | GetDecisionRequirementsResponse400 | GetDecisionRequirementsResponse401 | GetDecisionRequirementsResponse403 | GetDecisionRequirementsResponse404 | GetDecisionRequirementsResponse500]"""
        from .api.decision_requirements.get_decision_requirements import sync as get_decision_requirements_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_decision_requirements_sync(**_kwargs)


    async def get_decision_requirements_async(self, decision_requirements_key: str, **kwargs: Any) -> GetDecisionRequirementsResponse200:
        """Get decision requirements

 Returns Decision Requirements as JSON.

Args:
    decision_requirements_key (str): System-generated key for a deployed decision requirements
        definition. Example: 2251799813683346.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetDecisionRequirementsResponse200 | GetDecisionRequirementsResponse400 | GetDecisionRequirementsResponse401 | GetDecisionRequirementsResponse403 | GetDecisionRequirementsResponse404 | GetDecisionRequirementsResponse500]"""
        from .api.decision_requirements.get_decision_requirements import asyncio as get_decision_requirements_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_decision_requirements_asyncio(**_kwargs)


    def create_mapping_rule(self, *, data: CreateMappingRuleData, **kwargs: Any) -> CreateMappingRuleResponse201:
        """Create mapping rule

 Create a new mapping rule

Args:
    body (CreateMappingRuleData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateMappingRuleResponse201 | CreateMappingRuleResponse400 | CreateMappingRuleResponse403 | CreateMappingRuleResponse404 | CreateMappingRuleResponse500]"""
        from .api.mapping_rule.create_mapping_rule import sync as create_mapping_rule_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return create_mapping_rule_sync(**_kwargs)


    async def create_mapping_rule_async(self, *, data: CreateMappingRuleData, **kwargs: Any) -> CreateMappingRuleResponse201:
        """Create mapping rule

 Create a new mapping rule

Args:
    body (CreateMappingRuleData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateMappingRuleResponse201 | CreateMappingRuleResponse400 | CreateMappingRuleResponse403 | CreateMappingRuleResponse404 | CreateMappingRuleResponse500]"""
        from .api.mapping_rule.create_mapping_rule import asyncio as create_mapping_rule_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await create_mapping_rule_asyncio(**_kwargs)


    def search_mapping_rule(self, *, data: SearchMappingRuleData, **kwargs: Any) -> SearchMappingRuleResponse200:
        """Search mapping rules

 Search for mapping rules based on given criteria.

Args:
    body (SearchMappingRuleData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchMappingRuleResponse200 | SearchMappingRuleResponse400 | SearchMappingRuleResponse401 | SearchMappingRuleResponse403 | SearchMappingRuleResponse500]"""
        from .api.mapping_rule.search_mapping_rule import sync as search_mapping_rule_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_mapping_rule_sync(**_kwargs)


    async def search_mapping_rule_async(self, *, data: SearchMappingRuleData, **kwargs: Any) -> SearchMappingRuleResponse200:
        """Search mapping rules

 Search for mapping rules based on given criteria.

Args:
    body (SearchMappingRuleData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchMappingRuleResponse200 | SearchMappingRuleResponse400 | SearchMappingRuleResponse401 | SearchMappingRuleResponse403 | SearchMappingRuleResponse500]"""
        from .api.mapping_rule.search_mapping_rule import asyncio as search_mapping_rule_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_mapping_rule_asyncio(**_kwargs)


    def delete_mapping_rule(self, mapping_rule_id: str, **kwargs: Any) -> Any:
        """Delete a mapping rule

 Deletes the mapping rule with the given ID.

Args:
    mapping_rule_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteMappingRuleResponse401 | DeleteMappingRuleResponse404 | DeleteMappingRuleResponse500 | DeleteMappingRuleResponse503]"""
        from .api.mapping_rule.delete_mapping_rule import sync as delete_mapping_rule_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return delete_mapping_rule_sync(**_kwargs)


    async def delete_mapping_rule_async(self, mapping_rule_id: str, **kwargs: Any) -> Any:
        """Delete a mapping rule

 Deletes the mapping rule with the given ID.

Args:
    mapping_rule_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteMappingRuleResponse401 | DeleteMappingRuleResponse404 | DeleteMappingRuleResponse500 | DeleteMappingRuleResponse503]"""
        from .api.mapping_rule.delete_mapping_rule import asyncio as delete_mapping_rule_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await delete_mapping_rule_asyncio(**_kwargs)


    def get_mapping_rule(self, mapping_rule_id: str, **kwargs: Any) -> GetMappingRuleResponse200:
        """Get a mapping rule

 Gets the mapping rule with the given ID.

Args:
    mapping_rule_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetMappingRuleResponse200 | GetMappingRuleResponse401 | GetMappingRuleResponse404 | GetMappingRuleResponse500]"""
        from .api.mapping_rule.get_mapping_rule import sync as get_mapping_rule_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_mapping_rule_sync(**_kwargs)


    async def get_mapping_rule_async(self, mapping_rule_id: str, **kwargs: Any) -> GetMappingRuleResponse200:
        """Get a mapping rule

 Gets the mapping rule with the given ID.

Args:
    mapping_rule_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetMappingRuleResponse200 | GetMappingRuleResponse401 | GetMappingRuleResponse404 | GetMappingRuleResponse500]"""
        from .api.mapping_rule.get_mapping_rule import asyncio as get_mapping_rule_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_mapping_rule_asyncio(**_kwargs)


    def update_mapping_rule(self, mapping_rule_id: str, *, data: UpdateMappingRuleData, **kwargs: Any) -> UpdateMappingRuleResponse200:
        """Update mapping rule

 Update a mapping rule.

Args:
    mapping_rule_id (str):
    body (UpdateMappingRuleData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[UpdateMappingRuleResponse200 | UpdateMappingRuleResponse400 | UpdateMappingRuleResponse403 | UpdateMappingRuleResponse404 | UpdateMappingRuleResponse500 | UpdateMappingRuleResponse503]"""
        from .api.mapping_rule.update_mapping_rule import sync as update_mapping_rule_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return update_mapping_rule_sync(**_kwargs)


    async def update_mapping_rule_async(self, mapping_rule_id: str, *, data: UpdateMappingRuleData, **kwargs: Any) -> UpdateMappingRuleResponse200:
        """Update mapping rule

 Update a mapping rule.

Args:
    mapping_rule_id (str):
    body (UpdateMappingRuleData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[UpdateMappingRuleResponse200 | UpdateMappingRuleResponse400 | UpdateMappingRuleResponse403 | UpdateMappingRuleResponse404 | UpdateMappingRuleResponse500 | UpdateMappingRuleResponse503]"""
        from .api.mapping_rule.update_mapping_rule import asyncio as update_mapping_rule_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await update_mapping_rule_asyncio(**_kwargs)


    def evaluate_expression(self, *, data: EvaluateExpressionData, **kwargs: Any) -> EvaluateExpressionResponse200:
        """Evaluate an expression

 Evaluates a FEEL expression and returns the result. Supports references to tenant scoped cluster
variables when a tenant ID is provided.

Args:
    body (EvaluateExpressionData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[EvaluateExpressionResponse200 | EvaluateExpressionResponse400 | EvaluateExpressionResponse401 | EvaluateExpressionResponse403 | EvaluateExpressionResponse500]"""
        from .api.expression.evaluate_expression import sync as evaluate_expression_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return evaluate_expression_sync(**_kwargs)


    async def evaluate_expression_async(self, *, data: EvaluateExpressionData, **kwargs: Any) -> EvaluateExpressionResponse200:
        """Evaluate an expression

 Evaluates a FEEL expression and returns the result. Supports references to tenant scoped cluster
variables when a tenant ID is provided.

Args:
    body (EvaluateExpressionData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[EvaluateExpressionResponse200 | EvaluateExpressionResponse400 | EvaluateExpressionResponse401 | EvaluateExpressionResponse403 | EvaluateExpressionResponse500]"""
        from .api.expression.evaluate_expression import asyncio as evaluate_expression_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await evaluate_expression_asyncio(**_kwargs)


    def get_element_instance(self, element_instance_key: str, **kwargs: Any) -> GetElementInstanceResponse200:
        """Get element instance

 Returns element instance as JSON.

Args:
    element_instance_key (str): System-generated key for a element instance. Example:
        2251799813686789.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetElementInstanceResponse200 | GetElementInstanceResponse400 | GetElementInstanceResponse401 | GetElementInstanceResponse403 | GetElementInstanceResponse404 | GetElementInstanceResponse500]"""
        from .api.element_instance.get_element_instance import sync as get_element_instance_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_element_instance_sync(**_kwargs)


    async def get_element_instance_async(self, element_instance_key: str, **kwargs: Any) -> GetElementInstanceResponse200:
        """Get element instance

 Returns element instance as JSON.

Args:
    element_instance_key (str): System-generated key for a element instance. Example:
        2251799813686789.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetElementInstanceResponse200 | GetElementInstanceResponse400 | GetElementInstanceResponse401 | GetElementInstanceResponse403 | GetElementInstanceResponse404 | GetElementInstanceResponse500]"""
        from .api.element_instance.get_element_instance import asyncio as get_element_instance_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_element_instance_asyncio(**_kwargs)


    def search_element_instances(self, *, data: SearchElementInstancesData, **kwargs: Any) -> SearchElementInstancesResponse200:
        """Search element instances

 Search for element instances based on given criteria.

Args:
    body (SearchElementInstancesData): Element instance search request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchElementInstancesResponse200 | SearchElementInstancesResponse400 | SearchElementInstancesResponse401 | SearchElementInstancesResponse403 | SearchElementInstancesResponse500]"""
        from .api.element_instance.search_element_instances import sync as search_element_instances_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_element_instances_sync(**_kwargs)


    async def search_element_instances_async(self, *, data: SearchElementInstancesData, **kwargs: Any) -> SearchElementInstancesResponse200:
        """Search element instances

 Search for element instances based on given criteria.

Args:
    body (SearchElementInstancesData): Element instance search request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchElementInstancesResponse200 | SearchElementInstancesResponse400 | SearchElementInstancesResponse401 | SearchElementInstancesResponse403 | SearchElementInstancesResponse500]"""
        from .api.element_instance.search_element_instances import asyncio as search_element_instances_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_element_instances_asyncio(**_kwargs)


    def create_element_instance_variables(self, element_instance_key: str, *, data: CreateElementInstanceVariablesData, **kwargs: Any) -> Any:
        """Update element instance variables

 Updates all the variables of a particular scope (for example, process instance, element instance)
with the given variable data.
Specify the element instance in the `elementInstanceKey` parameter.

Args:
    element_instance_key (str): System-generated key for a element instance. Example:
        2251799813686789.
    body (CreateElementInstanceVariablesData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | CreateElementInstanceVariablesResponse400 | CreateElementInstanceVariablesResponse500 | CreateElementInstanceVariablesResponse503]"""
        from .api.element_instance.create_element_instance_variables import sync as create_element_instance_variables_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return create_element_instance_variables_sync(**_kwargs)


    async def create_element_instance_variables_async(self, element_instance_key: str, *, data: CreateElementInstanceVariablesData, **kwargs: Any) -> Any:
        """Update element instance variables

 Updates all the variables of a particular scope (for example, process instance, element instance)
with the given variable data.
Specify the element instance in the `elementInstanceKey` parameter.

Args:
    element_instance_key (str): System-generated key for a element instance. Example:
        2251799813686789.
    body (CreateElementInstanceVariablesData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | CreateElementInstanceVariablesResponse400 | CreateElementInstanceVariablesResponse500 | CreateElementInstanceVariablesResponse503]"""
        from .api.element_instance.create_element_instance_variables import asyncio as create_element_instance_variables_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await create_element_instance_variables_asyncio(**_kwargs)


    def search_element_instance_incidents(self, element_instance_key: str, *, data: SearchElementInstanceIncidentsData, **kwargs: Any) -> SearchElementInstanceIncidentsResponse200:
        """Search for incidents of a specific element instance

 Search for incidents caused by the specified element instance, including incidents of any child
instances created from this element instance.

Although the `elementInstanceKey` is provided as a path parameter to indicate the root element
instance,
you may also include an `elementInstanceKey` within the filter object to narrow results to specific
child element instances. This is useful, for example, if you want to isolate incidents associated
with
nested or subordinate elements within the given element instance while excluding incidents directly
tied
to the root element itself.

Args:
    element_instance_key (str): System-generated key for a element instance. Example:
        2251799813686789.
    body (SearchElementInstanceIncidentsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchElementInstanceIncidentsResponse200 | SearchElementInstanceIncidentsResponse400 | SearchElementInstanceIncidentsResponse401 | SearchElementInstanceIncidentsResponse403 | SearchElementInstanceIncidentsResponse404 | SearchElementInstanceIncidentsResponse500]"""
        from .api.element_instance.search_element_instance_incidents import sync as search_element_instance_incidents_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_element_instance_incidents_sync(**_kwargs)


    async def search_element_instance_incidents_async(self, element_instance_key: str, *, data: SearchElementInstanceIncidentsData, **kwargs: Any) -> SearchElementInstanceIncidentsResponse200:
        """Search for incidents of a specific element instance

 Search for incidents caused by the specified element instance, including incidents of any child
instances created from this element instance.

Although the `elementInstanceKey` is provided as a path parameter to indicate the root element
instance,
you may also include an `elementInstanceKey` within the filter object to narrow results to specific
child element instances. This is useful, for example, if you want to isolate incidents associated
with
nested or subordinate elements within the given element instance while excluding incidents directly
tied
to the root element itself.

Args:
    element_instance_key (str): System-generated key for a element instance. Example:
        2251799813686789.
    body (SearchElementInstanceIncidentsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchElementInstanceIncidentsResponse200 | SearchElementInstanceIncidentsResponse400 | SearchElementInstanceIncidentsResponse401 | SearchElementInstanceIncidentsResponse403 | SearchElementInstanceIncidentsResponse404 | SearchElementInstanceIncidentsResponse500]"""
        from .api.element_instance.search_element_instance_incidents import asyncio as search_element_instance_incidents_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_element_instance_incidents_asyncio(**_kwargs)


    def unassign_user_task(self, user_task_key: str, **kwargs: Any) -> Any:
        """Unassign user task

 Removes the assignee of a task with the given key.

Args:
    user_task_key (str): System-generated key for a user task.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignUserTaskResponse400 | UnassignUserTaskResponse404 | UnassignUserTaskResponse409 | UnassignUserTaskResponse500 | UnassignUserTaskResponse503]"""
        from .api.user_task.unassign_user_task import sync as unassign_user_task_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return unassign_user_task_sync(**_kwargs)


    async def unassign_user_task_async(self, user_task_key: str, **kwargs: Any) -> Any:
        """Unassign user task

 Removes the assignee of a task with the given key.

Args:
    user_task_key (str): System-generated key for a user task.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignUserTaskResponse400 | UnassignUserTaskResponse404 | UnassignUserTaskResponse409 | UnassignUserTaskResponse500 | UnassignUserTaskResponse503]"""
        from .api.user_task.unassign_user_task import asyncio as unassign_user_task_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await unassign_user_task_asyncio(**_kwargs)


    def search_user_task_variables(self, user_task_key: str, *, data: SearchUserTaskVariablesData, truncate_values: bool | Unset = UNSET, **kwargs: Any) -> SearchUserTaskVariablesResponse200:
        """Search user task variables

 Search for user task variables based on given criteria. By default, long variable values in the
response are truncated.

Args:
    user_task_key (str): System-generated key for a user task.
    truncate_values (bool | Unset):
    body (SearchUserTaskVariablesData): User task search query request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchUserTaskVariablesResponse200 | SearchUserTaskVariablesResponse400 | SearchUserTaskVariablesResponse500]"""
        from .api.user_task.search_user_task_variables import sync as search_user_task_variables_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_user_task_variables_sync(**_kwargs)


    async def search_user_task_variables_async(self, user_task_key: str, *, data: SearchUserTaskVariablesData, truncate_values: bool | Unset = UNSET, **kwargs: Any) -> SearchUserTaskVariablesResponse200:
        """Search user task variables

 Search for user task variables based on given criteria. By default, long variable values in the
response are truncated.

Args:
    user_task_key (str): System-generated key for a user task.
    truncate_values (bool | Unset):
    body (SearchUserTaskVariablesData): User task search query request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchUserTaskVariablesResponse200 | SearchUserTaskVariablesResponse400 | SearchUserTaskVariablesResponse500]"""
        from .api.user_task.search_user_task_variables import asyncio as search_user_task_variables_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_user_task_variables_asyncio(**_kwargs)


    def update_user_task(self, user_task_key: str, *, data: UpdateUserTaskData, **kwargs: Any) -> Any:
        """Update user task

 Update a user task with the given key.

Args:
    user_task_key (str): System-generated key for a user task.
    body (UpdateUserTaskData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UpdateUserTaskResponse400 | UpdateUserTaskResponse404 | UpdateUserTaskResponse409 | UpdateUserTaskResponse500 | UpdateUserTaskResponse503]"""
        from .api.user_task.update_user_task import sync as update_user_task_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return update_user_task_sync(**_kwargs)


    async def update_user_task_async(self, user_task_key: str, *, data: UpdateUserTaskData, **kwargs: Any) -> Any:
        """Update user task

 Update a user task with the given key.

Args:
    user_task_key (str): System-generated key for a user task.
    body (UpdateUserTaskData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UpdateUserTaskResponse400 | UpdateUserTaskResponse404 | UpdateUserTaskResponse409 | UpdateUserTaskResponse500 | UpdateUserTaskResponse503]"""
        from .api.user_task.update_user_task import asyncio as update_user_task_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await update_user_task_asyncio(**_kwargs)


    def get_user_task_form(self, user_task_key: str, **kwargs: Any) -> Any:
        """Get user task form

 Get the form of a user task.
Note that this endpoint will only return linked forms. This endpoint does not support embedded
forms.

Args:
    user_task_key (str): System-generated key for a user task.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | GetUserTaskFormResponse200 | GetUserTaskFormResponse400 | GetUserTaskFormResponse401 | GetUserTaskFormResponse403 | GetUserTaskFormResponse404 | GetUserTaskFormResponse500]"""
        from .api.user_task.get_user_task_form import sync as get_user_task_form_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_user_task_form_sync(**_kwargs)


    async def get_user_task_form_async(self, user_task_key: str, **kwargs: Any) -> Any:
        """Get user task form

 Get the form of a user task.
Note that this endpoint will only return linked forms. This endpoint does not support embedded
forms.

Args:
    user_task_key (str): System-generated key for a user task.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | GetUserTaskFormResponse200 | GetUserTaskFormResponse400 | GetUserTaskFormResponse401 | GetUserTaskFormResponse403 | GetUserTaskFormResponse404 | GetUserTaskFormResponse500]"""
        from .api.user_task.get_user_task_form import asyncio as get_user_task_form_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_user_task_form_asyncio(**_kwargs)


    def get_user_task(self, user_task_key: str, **kwargs: Any) -> GetUserTaskResponse200:
        """Get user task

 Get the user task by the user task key.

Args:
    user_task_key (str): System-generated key for a user task.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetUserTaskResponse200 | GetUserTaskResponse400 | GetUserTaskResponse401 | GetUserTaskResponse403 | GetUserTaskResponse404 | GetUserTaskResponse500]"""
        from .api.user_task.get_user_task import sync as get_user_task_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_user_task_sync(**_kwargs)


    async def get_user_task_async(self, user_task_key: str, **kwargs: Any) -> GetUserTaskResponse200:
        """Get user task

 Get the user task by the user task key.

Args:
    user_task_key (str): System-generated key for a user task.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetUserTaskResponse200 | GetUserTaskResponse400 | GetUserTaskResponse401 | GetUserTaskResponse403 | GetUserTaskResponse404 | GetUserTaskResponse500]"""
        from .api.user_task.get_user_task import asyncio as get_user_task_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_user_task_asyncio(**_kwargs)


    def complete_user_task(self, user_task_key: str, *, data: CompleteUserTaskData, **kwargs: Any) -> Any:
        """Complete user task

 Completes a user task with the given key.

Args:
    user_task_key (str): System-generated key for a user task.
    body (CompleteUserTaskData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | CompleteUserTaskResponse400 | CompleteUserTaskResponse404 | CompleteUserTaskResponse409 | CompleteUserTaskResponse500 | CompleteUserTaskResponse503]"""
        from .api.user_task.complete_user_task import sync as complete_user_task_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return complete_user_task_sync(**_kwargs)


    async def complete_user_task_async(self, user_task_key: str, *, data: CompleteUserTaskData, **kwargs: Any) -> Any:
        """Complete user task

 Completes a user task with the given key.

Args:
    user_task_key (str): System-generated key for a user task.
    body (CompleteUserTaskData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | CompleteUserTaskResponse400 | CompleteUserTaskResponse404 | CompleteUserTaskResponse409 | CompleteUserTaskResponse500 | CompleteUserTaskResponse503]"""
        from .api.user_task.complete_user_task import asyncio as complete_user_task_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await complete_user_task_asyncio(**_kwargs)


    def search_user_task_audit_logs(self, user_task_key: str, *, data: SearchUserTaskAuditLogsData, **kwargs: Any) -> SearchUserTaskAuditLogsResponse200:
        """Search user task audit logs

 Search for user task audit logs based on given criteria.

Args:
    user_task_key (str): System-generated key for a user task.
    body (SearchUserTaskAuditLogsData): User task search query request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchUserTaskAuditLogsResponse200 | SearchUserTaskAuditLogsResponse400 | SearchUserTaskAuditLogsResponse500]"""
        from .api.user_task.search_user_task_audit_logs import sync as search_user_task_audit_logs_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_user_task_audit_logs_sync(**_kwargs)


    async def search_user_task_audit_logs_async(self, user_task_key: str, *, data: SearchUserTaskAuditLogsData, **kwargs: Any) -> SearchUserTaskAuditLogsResponse200:
        """Search user task audit logs

 Search for user task audit logs based on given criteria.

Args:
    user_task_key (str): System-generated key for a user task.
    body (SearchUserTaskAuditLogsData): User task search query request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchUserTaskAuditLogsResponse200 | SearchUserTaskAuditLogsResponse400 | SearchUserTaskAuditLogsResponse500]"""
        from .api.user_task.search_user_task_audit_logs import asyncio as search_user_task_audit_logs_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_user_task_audit_logs_asyncio(**_kwargs)


    def search_user_tasks(self, *, data: SearchUserTasksData, **kwargs: Any) -> SearchUserTasksResponse200:
        """Search user tasks

 Search for user tasks based on given criteria.

Args:
    body (SearchUserTasksData): User task search query request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchUserTasksResponse200 | SearchUserTasksResponse400 | SearchUserTasksResponse401 | SearchUserTasksResponse403 | SearchUserTasksResponse500]"""
        from .api.user_task.search_user_tasks import sync as search_user_tasks_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_user_tasks_sync(**_kwargs)


    async def search_user_tasks_async(self, *, data: SearchUserTasksData, **kwargs: Any) -> SearchUserTasksResponse200:
        """Search user tasks

 Search for user tasks based on given criteria.

Args:
    body (SearchUserTasksData): User task search query request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchUserTasksResponse200 | SearchUserTasksResponse400 | SearchUserTasksResponse401 | SearchUserTasksResponse403 | SearchUserTasksResponse500]"""
        from .api.user_task.search_user_tasks import asyncio as search_user_tasks_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_user_tasks_asyncio(**_kwargs)


    def assign_user_task(self, user_task_key: str, *, data: AssignUserTaskData, **kwargs: Any) -> Any:
        """Assign user task

 Assigns a user task with the given key to the given assignee.

Args:
    user_task_key (str): System-generated key for a user task.
    body (AssignUserTaskData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignUserTaskResponse400 | AssignUserTaskResponse404 | AssignUserTaskResponse409 | AssignUserTaskResponse500 | AssignUserTaskResponse503]"""
        from .api.user_task.assign_user_task import sync as assign_user_task_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return assign_user_task_sync(**_kwargs)


    async def assign_user_task_async(self, user_task_key: str, *, data: AssignUserTaskData, **kwargs: Any) -> Any:
        """Assign user task

 Assigns a user task with the given key to the given assignee.

Args:
    user_task_key (str): System-generated key for a user task.
    body (AssignUserTaskData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignUserTaskResponse400 | AssignUserTaskResponse404 | AssignUserTaskResponse409 | AssignUserTaskResponse500 | AssignUserTaskResponse503]"""
        from .api.user_task.assign_user_task import asyncio as assign_user_task_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await assign_user_task_asyncio(**_kwargs)


    def search_correlated_message_subscriptions(self, *, data: SearchCorrelatedMessageSubscriptionsData, **kwargs: Any) -> SearchCorrelatedMessageSubscriptionsResponse200:
        """Search correlated message subscriptions

 Search correlated message subscriptions based on given criteria.

Args:
    body (SearchCorrelatedMessageSubscriptionsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchCorrelatedMessageSubscriptionsResponse200 | SearchCorrelatedMessageSubscriptionsResponse400 | SearchCorrelatedMessageSubscriptionsResponse401 | SearchCorrelatedMessageSubscriptionsResponse403 | SearchCorrelatedMessageSubscriptionsResponse500]"""
        from .api.message_subscription.search_correlated_message_subscriptions import sync as search_correlated_message_subscriptions_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_correlated_message_subscriptions_sync(**_kwargs)


    async def search_correlated_message_subscriptions_async(self, *, data: SearchCorrelatedMessageSubscriptionsData, **kwargs: Any) -> SearchCorrelatedMessageSubscriptionsResponse200:
        """Search correlated message subscriptions

 Search correlated message subscriptions based on given criteria.

Args:
    body (SearchCorrelatedMessageSubscriptionsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchCorrelatedMessageSubscriptionsResponse200 | SearchCorrelatedMessageSubscriptionsResponse400 | SearchCorrelatedMessageSubscriptionsResponse401 | SearchCorrelatedMessageSubscriptionsResponse403 | SearchCorrelatedMessageSubscriptionsResponse500]"""
        from .api.message_subscription.search_correlated_message_subscriptions import asyncio as search_correlated_message_subscriptions_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_correlated_message_subscriptions_asyncio(**_kwargs)


    def search_message_subscriptions(self, *, data: SearchMessageSubscriptionsData, **kwargs: Any) -> SearchMessageSubscriptionsResponse200:
        """Search message subscriptions

 Search for message subscriptions based on given criteria.

Args:
    body (SearchMessageSubscriptionsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchMessageSubscriptionsResponse200 | SearchMessageSubscriptionsResponse400 | SearchMessageSubscriptionsResponse401 | SearchMessageSubscriptionsResponse403 | SearchMessageSubscriptionsResponse500]"""
        from .api.message_subscription.search_message_subscriptions import sync as search_message_subscriptions_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_message_subscriptions_sync(**_kwargs)


    async def search_message_subscriptions_async(self, *, data: SearchMessageSubscriptionsData, **kwargs: Any) -> SearchMessageSubscriptionsResponse200:
        """Search message subscriptions

 Search for message subscriptions based on given criteria.

Args:
    body (SearchMessageSubscriptionsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchMessageSubscriptionsResponse200 | SearchMessageSubscriptionsResponse400 | SearchMessageSubscriptionsResponse401 | SearchMessageSubscriptionsResponse403 | SearchMessageSubscriptionsResponse500]"""
        from .api.message_subscription.search_message_subscriptions import asyncio as search_message_subscriptions_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_message_subscriptions_asyncio(**_kwargs)


    def get_decision_definition(self, decision_definition_key: str, **kwargs: Any) -> GetDecisionDefinitionResponse200:
        """Get decision definition

 Returns a decision definition by key.

Args:
    decision_definition_key (str): System-generated key for a decision definition. Example:
        2251799813326547.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetDecisionDefinitionResponse200 | GetDecisionDefinitionResponse400 | GetDecisionDefinitionResponse401 | GetDecisionDefinitionResponse403 | GetDecisionDefinitionResponse404 | GetDecisionDefinitionResponse500]"""
        from .api.decision_definition.get_decision_definition import sync as get_decision_definition_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_decision_definition_sync(**_kwargs)


    async def get_decision_definition_async(self, decision_definition_key: str, **kwargs: Any) -> GetDecisionDefinitionResponse200:
        """Get decision definition

 Returns a decision definition by key.

Args:
    decision_definition_key (str): System-generated key for a decision definition. Example:
        2251799813326547.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetDecisionDefinitionResponse200 | GetDecisionDefinitionResponse400 | GetDecisionDefinitionResponse401 | GetDecisionDefinitionResponse403 | GetDecisionDefinitionResponse404 | GetDecisionDefinitionResponse500]"""
        from .api.decision_definition.get_decision_definition import asyncio as get_decision_definition_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_decision_definition_asyncio(**_kwargs)


    def evaluate_decision(self, *, data: DecisionevaluationbyID | Decisionevaluationbykey, **kwargs: Any) -> Any:
        """Evaluate decision

 Evaluates a decision.
You specify the decision to evaluate either by using its unique key (as returned by
DeployResource), or using the decision ID. When using the decision ID, the latest deployed
version of the decision is used.

Args:
    body (DecisionevaluationbyID | Decisionevaluationbykey):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | EvaluateDecisionResponse200 | EvaluateDecisionResponse400 | EvaluateDecisionResponse500 | EvaluateDecisionResponse503]"""
        from .api.decision_definition.evaluate_decision import sync as evaluate_decision_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return evaluate_decision_sync(**_kwargs)


    async def evaluate_decision_async(self, *, data: DecisionevaluationbyID | Decisionevaluationbykey, **kwargs: Any) -> Any:
        """Evaluate decision

 Evaluates a decision.
You specify the decision to evaluate either by using its unique key (as returned by
DeployResource), or using the decision ID. When using the decision ID, the latest deployed
version of the decision is used.

Args:
    body (DecisionevaluationbyID | Decisionevaluationbykey):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | EvaluateDecisionResponse200 | EvaluateDecisionResponse400 | EvaluateDecisionResponse500 | EvaluateDecisionResponse503]"""
        from .api.decision_definition.evaluate_decision import asyncio as evaluate_decision_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await evaluate_decision_asyncio(**_kwargs)


    def search_decision_definitions(self, *, data: SearchDecisionDefinitionsData, **kwargs: Any) -> SearchDecisionDefinitionsResponse200:
        """Search decision definitions

 Search for decision definitions based on given criteria.

Args:
    body (SearchDecisionDefinitionsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchDecisionDefinitionsResponse200 | SearchDecisionDefinitionsResponse400 | SearchDecisionDefinitionsResponse401 | SearchDecisionDefinitionsResponse403 | SearchDecisionDefinitionsResponse500]"""
        from .api.decision_definition.search_decision_definitions import sync as search_decision_definitions_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_decision_definitions_sync(**_kwargs)


    async def search_decision_definitions_async(self, *, data: SearchDecisionDefinitionsData, **kwargs: Any) -> SearchDecisionDefinitionsResponse200:
        """Search decision definitions

 Search for decision definitions based on given criteria.

Args:
    body (SearchDecisionDefinitionsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchDecisionDefinitionsResponse200 | SearchDecisionDefinitionsResponse400 | SearchDecisionDefinitionsResponse401 | SearchDecisionDefinitionsResponse403 | SearchDecisionDefinitionsResponse500]"""
        from .api.decision_definition.search_decision_definitions import asyncio as search_decision_definitions_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_decision_definitions_asyncio(**_kwargs)


    def get_decision_definition_xml(self, decision_definition_key: str, **kwargs: Any) -> GetDecisionDefinitionXMLResponse400:
        """Get decision definition XML

 Returns decision definition as XML.

Args:
    decision_definition_key (str): System-generated key for a decision definition. Example:
        2251799813326547.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetDecisionDefinitionXMLResponse400 | GetDecisionDefinitionXMLResponse401 | GetDecisionDefinitionXMLResponse403 | GetDecisionDefinitionXMLResponse404 | GetDecisionDefinitionXMLResponse500 | str]"""
        from .api.decision_definition.get_decision_definition_xml import sync as get_decision_definition_xml_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_decision_definition_xml_sync(**_kwargs)


    async def get_decision_definition_xml_async(self, decision_definition_key: str, **kwargs: Any) -> GetDecisionDefinitionXMLResponse400:
        """Get decision definition XML

 Returns decision definition as XML.

Args:
    decision_definition_key (str): System-generated key for a decision definition. Example:
        2251799813326547.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetDecisionDefinitionXMLResponse400 | GetDecisionDefinitionXMLResponse401 | GetDecisionDefinitionXMLResponse403 | GetDecisionDefinitionXMLResponse404 | GetDecisionDefinitionXMLResponse500 | str]"""
        from .api.decision_definition.get_decision_definition_xml import asyncio as get_decision_definition_xml_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_decision_definition_xml_asyncio(**_kwargs)


    def create_authorization(self, *, data: Object | Object1, **kwargs: Any) -> CreateAuthorizationResponse201:
        """Create authorization

 Create the authorization.

Args:
    body (Object | Object1): Defines an authorization request.
        Either an id-based or a property-based authorization can be provided.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateAuthorizationResponse201 | CreateAuthorizationResponse400 | CreateAuthorizationResponse401 | CreateAuthorizationResponse403 | CreateAuthorizationResponse404 | CreateAuthorizationResponse500 | CreateAuthorizationResponse503]"""
        from .api.authorization.create_authorization import sync as create_authorization_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return create_authorization_sync(**_kwargs)


    async def create_authorization_async(self, *, data: Object | Object1, **kwargs: Any) -> CreateAuthorizationResponse201:
        """Create authorization

 Create the authorization.

Args:
    body (Object | Object1): Defines an authorization request.
        Either an id-based or a property-based authorization can be provided.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateAuthorizationResponse201 | CreateAuthorizationResponse400 | CreateAuthorizationResponse401 | CreateAuthorizationResponse403 | CreateAuthorizationResponse404 | CreateAuthorizationResponse500 | CreateAuthorizationResponse503]"""
        from .api.authorization.create_authorization import asyncio as create_authorization_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await create_authorization_asyncio(**_kwargs)


    def get_authorization(self, authorization_key: str, **kwargs: Any) -> GetAuthorizationResponse200:
        """Get authorization

 Get authorization by the given key.

Args:
    authorization_key (str): System-generated key for an authorization. Example:
        2251799813684332.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetAuthorizationResponse200 | GetAuthorizationResponse401 | GetAuthorizationResponse403 | GetAuthorizationResponse404 | GetAuthorizationResponse500]"""
        from .api.authorization.get_authorization import sync as get_authorization_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_authorization_sync(**_kwargs)


    async def get_authorization_async(self, authorization_key: str, **kwargs: Any) -> GetAuthorizationResponse200:
        """Get authorization

 Get authorization by the given key.

Args:
    authorization_key (str): System-generated key for an authorization. Example:
        2251799813684332.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetAuthorizationResponse200 | GetAuthorizationResponse401 | GetAuthorizationResponse403 | GetAuthorizationResponse404 | GetAuthorizationResponse500]"""
        from .api.authorization.get_authorization import asyncio as get_authorization_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_authorization_asyncio(**_kwargs)


    def update_authorization(self, authorization_key: str, *, data: Object | Object1, **kwargs: Any) -> Any:
        """Update authorization

 Update the authorization with the given key.

Args:
    authorization_key (str): System-generated key for an authorization. Example:
        2251799813684332.
    body (Object | Object1): Defines an authorization request.
        Either an id-based or a property-based authorization can be provided.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UpdateAuthorizationResponse401 | UpdateAuthorizationResponse404 | UpdateAuthorizationResponse500 | UpdateAuthorizationResponse503]"""
        from .api.authorization.update_authorization import sync as update_authorization_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return update_authorization_sync(**_kwargs)


    async def update_authorization_async(self, authorization_key: str, *, data: Object | Object1, **kwargs: Any) -> Any:
        """Update authorization

 Update the authorization with the given key.

Args:
    authorization_key (str): System-generated key for an authorization. Example:
        2251799813684332.
    body (Object | Object1): Defines an authorization request.
        Either an id-based or a property-based authorization can be provided.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UpdateAuthorizationResponse401 | UpdateAuthorizationResponse404 | UpdateAuthorizationResponse500 | UpdateAuthorizationResponse503]"""
        from .api.authorization.update_authorization import asyncio as update_authorization_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await update_authorization_asyncio(**_kwargs)


    def search_authorizations(self, *, data: SearchAuthorizationsData, **kwargs: Any) -> SearchAuthorizationsResponse200:
        """Search authorizations

 Search for authorizations based on given criteria.

Args:
    body (SearchAuthorizationsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchAuthorizationsResponse200 | SearchAuthorizationsResponse400 | SearchAuthorizationsResponse401 | SearchAuthorizationsResponse403 | SearchAuthorizationsResponse500]"""
        from .api.authorization.search_authorizations import sync as search_authorizations_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_authorizations_sync(**_kwargs)


    async def search_authorizations_async(self, *, data: SearchAuthorizationsData, **kwargs: Any) -> SearchAuthorizationsResponse200:
        """Search authorizations

 Search for authorizations based on given criteria.

Args:
    body (SearchAuthorizationsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchAuthorizationsResponse200 | SearchAuthorizationsResponse400 | SearchAuthorizationsResponse401 | SearchAuthorizationsResponse403 | SearchAuthorizationsResponse500]"""
        from .api.authorization.search_authorizations import asyncio as search_authorizations_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_authorizations_asyncio(**_kwargs)


    def delete_authorization(self, authorization_key: str, **kwargs: Any) -> Any:
        """Delete authorization

 Deletes the authorization with the given key.

Args:
    authorization_key (str): System-generated key for an authorization. Example:
        2251799813684332.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteAuthorizationResponse401 | DeleteAuthorizationResponse404 | DeleteAuthorizationResponse500 | DeleteAuthorizationResponse503]"""
        from .api.authorization.delete_authorization import sync as delete_authorization_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return delete_authorization_sync(**_kwargs)


    async def delete_authorization_async(self, authorization_key: str, **kwargs: Any) -> Any:
        """Delete authorization

 Deletes the authorization with the given key.

Args:
    authorization_key (str): System-generated key for an authorization. Example:
        2251799813684332.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteAuthorizationResponse401 | DeleteAuthorizationResponse404 | DeleteAuthorizationResponse500 | DeleteAuthorizationResponse503]"""
        from .api.authorization.delete_authorization import asyncio as delete_authorization_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await delete_authorization_asyncio(**_kwargs)


    def search_incidents(self, *, data: SearchIncidentsData, **kwargs: Any) -> SearchIncidentsResponse200:
        """Search incidents

 Search for incidents based on given criteria.

Args:
    body (SearchIncidentsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchIncidentsResponse200 | SearchIncidentsResponse400 | SearchIncidentsResponse401 | SearchIncidentsResponse403 | SearchIncidentsResponse500]"""
        from .api.incident.search_incidents import sync as search_incidents_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_incidents_sync(**_kwargs)


    async def search_incidents_async(self, *, data: SearchIncidentsData, **kwargs: Any) -> SearchIncidentsResponse200:
        """Search incidents

 Search for incidents based on given criteria.

Args:
    body (SearchIncidentsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchIncidentsResponse200 | SearchIncidentsResponse400 | SearchIncidentsResponse401 | SearchIncidentsResponse403 | SearchIncidentsResponse500]"""
        from .api.incident.search_incidents import asyncio as search_incidents_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_incidents_asyncio(**_kwargs)


    def get_process_instance_statistics_by_definition(self, *, data: GetProcessInstanceStatisticsByDefinitionData, **kwargs: Any) -> GetProcessInstanceStatisticsByDefinitionResponse200:
        """Get process instance statistics by definition

 Returns statistics for active process instances with incidents, grouped by process
definition. The result set is scoped to a specific incident error hash code, which must be
provided as a filter in the request body.

Args:
    body (GetProcessInstanceStatisticsByDefinitionData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetProcessInstanceStatisticsByDefinitionResponse200 | GetProcessInstanceStatisticsByDefinitionResponse400 | GetProcessInstanceStatisticsByDefinitionResponse401 | GetProcessInstanceStatisticsByDefinitionResponse403 | GetProcessInstanceStatisticsByDefinitionResponse500]"""
        from .api.incident.get_process_instance_statistics_by_definition import sync as get_process_instance_statistics_by_definition_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_process_instance_statistics_by_definition_sync(**_kwargs)


    async def get_process_instance_statistics_by_definition_async(self, *, data: GetProcessInstanceStatisticsByDefinitionData, **kwargs: Any) -> GetProcessInstanceStatisticsByDefinitionResponse200:
        """Get process instance statistics by definition

 Returns statistics for active process instances with incidents, grouped by process
definition. The result set is scoped to a specific incident error hash code, which must be
provided as a filter in the request body.

Args:
    body (GetProcessInstanceStatisticsByDefinitionData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetProcessInstanceStatisticsByDefinitionResponse200 | GetProcessInstanceStatisticsByDefinitionResponse400 | GetProcessInstanceStatisticsByDefinitionResponse401 | GetProcessInstanceStatisticsByDefinitionResponse403 | GetProcessInstanceStatisticsByDefinitionResponse500]"""
        from .api.incident.get_process_instance_statistics_by_definition import asyncio as get_process_instance_statistics_by_definition_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_process_instance_statistics_by_definition_asyncio(**_kwargs)


    def get_incident(self, incident_key: str, **kwargs: Any) -> GetIncidentResponse200:
        """Get incident

 Returns incident as JSON.

Args:
    incident_key (str): System-generated key for a incident. Example: 2251799813689432.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetIncidentResponse200 | GetIncidentResponse400 | GetIncidentResponse401 | GetIncidentResponse403 | GetIncidentResponse404 | GetIncidentResponse500]"""
        from .api.incident.get_incident import sync as get_incident_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_incident_sync(**_kwargs)


    async def get_incident_async(self, incident_key: str, **kwargs: Any) -> GetIncidentResponse200:
        """Get incident

 Returns incident as JSON.

Args:
    incident_key (str): System-generated key for a incident. Example: 2251799813689432.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetIncidentResponse200 | GetIncidentResponse400 | GetIncidentResponse401 | GetIncidentResponse403 | GetIncidentResponse404 | GetIncidentResponse500]"""
        from .api.incident.get_incident import asyncio as get_incident_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_incident_asyncio(**_kwargs)


    def resolve_incident(self, incident_key: str, *, data: ResolveIncidentData, **kwargs: Any) -> Any:
        """Resolve incident

 Marks the incident as resolved; most likely a call to Update job will be necessary
to reset the job's retries, followed by this call.

Args:
    incident_key (str): System-generated key for a incident. Example: 2251799813689432.
    body (ResolveIncidentData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | ResolveIncidentResponse400 | ResolveIncidentResponse404 | ResolveIncidentResponse500 | ResolveIncidentResponse503]"""
        from .api.incident.resolve_incident import sync as resolve_incident_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return resolve_incident_sync(**_kwargs)


    async def resolve_incident_async(self, incident_key: str, *, data: ResolveIncidentData, **kwargs: Any) -> Any:
        """Resolve incident

 Marks the incident as resolved; most likely a call to Update job will be necessary
to reset the job's retries, followed by this call.

Args:
    incident_key (str): System-generated key for a incident. Example: 2251799813689432.
    body (ResolveIncidentData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | ResolveIncidentResponse400 | ResolveIncidentResponse404 | ResolveIncidentResponse500 | ResolveIncidentResponse503]"""
        from .api.incident.resolve_incident import asyncio as resolve_incident_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await resolve_incident_asyncio(**_kwargs)


    def get_process_instance_statistics_by_error(self, *, data: GetProcessInstanceStatisticsByErrorData, **kwargs: Any) -> GetProcessInstanceStatisticsByErrorResponse200:
        """Get process instance statistics by error

 Returns statistics for active process instances that currently have active incidents,
grouped by incident error hash code.

Args:
    body (GetProcessInstanceStatisticsByErrorData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetProcessInstanceStatisticsByErrorResponse200 | GetProcessInstanceStatisticsByErrorResponse400 | GetProcessInstanceStatisticsByErrorResponse401 | GetProcessInstanceStatisticsByErrorResponse403 | GetProcessInstanceStatisticsByErrorResponse500]"""
        from .api.incident.get_process_instance_statistics_by_error import sync as get_process_instance_statistics_by_error_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_process_instance_statistics_by_error_sync(**_kwargs)


    async def get_process_instance_statistics_by_error_async(self, *, data: GetProcessInstanceStatisticsByErrorData, **kwargs: Any) -> GetProcessInstanceStatisticsByErrorResponse200:
        """Get process instance statistics by error

 Returns statistics for active process instances that currently have active incidents,
grouped by incident error hash code.

Args:
    body (GetProcessInstanceStatisticsByErrorData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetProcessInstanceStatisticsByErrorResponse200 | GetProcessInstanceStatisticsByErrorResponse400 | GetProcessInstanceStatisticsByErrorResponse401 | GetProcessInstanceStatisticsByErrorResponse403 | GetProcessInstanceStatisticsByErrorResponse500]"""
        from .api.incident.get_process_instance_statistics_by_error import asyncio as get_process_instance_statistics_by_error_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_process_instance_statistics_by_error_asyncio(**_kwargs)


    def get_user(self, username: str, **kwargs: Any) -> GetUserResponse200:
        """Get user

 Get a user by its username.

Args:
    username (str): The unique name of a user. Example: swillis.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetUserResponse200 | GetUserResponse401 | GetUserResponse403 | GetUserResponse404 | GetUserResponse500]"""
        from .api.user.get_user import sync as get_user_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_user_sync(**_kwargs)


    async def get_user_async(self, username: str, **kwargs: Any) -> GetUserResponse200:
        """Get user

 Get a user by its username.

Args:
    username (str): The unique name of a user. Example: swillis.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetUserResponse200 | GetUserResponse401 | GetUserResponse403 | GetUserResponse404 | GetUserResponse500]"""
        from .api.user.get_user import asyncio as get_user_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_user_asyncio(**_kwargs)


    def delete_user(self, username: str, **kwargs: Any) -> Any:
        """Delete user

 Deletes a user.

Args:
    username (str): The unique name of a user. Example: swillis.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteUserResponse400 | DeleteUserResponse404 | DeleteUserResponse500 | DeleteUserResponse503]"""
        from .api.user.delete_user import sync as delete_user_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return delete_user_sync(**_kwargs)


    async def delete_user_async(self, username: str, **kwargs: Any) -> Any:
        """Delete user

 Deletes a user.

Args:
    username (str): The unique name of a user. Example: swillis.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteUserResponse400 | DeleteUserResponse404 | DeleteUserResponse500 | DeleteUserResponse503]"""
        from .api.user.delete_user import asyncio as delete_user_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await delete_user_asyncio(**_kwargs)


    def create_user(self, *, data: CreateUserData, **kwargs: Any) -> CreateUserResponse201:
        """Create user

 Create a new user.

Args:
    body (CreateUserData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateUserResponse201 | CreateUserResponse400 | CreateUserResponse401 | CreateUserResponse403 | CreateUserResponse409 | CreateUserResponse500 | CreateUserResponse503]"""
        from .api.user.create_user import sync as create_user_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return create_user_sync(**_kwargs)


    async def create_user_async(self, *, data: CreateUserData, **kwargs: Any) -> CreateUserResponse201:
        """Create user

 Create a new user.

Args:
    body (CreateUserData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateUserResponse201 | CreateUserResponse400 | CreateUserResponse401 | CreateUserResponse403 | CreateUserResponse409 | CreateUserResponse500 | CreateUserResponse503]"""
        from .api.user.create_user import asyncio as create_user_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await create_user_asyncio(**_kwargs)


    def search_users(self, *, data: SearchUsersData, **kwargs: Any) -> SearchUsersResponse200:
        """Search users

 Search for users based on given criteria.

Args:
    body (SearchUsersData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchUsersResponse200 | SearchUsersResponse400 | SearchUsersResponse401 | SearchUsersResponse403 | SearchUsersResponse500]"""
        from .api.user.search_users import sync as search_users_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_users_sync(**_kwargs)


    async def search_users_async(self, *, data: SearchUsersData, **kwargs: Any) -> SearchUsersResponse200:
        """Search users

 Search for users based on given criteria.

Args:
    body (SearchUsersData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchUsersResponse200 | SearchUsersResponse400 | SearchUsersResponse401 | SearchUsersResponse403 | SearchUsersResponse500]"""
        from .api.user.search_users import asyncio as search_users_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_users_asyncio(**_kwargs)


    def update_user(self, username: str, *, data: UpdateUserData, **kwargs: Any) -> UpdateUserResponse200:
        """Update user

 Updates a user.

Args:
    username (str): The unique name of a user. Example: swillis.
    body (UpdateUserData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[UpdateUserResponse200 | UpdateUserResponse400 | UpdateUserResponse403 | UpdateUserResponse404 | UpdateUserResponse500 | UpdateUserResponse503]"""
        from .api.user.update_user import sync as update_user_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return update_user_sync(**_kwargs)


    async def update_user_async(self, username: str, *, data: UpdateUserData, **kwargs: Any) -> UpdateUserResponse200:
        """Update user

 Updates a user.

Args:
    username (str): The unique name of a user. Example: swillis.
    body (UpdateUserData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[UpdateUserResponse200 | UpdateUserResponse400 | UpdateUserResponse403 | UpdateUserResponse404 | UpdateUserResponse500 | UpdateUserResponse503]"""
        from .api.user.update_user import asyncio as update_user_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await update_user_asyncio(**_kwargs)


    def get_usage_metrics(self, *, start_time: datetime.datetime, end_time: datetime.datetime, tenant_id: str | Unset = UNSET, with_tenants: bool | Unset = False, **kwargs: Any) -> GetUsageMetricsResponse200:
        """Get usage metrics

 Retrieve the usage metrics based on given criteria.

Args:
    start_time (datetime.datetime):  Example: 2025-06-07T13:14:15Z.
    end_time (datetime.datetime):  Example: 2025-06-07T13:14:15Z.
    tenant_id (str | Unset): The unique identifier of the tenant. Example: customer-service.
    with_tenants (bool | Unset):  Default: False.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetUsageMetricsResponse200 | GetUsageMetricsResponse400 | GetUsageMetricsResponse401 | GetUsageMetricsResponse403 | GetUsageMetricsResponse500]"""
        from .api.system.get_usage_metrics import sync as get_usage_metrics_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_usage_metrics_sync(**_kwargs)


    async def get_usage_metrics_async(self, *, start_time: datetime.datetime, end_time: datetime.datetime, tenant_id: str | Unset = UNSET, with_tenants: bool | Unset = False, **kwargs: Any) -> GetUsageMetricsResponse200:
        """Get usage metrics

 Retrieve the usage metrics based on given criteria.

Args:
    start_time (datetime.datetime):  Example: 2025-06-07T13:14:15Z.
    end_time (datetime.datetime):  Example: 2025-06-07T13:14:15Z.
    tenant_id (str | Unset): The unique identifier of the tenant. Example: customer-service.
    with_tenants (bool | Unset):  Default: False.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetUsageMetricsResponse200 | GetUsageMetricsResponse400 | GetUsageMetricsResponse401 | GetUsageMetricsResponse403 | GetUsageMetricsResponse500]"""
        from .api.system.get_usage_metrics import asyncio as get_usage_metrics_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_usage_metrics_asyncio(**_kwargs)


    def update_role(self, role_id: str, *, data: UpdateRoleData, **kwargs: Any) -> UpdateRoleResponse200:
        """Update role

 Update a role with the given ID.

Args:
    role_id (str):
    body (UpdateRoleData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[UpdateRoleResponse200 | UpdateRoleResponse400 | UpdateRoleResponse401 | UpdateRoleResponse404 | UpdateRoleResponse500 | UpdateRoleResponse503]"""
        from .api.role.update_role import sync as update_role_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return update_role_sync(**_kwargs)


    async def update_role_async(self, role_id: str, *, data: UpdateRoleData, **kwargs: Any) -> UpdateRoleResponse200:
        """Update role

 Update a role with the given ID.

Args:
    role_id (str):
    body (UpdateRoleData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[UpdateRoleResponse200 | UpdateRoleResponse400 | UpdateRoleResponse401 | UpdateRoleResponse404 | UpdateRoleResponse500 | UpdateRoleResponse503]"""
        from .api.role.update_role import asyncio as update_role_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await update_role_asyncio(**_kwargs)


    def assign_role_to_client(self, role_id: str, client_id: str, **kwargs: Any) -> Any:
        """Assign a role to a client

 Assigns the specified role to the client. The client will inherit the authorizations associated with
this role.

Args:
    role_id (str):
    client_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignRoleToClientResponse400 | AssignRoleToClientResponse403 | AssignRoleToClientResponse404 | AssignRoleToClientResponse409 | AssignRoleToClientResponse500 | AssignRoleToClientResponse503]"""
        from .api.role.assign_role_to_client import sync as assign_role_to_client_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return assign_role_to_client_sync(**_kwargs)


    async def assign_role_to_client_async(self, role_id: str, client_id: str, **kwargs: Any) -> Any:
        """Assign a role to a client

 Assigns the specified role to the client. The client will inherit the authorizations associated with
this role.

Args:
    role_id (str):
    client_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignRoleToClientResponse400 | AssignRoleToClientResponse403 | AssignRoleToClientResponse404 | AssignRoleToClientResponse409 | AssignRoleToClientResponse500 | AssignRoleToClientResponse503]"""
        from .api.role.assign_role_to_client import asyncio as assign_role_to_client_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await assign_role_to_client_asyncio(**_kwargs)


    def get_role(self, role_id: str, **kwargs: Any) -> GetRoleResponse200:
        """Get role

 Get a role by its ID.

Args:
    role_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetRoleResponse200 | GetRoleResponse401 | GetRoleResponse403 | GetRoleResponse404 | GetRoleResponse500]"""
        from .api.role.get_role import sync as get_role_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_role_sync(**_kwargs)


    async def get_role_async(self, role_id: str, **kwargs: Any) -> GetRoleResponse200:
        """Get role

 Get a role by its ID.

Args:
    role_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetRoleResponse200 | GetRoleResponse401 | GetRoleResponse403 | GetRoleResponse404 | GetRoleResponse500]"""
        from .api.role.get_role import asyncio as get_role_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_role_asyncio(**_kwargs)


    def unassign_role_from_mapping_rule(self, role_id: str, mapping_rule_id: str, **kwargs: Any) -> Any:
        """Unassign a role from a mapping rule

 Unassigns a role from a mapping rule.

Args:
    role_id (str):
    mapping_rule_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignRoleFromMappingRuleResponse400 | UnassignRoleFromMappingRuleResponse403 | UnassignRoleFromMappingRuleResponse404 | UnassignRoleFromMappingRuleResponse500 | UnassignRoleFromMappingRuleResponse503]"""
        from .api.role.unassign_role_from_mapping_rule import sync as unassign_role_from_mapping_rule_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return unassign_role_from_mapping_rule_sync(**_kwargs)


    async def unassign_role_from_mapping_rule_async(self, role_id: str, mapping_rule_id: str, **kwargs: Any) -> Any:
        """Unassign a role from a mapping rule

 Unassigns a role from a mapping rule.

Args:
    role_id (str):
    mapping_rule_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignRoleFromMappingRuleResponse400 | UnassignRoleFromMappingRuleResponse403 | UnassignRoleFromMappingRuleResponse404 | UnassignRoleFromMappingRuleResponse500 | UnassignRoleFromMappingRuleResponse503]"""
        from .api.role.unassign_role_from_mapping_rule import asyncio as unassign_role_from_mapping_rule_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await unassign_role_from_mapping_rule_asyncio(**_kwargs)


    def search_users_for_role(self, role_id: str, *, data: SearchUsersForRoleData, **kwargs: Any) -> SearchUsersForRoleResponse200:
        """Search role users

 Search users with assigned role.

Args:
    role_id (str):
    body (SearchUsersForRoleData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchUsersForRoleResponse200 | SearchUsersForRoleResponse400 | SearchUsersForRoleResponse401 | SearchUsersForRoleResponse403 | SearchUsersForRoleResponse404 | SearchUsersForRoleResponse500]"""
        from .api.role.search_users_for_role import sync as search_users_for_role_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_users_for_role_sync(**_kwargs)


    async def search_users_for_role_async(self, role_id: str, *, data: SearchUsersForRoleData, **kwargs: Any) -> SearchUsersForRoleResponse200:
        """Search role users

 Search users with assigned role.

Args:
    role_id (str):
    body (SearchUsersForRoleData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchUsersForRoleResponse200 | SearchUsersForRoleResponse400 | SearchUsersForRoleResponse401 | SearchUsersForRoleResponse403 | SearchUsersForRoleResponse404 | SearchUsersForRoleResponse500]"""
        from .api.role.search_users_for_role import asyncio as search_users_for_role_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_users_for_role_asyncio(**_kwargs)


    def search_mapping_rules_for_role(self, role_id: str, *, data: SearchMappingRulesForRoleData, **kwargs: Any) -> SearchMappingRulesForRoleResponse200:
        """Search role mapping rules

 Search mapping rules with assigned role.

Args:
    role_id (str):
    body (SearchMappingRulesForRoleData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchMappingRulesForRoleResponse200 | SearchMappingRulesForRoleResponse400 | SearchMappingRulesForRoleResponse401 | SearchMappingRulesForRoleResponse403 | SearchMappingRulesForRoleResponse404 | SearchMappingRulesForRoleResponse500]"""
        from .api.role.search_mapping_rules_for_role import sync as search_mapping_rules_for_role_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_mapping_rules_for_role_sync(**_kwargs)


    async def search_mapping_rules_for_role_async(self, role_id: str, *, data: SearchMappingRulesForRoleData, **kwargs: Any) -> SearchMappingRulesForRoleResponse200:
        """Search role mapping rules

 Search mapping rules with assigned role.

Args:
    role_id (str):
    body (SearchMappingRulesForRoleData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchMappingRulesForRoleResponse200 | SearchMappingRulesForRoleResponse400 | SearchMappingRulesForRoleResponse401 | SearchMappingRulesForRoleResponse403 | SearchMappingRulesForRoleResponse404 | SearchMappingRulesForRoleResponse500]"""
        from .api.role.search_mapping_rules_for_role import asyncio as search_mapping_rules_for_role_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_mapping_rules_for_role_asyncio(**_kwargs)


    def search_groups_for_role(self, role_id: str, *, data: SearchGroupsForRoleData, **kwargs: Any) -> SearchGroupsForRoleResponse200:
        """Search role groups

 Search groups with assigned role.

Args:
    role_id (str):
    body (SearchGroupsForRoleData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchGroupsForRoleResponse200 | SearchGroupsForRoleResponse400 | SearchGroupsForRoleResponse401 | SearchGroupsForRoleResponse403 | SearchGroupsForRoleResponse404 | SearchGroupsForRoleResponse500]"""
        from .api.role.search_groups_for_role import sync as search_groups_for_role_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_groups_for_role_sync(**_kwargs)


    async def search_groups_for_role_async(self, role_id: str, *, data: SearchGroupsForRoleData, **kwargs: Any) -> SearchGroupsForRoleResponse200:
        """Search role groups

 Search groups with assigned role.

Args:
    role_id (str):
    body (SearchGroupsForRoleData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchGroupsForRoleResponse200 | SearchGroupsForRoleResponse400 | SearchGroupsForRoleResponse401 | SearchGroupsForRoleResponse403 | SearchGroupsForRoleResponse404 | SearchGroupsForRoleResponse500]"""
        from .api.role.search_groups_for_role import asyncio as search_groups_for_role_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_groups_for_role_asyncio(**_kwargs)


    def search_roles(self, *, data: SearchRolesData, **kwargs: Any) -> Any:
        """Search roles

 Search for roles based on given criteria.

Args:
    body (SearchRolesData): Role search request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | SearchRolesResponse200 | SearchRolesResponse400 | SearchRolesResponse401 | SearchRolesResponse403]"""
        from .api.role.search_roles import sync as search_roles_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_roles_sync(**_kwargs)


    async def search_roles_async(self, *, data: SearchRolesData, **kwargs: Any) -> Any:
        """Search roles

 Search for roles based on given criteria.

Args:
    body (SearchRolesData): Role search request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | SearchRolesResponse200 | SearchRolesResponse400 | SearchRolesResponse401 | SearchRolesResponse403]"""
        from .api.role.search_roles import asyncio as search_roles_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_roles_asyncio(**_kwargs)


    def search_clients_for_role(self, role_id: str, *, data: SearchClientsForRoleData, **kwargs: Any) -> SearchClientsForRoleResponse200:
        """Search role clients

 Search clients with assigned role.

Args:
    role_id (str):
    body (SearchClientsForRoleData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchClientsForRoleResponse200 | SearchClientsForRoleResponse400 | SearchClientsForRoleResponse401 | SearchClientsForRoleResponse403 | SearchClientsForRoleResponse404 | SearchClientsForRoleResponse500]"""
        from .api.role.search_clients_for_role import sync as search_clients_for_role_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return search_clients_for_role_sync(**_kwargs)


    async def search_clients_for_role_async(self, role_id: str, *, data: SearchClientsForRoleData, **kwargs: Any) -> SearchClientsForRoleResponse200:
        """Search role clients

 Search clients with assigned role.

Args:
    role_id (str):
    body (SearchClientsForRoleData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchClientsForRoleResponse200 | SearchClientsForRoleResponse400 | SearchClientsForRoleResponse401 | SearchClientsForRoleResponse403 | SearchClientsForRoleResponse404 | SearchClientsForRoleResponse500]"""
        from .api.role.search_clients_for_role import asyncio as search_clients_for_role_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await search_clients_for_role_asyncio(**_kwargs)


    def create_role(self, *, data: CreateRoleData, **kwargs: Any) -> CreateRoleResponse201:
        """Create role

 Create a new role.

Args:
    body (CreateRoleData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateRoleResponse201 | CreateRoleResponse400 | CreateRoleResponse401 | CreateRoleResponse403 | CreateRoleResponse500 | CreateRoleResponse503]"""
        from .api.role.create_role import sync as create_role_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return create_role_sync(**_kwargs)


    async def create_role_async(self, *, data: CreateRoleData, **kwargs: Any) -> CreateRoleResponse201:
        """Create role

 Create a new role.

Args:
    body (CreateRoleData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateRoleResponse201 | CreateRoleResponse400 | CreateRoleResponse401 | CreateRoleResponse403 | CreateRoleResponse500 | CreateRoleResponse503]"""
        from .api.role.create_role import asyncio as create_role_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await create_role_asyncio(**_kwargs)


    def assign_role_to_group(self, role_id: str, group_id: str, **kwargs: Any) -> Any:
        """Assign a role to a group

 Assigns the specified role to the group. Every member of the group (user or client) will inherit the
authorizations associated with this role.

Args:
    role_id (str):
    group_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignRoleToGroupResponse400 | AssignRoleToGroupResponse403 | AssignRoleToGroupResponse404 | AssignRoleToGroupResponse409 | AssignRoleToGroupResponse500 | AssignRoleToGroupResponse503]"""
        from .api.role.assign_role_to_group import sync as assign_role_to_group_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return assign_role_to_group_sync(**_kwargs)


    async def assign_role_to_group_async(self, role_id: str, group_id: str, **kwargs: Any) -> Any:
        """Assign a role to a group

 Assigns the specified role to the group. Every member of the group (user or client) will inherit the
authorizations associated with this role.

Args:
    role_id (str):
    group_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignRoleToGroupResponse400 | AssignRoleToGroupResponse403 | AssignRoleToGroupResponse404 | AssignRoleToGroupResponse409 | AssignRoleToGroupResponse500 | AssignRoleToGroupResponse503]"""
        from .api.role.assign_role_to_group import asyncio as assign_role_to_group_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await assign_role_to_group_asyncio(**_kwargs)


    def assign_role_to_mapping_rule(self, role_id: str, mapping_rule_id: str, **kwargs: Any) -> Any:
        """Assign a role to a mapping rule

 Assigns a role to a mapping rule.

Args:
    role_id (str):
    mapping_rule_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignRoleToMappingRuleResponse400 | AssignRoleToMappingRuleResponse403 | AssignRoleToMappingRuleResponse404 | AssignRoleToMappingRuleResponse409 | AssignRoleToMappingRuleResponse500 | AssignRoleToMappingRuleResponse503]"""
        from .api.role.assign_role_to_mapping_rule import sync as assign_role_to_mapping_rule_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return assign_role_to_mapping_rule_sync(**_kwargs)


    async def assign_role_to_mapping_rule_async(self, role_id: str, mapping_rule_id: str, **kwargs: Any) -> Any:
        """Assign a role to a mapping rule

 Assigns a role to a mapping rule.

Args:
    role_id (str):
    mapping_rule_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignRoleToMappingRuleResponse400 | AssignRoleToMappingRuleResponse403 | AssignRoleToMappingRuleResponse404 | AssignRoleToMappingRuleResponse409 | AssignRoleToMappingRuleResponse500 | AssignRoleToMappingRuleResponse503]"""
        from .api.role.assign_role_to_mapping_rule import asyncio as assign_role_to_mapping_rule_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await assign_role_to_mapping_rule_asyncio(**_kwargs)


    def unassign_role_from_client(self, role_id: str, client_id: str, **kwargs: Any) -> Any:
        """Unassign a role from a client

 Unassigns the specified role from the client. The client will no longer inherit the authorizations
associated with this role.

Args:
    role_id (str):
    client_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignRoleFromClientResponse400 | UnassignRoleFromClientResponse403 | UnassignRoleFromClientResponse404 | UnassignRoleFromClientResponse500 | UnassignRoleFromClientResponse503]"""
        from .api.role.unassign_role_from_client import sync as unassign_role_from_client_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return unassign_role_from_client_sync(**_kwargs)


    async def unassign_role_from_client_async(self, role_id: str, client_id: str, **kwargs: Any) -> Any:
        """Unassign a role from a client

 Unassigns the specified role from the client. The client will no longer inherit the authorizations
associated with this role.

Args:
    role_id (str):
    client_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignRoleFromClientResponse400 | UnassignRoleFromClientResponse403 | UnassignRoleFromClientResponse404 | UnassignRoleFromClientResponse500 | UnassignRoleFromClientResponse503]"""
        from .api.role.unassign_role_from_client import asyncio as unassign_role_from_client_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await unassign_role_from_client_asyncio(**_kwargs)


    def delete_role(self, role_id: str, **kwargs: Any) -> Any:
        """Delete role

 Deletes the role with the given ID.

Args:
    role_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteRoleResponse401 | DeleteRoleResponse404 | DeleteRoleResponse500 | DeleteRoleResponse503]"""
        from .api.role.delete_role import sync as delete_role_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return delete_role_sync(**_kwargs)


    async def delete_role_async(self, role_id: str, **kwargs: Any) -> Any:
        """Delete role

 Deletes the role with the given ID.

Args:
    role_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteRoleResponse401 | DeleteRoleResponse404 | DeleteRoleResponse500 | DeleteRoleResponse503]"""
        from .api.role.delete_role import asyncio as delete_role_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await delete_role_asyncio(**_kwargs)


    def assign_role_to_user(self, role_id: str, username: str, **kwargs: Any) -> Any:
        """Assign a role to a user

 Assigns the specified role to the user. The user will inherit the authorizations associated with
this role.

Args:
    role_id (str):
    username (str): The unique name of a user. Example: swillis.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignRoleToUserResponse400 | AssignRoleToUserResponse403 | AssignRoleToUserResponse404 | AssignRoleToUserResponse409 | AssignRoleToUserResponse500 | AssignRoleToUserResponse503]"""
        from .api.role.assign_role_to_user import sync as assign_role_to_user_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return assign_role_to_user_sync(**_kwargs)


    async def assign_role_to_user_async(self, role_id: str, username: str, **kwargs: Any) -> Any:
        """Assign a role to a user

 Assigns the specified role to the user. The user will inherit the authorizations associated with
this role.

Args:
    role_id (str):
    username (str): The unique name of a user. Example: swillis.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignRoleToUserResponse400 | AssignRoleToUserResponse403 | AssignRoleToUserResponse404 | AssignRoleToUserResponse409 | AssignRoleToUserResponse500 | AssignRoleToUserResponse503]"""
        from .api.role.assign_role_to_user import asyncio as assign_role_to_user_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await assign_role_to_user_asyncio(**_kwargs)


    def unassign_role_from_group(self, role_id: str, group_id: str, **kwargs: Any) -> Any:
        """Unassign a role from a group

 Unassigns the specified role from the group. All group members (user or client) no longer inherit
the authorizations associated with this role.

Args:
    role_id (str):
    group_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignRoleFromGroupResponse400 | UnassignRoleFromGroupResponse403 | UnassignRoleFromGroupResponse404 | UnassignRoleFromGroupResponse500 | UnassignRoleFromGroupResponse503]"""
        from .api.role.unassign_role_from_group import sync as unassign_role_from_group_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return unassign_role_from_group_sync(**_kwargs)


    async def unassign_role_from_group_async(self, role_id: str, group_id: str, **kwargs: Any) -> Any:
        """Unassign a role from a group

 Unassigns the specified role from the group. All group members (user or client) no longer inherit
the authorizations associated with this role.

Args:
    role_id (str):
    group_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignRoleFromGroupResponse400 | UnassignRoleFromGroupResponse403 | UnassignRoleFromGroupResponse404 | UnassignRoleFromGroupResponse500 | UnassignRoleFromGroupResponse503]"""
        from .api.role.unassign_role_from_group import asyncio as unassign_role_from_group_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await unassign_role_from_group_asyncio(**_kwargs)


    def unassign_role_from_user(self, role_id: str, username: str, **kwargs: Any) -> Any:
        """Unassign a role from a user

 Unassigns a role from a user. The user will no longer inherit the authorizations associated with
this role.

Args:
    role_id (str):
    username (str): The unique name of a user. Example: swillis.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignRoleFromUserResponse400 | UnassignRoleFromUserResponse403 | UnassignRoleFromUserResponse404 | UnassignRoleFromUserResponse500 | UnassignRoleFromUserResponse503]"""
        from .api.role.unassign_role_from_user import sync as unassign_role_from_user_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return unassign_role_from_user_sync(**_kwargs)


    async def unassign_role_from_user_async(self, role_id: str, username: str, **kwargs: Any) -> Any:
        """Unassign a role from a user

 Unassigns a role from a user. The user will no longer inherit the authorizations associated with
this role.

Args:
    role_id (str):
    username (str): The unique name of a user. Example: swillis.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignRoleFromUserResponse400 | UnassignRoleFromUserResponse403 | UnassignRoleFromUserResponse404 | UnassignRoleFromUserResponse500 | UnassignRoleFromUserResponse503]"""
        from .api.role.unassign_role_from_user import asyncio as unassign_role_from_user_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await unassign_role_from_user_asyncio(**_kwargs)


    def get_license(self, **kwargs: Any) -> GetLicenseResponse200:
        """Get license status

 Obtains the status of the current Camunda license.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetLicenseResponse200 | GetLicenseResponse500]"""
        from .api.license_.get_license import sync as get_license_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return get_license_sync(**_kwargs)


    async def get_license_async(self, **kwargs: Any) -> GetLicenseResponse200:
        """Get license status

 Obtains the status of the current Camunda license.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetLicenseResponse200 | GetLicenseResponse500]"""
        from .api.license_.get_license import asyncio as get_license_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await get_license_asyncio(**_kwargs)


    def broadcast_signal(self, *, data: BroadcastSignalData, **kwargs: Any) -> BroadcastSignalResponse200:
        """Broadcast signal

 Broadcasts a signal.

Args:
    body (BroadcastSignalData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[BroadcastSignalResponse200 | BroadcastSignalResponse400 | BroadcastSignalResponse404 | BroadcastSignalResponse500 | BroadcastSignalResponse503]"""
        from .api.signal.broadcast_signal import sync as broadcast_signal_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return broadcast_signal_sync(**_kwargs)


    async def broadcast_signal_async(self, *, data: BroadcastSignalData, **kwargs: Any) -> BroadcastSignalResponse200:
        """Broadcast signal

 Broadcasts a signal.

Args:
    body (BroadcastSignalData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[BroadcastSignalResponse200 | BroadcastSignalResponse400 | BroadcastSignalResponse404 | BroadcastSignalResponse500 | BroadcastSignalResponse503]"""
        from .api.signal.broadcast_signal import asyncio as broadcast_signal_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await broadcast_signal_asyncio(**_kwargs)


    def evaluate_conditionals(self, *, data: EvaluateConditionalsData, **kwargs: Any) -> EvaluateConditionalsResponse200:
        """Evaluate root level conditional start events

 Evaluates root-level conditional start events for process definitions.
If the evaluation is successful, it will return the keys of all created process instances, along
with their associated process definition key.
Multiple root-level conditional start events of the same process definition can trigger if their
conditions evaluate to true.

Args:
    body (EvaluateConditionalsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[EvaluateConditionalsResponse200 | EvaluateConditionalsResponse400 | EvaluateConditionalsResponse403 | EvaluateConditionalsResponse404 | EvaluateConditionalsResponse500 | EvaluateConditionalsResponse503]"""
        from .api.conditional.evaluate_conditionals import sync as evaluate_conditionals_sync
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return evaluate_conditionals_sync(**_kwargs)


    async def evaluate_conditionals_async(self, *, data: EvaluateConditionalsData, **kwargs: Any) -> EvaluateConditionalsResponse200:
        """Evaluate root level conditional start events

 Evaluates root-level conditional start events for process definitions.
If the evaluation is successful, it will return the keys of all created process instances, along
with their associated process definition key.
Multiple root-level conditional start events of the same process definition can trigger if their
conditions evaluate to true.

Args:
    body (EvaluateConditionalsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[EvaluateConditionalsResponse200 | EvaluateConditionalsResponse400 | EvaluateConditionalsResponse403 | EvaluateConditionalsResponse404 | EvaluateConditionalsResponse500 | EvaluateConditionalsResponse503]"""
        from .api.conditional.evaluate_conditionals import asyncio as evaluate_conditionals_asyncio
        _kwargs = locals()
        _kwargs.pop("self")
        _kwargs["client"] = self.client
        if "data" in _kwargs:
            _kwargs["body"] = _kwargs.pop("data")
        return await evaluate_conditionals_asyncio(**_kwargs)


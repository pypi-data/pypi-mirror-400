from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.processcreationbyid_runtime_instructions_item_type_0 import (
        ProcesscreationbyidRuntimeInstructionsItemType0,
    )
    from ..models.processcreationbyid_startinstructions_item import (
        ProcesscreationbyidStartinstructionsItem,
    )
    from ..models.processcreationbyid_variables import ProcesscreationbyidVariables


T = TypeVar("T", bound="Processcreationbyid")


@_attrs_define
class Processcreationbyid:
    """
    Attributes:
        process_definition_id (str): The BPMN process id of the process definition to start an instance of.
             Example: new-account-onboarding-workflow.
        process_definition_version (int | Unset): The version of the process. By default, the latest version of the
            process is used.
             Default: -1.
        variables (ProcesscreationbyidVariables | Unset): JSON object that will instantiate the variables for the root
            variable scope
            of the process instance.
        tenant_id (str | Unset): The tenant id of the process definition. Example: customer-service.
        operation_reference (int | Unset): A reference key chosen by the user that will be part of all records resulting
            from this operation.
            Must be > 0 if provided.
        start_instructions (list[ProcesscreationbyidStartinstructionsItem] | Unset): List of start instructions. By
            default, the process instance will start at
            the start event. If provided, the process instance will apply start instructions
            after it has been created.
        runtime_instructions (list[ProcesscreationbyidRuntimeInstructionsItemType0] | Unset): Runtime instructions
            (alpha). List of instructions that affect the runtime behavior of
            the process instance. Refer to specific instruction types for more details.

            This parameter is an alpha feature and may be subject to change
            in future releases.
        await_completion (bool | Unset): Wait for the process instance to complete. If the process instance completion
            does
            not occur within the requestTimeout, the request will be closed. This can lead to a 504
            response status. Disabled by default.
             Default: False.
        fetch_variables (list[str] | Unset): List of variables by name to be included in the response when
            awaitCompletion is set to true.
            If empty, all visible variables in the root scope will be returned.
        request_timeout (int | Unset): Timeout (in ms) the request waits for the process to complete. By default or
            when set to 0, the generic request timeout configured in the cluster is applied.
             Default: 0.
        tags (list[str] | Unset): List of tags. Tags need to start with a letter; then alphanumerics, `_`, `-`, `:`, or
            `.`; length ≤ 100. Example: ['high-touch', 'remediation'].
    """

    process_definition_id: ProcessDefinitionId
    process_definition_version: int | Unset = -1
    variables: ProcesscreationbyidVariables | Unset = UNSET
    tenant_id: TenantId | Unset = UNSET
    operation_reference: int | Unset = UNSET
    start_instructions: list[ProcesscreationbyidStartinstructionsItem] | Unset = UNSET
    runtime_instructions: (
        list[ProcesscreationbyidRuntimeInstructionsItemType0] | Unset
    ) = UNSET
    await_completion: bool | Unset = False
    fetch_variables: list[str] | Unset = UNSET
    request_timeout: int | Unset = 0
    tags: list[str] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.processcreationbyid_runtime_instructions_item_type_0 import (
            ProcesscreationbyidRuntimeInstructionsItemType0,
        )

        process_definition_id = self.process_definition_id

        process_definition_version = self.process_definition_version

        variables: dict[str, Any] | Unset = UNSET
        if not isinstance(self.variables, Unset):
            variables = self.variables.to_dict()

        tenant_id = self.tenant_id

        operation_reference = self.operation_reference

        start_instructions: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.start_instructions, Unset):
            start_instructions = []
            for start_instructions_item_data in self.start_instructions:
                start_instructions_item = start_instructions_item_data.to_dict()
                start_instructions.append(start_instructions_item)

        runtime_instructions: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.runtime_instructions, Unset):
            runtime_instructions = []
            for runtime_instructions_item_data in self.runtime_instructions:
                runtime_instructions_item: dict[str, Any]
                if isinstance(
                    runtime_instructions_item_data,
                    ProcesscreationbyidRuntimeInstructionsItemType0,
                ):
                    runtime_instructions_item = runtime_instructions_item_data.to_dict()

                runtime_instructions.append(runtime_instructions_item)

        await_completion = self.await_completion

        fetch_variables: list[str] | Unset = UNSET
        if not isinstance(self.fetch_variables, Unset):
            fetch_variables = self.fetch_variables

        request_timeout = self.request_timeout

        tags: list[str] | Unset = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "processDefinitionId": process_definition_id,
            }
        )
        if process_definition_version is not UNSET:
            field_dict["processDefinitionVersion"] = process_definition_version
        if variables is not UNSET:
            field_dict["variables"] = variables
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if operation_reference is not UNSET:
            field_dict["operationReference"] = operation_reference
        if start_instructions is not UNSET:
            field_dict["startInstructions"] = start_instructions
        if runtime_instructions is not UNSET:
            field_dict["runtimeInstructions"] = runtime_instructions
        if await_completion is not UNSET:
            field_dict["awaitCompletion"] = await_completion
        if fetch_variables is not UNSET:
            field_dict["fetchVariables"] = fetch_variables
        if request_timeout is not UNSET:
            field_dict["requestTimeout"] = request_timeout
        if tags is not UNSET:
            field_dict["tags"] = tags

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.processcreationbyid_runtime_instructions_item_type_0 import (
            ProcesscreationbyidRuntimeInstructionsItemType0,
        )
        from ..models.processcreationbyid_startinstructions_item import (
            ProcesscreationbyidStartinstructionsItem,
        )
        from ..models.processcreationbyid_variables import ProcesscreationbyidVariables

        d = dict(src_dict)
        process_definition_id = lift_process_definition_id(d.pop("processDefinitionId"))

        process_definition_version = d.pop("processDefinitionVersion", UNSET)

        _variables = d.pop("variables", UNSET)
        variables: ProcesscreationbyidVariables | Unset
        if isinstance(_variables, Unset):
            variables = UNSET
        else:
            variables = ProcesscreationbyidVariables.from_dict(_variables)

        tenant_id = lift_tenant_id(_val) if (_val := d.pop("tenantId", UNSET)) is not UNSET else UNSET

        operation_reference = d.pop("operationReference", UNSET)

        _start_instructions = d.pop("startInstructions", UNSET)
        start_instructions: list[ProcesscreationbyidStartinstructionsItem] | Unset = (
            UNSET
        )
        if _start_instructions is not UNSET:
            start_instructions = []
            for start_instructions_item_data in _start_instructions:
                start_instructions_item = (
                    ProcesscreationbyidStartinstructionsItem.from_dict(
                        start_instructions_item_data
                    )
                )

                start_instructions.append(start_instructions_item)

        _runtime_instructions = d.pop("runtimeInstructions", UNSET)
        runtime_instructions: (
            list[ProcesscreationbyidRuntimeInstructionsItemType0] | Unset
        ) = UNSET
        if _runtime_instructions is not UNSET:
            runtime_instructions = []
            for runtime_instructions_item_data in _runtime_instructions:

                def _parse_runtime_instructions_item(
                    data: object,
                ) -> ProcesscreationbyidRuntimeInstructionsItemType0:
                    if not isinstance(data, dict):
                        raise TypeError()
                    runtime_instructions_item_type_0 = (
                        ProcesscreationbyidRuntimeInstructionsItemType0.from_dict(data)
                    )

                    return runtime_instructions_item_type_0

                runtime_instructions_item = _parse_runtime_instructions_item(
                    runtime_instructions_item_data
                )

                runtime_instructions.append(runtime_instructions_item)

        await_completion = d.pop("awaitCompletion", UNSET)

        fetch_variables = cast(list[str], d.pop("fetchVariables", UNSET))

        request_timeout = d.pop("requestTimeout", UNSET)

        tags = cast(list[str], d.pop("tags", UNSET))

        processcreationbyid = cls(
            process_definition_id=process_definition_id,
            process_definition_version=process_definition_version,
            variables=variables,
            tenant_id=tenant_id,
            operation_reference=operation_reference,
            start_instructions=start_instructions,
            runtime_instructions=runtime_instructions,
            await_completion=await_completion,
            fetch_variables=fetch_variables,
            request_timeout=request_timeout,
            tags=tags,
        )

        return processcreationbyid

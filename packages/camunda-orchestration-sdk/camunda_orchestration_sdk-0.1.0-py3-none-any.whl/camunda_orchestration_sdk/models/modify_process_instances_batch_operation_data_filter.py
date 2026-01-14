from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.state_exactmatch_3 import StateExactmatch3
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.actorid_advancedfilter import ActoridAdvancedfilter
    from ..models.elementinstancekey_advancedfilter import (
        ElementinstancekeyAdvancedfilter,
    )
    from ..models.modify_process_instances_batch_operation_data_filter_or_item import (
        ModifyProcessInstancesBatchOperationDataFilterOrItem,
    )
    from ..models.modify_process_instances_batch_operation_data_filter_variables_item import (
        ModifyProcessInstancesBatchOperationDataFilterVariablesItem,
    )
    from ..models.partitionid_advancedfilter import PartitionidAdvancedfilter
    from ..models.processdefinitionkey_advancedfilter import (
        ProcessdefinitionkeyAdvancedfilter,
    )
    from ..models.processinstancekey_advancedfilter import (
        ProcessinstancekeyAdvancedfilter,
    )
    from ..models.state_advancedfilter_3 import StateAdvancedfilter3
    from ..models.state_advancedfilter_6 import StateAdvancedfilter6
    from ..models.timestamp_advancedfilter import TimestampAdvancedfilter


T = TypeVar("T", bound="ModifyProcessInstancesBatchOperationDataFilter")


@_attrs_define
class ModifyProcessInstancesBatchOperationDataFilter:
    """The process instance filter.

    Attributes:
        process_definition_id (ActoridAdvancedfilter | str | Unset):
        process_definition_name (ActoridAdvancedfilter | str | Unset):
        process_definition_version (int | PartitionidAdvancedfilter | Unset):
        process_definition_version_tag (ActoridAdvancedfilter | str | Unset):
        process_definition_key (ProcessdefinitionkeyAdvancedfilter | str | Unset):
        start_date (datetime.datetime | TimestampAdvancedfilter | Unset):
        end_date (datetime.datetime | TimestampAdvancedfilter | Unset):
        state (StateAdvancedfilter6 | StateExactmatch3 | Unset):
        has_incident (bool | Unset): Whether this process instance has a related incident or not.
        tenant_id (ActoridAdvancedfilter | str | Unset):
        variables (list[ModifyProcessInstancesBatchOperationDataFilterVariablesItem] | Unset): The process instance
            variables.
        process_instance_key (ProcessinstancekeyAdvancedfilter | str | Unset):
        parent_process_instance_key (ProcessinstancekeyAdvancedfilter | str | Unset):
        parent_element_instance_key (ElementinstancekeyAdvancedfilter | str | Unset):
        batch_operation_id (ActoridAdvancedfilter | str | Unset):
        error_message (ActoridAdvancedfilter | str | Unset):
        has_retries_left (bool | Unset): Whether the process has failed jobs with retries left.
        element_instance_state (StateAdvancedfilter3 | StateExactmatch3 | Unset):
        element_id (ActoridAdvancedfilter | str | Unset):
        has_element_instance_incident (bool | Unset): Whether the element instance has an incident or not.
        incident_error_hash_code (int | PartitionidAdvancedfilter | Unset):
        tags (list[str] | Unset): List of tags. Tags need to start with a letter; then alphanumerics, `_`, `-`, `:`, or
            `.`; length ≤ 100. Example: ['high-touch', 'remediation'].
        or_ (list[ModifyProcessInstancesBatchOperationDataFilterOrItem] | Unset): Defines a list of alternative filter
            groups combined using OR logic. Each object in the array is evaluated independently, and the filter matches if
            any one of them is satisfied.

            Top-level fields and the `$or` clause are combined using AND logic — meaning: (top-level filters) AND (any of
            the `$or` filters) must match.
            <br>
            <em>Example:</em>

            ```json
            {
              "state": "ACTIVE",
              "tenantId": 123,
              "$or": [
                { "processDefinitionId": "process_v1" },
                { "processDefinitionId": "process_v2", "hasIncident": true }
              ]
            }
            ```
            This matches process instances that:

            <ul style="padding-left: 20px; margin-left: 20px;">
              <li style="list-style-type: disc;">are in <em>ACTIVE</em> state</li>
              <li style="list-style-type: disc;">have tenant id equal to <em>123</em></li>
              <li style="list-style-type: disc;">and match either:
                <ul style="padding-left: 20px; margin-left: 20px;">
                  <li style="list-style-type: circle;"><code>processDefinitionId</code> is <em>process_v1</em>, or</li>
                  <li style="list-style-type: circle;"><code>processDefinitionId</code> is <em>process_v2</em> and
            <code>hasIncident</code> is <em>true</em></li>
                </ul>
              </li>
            </ul>
            <br>
            <p>Note: Using complex <code>$or</code> conditions may impact performance, use with caution in high-volume
            environments.
    """

    process_definition_id: ActoridAdvancedfilter | str | Unset = UNSET
    process_definition_name: ActoridAdvancedfilter | str | Unset = UNSET
    process_definition_version: int | PartitionidAdvancedfilter | Unset = UNSET
    process_definition_version_tag: ActoridAdvancedfilter | str | Unset = UNSET
    process_definition_key: ProcessdefinitionkeyAdvancedfilter | str | Unset = UNSET
    start_date: datetime.datetime | TimestampAdvancedfilter | Unset = UNSET
    end_date: datetime.datetime | TimestampAdvancedfilter | Unset = UNSET
    state: StateAdvancedfilter6 | StateExactmatch3 | Unset = UNSET
    has_incident: bool | Unset = UNSET
    tenant_id: ActoridAdvancedfilter | str | Unset = UNSET
    variables: (
        list[ModifyProcessInstancesBatchOperationDataFilterVariablesItem] | Unset
    ) = UNSET
    process_instance_key: ProcessinstancekeyAdvancedfilter | str | Unset = UNSET
    parent_process_instance_key: ProcessinstancekeyAdvancedfilter | str | Unset = UNSET
    parent_element_instance_key: ElementinstancekeyAdvancedfilter | str | Unset = UNSET
    batch_operation_id: ActoridAdvancedfilter | str | Unset = UNSET
    error_message: ActoridAdvancedfilter | str | Unset = UNSET
    has_retries_left: bool | Unset = UNSET
    element_instance_state: StateAdvancedfilter3 | StateExactmatch3 | Unset = UNSET
    element_id: ActoridAdvancedfilter | str | Unset = UNSET
    has_element_instance_incident: bool | Unset = UNSET
    incident_error_hash_code: int | PartitionidAdvancedfilter | Unset = UNSET
    tags: list[str] | Unset = UNSET
    or_: list[ModifyProcessInstancesBatchOperationDataFilterOrItem] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.actorid_advancedfilter import ActoridAdvancedfilter
        from ..models.elementinstancekey_advancedfilter import (
            ElementinstancekeyAdvancedfilter,
        )
        from ..models.partitionid_advancedfilter import PartitionidAdvancedfilter
        from ..models.processdefinitionkey_advancedfilter import (
            ProcessdefinitionkeyAdvancedfilter,
        )
        from ..models.processinstancekey_advancedfilter import (
            ProcessinstancekeyAdvancedfilter,
        )

        process_definition_id: dict[str, Any] | str | Unset
        if isinstance(self.process_definition_id, Unset):
            process_definition_id = UNSET
        elif isinstance(self.process_definition_id, ActoridAdvancedfilter):
            process_definition_id = self.process_definition_id.to_dict()
        else:
            process_definition_id = self.process_definition_id

        process_definition_name: dict[str, Any] | str | Unset
        if isinstance(self.process_definition_name, Unset):
            process_definition_name = UNSET
        elif isinstance(self.process_definition_name, ActoridAdvancedfilter):
            process_definition_name = self.process_definition_name.to_dict()
        else:
            process_definition_name = self.process_definition_name

        process_definition_version: dict[str, Any] | int | Unset
        if isinstance(self.process_definition_version, Unset):
            process_definition_version = UNSET
        elif isinstance(self.process_definition_version, PartitionidAdvancedfilter):
            process_definition_version = self.process_definition_version.to_dict()
        else:
            process_definition_version = self.process_definition_version

        process_definition_version_tag: dict[str, Any] | str | Unset
        if isinstance(self.process_definition_version_tag, Unset):
            process_definition_version_tag = UNSET
        elif isinstance(self.process_definition_version_tag, ActoridAdvancedfilter):
            process_definition_version_tag = (
                self.process_definition_version_tag.to_dict()
            )
        else:
            process_definition_version_tag = self.process_definition_version_tag

        process_definition_key: dict[str, Any] | str | Unset
        if isinstance(self.process_definition_key, Unset):
            process_definition_key = UNSET
        elif isinstance(
            self.process_definition_key, ProcessdefinitionkeyAdvancedfilter
        ):
            process_definition_key = self.process_definition_key.to_dict()
        else:
            process_definition_key = self.process_definition_key

        start_date: dict[str, Any] | str | Unset
        if isinstance(self.start_date, Unset):
            start_date = UNSET
        elif isinstance(self.start_date, datetime.datetime):
            start_date = self.start_date.isoformat()
        else:
            start_date = self.start_date.to_dict()

        end_date: dict[str, Any] | str | Unset
        if isinstance(self.end_date, Unset):
            end_date = UNSET
        elif isinstance(self.end_date, datetime.datetime):
            end_date = self.end_date.isoformat()
        else:
            end_date = self.end_date.to_dict()

        state: dict[str, Any] | str | Unset
        if isinstance(self.state, Unset):
            state = UNSET
        elif isinstance(self.state, StateExactmatch3):
            state = self.state.value
        else:
            state = self.state.to_dict()

        has_incident = self.has_incident

        tenant_id: dict[str, Any] | str | Unset
        if isinstance(self.tenant_id, Unset):
            tenant_id = UNSET
        elif isinstance(self.tenant_id, ActoridAdvancedfilter):
            tenant_id = self.tenant_id.to_dict()
        else:
            tenant_id = self.tenant_id

        variables: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.variables, Unset):
            variables = []
            for variables_item_data in self.variables:
                variables_item = variables_item_data.to_dict()
                variables.append(variables_item)

        process_instance_key: dict[str, Any] | str | Unset
        if isinstance(self.process_instance_key, Unset):
            process_instance_key = UNSET
        elif isinstance(self.process_instance_key, ProcessinstancekeyAdvancedfilter):
            process_instance_key = self.process_instance_key.to_dict()
        else:
            process_instance_key = self.process_instance_key

        parent_process_instance_key: dict[str, Any] | str | Unset
        if isinstance(self.parent_process_instance_key, Unset):
            parent_process_instance_key = UNSET
        elif isinstance(
            self.parent_process_instance_key, ProcessinstancekeyAdvancedfilter
        ):
            parent_process_instance_key = self.parent_process_instance_key.to_dict()
        else:
            parent_process_instance_key = self.parent_process_instance_key

        parent_element_instance_key: dict[str, Any] | str | Unset
        if isinstance(self.parent_element_instance_key, Unset):
            parent_element_instance_key = UNSET
        elif isinstance(
            self.parent_element_instance_key, ElementinstancekeyAdvancedfilter
        ):
            parent_element_instance_key = self.parent_element_instance_key.to_dict()
        else:
            parent_element_instance_key = self.parent_element_instance_key

        batch_operation_id: dict[str, Any] | str | Unset
        if isinstance(self.batch_operation_id, Unset):
            batch_operation_id = UNSET
        elif isinstance(self.batch_operation_id, ActoridAdvancedfilter):
            batch_operation_id = self.batch_operation_id.to_dict()
        else:
            batch_operation_id = self.batch_operation_id

        error_message: dict[str, Any] | str | Unset
        if isinstance(self.error_message, Unset):
            error_message = UNSET
        elif isinstance(self.error_message, ActoridAdvancedfilter):
            error_message = self.error_message.to_dict()
        else:
            error_message = self.error_message

        has_retries_left = self.has_retries_left

        element_instance_state: dict[str, Any] | str | Unset
        if isinstance(self.element_instance_state, Unset):
            element_instance_state = UNSET
        elif isinstance(self.element_instance_state, StateExactmatch3):
            element_instance_state = self.element_instance_state.value
        else:
            element_instance_state = self.element_instance_state.to_dict()

        element_id: dict[str, Any] | str | Unset
        if isinstance(self.element_id, Unset):
            element_id = UNSET
        elif isinstance(self.element_id, ActoridAdvancedfilter):
            element_id = self.element_id.to_dict()
        else:
            element_id = self.element_id

        has_element_instance_incident = self.has_element_instance_incident

        incident_error_hash_code: dict[str, Any] | int | Unset
        if isinstance(self.incident_error_hash_code, Unset):
            incident_error_hash_code = UNSET
        elif isinstance(self.incident_error_hash_code, PartitionidAdvancedfilter):
            incident_error_hash_code = self.incident_error_hash_code.to_dict()
        else:
            incident_error_hash_code = self.incident_error_hash_code

        tags: list[str] | Unset = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags

        or_: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.or_, Unset):
            or_ = []
            for or_item_data in self.or_:
                or_item = or_item_data.to_dict()
                or_.append(or_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if process_definition_id is not UNSET:
            field_dict["processDefinitionId"] = process_definition_id
        if process_definition_name is not UNSET:
            field_dict["processDefinitionName"] = process_definition_name
        if process_definition_version is not UNSET:
            field_dict["processDefinitionVersion"] = process_definition_version
        if process_definition_version_tag is not UNSET:
            field_dict["processDefinitionVersionTag"] = process_definition_version_tag
        if process_definition_key is not UNSET:
            field_dict["processDefinitionKey"] = process_definition_key
        if start_date is not UNSET:
            field_dict["startDate"] = start_date
        if end_date is not UNSET:
            field_dict["endDate"] = end_date
        if state is not UNSET:
            field_dict["state"] = state
        if has_incident is not UNSET:
            field_dict["hasIncident"] = has_incident
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if variables is not UNSET:
            field_dict["variables"] = variables
        if process_instance_key is not UNSET:
            field_dict["processInstanceKey"] = process_instance_key
        if parent_process_instance_key is not UNSET:
            field_dict["parentProcessInstanceKey"] = parent_process_instance_key
        if parent_element_instance_key is not UNSET:
            field_dict["parentElementInstanceKey"] = parent_element_instance_key
        if batch_operation_id is not UNSET:
            field_dict["batchOperationId"] = batch_operation_id
        if error_message is not UNSET:
            field_dict["errorMessage"] = error_message
        if has_retries_left is not UNSET:
            field_dict["hasRetriesLeft"] = has_retries_left
        if element_instance_state is not UNSET:
            field_dict["elementInstanceState"] = element_instance_state
        if element_id is not UNSET:
            field_dict["elementId"] = element_id
        if has_element_instance_incident is not UNSET:
            field_dict["hasElementInstanceIncident"] = has_element_instance_incident
        if incident_error_hash_code is not UNSET:
            field_dict["incidentErrorHashCode"] = incident_error_hash_code
        if tags is not UNSET:
            field_dict["tags"] = tags
        if or_ is not UNSET:
            field_dict["$or"] = or_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.actorid_advancedfilter import ActoridAdvancedfilter
        from ..models.elementinstancekey_advancedfilter import (
            ElementinstancekeyAdvancedfilter,
        )
        from ..models.modify_process_instances_batch_operation_data_filter_or_item import (
            ModifyProcessInstancesBatchOperationDataFilterOrItem,
        )
        from ..models.modify_process_instances_batch_operation_data_filter_variables_item import (
            ModifyProcessInstancesBatchOperationDataFilterVariablesItem,
        )
        from ..models.partitionid_advancedfilter import PartitionidAdvancedfilter
        from ..models.processdefinitionkey_advancedfilter import (
            ProcessdefinitionkeyAdvancedfilter,
        )
        from ..models.processinstancekey_advancedfilter import (
            ProcessinstancekeyAdvancedfilter,
        )
        from ..models.state_advancedfilter_3 import StateAdvancedfilter3
        from ..models.state_advancedfilter_6 import StateAdvancedfilter6
        from ..models.timestamp_advancedfilter import TimestampAdvancedfilter

        d = dict(src_dict)

        def _parse_process_definition_id(
            data: object,
        ) -> ActoridAdvancedfilter | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                process_definition_id_type_1 = ActoridAdvancedfilter.from_dict(data)

                return process_definition_id_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ActoridAdvancedfilter | str | Unset, data)

        process_definition_id = _parse_process_definition_id(
            d.pop("processDefinitionId", UNSET)
        )

        def _parse_process_definition_name(
            data: object,
        ) -> ActoridAdvancedfilter | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                process_definition_name_type_1 = ActoridAdvancedfilter.from_dict(data)

                return process_definition_name_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ActoridAdvancedfilter | str | Unset, data)

        process_definition_name = _parse_process_definition_name(
            d.pop("processDefinitionName", UNSET)
        )

        def _parse_process_definition_version(
            data: object,
        ) -> int | PartitionidAdvancedfilter | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                process_definition_version_type_1 = PartitionidAdvancedfilter.from_dict(
                    data
                )

                return process_definition_version_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(int | PartitionidAdvancedfilter | Unset, data)

        process_definition_version = _parse_process_definition_version(
            d.pop("processDefinitionVersion", UNSET)
        )

        def _parse_process_definition_version_tag(
            data: object,
        ) -> ActoridAdvancedfilter | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                process_definition_version_tag_type_1 = ActoridAdvancedfilter.from_dict(
                    data
                )

                return process_definition_version_tag_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ActoridAdvancedfilter | str | Unset, data)

        process_definition_version_tag = _parse_process_definition_version_tag(
            d.pop("processDefinitionVersionTag", UNSET)
        )

        def _parse_process_definition_key(
            data: object,
        ) -> ProcessdefinitionkeyAdvancedfilter | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                process_definition_key_type_1 = (
                    ProcessdefinitionkeyAdvancedfilter.from_dict(data)
                )

                return process_definition_key_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ProcessdefinitionkeyAdvancedfilter | str | Unset, data)

        process_definition_key = _parse_process_definition_key(
            d.pop("processDefinitionKey", UNSET)
        )

        def _parse_start_date(
            data: object,
        ) -> datetime.datetime | TimestampAdvancedfilter | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                start_date_type_0 = isoparse(data)

                return start_date_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            start_date_type_1 = TimestampAdvancedfilter.from_dict(data)

            return start_date_type_1

        start_date = _parse_start_date(d.pop("startDate", UNSET))

        def _parse_end_date(
            data: object,
        ) -> datetime.datetime | TimestampAdvancedfilter | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                end_date_type_0 = isoparse(data)

                return end_date_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            end_date_type_1 = TimestampAdvancedfilter.from_dict(data)

            return end_date_type_1

        end_date = _parse_end_date(d.pop("endDate", UNSET))

        def _parse_state(
            data: object,
        ) -> StateAdvancedfilter6 | StateExactmatch3 | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                state_type_0 = StateExactmatch3(data)

                return state_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            state_type_1 = StateAdvancedfilter6.from_dict(data)

            return state_type_1

        state = _parse_state(d.pop("state", UNSET))

        has_incident = d.pop("hasIncident", UNSET)

        def _parse_tenant_id(data: object) -> ActoridAdvancedfilter | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                tenant_id_type_1 = ActoridAdvancedfilter.from_dict(data)

                return tenant_id_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ActoridAdvancedfilter | str | Unset, data)

        tenant_id = _parse_tenant_id(d.pop("tenantId", UNSET))

        _variables = d.pop("variables", UNSET)
        variables: (
            list[ModifyProcessInstancesBatchOperationDataFilterVariablesItem] | Unset
        ) = UNSET
        if _variables is not UNSET:
            variables = []
            for variables_item_data in _variables:
                variables_item = ModifyProcessInstancesBatchOperationDataFilterVariablesItem.from_dict(
                    variables_item_data
                )

                variables.append(variables_item)

        def _parse_process_instance_key(
            data: object,
        ) -> ProcessinstancekeyAdvancedfilter | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                process_instance_key_type_1 = (
                    ProcessinstancekeyAdvancedfilter.from_dict(data)
                )

                return process_instance_key_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ProcessinstancekeyAdvancedfilter | str | Unset, data)

        process_instance_key = _parse_process_instance_key(
            d.pop("processInstanceKey", UNSET)
        )

        def _parse_parent_process_instance_key(
            data: object,
        ) -> ProcessinstancekeyAdvancedfilter | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                parent_process_instance_key_type_1 = (
                    ProcessinstancekeyAdvancedfilter.from_dict(data)
                )

                return parent_process_instance_key_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ProcessinstancekeyAdvancedfilter | str | Unset, data)

        parent_process_instance_key = _parse_parent_process_instance_key(
            d.pop("parentProcessInstanceKey", UNSET)
        )

        def _parse_parent_element_instance_key(
            data: object,
        ) -> ElementinstancekeyAdvancedfilter | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                parent_element_instance_key_type_1 = (
                    ElementinstancekeyAdvancedfilter.from_dict(data)
                )

                return parent_element_instance_key_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ElementinstancekeyAdvancedfilter | str | Unset, data)

        parent_element_instance_key = _parse_parent_element_instance_key(
            d.pop("parentElementInstanceKey", UNSET)
        )

        def _parse_batch_operation_id(
            data: object,
        ) -> ActoridAdvancedfilter | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                batch_operation_id_type_1 = ActoridAdvancedfilter.from_dict(data)

                return batch_operation_id_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ActoridAdvancedfilter | str | Unset, data)

        batch_operation_id = _parse_batch_operation_id(d.pop("batchOperationId", UNSET))

        def _parse_error_message(data: object) -> ActoridAdvancedfilter | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                error_message_type_1 = ActoridAdvancedfilter.from_dict(data)

                return error_message_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ActoridAdvancedfilter | str | Unset, data)

        error_message = _parse_error_message(d.pop("errorMessage", UNSET))

        has_retries_left = d.pop("hasRetriesLeft", UNSET)

        def _parse_element_instance_state(
            data: object,
        ) -> StateAdvancedfilter3 | StateExactmatch3 | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                element_instance_state_type_0 = StateExactmatch3(data)

                return element_instance_state_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            element_instance_state_type_1 = StateAdvancedfilter3.from_dict(data)

            return element_instance_state_type_1

        element_instance_state = _parse_element_instance_state(
            d.pop("elementInstanceState", UNSET)
        )

        def _parse_element_id(data: object) -> ActoridAdvancedfilter | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                element_id_type_1 = ActoridAdvancedfilter.from_dict(data)

                return element_id_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ActoridAdvancedfilter | str | Unset, data)

        element_id = _parse_element_id(d.pop("elementId", UNSET))

        has_element_instance_incident = d.pop("hasElementInstanceIncident", UNSET)

        def _parse_incident_error_hash_code(
            data: object,
        ) -> int | PartitionidAdvancedfilter | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                incident_error_hash_code_type_1 = PartitionidAdvancedfilter.from_dict(
                    data
                )

                return incident_error_hash_code_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(int | PartitionidAdvancedfilter | Unset, data)

        incident_error_hash_code = _parse_incident_error_hash_code(
            d.pop("incidentErrorHashCode", UNSET)
        )

        tags = cast(list[str], d.pop("tags", UNSET))

        _or_ = d.pop("$or", UNSET)
        or_: list[ModifyProcessInstancesBatchOperationDataFilterOrItem] | Unset = UNSET
        if _or_ is not UNSET:
            or_ = []
            for or_item_data in _or_:
                or_item = (
                    ModifyProcessInstancesBatchOperationDataFilterOrItem.from_dict(
                        or_item_data
                    )
                )

                or_.append(or_item)

        modify_process_instances_batch_operation_data_filter = cls(
            process_definition_id=process_definition_id,
            process_definition_name=process_definition_name,
            process_definition_version=process_definition_version,
            process_definition_version_tag=process_definition_version_tag,
            process_definition_key=process_definition_key,
            start_date=start_date,
            end_date=end_date,
            state=state,
            has_incident=has_incident,
            tenant_id=tenant_id,
            variables=variables,
            process_instance_key=process_instance_key,
            parent_process_instance_key=parent_process_instance_key,
            parent_element_instance_key=parent_element_instance_key,
            batch_operation_id=batch_operation_id,
            error_message=error_message,
            has_retries_left=has_retries_left,
            element_instance_state=element_instance_state,
            element_id=element_id,
            has_element_instance_incident=has_element_instance_incident,
            incident_error_hash_code=incident_error_hash_code,
            tags=tags,
            or_=or_,
        )

        modify_process_instances_batch_operation_data_filter.additional_properties = d
        return modify_process_instances_batch_operation_data_filter

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

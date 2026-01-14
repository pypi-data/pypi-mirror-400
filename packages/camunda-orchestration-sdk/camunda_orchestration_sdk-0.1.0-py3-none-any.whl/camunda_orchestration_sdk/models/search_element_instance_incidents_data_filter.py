from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.errortype_exactmatch import ErrortypeExactmatch
from ..models.state_exactmatch_4 import StateExactmatch4
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.actorid_advancedfilter import ActoridAdvancedfilter
    from ..models.batchoperationkey_advancedfilter import (
        BatchoperationkeyAdvancedfilter,
    )
    from ..models.elementinstancekey_advancedfilter import (
        ElementinstancekeyAdvancedfilter,
    )
    from ..models.errortype_advancedfilter import ErrortypeAdvancedfilter
    from ..models.jobkey_advancedfilter import JobkeyAdvancedfilter
    from ..models.processdefinitionkey_advancedfilter import (
        ProcessdefinitionkeyAdvancedfilter,
    )
    from ..models.processinstancekey_advancedfilter import (
        ProcessinstancekeyAdvancedfilter,
    )
    from ..models.state_advancedfilter_4 import StateAdvancedfilter4
    from ..models.timestamp_advancedfilter import TimestampAdvancedfilter


T = TypeVar("T", bound="SearchElementInstanceIncidentsDataFilter")


@_attrs_define
class SearchElementInstanceIncidentsDataFilter:
    """The incident search filters.

    Attributes:
        process_definition_id (ActoridAdvancedfilter | str | Unset):
        error_type (ErrortypeAdvancedfilter | ErrortypeExactmatch | Unset):
        error_message (ActoridAdvancedfilter | str | Unset):
        element_id (ActoridAdvancedfilter | str | Unset):
        creation_time (datetime.datetime | TimestampAdvancedfilter | Unset):
        state (StateAdvancedfilter4 | StateExactmatch4 | Unset):
        tenant_id (ActoridAdvancedfilter | str | Unset):
        incident_key (BatchoperationkeyAdvancedfilter | str | Unset):
        process_definition_key (ProcessdefinitionkeyAdvancedfilter | str | Unset):
        process_instance_key (ProcessinstancekeyAdvancedfilter | str | Unset):
        element_instance_key (ElementinstancekeyAdvancedfilter | str | Unset):
        job_key (JobkeyAdvancedfilter | str | Unset):
    """

    process_definition_id: ActoridAdvancedfilter | str | Unset = UNSET
    error_type: ErrortypeAdvancedfilter | ErrortypeExactmatch | Unset = UNSET
    error_message: ActoridAdvancedfilter | str | Unset = UNSET
    element_id: ActoridAdvancedfilter | str | Unset = UNSET
    creation_time: datetime.datetime | TimestampAdvancedfilter | Unset = UNSET
    state: StateAdvancedfilter4 | StateExactmatch4 | Unset = UNSET
    tenant_id: ActoridAdvancedfilter | str | Unset = UNSET
    incident_key: BatchoperationkeyAdvancedfilter | str | Unset = UNSET
    process_definition_key: ProcessdefinitionkeyAdvancedfilter | str | Unset = UNSET
    process_instance_key: ProcessinstancekeyAdvancedfilter | str | Unset = UNSET
    element_instance_key: ElementinstancekeyAdvancedfilter | str | Unset = UNSET
    job_key: JobkeyAdvancedfilter | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.actorid_advancedfilter import ActoridAdvancedfilter
        from ..models.batchoperationkey_advancedfilter import (
            BatchoperationkeyAdvancedfilter,
        )
        from ..models.elementinstancekey_advancedfilter import (
            ElementinstancekeyAdvancedfilter,
        )
        from ..models.jobkey_advancedfilter import JobkeyAdvancedfilter
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

        error_type: dict[str, Any] | str | Unset
        if isinstance(self.error_type, Unset):
            error_type = UNSET
        elif isinstance(self.error_type, ErrortypeExactmatch):
            error_type = self.error_type.value
        else:
            error_type = self.error_type.to_dict()

        error_message: dict[str, Any] | str | Unset
        if isinstance(self.error_message, Unset):
            error_message = UNSET
        elif isinstance(self.error_message, ActoridAdvancedfilter):
            error_message = self.error_message.to_dict()
        else:
            error_message = self.error_message

        element_id: dict[str, Any] | str | Unset
        if isinstance(self.element_id, Unset):
            element_id = UNSET
        elif isinstance(self.element_id, ActoridAdvancedfilter):
            element_id = self.element_id.to_dict()
        else:
            element_id = self.element_id

        creation_time: dict[str, Any] | str | Unset
        if isinstance(self.creation_time, Unset):
            creation_time = UNSET
        elif isinstance(self.creation_time, datetime.datetime):
            creation_time = self.creation_time.isoformat()
        else:
            creation_time = self.creation_time.to_dict()

        state: dict[str, Any] | str | Unset
        if isinstance(self.state, Unset):
            state = UNSET
        elif isinstance(self.state, StateExactmatch4):
            state = self.state.value
        else:
            state = self.state.to_dict()

        tenant_id: dict[str, Any] | str | Unset
        if isinstance(self.tenant_id, Unset):
            tenant_id = UNSET
        elif isinstance(self.tenant_id, ActoridAdvancedfilter):
            tenant_id = self.tenant_id.to_dict()
        else:
            tenant_id = self.tenant_id

        incident_key: dict[str, Any] | str | Unset
        if isinstance(self.incident_key, Unset):
            incident_key = UNSET
        elif isinstance(self.incident_key, BatchoperationkeyAdvancedfilter):
            incident_key = self.incident_key.to_dict()
        else:
            incident_key = self.incident_key

        process_definition_key: dict[str, Any] | str | Unset
        if isinstance(self.process_definition_key, Unset):
            process_definition_key = UNSET
        elif isinstance(
            self.process_definition_key, ProcessdefinitionkeyAdvancedfilter
        ):
            process_definition_key = self.process_definition_key.to_dict()
        else:
            process_definition_key = self.process_definition_key

        process_instance_key: dict[str, Any] | str | Unset
        if isinstance(self.process_instance_key, Unset):
            process_instance_key = UNSET
        elif isinstance(self.process_instance_key, ProcessinstancekeyAdvancedfilter):
            process_instance_key = self.process_instance_key.to_dict()
        else:
            process_instance_key = self.process_instance_key

        element_instance_key: dict[str, Any] | str | Unset
        if isinstance(self.element_instance_key, Unset):
            element_instance_key = UNSET
        elif isinstance(self.element_instance_key, ElementinstancekeyAdvancedfilter):
            element_instance_key = self.element_instance_key.to_dict()
        else:
            element_instance_key = self.element_instance_key

        job_key: dict[str, Any] | str | Unset
        if isinstance(self.job_key, Unset):
            job_key = UNSET
        elif isinstance(self.job_key, JobkeyAdvancedfilter):
            job_key = self.job_key.to_dict()
        else:
            job_key = self.job_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if process_definition_id is not UNSET:
            field_dict["processDefinitionId"] = process_definition_id
        if error_type is not UNSET:
            field_dict["errorType"] = error_type
        if error_message is not UNSET:
            field_dict["errorMessage"] = error_message
        if element_id is not UNSET:
            field_dict["elementId"] = element_id
        if creation_time is not UNSET:
            field_dict["creationTime"] = creation_time
        if state is not UNSET:
            field_dict["state"] = state
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if incident_key is not UNSET:
            field_dict["incidentKey"] = incident_key
        if process_definition_key is not UNSET:
            field_dict["processDefinitionKey"] = process_definition_key
        if process_instance_key is not UNSET:
            field_dict["processInstanceKey"] = process_instance_key
        if element_instance_key is not UNSET:
            field_dict["elementInstanceKey"] = element_instance_key
        if job_key is not UNSET:
            field_dict["jobKey"] = job_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.actorid_advancedfilter import ActoridAdvancedfilter
        from ..models.batchoperationkey_advancedfilter import (
            BatchoperationkeyAdvancedfilter,
        )
        from ..models.elementinstancekey_advancedfilter import (
            ElementinstancekeyAdvancedfilter,
        )
        from ..models.errortype_advancedfilter import ErrortypeAdvancedfilter
        from ..models.jobkey_advancedfilter import JobkeyAdvancedfilter
        from ..models.processdefinitionkey_advancedfilter import (
            ProcessdefinitionkeyAdvancedfilter,
        )
        from ..models.processinstancekey_advancedfilter import (
            ProcessinstancekeyAdvancedfilter,
        )
        from ..models.state_advancedfilter_4 import StateAdvancedfilter4
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

        def _parse_error_type(
            data: object,
        ) -> ErrortypeAdvancedfilter | ErrortypeExactmatch | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                error_type_type_0 = ErrortypeExactmatch(data)

                return error_type_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            error_type_type_1 = ErrortypeAdvancedfilter.from_dict(data)

            return error_type_type_1

        error_type = _parse_error_type(d.pop("errorType", UNSET))

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

        def _parse_creation_time(
            data: object,
        ) -> datetime.datetime | TimestampAdvancedfilter | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                creation_time_type_0 = isoparse(data)

                return creation_time_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            creation_time_type_1 = TimestampAdvancedfilter.from_dict(data)

            return creation_time_type_1

        creation_time = _parse_creation_time(d.pop("creationTime", UNSET))

        def _parse_state(
            data: object,
        ) -> StateAdvancedfilter4 | StateExactmatch4 | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                state_type_0 = StateExactmatch4(data)

                return state_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            state_type_1 = StateAdvancedfilter4.from_dict(data)

            return state_type_1

        state = _parse_state(d.pop("state", UNSET))

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

        def _parse_incident_key(
            data: object,
        ) -> BatchoperationkeyAdvancedfilter | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                incident_key_type_1 = BatchoperationkeyAdvancedfilter.from_dict(data)

                return incident_key_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(BatchoperationkeyAdvancedfilter | str | Unset, data)

        incident_key = _parse_incident_key(d.pop("incidentKey", UNSET))

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

        def _parse_element_instance_key(
            data: object,
        ) -> ElementinstancekeyAdvancedfilter | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                element_instance_key_type_1 = (
                    ElementinstancekeyAdvancedfilter.from_dict(data)
                )

                return element_instance_key_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ElementinstancekeyAdvancedfilter | str | Unset, data)

        element_instance_key = _parse_element_instance_key(
            d.pop("elementInstanceKey", UNSET)
        )

        def _parse_job_key(data: object) -> JobkeyAdvancedfilter | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                job_key_type_1 = JobkeyAdvancedfilter.from_dict(data)

                return job_key_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(JobkeyAdvancedfilter | str | Unset, data)

        job_key = _parse_job_key(d.pop("jobKey", UNSET))

        search_element_instance_incidents_data_filter = cls(
            process_definition_id=process_definition_id,
            error_type=error_type,
            error_message=error_message,
            element_id=element_id,
            creation_time=creation_time,
            state=state,
            tenant_id=tenant_id,
            incident_key=incident_key,
            process_definition_key=process_definition_key,
            process_instance_key=process_instance_key,
            element_instance_key=element_instance_key,
            job_key=job_key,
        )

        search_element_instance_incidents_data_filter.additional_properties = d
        return search_element_instance_incidents_data_filter

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

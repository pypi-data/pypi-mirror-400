from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.kind_exactmatch import KindExactmatch
from ..models.listenereventtype_exactmatch import ListenereventtypeExactmatch
from ..models.state_exactmatch_5 import StateExactmatch5
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.actorid_advancedfilter import ActoridAdvancedfilter
    from ..models.elementinstancekey_advancedfilter import (
        ElementinstancekeyAdvancedfilter,
    )
    from ..models.jobkey_advancedfilter import JobkeyAdvancedfilter
    from ..models.kind_advancedfilter import KindAdvancedfilter
    from ..models.listenereventtype_advancedfilter import (
        ListenereventtypeAdvancedfilter,
    )
    from ..models.partitionid_advancedfilter import PartitionidAdvancedfilter
    from ..models.processdefinitionkey_advancedfilter import (
        ProcessdefinitionkeyAdvancedfilter,
    )
    from ..models.processinstancekey_advancedfilter import (
        ProcessinstancekeyAdvancedfilter,
    )
    from ..models.state_advancedfilter_5 import StateAdvancedfilter5
    from ..models.timestamp_advancedfilter import TimestampAdvancedfilter


T = TypeVar("T", bound="SearchJobsDataFilter")


@_attrs_define
class SearchJobsDataFilter:
    """The job search filters.

    Attributes:
        deadline (datetime.datetime | None | TimestampAdvancedfilter | Unset):
        denied_reason (ActoridAdvancedfilter | str | Unset):
        element_id (ActoridAdvancedfilter | str | Unset):
        element_instance_key (ElementinstancekeyAdvancedfilter | str | Unset):
        end_time (datetime.datetime | TimestampAdvancedfilter | Unset):
        error_code (ActoridAdvancedfilter | str | Unset):
        error_message (ActoridAdvancedfilter | str | Unset):
        has_failed_with_retries_left (bool | Unset): Indicates whether the job has failed with retries left.
        is_denied (bool | None | Unset): Indicates whether the user task listener denies the work.
        job_key (JobkeyAdvancedfilter | str | Unset):
        kind (KindAdvancedfilter | KindExactmatch | Unset):
        listener_event_type (ListenereventtypeAdvancedfilter | ListenereventtypeExactmatch | Unset):
        process_definition_id (ActoridAdvancedfilter | str | Unset):
        process_definition_key (ProcessdefinitionkeyAdvancedfilter | str | Unset):
        process_instance_key (ProcessinstancekeyAdvancedfilter | str | Unset):
        retries (int | PartitionidAdvancedfilter | Unset):
        state (StateAdvancedfilter5 | StateExactmatch5 | Unset):
        tenant_id (ActoridAdvancedfilter | str | Unset):
        type_ (ActoridAdvancedfilter | str | Unset):
        worker (ActoridAdvancedfilter | str | Unset):
        creation_time (datetime.datetime | TimestampAdvancedfilter | Unset):
        last_update_time (datetime.datetime | TimestampAdvancedfilter | Unset):
    """

    deadline: datetime.datetime | None | TimestampAdvancedfilter | Unset = UNSET
    denied_reason: ActoridAdvancedfilter | str | Unset = UNSET
    element_id: ActoridAdvancedfilter | str | Unset = UNSET
    element_instance_key: ElementinstancekeyAdvancedfilter | str | Unset = UNSET
    end_time: datetime.datetime | TimestampAdvancedfilter | Unset = UNSET
    error_code: ActoridAdvancedfilter | str | Unset = UNSET
    error_message: ActoridAdvancedfilter | str | Unset = UNSET
    has_failed_with_retries_left: bool | Unset = UNSET
    is_denied: bool | None | Unset = UNSET
    job_key: JobkeyAdvancedfilter | str | Unset = UNSET
    kind: KindAdvancedfilter | KindExactmatch | Unset = UNSET
    listener_event_type: (
        ListenereventtypeAdvancedfilter | ListenereventtypeExactmatch | Unset
    ) = UNSET
    process_definition_id: ActoridAdvancedfilter | str | Unset = UNSET
    process_definition_key: ProcessdefinitionkeyAdvancedfilter | str | Unset = UNSET
    process_instance_key: ProcessinstancekeyAdvancedfilter | str | Unset = UNSET
    retries: int | PartitionidAdvancedfilter | Unset = UNSET
    state: StateAdvancedfilter5 | StateExactmatch5 | Unset = UNSET
    tenant_id: ActoridAdvancedfilter | str | Unset = UNSET
    type_: ActoridAdvancedfilter | str | Unset = UNSET
    worker: ActoridAdvancedfilter | str | Unset = UNSET
    creation_time: datetime.datetime | TimestampAdvancedfilter | Unset = UNSET
    last_update_time: datetime.datetime | TimestampAdvancedfilter | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.actorid_advancedfilter import ActoridAdvancedfilter
        from ..models.elementinstancekey_advancedfilter import (
            ElementinstancekeyAdvancedfilter,
        )
        from ..models.jobkey_advancedfilter import JobkeyAdvancedfilter
        from ..models.partitionid_advancedfilter import PartitionidAdvancedfilter
        from ..models.processdefinitionkey_advancedfilter import (
            ProcessdefinitionkeyAdvancedfilter,
        )
        from ..models.processinstancekey_advancedfilter import (
            ProcessinstancekeyAdvancedfilter,
        )
        from ..models.timestamp_advancedfilter import TimestampAdvancedfilter

        deadline: dict[str, Any] | None | str | Unset
        if isinstance(self.deadline, Unset):
            deadline = UNSET
        elif isinstance(self.deadline, datetime.datetime):
            deadline = self.deadline.isoformat()
        elif isinstance(self.deadline, TimestampAdvancedfilter):
            deadline = self.deadline.to_dict()
        else:
            deadline = self.deadline

        denied_reason: dict[str, Any] | str | Unset
        if isinstance(self.denied_reason, Unset):
            denied_reason = UNSET
        elif isinstance(self.denied_reason, ActoridAdvancedfilter):
            denied_reason = self.denied_reason.to_dict()
        else:
            denied_reason = self.denied_reason

        element_id: dict[str, Any] | str | Unset
        if isinstance(self.element_id, Unset):
            element_id = UNSET
        elif isinstance(self.element_id, ActoridAdvancedfilter):
            element_id = self.element_id.to_dict()
        else:
            element_id = self.element_id

        element_instance_key: dict[str, Any] | str | Unset
        if isinstance(self.element_instance_key, Unset):
            element_instance_key = UNSET
        elif isinstance(self.element_instance_key, ElementinstancekeyAdvancedfilter):
            element_instance_key = self.element_instance_key.to_dict()
        else:
            element_instance_key = self.element_instance_key

        end_time: dict[str, Any] | str | Unset
        if isinstance(self.end_time, Unset):
            end_time = UNSET
        elif isinstance(self.end_time, datetime.datetime):
            end_time = self.end_time.isoformat()
        else:
            end_time = self.end_time.to_dict()

        error_code: dict[str, Any] | str | Unset
        if isinstance(self.error_code, Unset):
            error_code = UNSET
        elif isinstance(self.error_code, ActoridAdvancedfilter):
            error_code = self.error_code.to_dict()
        else:
            error_code = self.error_code

        error_message: dict[str, Any] | str | Unset
        if isinstance(self.error_message, Unset):
            error_message = UNSET
        elif isinstance(self.error_message, ActoridAdvancedfilter):
            error_message = self.error_message.to_dict()
        else:
            error_message = self.error_message

        has_failed_with_retries_left = self.has_failed_with_retries_left

        is_denied: bool | None | Unset
        if isinstance(self.is_denied, Unset):
            is_denied = UNSET
        else:
            is_denied = self.is_denied

        job_key: dict[str, Any] | str | Unset
        if isinstance(self.job_key, Unset):
            job_key = UNSET
        elif isinstance(self.job_key, JobkeyAdvancedfilter):
            job_key = self.job_key.to_dict()
        else:
            job_key = self.job_key

        kind: dict[str, Any] | str | Unset
        if isinstance(self.kind, Unset):
            kind = UNSET
        elif isinstance(self.kind, KindExactmatch):
            kind = self.kind.value
        else:
            kind = self.kind.to_dict()

        listener_event_type: dict[str, Any] | str | Unset
        if isinstance(self.listener_event_type, Unset):
            listener_event_type = UNSET
        elif isinstance(self.listener_event_type, ListenereventtypeExactmatch):
            listener_event_type = self.listener_event_type.value
        else:
            listener_event_type = self.listener_event_type.to_dict()

        process_definition_id: dict[str, Any] | str | Unset
        if isinstance(self.process_definition_id, Unset):
            process_definition_id = UNSET
        elif isinstance(self.process_definition_id, ActoridAdvancedfilter):
            process_definition_id = self.process_definition_id.to_dict()
        else:
            process_definition_id = self.process_definition_id

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

        retries: dict[str, Any] | int | Unset
        if isinstance(self.retries, Unset):
            retries = UNSET
        elif isinstance(self.retries, PartitionidAdvancedfilter):
            retries = self.retries.to_dict()
        else:
            retries = self.retries

        state: dict[str, Any] | str | Unset
        if isinstance(self.state, Unset):
            state = UNSET
        elif isinstance(self.state, StateExactmatch5):
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

        type_: dict[str, Any] | str | Unset
        if isinstance(self.type_, Unset):
            type_ = UNSET
        elif isinstance(self.type_, ActoridAdvancedfilter):
            type_ = self.type_.to_dict()
        else:
            type_ = self.type_

        worker: dict[str, Any] | str | Unset
        if isinstance(self.worker, Unset):
            worker = UNSET
        elif isinstance(self.worker, ActoridAdvancedfilter):
            worker = self.worker.to_dict()
        else:
            worker = self.worker

        creation_time: dict[str, Any] | str | Unset
        if isinstance(self.creation_time, Unset):
            creation_time = UNSET
        elif isinstance(self.creation_time, datetime.datetime):
            creation_time = self.creation_time.isoformat()
        else:
            creation_time = self.creation_time.to_dict()

        last_update_time: dict[str, Any] | str | Unset
        if isinstance(self.last_update_time, Unset):
            last_update_time = UNSET
        elif isinstance(self.last_update_time, datetime.datetime):
            last_update_time = self.last_update_time.isoformat()
        else:
            last_update_time = self.last_update_time.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if deadline is not UNSET:
            field_dict["deadline"] = deadline
        if denied_reason is not UNSET:
            field_dict["deniedReason"] = denied_reason
        if element_id is not UNSET:
            field_dict["elementId"] = element_id
        if element_instance_key is not UNSET:
            field_dict["elementInstanceKey"] = element_instance_key
        if end_time is not UNSET:
            field_dict["endTime"] = end_time
        if error_code is not UNSET:
            field_dict["errorCode"] = error_code
        if error_message is not UNSET:
            field_dict["errorMessage"] = error_message
        if has_failed_with_retries_left is not UNSET:
            field_dict["hasFailedWithRetriesLeft"] = has_failed_with_retries_left
        if is_denied is not UNSET:
            field_dict["isDenied"] = is_denied
        if job_key is not UNSET:
            field_dict["jobKey"] = job_key
        if kind is not UNSET:
            field_dict["kind"] = kind
        if listener_event_type is not UNSET:
            field_dict["listenerEventType"] = listener_event_type
        if process_definition_id is not UNSET:
            field_dict["processDefinitionId"] = process_definition_id
        if process_definition_key is not UNSET:
            field_dict["processDefinitionKey"] = process_definition_key
        if process_instance_key is not UNSET:
            field_dict["processInstanceKey"] = process_instance_key
        if retries is not UNSET:
            field_dict["retries"] = retries
        if state is not UNSET:
            field_dict["state"] = state
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if type_ is not UNSET:
            field_dict["type"] = type_
        if worker is not UNSET:
            field_dict["worker"] = worker
        if creation_time is not UNSET:
            field_dict["creationTime"] = creation_time
        if last_update_time is not UNSET:
            field_dict["lastUpdateTime"] = last_update_time

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.actorid_advancedfilter import ActoridAdvancedfilter
        from ..models.elementinstancekey_advancedfilter import (
            ElementinstancekeyAdvancedfilter,
        )
        from ..models.jobkey_advancedfilter import JobkeyAdvancedfilter
        from ..models.kind_advancedfilter import KindAdvancedfilter
        from ..models.listenereventtype_advancedfilter import (
            ListenereventtypeAdvancedfilter,
        )
        from ..models.partitionid_advancedfilter import PartitionidAdvancedfilter
        from ..models.processdefinitionkey_advancedfilter import (
            ProcessdefinitionkeyAdvancedfilter,
        )
        from ..models.processinstancekey_advancedfilter import (
            ProcessinstancekeyAdvancedfilter,
        )
        from ..models.state_advancedfilter_5 import StateAdvancedfilter5
        from ..models.timestamp_advancedfilter import TimestampAdvancedfilter

        d = dict(src_dict)

        def _parse_deadline(
            data: object,
        ) -> datetime.datetime | None | TimestampAdvancedfilter | Unset:
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
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                deadline_type_1 = TimestampAdvancedfilter.from_dict(data)

                return deadline_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                datetime.datetime | None | TimestampAdvancedfilter | Unset, data
            )

        deadline = _parse_deadline(d.pop("deadline", UNSET))

        def _parse_denied_reason(data: object) -> ActoridAdvancedfilter | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                denied_reason_type_1 = ActoridAdvancedfilter.from_dict(data)

                return denied_reason_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ActoridAdvancedfilter | str | Unset, data)

        denied_reason = _parse_denied_reason(d.pop("deniedReason", UNSET))

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

        def _parse_end_time(
            data: object,
        ) -> datetime.datetime | TimestampAdvancedfilter | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                end_time_type_0 = isoparse(data)

                return end_time_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            end_time_type_1 = TimestampAdvancedfilter.from_dict(data)

            return end_time_type_1

        end_time = _parse_end_time(d.pop("endTime", UNSET))

        def _parse_error_code(data: object) -> ActoridAdvancedfilter | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                error_code_type_1 = ActoridAdvancedfilter.from_dict(data)

                return error_code_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ActoridAdvancedfilter | str | Unset, data)

        error_code = _parse_error_code(d.pop("errorCode", UNSET))

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

        has_failed_with_retries_left = d.pop("hasFailedWithRetriesLeft", UNSET)

        def _parse_is_denied(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_denied = _parse_is_denied(d.pop("isDenied", UNSET))

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

        def _parse_kind(data: object) -> KindAdvancedfilter | KindExactmatch | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                kind_type_0 = KindExactmatch(data)

                return kind_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            kind_type_1 = KindAdvancedfilter.from_dict(data)

            return kind_type_1

        kind = _parse_kind(d.pop("kind", UNSET))

        def _parse_listener_event_type(
            data: object,
        ) -> ListenereventtypeAdvancedfilter | ListenereventtypeExactmatch | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                listener_event_type_type_0 = ListenereventtypeExactmatch(data)

                return listener_event_type_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            listener_event_type_type_1 = ListenereventtypeAdvancedfilter.from_dict(data)

            return listener_event_type_type_1

        listener_event_type = _parse_listener_event_type(
            d.pop("listenerEventType", UNSET)
        )

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

        def _parse_retries(data: object) -> int | PartitionidAdvancedfilter | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                retries_type_1 = PartitionidAdvancedfilter.from_dict(data)

                return retries_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(int | PartitionidAdvancedfilter | Unset, data)

        retries = _parse_retries(d.pop("retries", UNSET))

        def _parse_state(
            data: object,
        ) -> StateAdvancedfilter5 | StateExactmatch5 | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                state_type_0 = StateExactmatch5(data)

                return state_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            state_type_1 = StateAdvancedfilter5.from_dict(data)

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

        def _parse_type_(data: object) -> ActoridAdvancedfilter | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                type_type_1 = ActoridAdvancedfilter.from_dict(data)

                return type_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ActoridAdvancedfilter | str | Unset, data)

        type_ = _parse_type_(d.pop("type", UNSET))

        def _parse_worker(data: object) -> ActoridAdvancedfilter | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                worker_type_1 = ActoridAdvancedfilter.from_dict(data)

                return worker_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ActoridAdvancedfilter | str | Unset, data)

        worker = _parse_worker(d.pop("worker", UNSET))

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

        def _parse_last_update_time(
            data: object,
        ) -> datetime.datetime | TimestampAdvancedfilter | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_update_time_type_0 = isoparse(data)

                return last_update_time_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            last_update_time_type_1 = TimestampAdvancedfilter.from_dict(data)

            return last_update_time_type_1

        last_update_time = _parse_last_update_time(d.pop("lastUpdateTime", UNSET))

        search_jobs_data_filter = cls(
            deadline=deadline,
            denied_reason=denied_reason,
            element_id=element_id,
            element_instance_key=element_instance_key,
            end_time=end_time,
            error_code=error_code,
            error_message=error_message,
            has_failed_with_retries_left=has_failed_with_retries_left,
            is_denied=is_denied,
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
            creation_time=creation_time,
            last_update_time=last_update_time,
        )

        search_jobs_data_filter.additional_properties = d
        return search_jobs_data_filter

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

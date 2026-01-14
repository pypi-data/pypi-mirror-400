from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.category_exactmatch import CategoryExactmatch
from ..models.entitytype_exactmatch import EntitytypeExactmatch
from ..models.operationtype_exactmatch import OperationtypeExactmatch
from ..models.search_audit_logs_data_filter_actor_type import (
    SearchAuditLogsDataFilterActorType,
)
from ..models.search_audit_logs_data_filter_result import (
    SearchAuditLogsDataFilterResult,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.actorid_advancedfilter import ActoridAdvancedfilter
    from ..models.auditlogkey_advancedfilter import AuditlogkeyAdvancedfilter
    from ..models.category_advancedfilter import CategoryAdvancedfilter
    from ..models.elementinstancekey_advancedfilter import (
        ElementinstancekeyAdvancedfilter,
    )
    from ..models.entitytype_advancedfilter import EntitytypeAdvancedfilter
    from ..models.operationtype_advancedfilter import OperationtypeAdvancedfilter
    from ..models.processdefinitionkey_advancedfilter import (
        ProcessdefinitionkeyAdvancedfilter,
    )
    from ..models.processinstancekey_advancedfilter import (
        ProcessinstancekeyAdvancedfilter,
    )
    from ..models.timestamp_advancedfilter import TimestampAdvancedfilter


T = TypeVar("T", bound="SearchAuditLogsDataFilter")


@_attrs_define
class SearchAuditLogsDataFilter:
    """The audit log search filters.

    Attributes:
        audit_log_key (AuditlogkeyAdvancedfilter | str | Unset):
        process_definition_key (ProcessdefinitionkeyAdvancedfilter | str | Unset):
        process_instance_key (ProcessinstancekeyAdvancedfilter | str | Unset):
        element_instance_key (ElementinstancekeyAdvancedfilter | str | Unset):
        operation_type (OperationtypeAdvancedfilter | OperationtypeExactmatch | Unset):
        result (SearchAuditLogsDataFilterResult | Unset): The result search filter.
        timestamp (datetime.datetime | TimestampAdvancedfilter | Unset):
        actor_id (ActoridAdvancedfilter | str | Unset):
        actor_type (SearchAuditLogsDataFilterActorType | Unset): The actor type search filter.
        entity_type (EntitytypeAdvancedfilter | EntitytypeExactmatch | Unset):
        tenant_id (ActoridAdvancedfilter | str | Unset):
        category (CategoryAdvancedfilter | CategoryExactmatch | Unset):
    """

    audit_log_key: AuditlogkeyAdvancedfilter | str | Unset = UNSET
    process_definition_key: ProcessdefinitionkeyAdvancedfilter | str | Unset = UNSET
    process_instance_key: ProcessinstancekeyAdvancedfilter | str | Unset = UNSET
    element_instance_key: ElementinstancekeyAdvancedfilter | str | Unset = UNSET
    operation_type: OperationtypeAdvancedfilter | OperationtypeExactmatch | Unset = (
        UNSET
    )
    result: SearchAuditLogsDataFilterResult | Unset = UNSET
    timestamp: datetime.datetime | TimestampAdvancedfilter | Unset = UNSET
    actor_id: ActoridAdvancedfilter | str | Unset = UNSET
    actor_type: SearchAuditLogsDataFilterActorType | Unset = UNSET
    entity_type: EntitytypeAdvancedfilter | EntitytypeExactmatch | Unset = UNSET
    tenant_id: ActoridAdvancedfilter | str | Unset = UNSET
    category: CategoryAdvancedfilter | CategoryExactmatch | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.actorid_advancedfilter import ActoridAdvancedfilter
        from ..models.auditlogkey_advancedfilter import AuditlogkeyAdvancedfilter
        from ..models.elementinstancekey_advancedfilter import (
            ElementinstancekeyAdvancedfilter,
        )
        from ..models.processdefinitionkey_advancedfilter import (
            ProcessdefinitionkeyAdvancedfilter,
        )
        from ..models.processinstancekey_advancedfilter import (
            ProcessinstancekeyAdvancedfilter,
        )

        audit_log_key: dict[str, Any] | str | Unset
        if isinstance(self.audit_log_key, Unset):
            audit_log_key = UNSET
        elif isinstance(self.audit_log_key, AuditlogkeyAdvancedfilter):
            audit_log_key = self.audit_log_key.to_dict()
        else:
            audit_log_key = self.audit_log_key

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

        operation_type: dict[str, Any] | str | Unset
        if isinstance(self.operation_type, Unset):
            operation_type = UNSET
        elif isinstance(self.operation_type, OperationtypeExactmatch):
            operation_type = self.operation_type.value
        else:
            operation_type = self.operation_type.to_dict()

        result: str | Unset = UNSET
        if not isinstance(self.result, Unset):
            result = self.result.value

        timestamp: dict[str, Any] | str | Unset
        if isinstance(self.timestamp, Unset):
            timestamp = UNSET
        elif isinstance(self.timestamp, datetime.datetime):
            timestamp = self.timestamp.isoformat()
        else:
            timestamp = self.timestamp.to_dict()

        actor_id: dict[str, Any] | str | Unset
        if isinstance(self.actor_id, Unset):
            actor_id = UNSET
        elif isinstance(self.actor_id, ActoridAdvancedfilter):
            actor_id = self.actor_id.to_dict()
        else:
            actor_id = self.actor_id

        actor_type: str | Unset = UNSET
        if not isinstance(self.actor_type, Unset):
            actor_type = self.actor_type.value

        entity_type: dict[str, Any] | str | Unset
        if isinstance(self.entity_type, Unset):
            entity_type = UNSET
        elif isinstance(self.entity_type, EntitytypeExactmatch):
            entity_type = self.entity_type.value
        else:
            entity_type = self.entity_type.to_dict()

        tenant_id: dict[str, Any] | str | Unset
        if isinstance(self.tenant_id, Unset):
            tenant_id = UNSET
        elif isinstance(self.tenant_id, ActoridAdvancedfilter):
            tenant_id = self.tenant_id.to_dict()
        else:
            tenant_id = self.tenant_id

        category: dict[str, Any] | str | Unset
        if isinstance(self.category, Unset):
            category = UNSET
        elif isinstance(self.category, CategoryExactmatch):
            category = self.category.value
        else:
            category = self.category.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if audit_log_key is not UNSET:
            field_dict["auditLogKey"] = audit_log_key
        if process_definition_key is not UNSET:
            field_dict["processDefinitionKey"] = process_definition_key
        if process_instance_key is not UNSET:
            field_dict["processInstanceKey"] = process_instance_key
        if element_instance_key is not UNSET:
            field_dict["elementInstanceKey"] = element_instance_key
        if operation_type is not UNSET:
            field_dict["operationType"] = operation_type
        if result is not UNSET:
            field_dict["result"] = result
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp
        if actor_id is not UNSET:
            field_dict["actorId"] = actor_id
        if actor_type is not UNSET:
            field_dict["actorType"] = actor_type
        if entity_type is not UNSET:
            field_dict["entityType"] = entity_type
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if category is not UNSET:
            field_dict["category"] = category

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.actorid_advancedfilter import ActoridAdvancedfilter
        from ..models.auditlogkey_advancedfilter import AuditlogkeyAdvancedfilter
        from ..models.category_advancedfilter import CategoryAdvancedfilter
        from ..models.elementinstancekey_advancedfilter import (
            ElementinstancekeyAdvancedfilter,
        )
        from ..models.entitytype_advancedfilter import EntitytypeAdvancedfilter
        from ..models.operationtype_advancedfilter import OperationtypeAdvancedfilter
        from ..models.processdefinitionkey_advancedfilter import (
            ProcessdefinitionkeyAdvancedfilter,
        )
        from ..models.processinstancekey_advancedfilter import (
            ProcessinstancekeyAdvancedfilter,
        )
        from ..models.timestamp_advancedfilter import TimestampAdvancedfilter

        d = dict(src_dict)

        def _parse_audit_log_key(
            data: object,
        ) -> AuditlogkeyAdvancedfilter | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                audit_log_key_type_1 = AuditlogkeyAdvancedfilter.from_dict(data)

                return audit_log_key_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AuditlogkeyAdvancedfilter | str | Unset, data)

        audit_log_key = _parse_audit_log_key(d.pop("auditLogKey", UNSET))

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

        def _parse_operation_type(
            data: object,
        ) -> OperationtypeAdvancedfilter | OperationtypeExactmatch | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                operation_type_type_0 = OperationtypeExactmatch(data)

                return operation_type_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            operation_type_type_1 = OperationtypeAdvancedfilter.from_dict(data)

            return operation_type_type_1

        operation_type = _parse_operation_type(d.pop("operationType", UNSET))

        _result = d.pop("result", UNSET)
        result: SearchAuditLogsDataFilterResult | Unset
        if isinstance(_result, Unset):
            result = UNSET
        else:
            result = SearchAuditLogsDataFilterResult(_result)

        def _parse_timestamp(
            data: object,
        ) -> datetime.datetime | TimestampAdvancedfilter | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                timestamp_type_0 = isoparse(data)

                return timestamp_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            timestamp_type_1 = TimestampAdvancedfilter.from_dict(data)

            return timestamp_type_1

        timestamp = _parse_timestamp(d.pop("timestamp", UNSET))

        def _parse_actor_id(data: object) -> ActoridAdvancedfilter | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                actor_id_type_1 = ActoridAdvancedfilter.from_dict(data)

                return actor_id_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ActoridAdvancedfilter | str | Unset, data)

        actor_id = _parse_actor_id(d.pop("actorId", UNSET))

        _actor_type = d.pop("actorType", UNSET)
        actor_type: SearchAuditLogsDataFilterActorType | Unset
        if isinstance(_actor_type, Unset):
            actor_type = UNSET
        else:
            actor_type = SearchAuditLogsDataFilterActorType(_actor_type)

        def _parse_entity_type(
            data: object,
        ) -> EntitytypeAdvancedfilter | EntitytypeExactmatch | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                entity_type_type_0 = EntitytypeExactmatch(data)

                return entity_type_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            entity_type_type_1 = EntitytypeAdvancedfilter.from_dict(data)

            return entity_type_type_1

        entity_type = _parse_entity_type(d.pop("entityType", UNSET))

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

        def _parse_category(
            data: object,
        ) -> CategoryAdvancedfilter | CategoryExactmatch | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                category_type_0 = CategoryExactmatch(data)

                return category_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            category_type_1 = CategoryAdvancedfilter.from_dict(data)

            return category_type_1

        category = _parse_category(d.pop("category", UNSET))

        search_audit_logs_data_filter = cls(
            audit_log_key=audit_log_key,
            process_definition_key=process_definition_key,
            process_instance_key=process_instance_key,
            element_instance_key=element_instance_key,
            operation_type=operation_type,
            result=result,
            timestamp=timestamp,
            actor_id=actor_id,
            actor_type=actor_type,
            entity_type=entity_type,
            tenant_id=tenant_id,
            category=category,
        )

        search_audit_logs_data_filter.additional_properties = d
        return search_audit_logs_data_filter

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

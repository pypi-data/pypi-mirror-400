from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.actorid_advancedfilter import ActoridAdvancedfilter
    from ..models.batchoperationkey_advancedfilter import (
        BatchoperationkeyAdvancedfilter,
    )
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
    from ..models.subscriptionkey_advancedfilter import SubscriptionkeyAdvancedfilter
    from ..models.timestamp_advancedfilter import TimestampAdvancedfilter


T = TypeVar("T", bound="SearchCorrelatedMessageSubscriptionsDataFilter")


@_attrs_define
class SearchCorrelatedMessageSubscriptionsDataFilter:
    """The correlated message subscriptions search filters.

    Attributes:
        correlation_key (ActoridAdvancedfilter | str | Unset):
        correlation_time (datetime.datetime | TimestampAdvancedfilter | Unset):
        element_id (ActoridAdvancedfilter | str | Unset):
        element_instance_key (ElementinstancekeyAdvancedfilter | str | Unset):
        message_key (BatchoperationkeyAdvancedfilter | str | Unset):
        message_name (ActoridAdvancedfilter | str | Unset):
        partition_id (int | PartitionidAdvancedfilter | Unset):
        process_definition_id (ActoridAdvancedfilter | str | Unset):
        process_definition_key (ProcessdefinitionkeyAdvancedfilter | str | Unset):
        process_instance_key (ProcessinstancekeyAdvancedfilter | str | Unset):
        subscription_key (str | SubscriptionkeyAdvancedfilter | Unset):
        tenant_id (ActoridAdvancedfilter | str | Unset):
    """

    correlation_key: ActoridAdvancedfilter | str | Unset = UNSET
    correlation_time: datetime.datetime | TimestampAdvancedfilter | Unset = UNSET
    element_id: ActoridAdvancedfilter | str | Unset = UNSET
    element_instance_key: ElementinstancekeyAdvancedfilter | str | Unset = UNSET
    message_key: BatchoperationkeyAdvancedfilter | str | Unset = UNSET
    message_name: ActoridAdvancedfilter | str | Unset = UNSET
    partition_id: int | PartitionidAdvancedfilter | Unset = UNSET
    process_definition_id: ActoridAdvancedfilter | str | Unset = UNSET
    process_definition_key: ProcessdefinitionkeyAdvancedfilter | str | Unset = UNSET
    process_instance_key: ProcessinstancekeyAdvancedfilter | str | Unset = UNSET
    subscription_key: MessageSubscriptionKey | SubscriptionkeyAdvancedfilter | Unset = UNSET
    tenant_id: ActoridAdvancedfilter | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.actorid_advancedfilter import ActoridAdvancedfilter
        from ..models.batchoperationkey_advancedfilter import (
            BatchoperationkeyAdvancedfilter,
        )
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
        from ..models.subscriptionkey_advancedfilter import (
            SubscriptionkeyAdvancedfilter,
        )

        correlation_key: dict[str, Any] | str | Unset
        if isinstance(self.correlation_key, Unset):
            correlation_key = UNSET
        elif isinstance(self.correlation_key, ActoridAdvancedfilter):
            correlation_key = self.correlation_key.to_dict()
        else:
            correlation_key = self.correlation_key

        correlation_time: dict[str, Any] | str | Unset
        if isinstance(self.correlation_time, Unset):
            correlation_time = UNSET
        elif isinstance(self.correlation_time, datetime.datetime):
            correlation_time = self.correlation_time.isoformat()
        else:
            correlation_time = self.correlation_time.to_dict()

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

        message_key: dict[str, Any] | str | Unset
        if isinstance(self.message_key, Unset):
            message_key = UNSET
        elif isinstance(self.message_key, BatchoperationkeyAdvancedfilter):
            message_key = self.message_key.to_dict()
        else:
            message_key = self.message_key

        message_name: dict[str, Any] | str | Unset
        if isinstance(self.message_name, Unset):
            message_name = UNSET
        elif isinstance(self.message_name, ActoridAdvancedfilter):
            message_name = self.message_name.to_dict()
        else:
            message_name = self.message_name

        partition_id: dict[str, Any] | int | Unset
        if isinstance(self.partition_id, Unset):
            partition_id = UNSET
        elif isinstance(self.partition_id, PartitionidAdvancedfilter):
            partition_id = self.partition_id.to_dict()
        else:
            partition_id = self.partition_id

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

        subscription_key: dict[str, Any] | str | Unset
        if isinstance(self.subscription_key, Unset):
            subscription_key = UNSET
        elif isinstance(self.subscription_key, SubscriptionkeyAdvancedfilter):
            subscription_key = self.subscription_key.to_dict()
        else:
            subscription_key = self.subscription_key

        tenant_id: dict[str, Any] | str | Unset
        if isinstance(self.tenant_id, Unset):
            tenant_id = UNSET
        elif isinstance(self.tenant_id, ActoridAdvancedfilter):
            tenant_id = self.tenant_id.to_dict()
        else:
            tenant_id = self.tenant_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if correlation_key is not UNSET:
            field_dict["correlationKey"] = correlation_key
        if correlation_time is not UNSET:
            field_dict["correlationTime"] = correlation_time
        if element_id is not UNSET:
            field_dict["elementId"] = element_id
        if element_instance_key is not UNSET:
            field_dict["elementInstanceKey"] = element_instance_key
        if message_key is not UNSET:
            field_dict["messageKey"] = message_key
        if message_name is not UNSET:
            field_dict["messageName"] = message_name
        if partition_id is not UNSET:
            field_dict["partitionId"] = partition_id
        if process_definition_id is not UNSET:
            field_dict["processDefinitionId"] = process_definition_id
        if process_definition_key is not UNSET:
            field_dict["processDefinitionKey"] = process_definition_key
        if process_instance_key is not UNSET:
            field_dict["processInstanceKey"] = process_instance_key
        if subscription_key is not UNSET:
            field_dict["subscriptionKey"] = subscription_key
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id

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
        from ..models.partitionid_advancedfilter import PartitionidAdvancedfilter
        from ..models.processdefinitionkey_advancedfilter import (
            ProcessdefinitionkeyAdvancedfilter,
        )
        from ..models.processinstancekey_advancedfilter import (
            ProcessinstancekeyAdvancedfilter,
        )
        from ..models.subscriptionkey_advancedfilter import (
            SubscriptionkeyAdvancedfilter,
        )
        from ..models.timestamp_advancedfilter import TimestampAdvancedfilter

        d = dict(src_dict)

        def _parse_correlation_key(data: object) -> ActoridAdvancedfilter | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                correlation_key_type_1 = ActoridAdvancedfilter.from_dict(data)

                return correlation_key_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ActoridAdvancedfilter | str | Unset, data)

        correlation_key = _parse_correlation_key(d.pop("correlationKey", UNSET))

        def _parse_correlation_time(
            data: object,
        ) -> datetime.datetime | TimestampAdvancedfilter | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                correlation_time_type_0 = isoparse(data)

                return correlation_time_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            correlation_time_type_1 = TimestampAdvancedfilter.from_dict(data)

            return correlation_time_type_1

        correlation_time = _parse_correlation_time(d.pop("correlationTime", UNSET))

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

        def _parse_message_key(
            data: object,
        ) -> BatchoperationkeyAdvancedfilter | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                message_key_type_1 = BatchoperationkeyAdvancedfilter.from_dict(data)

                return message_key_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(BatchoperationkeyAdvancedfilter | str | Unset, data)

        message_key = _parse_message_key(d.pop("messageKey", UNSET))

        def _parse_message_name(data: object) -> ActoridAdvancedfilter | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                message_name_type_1 = ActoridAdvancedfilter.from_dict(data)

                return message_name_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ActoridAdvancedfilter | str | Unset, data)

        message_name = _parse_message_name(d.pop("messageName", UNSET))

        def _parse_partition_id(
            data: object,
        ) -> int | PartitionidAdvancedfilter | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                partition_id_type_1 = PartitionidAdvancedfilter.from_dict(data)

                return partition_id_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(int | PartitionidAdvancedfilter | Unset, data)

        partition_id = _parse_partition_id(d.pop("partitionId", UNSET))

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

        def _parse_subscription_key(
            data: object,
        ) -> str | SubscriptionkeyAdvancedfilter | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                subscription_key_type_1 = SubscriptionkeyAdvancedfilter.from_dict(data)

                return subscription_key_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(str | SubscriptionkeyAdvancedfilter | Unset, data)

        subscription_key = _parse_subscription_key(d.pop("subscriptionKey", UNSET))

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

        search_correlated_message_subscriptions_data_filter = cls(
            correlation_key=correlation_key,
            correlation_time=correlation_time,
            element_id=element_id,
            element_instance_key=element_instance_key,
            message_key=message_key,
            message_name=message_name,
            partition_id=partition_id,
            process_definition_id=process_definition_id,
            process_definition_key=process_definition_key,
            process_instance_key=process_instance_key,
            subscription_key=subscription_key,
            tenant_id=tenant_id,
        )

        search_correlated_message_subscriptions_data_filter.additional_properties = d
        return search_correlated_message_subscriptions_data_filter

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

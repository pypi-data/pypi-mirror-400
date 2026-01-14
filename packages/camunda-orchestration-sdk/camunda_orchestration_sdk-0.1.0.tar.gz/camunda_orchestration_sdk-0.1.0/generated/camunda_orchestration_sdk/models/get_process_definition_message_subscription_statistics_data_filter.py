from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.messagesubscriptionstate_exactmatch import (
    MessagesubscriptionstateExactmatch,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.actorid_advancedfilter import ActoridAdvancedfilter
    from ..models.elementinstancekey_advancedfilter import (
        ElementinstancekeyAdvancedfilter,
    )
    from ..models.messagesubscriptionstate_advancedfilter import (
        MessagesubscriptionstateAdvancedfilter,
    )
    from ..models.processdefinitionkey_advancedfilter import (
        ProcessdefinitionkeyAdvancedfilter,
    )
    from ..models.processinstancekey_advancedfilter import (
        ProcessinstancekeyAdvancedfilter,
    )
    from ..models.subscriptionkey_advancedfilter import SubscriptionkeyAdvancedfilter
    from ..models.timestamp_advancedfilter import TimestampAdvancedfilter


T = TypeVar("T", bound="GetProcessDefinitionMessageSubscriptionStatisticsDataFilter")


@_attrs_define
class GetProcessDefinitionMessageSubscriptionStatisticsDataFilter:
    """The message subscription filters.

    Attributes:
        message_subscription_key (str | SubscriptionkeyAdvancedfilter | Unset):
        process_definition_key (ProcessdefinitionkeyAdvancedfilter | str | Unset):
        process_definition_id (ActoridAdvancedfilter | str | Unset):
        process_instance_key (ProcessinstancekeyAdvancedfilter | str | Unset):
        element_id (ActoridAdvancedfilter | str | Unset):
        element_instance_key (ElementinstancekeyAdvancedfilter | str | Unset):
        message_subscription_state (MessagesubscriptionstateAdvancedfilter | MessagesubscriptionstateExactmatch |
            Unset):
        last_updated_date (datetime.datetime | TimestampAdvancedfilter | Unset):
        message_name (ActoridAdvancedfilter | str | Unset):
        correlation_key (ActoridAdvancedfilter | str | Unset):
        tenant_id (ActoridAdvancedfilter | str | Unset):
    """

    message_subscription_key: MessageSubscriptionKey | SubscriptionkeyAdvancedfilter | Unset = UNSET
    process_definition_key: ProcessdefinitionkeyAdvancedfilter | str | Unset = UNSET
    process_definition_id: ActoridAdvancedfilter | str | Unset = UNSET
    process_instance_key: ProcessinstancekeyAdvancedfilter | str | Unset = UNSET
    element_id: ActoridAdvancedfilter | str | Unset = UNSET
    element_instance_key: ElementinstancekeyAdvancedfilter | str | Unset = UNSET
    message_subscription_state: (
        MessagesubscriptionstateAdvancedfilter
        | MessagesubscriptionstateExactmatch
        | Unset
    ) = UNSET
    last_updated_date: datetime.datetime | TimestampAdvancedfilter | Unset = UNSET
    message_name: ActoridAdvancedfilter | str | Unset = UNSET
    correlation_key: ActoridAdvancedfilter | str | Unset = UNSET
    tenant_id: ActoridAdvancedfilter | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.actorid_advancedfilter import ActoridAdvancedfilter
        from ..models.elementinstancekey_advancedfilter import (
            ElementinstancekeyAdvancedfilter,
        )
        from ..models.processdefinitionkey_advancedfilter import (
            ProcessdefinitionkeyAdvancedfilter,
        )
        from ..models.processinstancekey_advancedfilter import (
            ProcessinstancekeyAdvancedfilter,
        )
        from ..models.subscriptionkey_advancedfilter import (
            SubscriptionkeyAdvancedfilter,
        )

        message_subscription_key: dict[str, Any] | str | Unset
        if isinstance(self.message_subscription_key, Unset):
            message_subscription_key = UNSET
        elif isinstance(self.message_subscription_key, SubscriptionkeyAdvancedfilter):
            message_subscription_key = self.message_subscription_key.to_dict()
        else:
            message_subscription_key = self.message_subscription_key

        process_definition_key: dict[str, Any] | str | Unset
        if isinstance(self.process_definition_key, Unset):
            process_definition_key = UNSET
        elif isinstance(
            self.process_definition_key, ProcessdefinitionkeyAdvancedfilter
        ):
            process_definition_key = self.process_definition_key.to_dict()
        else:
            process_definition_key = self.process_definition_key

        process_definition_id: dict[str, Any] | str | Unset
        if isinstance(self.process_definition_id, Unset):
            process_definition_id = UNSET
        elif isinstance(self.process_definition_id, ActoridAdvancedfilter):
            process_definition_id = self.process_definition_id.to_dict()
        else:
            process_definition_id = self.process_definition_id

        process_instance_key: dict[str, Any] | str | Unset
        if isinstance(self.process_instance_key, Unset):
            process_instance_key = UNSET
        elif isinstance(self.process_instance_key, ProcessinstancekeyAdvancedfilter):
            process_instance_key = self.process_instance_key.to_dict()
        else:
            process_instance_key = self.process_instance_key

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

        message_subscription_state: dict[str, Any] | str | Unset
        if isinstance(self.message_subscription_state, Unset):
            message_subscription_state = UNSET
        elif isinstance(
            self.message_subscription_state, MessagesubscriptionstateExactmatch
        ):
            message_subscription_state = self.message_subscription_state.value
        else:
            message_subscription_state = self.message_subscription_state.to_dict()

        last_updated_date: dict[str, Any] | str | Unset
        if isinstance(self.last_updated_date, Unset):
            last_updated_date = UNSET
        elif isinstance(self.last_updated_date, datetime.datetime):
            last_updated_date = self.last_updated_date.isoformat()
        else:
            last_updated_date = self.last_updated_date.to_dict()

        message_name: dict[str, Any] | str | Unset
        if isinstance(self.message_name, Unset):
            message_name = UNSET
        elif isinstance(self.message_name, ActoridAdvancedfilter):
            message_name = self.message_name.to_dict()
        else:
            message_name = self.message_name

        correlation_key: dict[str, Any] | str | Unset
        if isinstance(self.correlation_key, Unset):
            correlation_key = UNSET
        elif isinstance(self.correlation_key, ActoridAdvancedfilter):
            correlation_key = self.correlation_key.to_dict()
        else:
            correlation_key = self.correlation_key

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
        if message_subscription_key is not UNSET:
            field_dict["messageSubscriptionKey"] = message_subscription_key
        if process_definition_key is not UNSET:
            field_dict["processDefinitionKey"] = process_definition_key
        if process_definition_id is not UNSET:
            field_dict["processDefinitionId"] = process_definition_id
        if process_instance_key is not UNSET:
            field_dict["processInstanceKey"] = process_instance_key
        if element_id is not UNSET:
            field_dict["elementId"] = element_id
        if element_instance_key is not UNSET:
            field_dict["elementInstanceKey"] = element_instance_key
        if message_subscription_state is not UNSET:
            field_dict["messageSubscriptionState"] = message_subscription_state
        if last_updated_date is not UNSET:
            field_dict["lastUpdatedDate"] = last_updated_date
        if message_name is not UNSET:
            field_dict["messageName"] = message_name
        if correlation_key is not UNSET:
            field_dict["correlationKey"] = correlation_key
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.actorid_advancedfilter import ActoridAdvancedfilter
        from ..models.elementinstancekey_advancedfilter import (
            ElementinstancekeyAdvancedfilter,
        )
        from ..models.messagesubscriptionstate_advancedfilter import (
            MessagesubscriptionstateAdvancedfilter,
        )
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

        def _parse_message_subscription_key(
            data: object,
        ) -> str | SubscriptionkeyAdvancedfilter | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                message_subscription_key_type_1 = (
                    SubscriptionkeyAdvancedfilter.from_dict(data)
                )

                return message_subscription_key_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(str | SubscriptionkeyAdvancedfilter | Unset, data)

        message_subscription_key = _parse_message_subscription_key(
            d.pop("messageSubscriptionKey", UNSET)
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

        def _parse_message_subscription_state(
            data: object,
        ) -> (
            MessagesubscriptionstateAdvancedfilter
            | MessagesubscriptionstateExactmatch
            | Unset
        ):
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                message_subscription_state_type_0 = MessagesubscriptionstateExactmatch(
                    data
                )

                return message_subscription_state_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            message_subscription_state_type_1 = (
                MessagesubscriptionstateAdvancedfilter.from_dict(data)
            )

            return message_subscription_state_type_1

        message_subscription_state = _parse_message_subscription_state(
            d.pop("messageSubscriptionState", UNSET)
        )

        def _parse_last_updated_date(
            data: object,
        ) -> datetime.datetime | TimestampAdvancedfilter | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_updated_date_type_0 = isoparse(data)

                return last_updated_date_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            last_updated_date_type_1 = TimestampAdvancedfilter.from_dict(data)

            return last_updated_date_type_1

        last_updated_date = _parse_last_updated_date(d.pop("lastUpdatedDate", UNSET))

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

        get_process_definition_message_subscription_statistics_data_filter = cls(
            message_subscription_key=message_subscription_key,
            process_definition_key=process_definition_key,
            process_definition_id=process_definition_id,
            process_instance_key=process_instance_key,
            element_id=element_id,
            element_instance_key=element_instance_key,
            message_subscription_state=message_subscription_state,
            last_updated_date=last_updated_date,
            message_name=message_name,
            correlation_key=correlation_key,
            tenant_id=tenant_id,
        )

        get_process_definition_message_subscription_statistics_data_filter.additional_properties = d
        return get_process_definition_message_subscription_statistics_data_filter

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

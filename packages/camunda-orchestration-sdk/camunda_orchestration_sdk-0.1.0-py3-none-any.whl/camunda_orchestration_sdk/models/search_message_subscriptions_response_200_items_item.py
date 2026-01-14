from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.search_message_subscriptions_response_200_items_item_message_subscription_state import (
    SearchMessageSubscriptionsResponse200ItemsItemMessageSubscriptionState,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="SearchMessageSubscriptionsResponse200ItemsItem")


@_attrs_define
class SearchMessageSubscriptionsResponse200ItemsItem:
    """
    Attributes:
        message_subscription_key (str | Unset): The message subscription key associated with this message subscription.
            Example: 2251799813632456.
        process_definition_id (str | Unset): The process definition ID associated with this message subscription.
            Example: new-account-onboarding-workflow.
        process_definition_key (str | Unset): The process definition key associated with this message subscription.
            Example: 2251799813686749.
        process_instance_key (str | Unset): The process instance key associated with this message subscription. Example:
            2251799813690746.
        element_id (str | Unset): The element ID associated with this message subscription. Example: Activity_106kosb.
        element_instance_key (str | Unset): The element instance key associated with this message subscription. Example:
            2251799813686789.
        message_subscription_state (SearchMessageSubscriptionsResponse200ItemsItemMessageSubscriptionState | Unset): The
            state of message subscription.
        last_updated_date (datetime.datetime | Unset): The last updated date of the message subscription.
        message_name (str | Unset): The name of the message associated with the message subscription.
        correlation_key (str | Unset): The correlation key of the message subscription. Example: 2251799813634265.
        tenant_id (str | Unset): The unique identifier of the tenant. Example: customer-service.
    """

    message_subscription_key: MessageSubscriptionKey | Unset = UNSET
    process_definition_id: ProcessDefinitionId | Unset = UNSET
    process_definition_key: ProcessDefinitionKey | Unset = UNSET
    process_instance_key: ProcessInstanceKey | Unset = UNSET
    element_id: ElementId | Unset = UNSET
    element_instance_key: ElementInstanceKey | Unset = UNSET
    message_subscription_state: (
        SearchMessageSubscriptionsResponse200ItemsItemMessageSubscriptionState | Unset
    ) = UNSET
    last_updated_date: datetime.datetime | Unset = UNSET
    message_name: str | Unset = UNSET
    correlation_key: MessageCorrelationKey | Unset = UNSET
    tenant_id: TenantId | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        message_subscription_key = self.message_subscription_key

        process_definition_id = self.process_definition_id

        process_definition_key = self.process_definition_key

        process_instance_key = self.process_instance_key

        element_id = self.element_id

        element_instance_key = self.element_instance_key

        message_subscription_state: str | Unset = UNSET
        if not isinstance(self.message_subscription_state, Unset):
            message_subscription_state = self.message_subscription_state.value

        last_updated_date: str | Unset = UNSET
        if not isinstance(self.last_updated_date, Unset):
            last_updated_date = self.last_updated_date.isoformat()

        message_name = self.message_name

        correlation_key = self.correlation_key

        tenant_id = self.tenant_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if message_subscription_key is not UNSET:
            field_dict["messageSubscriptionKey"] = message_subscription_key
        if process_definition_id is not UNSET:
            field_dict["processDefinitionId"] = process_definition_id
        if process_definition_key is not UNSET:
            field_dict["processDefinitionKey"] = process_definition_key
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
        d = dict(src_dict)
        message_subscription_key = lift_message_subscription_key(_val) if (_val := d.pop("messageSubscriptionKey", UNSET)) is not UNSET else UNSET

        process_definition_id = lift_process_definition_id(_val) if (_val := d.pop("processDefinitionId", UNSET)) is not UNSET else UNSET

        process_definition_key = lift_process_definition_key(_val) if (_val := d.pop("processDefinitionKey", UNSET)) is not UNSET else UNSET

        process_instance_key = lift_process_instance_key(_val) if (_val := d.pop("processInstanceKey", UNSET)) is not UNSET else UNSET

        element_id = lift_element_id(_val) if (_val := d.pop("elementId", UNSET)) is not UNSET else UNSET

        element_instance_key = lift_element_instance_key(_val) if (_val := d.pop("elementInstanceKey", UNSET)) is not UNSET else UNSET

        _message_subscription_state = d.pop("messageSubscriptionState", UNSET)
        message_subscription_state: (
            SearchMessageSubscriptionsResponse200ItemsItemMessageSubscriptionState
            | Unset
        )
        if isinstance(_message_subscription_state, Unset):
            message_subscription_state = UNSET
        else:
            message_subscription_state = (
                SearchMessageSubscriptionsResponse200ItemsItemMessageSubscriptionState(
                    _message_subscription_state
                )
            )

        _last_updated_date = d.pop("lastUpdatedDate", UNSET)
        last_updated_date: datetime.datetime | Unset
        if isinstance(_last_updated_date, Unset):
            last_updated_date = UNSET
        else:
            last_updated_date = isoparse(_last_updated_date)

        message_name = d.pop("messageName", UNSET)

        correlation_key = lift_message_correlation_key(_val) if (_val := d.pop("correlationKey", UNSET)) is not UNSET else UNSET

        tenant_id = lift_tenant_id(_val) if (_val := d.pop("tenantId", UNSET)) is not UNSET else UNSET

        search_message_subscriptions_response_200_items_item = cls(
            message_subscription_key=message_subscription_key,
            process_definition_id=process_definition_id,
            process_definition_key=process_definition_key,
            process_instance_key=process_instance_key,
            element_id=element_id,
            element_instance_key=element_instance_key,
            message_subscription_state=message_subscription_state,
            last_updated_date=last_updated_date,
            message_name=message_name,
            correlation_key=correlation_key,
            tenant_id=tenant_id,
        )

        search_message_subscriptions_response_200_items_item.additional_properties = d
        return search_message_subscriptions_response_200_items_item

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

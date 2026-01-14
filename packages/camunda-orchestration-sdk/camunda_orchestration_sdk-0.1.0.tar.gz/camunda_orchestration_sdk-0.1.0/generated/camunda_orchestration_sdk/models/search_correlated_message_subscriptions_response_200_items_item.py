from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="SearchCorrelatedMessageSubscriptionsResponse200ItemsItem")


@_attrs_define
class SearchCorrelatedMessageSubscriptionsResponse200ItemsItem:
    """
    Attributes:
        correlation_key (str): The correlation key of the message.
        correlation_time (datetime.datetime): The time when the message was correlated.
        element_id (str): The element ID that received the message.
        message_key (str): The message key. Example: 2251799813683467.
        message_name (str): The name of the message.
        partition_id (int): The partition ID that correlated the message.
        process_definition_id (str): The process definition ID associated with this correlated message subscription.
            Example: new-account-onboarding-workflow.
        process_instance_key (str): The process instance key associated with this correlated message subscription.
            Example: 2251799813690746.
        subscription_key (str): The subscription key that received the message. Example: 2251799813632456.
        tenant_id (str): The tenant ID associated with this correlated message subscription. Example: customer-service.
        element_instance_key (str | Unset): The element instance key that received the message. Example:
            2251799813686789.
        process_definition_key (str | Unset): The process definition key associated with this correlated message
            subscription. Example: 2251799813686749.
    """

    correlation_key: MessageCorrelationKey
    correlation_time: datetime.datetime
    element_id: ElementId
    message_key: MessageKey
    message_name: str
    partition_id: int
    process_definition_id: ProcessDefinitionId
    process_instance_key: ProcessInstanceKey
    subscription_key: MessageSubscriptionKey
    tenant_id: TenantId
    element_instance_key: ElementInstanceKey | Unset = UNSET
    process_definition_key: ProcessDefinitionKey | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        correlation_key = self.correlation_key

        correlation_time = self.correlation_time.isoformat()

        element_id = self.element_id

        message_key = self.message_key

        message_name = self.message_name

        partition_id = self.partition_id

        process_definition_id = self.process_definition_id

        process_instance_key = self.process_instance_key

        subscription_key = self.subscription_key

        tenant_id = self.tenant_id

        element_instance_key = self.element_instance_key

        process_definition_key = self.process_definition_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "correlationKey": correlation_key,
                "correlationTime": correlation_time,
                "elementId": element_id,
                "messageKey": message_key,
                "messageName": message_name,
                "partitionId": partition_id,
                "processDefinitionId": process_definition_id,
                "processInstanceKey": process_instance_key,
                "subscriptionKey": subscription_key,
                "tenantId": tenant_id,
            }
        )
        if element_instance_key is not UNSET:
            field_dict["elementInstanceKey"] = element_instance_key
        if process_definition_key is not UNSET:
            field_dict["processDefinitionKey"] = process_definition_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        correlation_key = lift_message_correlation_key(d.pop("correlationKey"))

        correlation_time = isoparse(d.pop("correlationTime"))

        element_id = lift_element_id(d.pop("elementId"))

        message_key = lift_message_key(d.pop("messageKey"))

        message_name = d.pop("messageName")

        partition_id = d.pop("partitionId")

        process_definition_id = lift_process_definition_id(d.pop("processDefinitionId"))

        process_instance_key = lift_process_instance_key(d.pop("processInstanceKey"))

        subscription_key = lift_message_subscription_key(d.pop("subscriptionKey"))

        tenant_id = lift_tenant_id(d.pop("tenantId"))

        element_instance_key = lift_element_instance_key(_val) if (_val := d.pop("elementInstanceKey", UNSET)) is not UNSET else UNSET

        process_definition_key = lift_process_definition_key(_val) if (_val := d.pop("processDefinitionKey", UNSET)) is not UNSET else UNSET

        search_correlated_message_subscriptions_response_200_items_item = cls(
            correlation_key=correlation_key,
            correlation_time=correlation_time,
            element_id=element_id,
            message_key=message_key,
            message_name=message_name,
            partition_id=partition_id,
            process_definition_id=process_definition_id,
            process_instance_key=process_instance_key,
            subscription_key=subscription_key,
            tenant_id=tenant_id,
            element_instance_key=element_instance_key,
            process_definition_key=process_definition_key,
        )

        search_correlated_message_subscriptions_response_200_items_item.additional_properties = d
        return search_correlated_message_subscriptions_response_200_items_item

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

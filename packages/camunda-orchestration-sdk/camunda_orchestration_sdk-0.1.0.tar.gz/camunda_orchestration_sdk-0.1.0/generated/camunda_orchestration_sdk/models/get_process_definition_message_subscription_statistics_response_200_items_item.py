from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar(
    "T", bound="GetProcessDefinitionMessageSubscriptionStatisticsResponse200ItemsItem"
)


@_attrs_define
class GetProcessDefinitionMessageSubscriptionStatisticsResponse200ItemsItem:
    """
    Attributes:
        process_definition_id (str | Unset): The process definition ID associated with this message subscription.
            Example: new-account-onboarding-workflow.
        tenant_id (str | Unset): The tenant ID associated with this message subscription. Example: customer-service.
        process_definition_key (str | Unset): The process definition key associated with this message subscription.
            Example: 2251799813686749.
        process_instances_with_active_subscriptions (int | Unset): The number of process instances with active message
            subscriptions.
        active_subscriptions (int | Unset): The total number of active message subscriptions for this process definition
            key.
    """

    process_definition_id: ProcessDefinitionId | Unset = UNSET
    tenant_id: TenantId | Unset = UNSET
    process_definition_key: ProcessDefinitionKey | Unset = UNSET
    process_instances_with_active_subscriptions: int | Unset = UNSET
    active_subscriptions: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        process_definition_id = self.process_definition_id

        tenant_id = self.tenant_id

        process_definition_key = self.process_definition_key

        process_instances_with_active_subscriptions = (
            self.process_instances_with_active_subscriptions
        )

        active_subscriptions = self.active_subscriptions

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if process_definition_id is not UNSET:
            field_dict["processDefinitionId"] = process_definition_id
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if process_definition_key is not UNSET:
            field_dict["processDefinitionKey"] = process_definition_key
        if process_instances_with_active_subscriptions is not UNSET:
            field_dict["processInstancesWithActiveSubscriptions"] = (
                process_instances_with_active_subscriptions
            )
        if active_subscriptions is not UNSET:
            field_dict["activeSubscriptions"] = active_subscriptions

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        process_definition_id = lift_process_definition_id(_val) if (_val := d.pop("processDefinitionId", UNSET)) is not UNSET else UNSET

        tenant_id = lift_tenant_id(_val) if (_val := d.pop("tenantId", UNSET)) is not UNSET else UNSET

        process_definition_key = lift_process_definition_key(_val) if (_val := d.pop("processDefinitionKey", UNSET)) is not UNSET else UNSET

        process_instances_with_active_subscriptions = d.pop(
            "processInstancesWithActiveSubscriptions", UNSET
        )

        active_subscriptions = d.pop("activeSubscriptions", UNSET)

        get_process_definition_message_subscription_statistics_response_200_items_item = cls(
            process_definition_id=process_definition_id,
            tenant_id=tenant_id,
            process_definition_key=process_definition_key,
            process_instances_with_active_subscriptions=process_instances_with_active_subscriptions,
            active_subscriptions=active_subscriptions,
        )

        get_process_definition_message_subscription_statistics_response_200_items_item.additional_properties = d
        return get_process_definition_message_subscription_statistics_response_200_items_item

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

from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.actorid_advancedfilter import ActoridAdvancedfilter
    from ..models.processinstancekey_advancedfilter import (
        ProcessinstancekeyAdvancedfilter,
    )
    from ..models.scopekey_advancedfilter import ScopekeyAdvancedfilter
    from ..models.variablekey_advancedfilter import VariablekeyAdvancedfilter


T = TypeVar("T", bound="SearchVariablesDataFilter")


@_attrs_define
class SearchVariablesDataFilter:
    """The variable search filters.

    Attributes:
        name (ActoridAdvancedfilter | str | Unset):
        value (ActoridAdvancedfilter | str | Unset):
        tenant_id (str | Unset): Tenant ID of this variable. Example: customer-service.
        is_truncated (bool | Unset): Whether the value is truncated or not.
        variable_key (str | Unset | VariablekeyAdvancedfilter):
        scope_key (ScopekeyAdvancedfilter | str | Unset):
        process_instance_key (ProcessinstancekeyAdvancedfilter | str | Unset):
    """

    name: ActoridAdvancedfilter | str | Unset = UNSET
    value: ActoridAdvancedfilter | str | Unset = UNSET
    tenant_id: TenantId | Unset = UNSET
    is_truncated: bool | Unset = UNSET
    variable_key: VariableKey | Unset | VariablekeyAdvancedfilter = UNSET
    scope_key: ScopekeyAdvancedfilter | str | Unset = UNSET
    process_instance_key: ProcessinstancekeyAdvancedfilter | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.actorid_advancedfilter import ActoridAdvancedfilter
        from ..models.processinstancekey_advancedfilter import (
            ProcessinstancekeyAdvancedfilter,
        )
        from ..models.scopekey_advancedfilter import ScopekeyAdvancedfilter
        from ..models.variablekey_advancedfilter import VariablekeyAdvancedfilter

        name: dict[str, Any] | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        elif isinstance(self.name, ActoridAdvancedfilter):
            name = self.name.to_dict()
        else:
            name = self.name

        value: dict[str, Any] | str | Unset
        if isinstance(self.value, Unset):
            value = UNSET
        elif isinstance(self.value, ActoridAdvancedfilter):
            value = self.value.to_dict()
        else:
            value = self.value

        tenant_id = self.tenant_id

        is_truncated = self.is_truncated

        variable_key: dict[str, Any] | str | Unset
        if isinstance(self.variable_key, Unset):
            variable_key = UNSET
        elif isinstance(self.variable_key, VariablekeyAdvancedfilter):
            variable_key = self.variable_key.to_dict()
        else:
            variable_key = self.variable_key

        scope_key: dict[str, Any] | str | Unset
        if isinstance(self.scope_key, Unset):
            scope_key = UNSET
        elif isinstance(self.scope_key, ScopekeyAdvancedfilter):
            scope_key = self.scope_key.to_dict()
        else:
            scope_key = self.scope_key

        process_instance_key: dict[str, Any] | str | Unset
        if isinstance(self.process_instance_key, Unset):
            process_instance_key = UNSET
        elif isinstance(self.process_instance_key, ProcessinstancekeyAdvancedfilter):
            process_instance_key = self.process_instance_key.to_dict()
        else:
            process_instance_key = self.process_instance_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if value is not UNSET:
            field_dict["value"] = value
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if is_truncated is not UNSET:
            field_dict["isTruncated"] = is_truncated
        if variable_key is not UNSET:
            field_dict["variableKey"] = variable_key
        if scope_key is not UNSET:
            field_dict["scopeKey"] = scope_key
        if process_instance_key is not UNSET:
            field_dict["processInstanceKey"] = process_instance_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.actorid_advancedfilter import ActoridAdvancedfilter
        from ..models.processinstancekey_advancedfilter import (
            ProcessinstancekeyAdvancedfilter,
        )
        from ..models.scopekey_advancedfilter import ScopekeyAdvancedfilter
        from ..models.variablekey_advancedfilter import VariablekeyAdvancedfilter

        d = dict(src_dict)

        def _parse_name(data: object) -> ActoridAdvancedfilter | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                name_type_1 = ActoridAdvancedfilter.from_dict(data)

                return name_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ActoridAdvancedfilter | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_value(data: object) -> ActoridAdvancedfilter | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                value_type_1 = ActoridAdvancedfilter.from_dict(data)

                return value_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ActoridAdvancedfilter | str | Unset, data)

        value = _parse_value(d.pop("value", UNSET))

        tenant_id = lift_tenant_id(_val) if (_val := d.pop("tenantId", UNSET)) is not UNSET else UNSET

        is_truncated = d.pop("isTruncated", UNSET)

        def _parse_variable_key(
            data: object,
        ) -> str | Unset | VariablekeyAdvancedfilter:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                variable_key_type_1 = VariablekeyAdvancedfilter.from_dict(data)

                return variable_key_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(str | Unset | VariablekeyAdvancedfilter, data)

        variable_key = _parse_variable_key(d.pop("variableKey", UNSET))

        def _parse_scope_key(data: object) -> ScopekeyAdvancedfilter | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                scope_key_type_1 = ScopekeyAdvancedfilter.from_dict(data)

                return scope_key_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ScopekeyAdvancedfilter | str | Unset, data)

        scope_key = _parse_scope_key(d.pop("scopeKey", UNSET))

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

        search_variables_data_filter = cls(
            name=name,
            value=value,
            tenant_id=tenant_id,
            is_truncated=is_truncated,
            variable_key=variable_key,
            scope_key=scope_key,
            process_instance_key=process_instance_key,
        )

        search_variables_data_filter.additional_properties = d
        return search_variables_data_filter

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

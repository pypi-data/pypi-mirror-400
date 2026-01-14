from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.actorid_advancedfilter import ActoridAdvancedfilter


T = TypeVar("T", bound="SearchProcessDefinitionsDataFilter")


@_attrs_define
class SearchProcessDefinitionsDataFilter:
    """The process definition search filters.

    Attributes:
        name (ActoridAdvancedfilter | str | Unset):
        is_latest_version (bool | Unset): Whether to only return the latest version of each process definition.
            When using this filter, pagination functionality is limited, you can only paginate forward using `after` and
            `limit`.
            The response contains no `startCursor` in the `page`, and requests ignore the `from` and `before` in the `page`.
        resource_name (str | Unset): Resource name of this process definition.
        version (int | Unset): Version of this process definition.
        version_tag (str | Unset): Version tag of this process definition.
        process_definition_id (ActoridAdvancedfilter | str | Unset):
        tenant_id (str | Unset): Tenant ID of this process definition. Example: customer-service.
        process_definition_key (str | Unset): The key for this process definition. Example: 2251799813686749.
        has_start_form (bool | Unset): Indicates whether the start event of the process has an associated Form Key.
    """

    name: ActoridAdvancedfilter | str | Unset = UNSET
    is_latest_version: bool | Unset = UNSET
    resource_name: str | Unset = UNSET
    version: int | Unset = UNSET
    version_tag: str | Unset = UNSET
    process_definition_id: ActoridAdvancedfilter | str | Unset = UNSET
    tenant_id: TenantId | Unset = UNSET
    process_definition_key: ProcessDefinitionKey | Unset = UNSET
    has_start_form: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.actorid_advancedfilter import ActoridAdvancedfilter

        name: dict[str, Any] | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        elif isinstance(self.name, ActoridAdvancedfilter):
            name = self.name.to_dict()
        else:
            name = self.name

        is_latest_version = self.is_latest_version

        resource_name = self.resource_name

        version = self.version

        version_tag = self.version_tag

        process_definition_id: dict[str, Any] | str | Unset
        if isinstance(self.process_definition_id, Unset):
            process_definition_id = UNSET
        elif isinstance(self.process_definition_id, ActoridAdvancedfilter):
            process_definition_id = self.process_definition_id.to_dict()
        else:
            process_definition_id = self.process_definition_id

        tenant_id = self.tenant_id

        process_definition_key = self.process_definition_key

        has_start_form = self.has_start_form

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if is_latest_version is not UNSET:
            field_dict["isLatestVersion"] = is_latest_version
        if resource_name is not UNSET:
            field_dict["resourceName"] = resource_name
        if version is not UNSET:
            field_dict["version"] = version
        if version_tag is not UNSET:
            field_dict["versionTag"] = version_tag
        if process_definition_id is not UNSET:
            field_dict["processDefinitionId"] = process_definition_id
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if process_definition_key is not UNSET:
            field_dict["processDefinitionKey"] = process_definition_key
        if has_start_form is not UNSET:
            field_dict["hasStartForm"] = has_start_form

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.actorid_advancedfilter import ActoridAdvancedfilter

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

        is_latest_version = d.pop("isLatestVersion", UNSET)

        resource_name = d.pop("resourceName", UNSET)

        version = d.pop("version", UNSET)

        version_tag = d.pop("versionTag", UNSET)

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

        tenant_id = lift_tenant_id(_val) if (_val := d.pop("tenantId", UNSET)) is not UNSET else UNSET

        process_definition_key = lift_process_definition_key(_val) if (_val := d.pop("processDefinitionKey", UNSET)) is not UNSET else UNSET

        has_start_form = d.pop("hasStartForm", UNSET)

        search_process_definitions_data_filter = cls(
            name=name,
            is_latest_version=is_latest_version,
            resource_name=resource_name,
            version=version,
            version_tag=version_tag,
            process_definition_id=process_definition_id,
            tenant_id=tenant_id,
            process_definition_key=process_definition_key,
            has_start_form=has_start_form,
        )

        search_process_definitions_data_filter.additional_properties = d
        return search_process_definitions_data_filter

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

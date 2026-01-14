from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_element_instance_variables_data_variables import (
        CreateElementInstanceVariablesDataVariables,
    )


T = TypeVar("T", bound="CreateElementInstanceVariablesData")


@_attrs_define
class CreateElementInstanceVariablesData:
    """
    Attributes:
        variables (CreateElementInstanceVariablesDataVariables): JSON object representing the variables to set in the
            element’s scope.
        local (bool | Unset): If set to true, the variables are merged strictly into the local scope (as specified by
            the `elementInstanceKey`).
            Otherwise, the variables are propagated to upper scopes and set at the outermost one.
            Let’s consider the following example:
            There are two scopes '1' and '2'.
            Scope '1' is the parent scope of '2'. The effective variables of the scopes are:
            1 => { "foo" : 2 }
            2 => { "bar" : 1 }
            An update request with elementInstanceKey as '2', variables { "foo" : 5 }, and local set
            to true leaves scope '1' unchanged and adjusts scope '2' to { "bar" : 1, "foo" 5 }.
            By default, with local set to false, scope '1' will be { "foo": 5 }
            and scope '2' will be { "bar" : 1 }.
             Default: False.
        operation_reference (int | Unset): A reference key chosen by the user that will be part of all records resulting
            from this operation.
            Must be > 0 if provided.
    """

    variables: CreateElementInstanceVariablesDataVariables
    local: bool | Unset = False
    operation_reference: int | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        variables = self.variables.to_dict()

        local = self.local

        operation_reference = self.operation_reference

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "variables": variables,
            }
        )
        if local is not UNSET:
            field_dict["local"] = local
        if operation_reference is not UNSET:
            field_dict["operationReference"] = operation_reference

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_element_instance_variables_data_variables import (
            CreateElementInstanceVariablesDataVariables,
        )

        d = dict(src_dict)
        variables = CreateElementInstanceVariablesDataVariables.from_dict(
            d.pop("variables")
        )

        local = d.pop("local", UNSET)

        operation_reference = d.pop("operationReference", UNSET)

        create_element_instance_variables_data = cls(
            variables=variables,
            local=local,
            operation_reference=operation_reference,
        )

        return create_element_instance_variables_data

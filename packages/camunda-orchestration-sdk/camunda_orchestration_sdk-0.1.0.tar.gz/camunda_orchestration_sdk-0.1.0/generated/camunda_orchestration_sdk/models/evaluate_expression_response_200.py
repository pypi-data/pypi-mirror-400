from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.evaluate_expression_response_200_result import (
        EvaluateExpressionResponse200Result,
    )


T = TypeVar("T", bound="EvaluateExpressionResponse200")


@_attrs_define
class EvaluateExpressionResponse200:
    """
    Attributes:
        expression (str): The evaluated expression Example: =x + y.
        result (EvaluateExpressionResponse200Result): The result value. Its type can vary. Example: 30.
        warnings (list[str]): List of warnings generated during expression evaluation
    """

    expression: str
    result: EvaluateExpressionResponse200Result
    warnings: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        expression = self.expression

        result = self.result.to_dict()

        warnings = self.warnings

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "expression": expression,
                "result": result,
                "warnings": warnings,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.evaluate_expression_response_200_result import (
            EvaluateExpressionResponse200Result,
        )

        d = dict(src_dict)
        expression = d.pop("expression")

        result = EvaluateExpressionResponse200Result.from_dict(d.pop("result"))

        warnings = cast(list[str], d.pop("warnings"))

        evaluate_expression_response_200 = cls(
            expression=expression,
            result=result,
            warnings=warnings,
        )

        evaluate_expression_response_200.additional_properties = d
        return evaluate_expression_response_200

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

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.fail_job_data_variables import FailJobDataVariables


T = TypeVar("T", bound="FailJobData")


@_attrs_define
class FailJobData:
    """
    Attributes:
        retries (int | Unset): The amount of retries the job should have left Default: 0.
        error_message (str | Unset): An optional error message describing why the job failed; if not provided, an empty
            string is used.
        retry_back_off (int | Unset): An optional retry back off for the failed job. The job will not be retryable
            before the current time plus the back off time. The default is 0 which means the job is retryable immediately.
            Default: 0.
        variables (FailJobDataVariables | Unset): JSON object that will instantiate the variables at the local scope of
            the job's associated task.
    """

    retries: int | Unset = 0
    error_message: str | Unset = UNSET
    retry_back_off: int | Unset = 0
    variables: FailJobDataVariables | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        retries = self.retries

        error_message = self.error_message

        retry_back_off = self.retry_back_off

        variables: dict[str, Any] | Unset = UNSET
        if not isinstance(self.variables, Unset):
            variables = self.variables.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if retries is not UNSET:
            field_dict["retries"] = retries
        if error_message is not UNSET:
            field_dict["errorMessage"] = error_message
        if retry_back_off is not UNSET:
            field_dict["retryBackOff"] = retry_back_off
        if variables is not UNSET:
            field_dict["variables"] = variables

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.fail_job_data_variables import FailJobDataVariables

        d = dict(src_dict)
        retries = d.pop("retries", UNSET)

        error_message = d.pop("errorMessage", UNSET)

        retry_back_off = d.pop("retryBackOff", UNSET)

        _variables = d.pop("variables", UNSET)
        variables: FailJobDataVariables | Unset
        if isinstance(_variables, Unset):
            variables = UNSET
        else:
            variables = FailJobDataVariables.from_dict(_variables)

        fail_job_data = cls(
            retries=retries,
            error_message=error_message,
            retry_back_off=retry_back_off,
            variables=variables,
        )

        return fail_job_data

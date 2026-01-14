from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="ActivateJobsData")


@_attrs_define
class ActivateJobsData:
    """
    Attributes:
        type_ (str): The job type, as defined in the BPMN process (e.g. <zeebe:taskDefinition type="payment-service" />)
            Example: create-new-user-record.
        timeout (int): A job returned after this call will not be activated by another call until the timeout (in ms)
            has been reached.
             Example: 20000.
        max_jobs_to_activate (int): The maximum jobs to activate by this request. Example: 5.
        worker (str | Unset): The name of the worker activating the jobs, mostly used for logging purposes. Example:
            worker-324.
        fetch_variable (list[str] | Unset): A list of variables to fetch as the job variables; if empty, all visible
            variables at the time of activation for the scope of the job will be returned. Example: ['firstName',
            'lastName', 'email'].
        request_timeout (int | Unset): The request will be completed when at least one job is activated or after the
            requestTimeout (in ms). If the requestTimeout = 0, a default timeout is used. If the requestTimeout < 0, long
            polling is disabled and the request is completed immediately, even when no job is activated.
             Example: 60000.
        tenant_ids (list[str] | Unset): A list of IDs of tenants for which to activate jobs.
    """

    type_: str
    timeout: int
    max_jobs_to_activate: int
    worker: str | Unset = UNSET
    fetch_variable: list[str] | Unset = UNSET
    request_timeout: int | Unset = UNSET
    tenant_ids: list[str] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        timeout = self.timeout

        max_jobs_to_activate = self.max_jobs_to_activate

        worker = self.worker

        fetch_variable: list[str] | Unset = UNSET
        if not isinstance(self.fetch_variable, Unset):
            fetch_variable = self.fetch_variable

        request_timeout = self.request_timeout

        tenant_ids: list[str] | Unset = UNSET
        if not isinstance(self.tenant_ids, Unset):
            tenant_ids = self.tenant_ids

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
                "timeout": timeout,
                "maxJobsToActivate": max_jobs_to_activate,
            }
        )
        if worker is not UNSET:
            field_dict["worker"] = worker
        if fetch_variable is not UNSET:
            field_dict["fetchVariable"] = fetch_variable
        if request_timeout is not UNSET:
            field_dict["requestTimeout"] = request_timeout
        if tenant_ids is not UNSET:
            field_dict["tenantIds"] = tenant_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = d.pop("type")

        timeout = d.pop("timeout")

        max_jobs_to_activate = d.pop("maxJobsToActivate")

        worker = d.pop("worker", UNSET)

        fetch_variable = cast(list[str], d.pop("fetchVariable", UNSET))

        request_timeout = d.pop("requestTimeout", UNSET)

        tenant_ids = cast(list[str], d.pop("tenantIds", UNSET))

        activate_jobs_data = cls(
            type_=type_,
            timeout=timeout,
            max_jobs_to_activate=max_jobs_to_activate,
            worker=worker,
            fetch_variable=fetch_variable,
            request_timeout=request_timeout,
            tenant_ids=tenant_ids,
        )

        return activate_jobs_data

import datetime
from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_usage_metrics_response_200 import GetUsageMetricsResponse200
from ...models.get_usage_metrics_response_400 import GetUsageMetricsResponse400
from ...models.get_usage_metrics_response_401 import GetUsageMetricsResponse401
from ...models.get_usage_metrics_response_403 import GetUsageMetricsResponse403
from ...models.get_usage_metrics_response_500 import GetUsageMetricsResponse500
from ...types import UNSET, Response, Unset

def _get_kwargs(*, start_time: datetime.datetime, end_time: datetime.datetime, tenant_id: str | Unset=UNSET, with_tenants: bool | Unset=False) -> dict[str, Any]:
    params: dict[str, Any] = {}
    json_start_time = start_time.isoformat()
    params['startTime'] = json_start_time
    json_end_time = end_time.isoformat()
    params['endTime'] = json_end_time
    params['tenantId'] = tenant_id
    params['withTenants'] = with_tenants
    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}
    _kwargs: dict[str, Any] = {'method': 'get', 'url': '/system/usage-metrics', 'params': params}
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetUsageMetricsResponse200 | GetUsageMetricsResponse400 | GetUsageMetricsResponse401 | GetUsageMetricsResponse403 | GetUsageMetricsResponse500 | None:
    if response.status_code == 200:
        response_200 = GetUsageMetricsResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = GetUsageMetricsResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = GetUsageMetricsResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = GetUsageMetricsResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 500:
        response_500 = GetUsageMetricsResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GetUsageMetricsResponse200 | GetUsageMetricsResponse400 | GetUsageMetricsResponse401 | GetUsageMetricsResponse403 | GetUsageMetricsResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(*, client: AuthenticatedClient | Client, start_time: datetime.datetime, end_time: datetime.datetime, tenant_id: str | Unset=UNSET, with_tenants: bool | Unset=False) -> Response[GetUsageMetricsResponse200 | GetUsageMetricsResponse400 | GetUsageMetricsResponse401 | GetUsageMetricsResponse403 | GetUsageMetricsResponse500]:
    """Get usage metrics

     Retrieve the usage metrics based on given criteria.

    Args:
        start_time (datetime.datetime):  Example: 2025-06-07T13:14:15Z.
        end_time (datetime.datetime):  Example: 2025-06-07T13:14:15Z.
        tenant_id (str | Unset): The unique identifier of the tenant. Example: customer-service.
        with_tenants (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetUsageMetricsResponse200 | GetUsageMetricsResponse400 | GetUsageMetricsResponse401 | GetUsageMetricsResponse403 | GetUsageMetricsResponse500]
    """
    kwargs = _get_kwargs(start_time=start_time, end_time=end_time, tenant_id=tenant_id, with_tenants=with_tenants)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(*, client: AuthenticatedClient | Client, start_time: datetime.datetime, end_time: datetime.datetime, tenant_id: str | Unset=UNSET, with_tenants: bool | Unset=False, **kwargs) -> GetUsageMetricsResponse200:
    """Get usage metrics

 Retrieve the usage metrics based on given criteria.

Args:
    start_time (datetime.datetime):  Example: 2025-06-07T13:14:15Z.
    end_time (datetime.datetime):  Example: 2025-06-07T13:14:15Z.
    tenant_id (str | Unset): The unique identifier of the tenant. Example: customer-service.
    with_tenants (bool | Unset):  Default: False.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetUsageMetricsResponse200 | GetUsageMetricsResponse400 | GetUsageMetricsResponse401 | GetUsageMetricsResponse403 | GetUsageMetricsResponse500]"""
    response = sync_detailed(client=client, start_time=start_time, end_time=end_time, tenant_id=tenant_id, with_tenants=with_tenants)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(*, client: AuthenticatedClient | Client, start_time: datetime.datetime, end_time: datetime.datetime, tenant_id: str | Unset=UNSET, with_tenants: bool | Unset=False) -> Response[GetUsageMetricsResponse200 | GetUsageMetricsResponse400 | GetUsageMetricsResponse401 | GetUsageMetricsResponse403 | GetUsageMetricsResponse500]:
    """Get usage metrics

     Retrieve the usage metrics based on given criteria.

    Args:
        start_time (datetime.datetime):  Example: 2025-06-07T13:14:15Z.
        end_time (datetime.datetime):  Example: 2025-06-07T13:14:15Z.
        tenant_id (str | Unset): The unique identifier of the tenant. Example: customer-service.
        with_tenants (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetUsageMetricsResponse200 | GetUsageMetricsResponse400 | GetUsageMetricsResponse401 | GetUsageMetricsResponse403 | GetUsageMetricsResponse500]
    """
    kwargs = _get_kwargs(start_time=start_time, end_time=end_time, tenant_id=tenant_id, with_tenants=with_tenants)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(*, client: AuthenticatedClient | Client, start_time: datetime.datetime, end_time: datetime.datetime, tenant_id: str | Unset=UNSET, with_tenants: bool | Unset=False, **kwargs) -> GetUsageMetricsResponse200:
    """Get usage metrics

 Retrieve the usage metrics based on given criteria.

Args:
    start_time (datetime.datetime):  Example: 2025-06-07T13:14:15Z.
    end_time (datetime.datetime):  Example: 2025-06-07T13:14:15Z.
    tenant_id (str | Unset): The unique identifier of the tenant. Example: customer-service.
    with_tenants (bool | Unset):  Default: False.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetUsageMetricsResponse200 | GetUsageMetricsResponse400 | GetUsageMetricsResponse401 | GetUsageMetricsResponse403 | GetUsageMetricsResponse500]"""
    response = await asyncio_detailed(client=client, start_time=start_time, end_time=end_time, tenant_id=tenant_id, with_tenants=with_tenants)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
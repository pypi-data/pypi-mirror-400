from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_tenant_cluster_variable_response_200 import GetTenantClusterVariableResponse200
from ...models.get_tenant_cluster_variable_response_400 import GetTenantClusterVariableResponse400
from ...models.get_tenant_cluster_variable_response_401 import GetTenantClusterVariableResponse401
from ...models.get_tenant_cluster_variable_response_403 import GetTenantClusterVariableResponse403
from ...models.get_tenant_cluster_variable_response_404 import GetTenantClusterVariableResponse404
from ...models.get_tenant_cluster_variable_response_500 import GetTenantClusterVariableResponse500
from ...types import Response

def _get_kwargs(tenant_id: str, name: str) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {'method': 'get', 'url': '/cluster-variables/tenants/{tenant_id}/{name}'.format(tenant_id=tenant_id, name=name)}
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetTenantClusterVariableResponse200 | GetTenantClusterVariableResponse400 | GetTenantClusterVariableResponse401 | GetTenantClusterVariableResponse403 | GetTenantClusterVariableResponse404 | GetTenantClusterVariableResponse500 | None:
    if response.status_code == 200:
        response_200 = GetTenantClusterVariableResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = GetTenantClusterVariableResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = GetTenantClusterVariableResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = GetTenantClusterVariableResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = GetTenantClusterVariableResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = GetTenantClusterVariableResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GetTenantClusterVariableResponse200 | GetTenantClusterVariableResponse400 | GetTenantClusterVariableResponse401 | GetTenantClusterVariableResponse403 | GetTenantClusterVariableResponse404 | GetTenantClusterVariableResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(tenant_id: str, name: str, *, client: AuthenticatedClient | Client) -> Response[GetTenantClusterVariableResponse200 | GetTenantClusterVariableResponse400 | GetTenantClusterVariableResponse401 | GetTenantClusterVariableResponse403 | GetTenantClusterVariableResponse404 | GetTenantClusterVariableResponse500]:
    """Get a tenant-scoped cluster variable

    Args:
        tenant_id (str): The unique identifier of the tenant. Example: customer-service.
        name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetTenantClusterVariableResponse200 | GetTenantClusterVariableResponse400 | GetTenantClusterVariableResponse401 | GetTenantClusterVariableResponse403 | GetTenantClusterVariableResponse404 | GetTenantClusterVariableResponse500]
    """
    kwargs = _get_kwargs(tenant_id=tenant_id, name=name)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(tenant_id: str, name: str, *, client: AuthenticatedClient | Client, **kwargs) -> GetTenantClusterVariableResponse200:
    """Get a tenant-scoped cluster variable

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    name (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetTenantClusterVariableResponse200 | GetTenantClusterVariableResponse400 | GetTenantClusterVariableResponse401 | GetTenantClusterVariableResponse403 | GetTenantClusterVariableResponse404 | GetTenantClusterVariableResponse500]"""
    response = sync_detailed(tenant_id=tenant_id, name=name, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(tenant_id: str, name: str, *, client: AuthenticatedClient | Client) -> Response[GetTenantClusterVariableResponse200 | GetTenantClusterVariableResponse400 | GetTenantClusterVariableResponse401 | GetTenantClusterVariableResponse403 | GetTenantClusterVariableResponse404 | GetTenantClusterVariableResponse500]:
    """Get a tenant-scoped cluster variable

    Args:
        tenant_id (str): The unique identifier of the tenant. Example: customer-service.
        name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetTenantClusterVariableResponse200 | GetTenantClusterVariableResponse400 | GetTenantClusterVariableResponse401 | GetTenantClusterVariableResponse403 | GetTenantClusterVariableResponse404 | GetTenantClusterVariableResponse500]
    """
    kwargs = _get_kwargs(tenant_id=tenant_id, name=name)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(tenant_id: str, name: str, *, client: AuthenticatedClient | Client, **kwargs) -> GetTenantClusterVariableResponse200:
    """Get a tenant-scoped cluster variable

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    name (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetTenantClusterVariableResponse200 | GetTenantClusterVariableResponse400 | GetTenantClusterVariableResponse401 | GetTenantClusterVariableResponse403 | GetTenantClusterVariableResponse404 | GetTenantClusterVariableResponse500]"""
    response = await asyncio_detailed(tenant_id=tenant_id, name=name, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
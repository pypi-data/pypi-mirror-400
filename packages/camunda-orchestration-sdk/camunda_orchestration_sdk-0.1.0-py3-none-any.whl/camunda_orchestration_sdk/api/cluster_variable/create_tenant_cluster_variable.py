from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_tenant_cluster_variable_data import CreateTenantClusterVariableData
from ...models.create_tenant_cluster_variable_response_200 import CreateTenantClusterVariableResponse200
from ...models.create_tenant_cluster_variable_response_400 import CreateTenantClusterVariableResponse400
from ...models.create_tenant_cluster_variable_response_401 import CreateTenantClusterVariableResponse401
from ...models.create_tenant_cluster_variable_response_403 import CreateTenantClusterVariableResponse403
from ...models.create_tenant_cluster_variable_response_500 import CreateTenantClusterVariableResponse500
from ...types import Response

def _get_kwargs(tenant_id: str, *, body: CreateTenantClusterVariableData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/cluster-variables/tenants/{tenant_id}'.format(tenant_id=tenant_id)}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> CreateTenantClusterVariableResponse200 | CreateTenantClusterVariableResponse400 | CreateTenantClusterVariableResponse401 | CreateTenantClusterVariableResponse403 | CreateTenantClusterVariableResponse500 | None:
    if response.status_code == 200:
        response_200 = CreateTenantClusterVariableResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = CreateTenantClusterVariableResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = CreateTenantClusterVariableResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = CreateTenantClusterVariableResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 500:
        response_500 = CreateTenantClusterVariableResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[CreateTenantClusterVariableResponse200 | CreateTenantClusterVariableResponse400 | CreateTenantClusterVariableResponse401 | CreateTenantClusterVariableResponse403 | CreateTenantClusterVariableResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(tenant_id: str, *, client: AuthenticatedClient | Client, body: CreateTenantClusterVariableData) -> Response[CreateTenantClusterVariableResponse200 | CreateTenantClusterVariableResponse400 | CreateTenantClusterVariableResponse401 | CreateTenantClusterVariableResponse403 | CreateTenantClusterVariableResponse500]:
    """Create a tenant-scoped cluster variable

    Args:
        tenant_id (str): The unique identifier of the tenant. Example: customer-service.
        body (CreateTenantClusterVariableData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateTenantClusterVariableResponse200 | CreateTenantClusterVariableResponse400 | CreateTenantClusterVariableResponse401 | CreateTenantClusterVariableResponse403 | CreateTenantClusterVariableResponse500]
    """
    kwargs = _get_kwargs(tenant_id=tenant_id, body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(tenant_id: str, *, client: AuthenticatedClient | Client, body: CreateTenantClusterVariableData, **kwargs) -> CreateTenantClusterVariableResponse200:
    """Create a tenant-scoped cluster variable

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    body (CreateTenantClusterVariableData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateTenantClusterVariableResponse200 | CreateTenantClusterVariableResponse400 | CreateTenantClusterVariableResponse401 | CreateTenantClusterVariableResponse403 | CreateTenantClusterVariableResponse500]"""
    response = sync_detailed(tenant_id=tenant_id, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(tenant_id: str, *, client: AuthenticatedClient | Client, body: CreateTenantClusterVariableData) -> Response[CreateTenantClusterVariableResponse200 | CreateTenantClusterVariableResponse400 | CreateTenantClusterVariableResponse401 | CreateTenantClusterVariableResponse403 | CreateTenantClusterVariableResponse500]:
    """Create a tenant-scoped cluster variable

    Args:
        tenant_id (str): The unique identifier of the tenant. Example: customer-service.
        body (CreateTenantClusterVariableData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateTenantClusterVariableResponse200 | CreateTenantClusterVariableResponse400 | CreateTenantClusterVariableResponse401 | CreateTenantClusterVariableResponse403 | CreateTenantClusterVariableResponse500]
    """
    kwargs = _get_kwargs(tenant_id=tenant_id, body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(tenant_id: str, *, client: AuthenticatedClient | Client, body: CreateTenantClusterVariableData, **kwargs) -> CreateTenantClusterVariableResponse200:
    """Create a tenant-scoped cluster variable

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    body (CreateTenantClusterVariableData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateTenantClusterVariableResponse200 | CreateTenantClusterVariableResponse400 | CreateTenantClusterVariableResponse401 | CreateTenantClusterVariableResponse403 | CreateTenantClusterVariableResponse500]"""
    response = await asyncio_detailed(tenant_id=tenant_id, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
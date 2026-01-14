from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.search_roles_for_tenant_data import SearchRolesForTenantData
from ...models.search_roles_for_tenant_response_200 import SearchRolesForTenantResponse200
from ...types import Response

def _get_kwargs(tenant_id: str, *, body: SearchRolesForTenantData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/tenants/{tenant_id}/roles/search'.format(tenant_id=tenant_id)}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> SearchRolesForTenantResponse200 | None:
    if response.status_code == 200:
        response_200 = SearchRolesForTenantResponse200.from_dict(response.json())
        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[SearchRolesForTenantResponse200]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(tenant_id: str, *, client: AuthenticatedClient | Client, body: SearchRolesForTenantData) -> Response[SearchRolesForTenantResponse200]:
    """Search roles for tenant

     Retrieves a filtered and sorted list of roles for a specified tenant.

    Args:
        tenant_id (str): The unique identifier of the tenant. Example: customer-service.
        body (SearchRolesForTenantData): Role search request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchRolesForTenantResponse200]
    """
    kwargs = _get_kwargs(tenant_id=tenant_id, body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(tenant_id: str, *, client: AuthenticatedClient | Client, body: SearchRolesForTenantData, **kwargs) -> SearchRolesForTenantResponse200:
    """Search roles for tenant

 Retrieves a filtered and sorted list of roles for a specified tenant.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    body (SearchRolesForTenantData): Role search request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchRolesForTenantResponse200]"""
    response = sync_detailed(tenant_id=tenant_id, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(tenant_id: str, *, client: AuthenticatedClient | Client, body: SearchRolesForTenantData) -> Response[SearchRolesForTenantResponse200]:
    """Search roles for tenant

     Retrieves a filtered and sorted list of roles for a specified tenant.

    Args:
        tenant_id (str): The unique identifier of the tenant. Example: customer-service.
        body (SearchRolesForTenantData): Role search request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchRolesForTenantResponse200]
    """
    kwargs = _get_kwargs(tenant_id=tenant_id, body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(tenant_id: str, *, client: AuthenticatedClient | Client, body: SearchRolesForTenantData, **kwargs) -> SearchRolesForTenantResponse200:
    """Search roles for tenant

 Retrieves a filtered and sorted list of roles for a specified tenant.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    body (SearchRolesForTenantData): Role search request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchRolesForTenantResponse200]"""
    response = await asyncio_detailed(tenant_id=tenant_id, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
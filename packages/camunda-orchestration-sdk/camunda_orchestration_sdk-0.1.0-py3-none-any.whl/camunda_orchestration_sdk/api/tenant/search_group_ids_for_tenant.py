from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.search_group_ids_for_tenant_data import SearchGroupIdsForTenantData
from ...models.search_group_ids_for_tenant_response_200 import SearchGroupIdsForTenantResponse200
from ...types import Response

def _get_kwargs(tenant_id: str, *, body: SearchGroupIdsForTenantData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/tenants/{tenant_id}/groups/search'.format(tenant_id=tenant_id)}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> SearchGroupIdsForTenantResponse200 | None:
    if response.status_code == 200:
        response_200 = SearchGroupIdsForTenantResponse200.from_dict(response.json())
        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[SearchGroupIdsForTenantResponse200]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(tenant_id: str, *, client: AuthenticatedClient | Client, body: SearchGroupIdsForTenantData) -> Response[SearchGroupIdsForTenantResponse200]:
    """Search groups for tenant

     Retrieves a filtered and sorted list of groups for a specified tenant.

    Args:
        tenant_id (str): The unique identifier of the tenant. Example: customer-service.
        body (SearchGroupIdsForTenantData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchGroupIdsForTenantResponse200]
    """
    kwargs = _get_kwargs(tenant_id=tenant_id, body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(tenant_id: str, *, client: AuthenticatedClient | Client, body: SearchGroupIdsForTenantData, **kwargs) -> SearchGroupIdsForTenantResponse200:
    """Search groups for tenant

 Retrieves a filtered and sorted list of groups for a specified tenant.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    body (SearchGroupIdsForTenantData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchGroupIdsForTenantResponse200]"""
    response = sync_detailed(tenant_id=tenant_id, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(tenant_id: str, *, client: AuthenticatedClient | Client, body: SearchGroupIdsForTenantData) -> Response[SearchGroupIdsForTenantResponse200]:
    """Search groups for tenant

     Retrieves a filtered and sorted list of groups for a specified tenant.

    Args:
        tenant_id (str): The unique identifier of the tenant. Example: customer-service.
        body (SearchGroupIdsForTenantData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchGroupIdsForTenantResponse200]
    """
    kwargs = _get_kwargs(tenant_id=tenant_id, body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(tenant_id: str, *, client: AuthenticatedClient | Client, body: SearchGroupIdsForTenantData, **kwargs) -> SearchGroupIdsForTenantResponse200:
    """Search groups for tenant

 Retrieves a filtered and sorted list of groups for a specified tenant.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    body (SearchGroupIdsForTenantData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchGroupIdsForTenantResponse200]"""
    response = await asyncio_detailed(tenant_id=tenant_id, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
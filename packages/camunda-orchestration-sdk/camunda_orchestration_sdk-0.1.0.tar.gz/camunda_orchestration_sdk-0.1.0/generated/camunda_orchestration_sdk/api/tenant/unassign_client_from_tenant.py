from http import HTTPStatus
from typing import Any, cast
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.unassign_client_from_tenant_response_400 import UnassignClientFromTenantResponse400
from ...models.unassign_client_from_tenant_response_403 import UnassignClientFromTenantResponse403
from ...models.unassign_client_from_tenant_response_404 import UnassignClientFromTenantResponse404
from ...models.unassign_client_from_tenant_response_500 import UnassignClientFromTenantResponse500
from ...models.unassign_client_from_tenant_response_503 import UnassignClientFromTenantResponse503
from ...types import Response

def _get_kwargs(tenant_id: str, client_id: str) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {'method': 'delete', 'url': '/tenants/{tenant_id}/clients/{client_id}'.format(tenant_id=tenant_id, client_id=client_id)}
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | UnassignClientFromTenantResponse400 | UnassignClientFromTenantResponse403 | UnassignClientFromTenantResponse404 | UnassignClientFromTenantResponse500 | UnassignClientFromTenantResponse503 | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 400:
        response_400 = UnassignClientFromTenantResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 403:
        response_403 = UnassignClientFromTenantResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = UnassignClientFromTenantResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = UnassignClientFromTenantResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = UnassignClientFromTenantResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | UnassignClientFromTenantResponse400 | UnassignClientFromTenantResponse403 | UnassignClientFromTenantResponse404 | UnassignClientFromTenantResponse500 | UnassignClientFromTenantResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(tenant_id: str, client_id: str, *, client: AuthenticatedClient | Client) -> Response[Any | UnassignClientFromTenantResponse400 | UnassignClientFromTenantResponse403 | UnassignClientFromTenantResponse404 | UnassignClientFromTenantResponse500 | UnassignClientFromTenantResponse503]:
    """Unassign a client from a tenant

     Unassigns the client from the specified tenant.
    The client can no longer access tenant data.

    Args:
        tenant_id (str): The unique identifier of the tenant. Example: customer-service.
        client_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | UnassignClientFromTenantResponse400 | UnassignClientFromTenantResponse403 | UnassignClientFromTenantResponse404 | UnassignClientFromTenantResponse500 | UnassignClientFromTenantResponse503]
    """
    kwargs = _get_kwargs(tenant_id=tenant_id, client_id=client_id)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(tenant_id: str, client_id: str, *, client: AuthenticatedClient | Client, **kwargs) -> Any:
    """Unassign a client from a tenant

 Unassigns the client from the specified tenant.
The client can no longer access tenant data.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    client_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignClientFromTenantResponse400 | UnassignClientFromTenantResponse403 | UnassignClientFromTenantResponse404 | UnassignClientFromTenantResponse500 | UnassignClientFromTenantResponse503]"""
    response = sync_detailed(tenant_id=tenant_id, client_id=client_id, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(tenant_id: str, client_id: str, *, client: AuthenticatedClient | Client) -> Response[Any | UnassignClientFromTenantResponse400 | UnassignClientFromTenantResponse403 | UnassignClientFromTenantResponse404 | UnassignClientFromTenantResponse500 | UnassignClientFromTenantResponse503]:
    """Unassign a client from a tenant

     Unassigns the client from the specified tenant.
    The client can no longer access tenant data.

    Args:
        tenant_id (str): The unique identifier of the tenant. Example: customer-service.
        client_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | UnassignClientFromTenantResponse400 | UnassignClientFromTenantResponse403 | UnassignClientFromTenantResponse404 | UnassignClientFromTenantResponse500 | UnassignClientFromTenantResponse503]
    """
    kwargs = _get_kwargs(tenant_id=tenant_id, client_id=client_id)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(tenant_id: str, client_id: str, *, client: AuthenticatedClient | Client, **kwargs) -> Any:
    """Unassign a client from a tenant

 Unassigns the client from the specified tenant.
The client can no longer access tenant data.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    client_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignClientFromTenantResponse400 | UnassignClientFromTenantResponse403 | UnassignClientFromTenantResponse404 | UnassignClientFromTenantResponse500 | UnassignClientFromTenantResponse503]"""
    response = await asyncio_detailed(tenant_id=tenant_id, client_id=client_id, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
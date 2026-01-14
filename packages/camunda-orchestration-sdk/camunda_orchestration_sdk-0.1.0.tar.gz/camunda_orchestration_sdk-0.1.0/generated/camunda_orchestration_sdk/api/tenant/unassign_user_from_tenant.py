from http import HTTPStatus
from typing import Any, cast
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.unassign_user_from_tenant_response_400 import UnassignUserFromTenantResponse400
from ...models.unassign_user_from_tenant_response_403 import UnassignUserFromTenantResponse403
from ...models.unassign_user_from_tenant_response_404 import UnassignUserFromTenantResponse404
from ...models.unassign_user_from_tenant_response_500 import UnassignUserFromTenantResponse500
from ...models.unassign_user_from_tenant_response_503 import UnassignUserFromTenantResponse503
from ...types import Response

def _get_kwargs(tenant_id: str, username: str) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {'method': 'delete', 'url': '/tenants/{tenant_id}/users/{username}'.format(tenant_id=tenant_id, username=username)}
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | UnassignUserFromTenantResponse400 | UnassignUserFromTenantResponse403 | UnassignUserFromTenantResponse404 | UnassignUserFromTenantResponse500 | UnassignUserFromTenantResponse503 | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 400:
        response_400 = UnassignUserFromTenantResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 403:
        response_403 = UnassignUserFromTenantResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = UnassignUserFromTenantResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = UnassignUserFromTenantResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = UnassignUserFromTenantResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | UnassignUserFromTenantResponse400 | UnassignUserFromTenantResponse403 | UnassignUserFromTenantResponse404 | UnassignUserFromTenantResponse500 | UnassignUserFromTenantResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(tenant_id: str, username: str, *, client: AuthenticatedClient | Client) -> Response[Any | UnassignUserFromTenantResponse400 | UnassignUserFromTenantResponse403 | UnassignUserFromTenantResponse404 | UnassignUserFromTenantResponse500 | UnassignUserFromTenantResponse503]:
    """Unassign a user from a tenant

     Unassigns the user from the specified tenant.
    The user can no longer access tenant data.

    Args:
        tenant_id (str): The unique identifier of the tenant. Example: customer-service.
        username (str): The unique name of a user. Example: swillis.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | UnassignUserFromTenantResponse400 | UnassignUserFromTenantResponse403 | UnassignUserFromTenantResponse404 | UnassignUserFromTenantResponse500 | UnassignUserFromTenantResponse503]
    """
    kwargs = _get_kwargs(tenant_id=tenant_id, username=username)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(tenant_id: str, username: str, *, client: AuthenticatedClient | Client, **kwargs) -> Any:
    """Unassign a user from a tenant

 Unassigns the user from the specified tenant.
The user can no longer access tenant data.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    username (str): The unique name of a user. Example: swillis.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignUserFromTenantResponse400 | UnassignUserFromTenantResponse403 | UnassignUserFromTenantResponse404 | UnassignUserFromTenantResponse500 | UnassignUserFromTenantResponse503]"""
    response = sync_detailed(tenant_id=tenant_id, username=username, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(tenant_id: str, username: str, *, client: AuthenticatedClient | Client) -> Response[Any | UnassignUserFromTenantResponse400 | UnassignUserFromTenantResponse403 | UnassignUserFromTenantResponse404 | UnassignUserFromTenantResponse500 | UnassignUserFromTenantResponse503]:
    """Unassign a user from a tenant

     Unassigns the user from the specified tenant.
    The user can no longer access tenant data.

    Args:
        tenant_id (str): The unique identifier of the tenant. Example: customer-service.
        username (str): The unique name of a user. Example: swillis.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | UnassignUserFromTenantResponse400 | UnassignUserFromTenantResponse403 | UnassignUserFromTenantResponse404 | UnassignUserFromTenantResponse500 | UnassignUserFromTenantResponse503]
    """
    kwargs = _get_kwargs(tenant_id=tenant_id, username=username)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(tenant_id: str, username: str, *, client: AuthenticatedClient | Client, **kwargs) -> Any:
    """Unassign a user from a tenant

 Unassigns the user from the specified tenant.
The user can no longer access tenant data.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    username (str): The unique name of a user. Example: swillis.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignUserFromTenantResponse400 | UnassignUserFromTenantResponse403 | UnassignUserFromTenantResponse404 | UnassignUserFromTenantResponse500 | UnassignUserFromTenantResponse503]"""
    response = await asyncio_detailed(tenant_id=tenant_id, username=username, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
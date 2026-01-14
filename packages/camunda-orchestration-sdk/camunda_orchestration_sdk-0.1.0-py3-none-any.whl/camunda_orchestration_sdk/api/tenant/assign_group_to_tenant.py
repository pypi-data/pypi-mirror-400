from http import HTTPStatus
from typing import Any, cast
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.assign_group_to_tenant_response_400 import AssignGroupToTenantResponse400
from ...models.assign_group_to_tenant_response_403 import AssignGroupToTenantResponse403
from ...models.assign_group_to_tenant_response_404 import AssignGroupToTenantResponse404
from ...models.assign_group_to_tenant_response_500 import AssignGroupToTenantResponse500
from ...models.assign_group_to_tenant_response_503 import AssignGroupToTenantResponse503
from ...types import Response

def _get_kwargs(tenant_id: str, group_id: str) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {'method': 'put', 'url': '/tenants/{tenant_id}/groups/{group_id}'.format(tenant_id=tenant_id, group_id=group_id)}
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | AssignGroupToTenantResponse400 | AssignGroupToTenantResponse403 | AssignGroupToTenantResponse404 | AssignGroupToTenantResponse500 | AssignGroupToTenantResponse503 | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 400:
        response_400 = AssignGroupToTenantResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 403:
        response_403 = AssignGroupToTenantResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = AssignGroupToTenantResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = AssignGroupToTenantResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = AssignGroupToTenantResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | AssignGroupToTenantResponse400 | AssignGroupToTenantResponse403 | AssignGroupToTenantResponse404 | AssignGroupToTenantResponse500 | AssignGroupToTenantResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(tenant_id: str, group_id: str, *, client: AuthenticatedClient | Client) -> Response[Any | AssignGroupToTenantResponse400 | AssignGroupToTenantResponse403 | AssignGroupToTenantResponse404 | AssignGroupToTenantResponse500 | AssignGroupToTenantResponse503]:
    """Assign a group to a tenant

     Assigns a group to a specified tenant.
    Group members (users, clients) can then access tenant data and perform authorized actions.

    Args:
        tenant_id (str): The unique identifier of the tenant. Example: customer-service.
        group_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | AssignGroupToTenantResponse400 | AssignGroupToTenantResponse403 | AssignGroupToTenantResponse404 | AssignGroupToTenantResponse500 | AssignGroupToTenantResponse503]
    """
    kwargs = _get_kwargs(tenant_id=tenant_id, group_id=group_id)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(tenant_id: str, group_id: str, *, client: AuthenticatedClient | Client, **kwargs) -> Any:
    """Assign a group to a tenant

 Assigns a group to a specified tenant.
Group members (users, clients) can then access tenant data and perform authorized actions.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    group_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignGroupToTenantResponse400 | AssignGroupToTenantResponse403 | AssignGroupToTenantResponse404 | AssignGroupToTenantResponse500 | AssignGroupToTenantResponse503]"""
    response = sync_detailed(tenant_id=tenant_id, group_id=group_id, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(tenant_id: str, group_id: str, *, client: AuthenticatedClient | Client) -> Response[Any | AssignGroupToTenantResponse400 | AssignGroupToTenantResponse403 | AssignGroupToTenantResponse404 | AssignGroupToTenantResponse500 | AssignGroupToTenantResponse503]:
    """Assign a group to a tenant

     Assigns a group to a specified tenant.
    Group members (users, clients) can then access tenant data and perform authorized actions.

    Args:
        tenant_id (str): The unique identifier of the tenant. Example: customer-service.
        group_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | AssignGroupToTenantResponse400 | AssignGroupToTenantResponse403 | AssignGroupToTenantResponse404 | AssignGroupToTenantResponse500 | AssignGroupToTenantResponse503]
    """
    kwargs = _get_kwargs(tenant_id=tenant_id, group_id=group_id)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(tenant_id: str, group_id: str, *, client: AuthenticatedClient | Client, **kwargs) -> Any:
    """Assign a group to a tenant

 Assigns a group to a specified tenant.
Group members (users, clients) can then access tenant data and perform authorized actions.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    group_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignGroupToTenantResponse400 | AssignGroupToTenantResponse403 | AssignGroupToTenantResponse404 | AssignGroupToTenantResponse500 | AssignGroupToTenantResponse503]"""
    response = await asyncio_detailed(tenant_id=tenant_id, group_id=group_id, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
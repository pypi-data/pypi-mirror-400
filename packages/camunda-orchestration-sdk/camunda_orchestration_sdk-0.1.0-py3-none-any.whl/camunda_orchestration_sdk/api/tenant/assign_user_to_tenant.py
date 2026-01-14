from http import HTTPStatus
from typing import Any, cast
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.assign_user_to_tenant_response_400 import AssignUserToTenantResponse400
from ...models.assign_user_to_tenant_response_403 import AssignUserToTenantResponse403
from ...models.assign_user_to_tenant_response_404 import AssignUserToTenantResponse404
from ...models.assign_user_to_tenant_response_500 import AssignUserToTenantResponse500
from ...models.assign_user_to_tenant_response_503 import AssignUserToTenantResponse503
from ...types import Response

def _get_kwargs(tenant_id: str, username: str) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {'method': 'put', 'url': '/tenants/{tenant_id}/users/{username}'.format(tenant_id=tenant_id, username=username)}
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | AssignUserToTenantResponse400 | AssignUserToTenantResponse403 | AssignUserToTenantResponse404 | AssignUserToTenantResponse500 | AssignUserToTenantResponse503 | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 400:
        response_400 = AssignUserToTenantResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 403:
        response_403 = AssignUserToTenantResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = AssignUserToTenantResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = AssignUserToTenantResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = AssignUserToTenantResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | AssignUserToTenantResponse400 | AssignUserToTenantResponse403 | AssignUserToTenantResponse404 | AssignUserToTenantResponse500 | AssignUserToTenantResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(tenant_id: str, username: str, *, client: AuthenticatedClient | Client) -> Response[Any | AssignUserToTenantResponse400 | AssignUserToTenantResponse403 | AssignUserToTenantResponse404 | AssignUserToTenantResponse500 | AssignUserToTenantResponse503]:
    """Assign a user to a tenant

     Assign a single user to a specified tenant. The user can then access tenant data and perform
    authorized actions.

    Args:
        tenant_id (str): The unique identifier of the tenant. Example: customer-service.
        username (str): The unique name of a user. Example: swillis.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | AssignUserToTenantResponse400 | AssignUserToTenantResponse403 | AssignUserToTenantResponse404 | AssignUserToTenantResponse500 | AssignUserToTenantResponse503]
    """
    kwargs = _get_kwargs(tenant_id=tenant_id, username=username)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(tenant_id: str, username: str, *, client: AuthenticatedClient | Client, **kwargs) -> Any:
    """Assign a user to a tenant

 Assign a single user to a specified tenant. The user can then access tenant data and perform
authorized actions.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    username (str): The unique name of a user. Example: swillis.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignUserToTenantResponse400 | AssignUserToTenantResponse403 | AssignUserToTenantResponse404 | AssignUserToTenantResponse500 | AssignUserToTenantResponse503]"""
    response = sync_detailed(tenant_id=tenant_id, username=username, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(tenant_id: str, username: str, *, client: AuthenticatedClient | Client) -> Response[Any | AssignUserToTenantResponse400 | AssignUserToTenantResponse403 | AssignUserToTenantResponse404 | AssignUserToTenantResponse500 | AssignUserToTenantResponse503]:
    """Assign a user to a tenant

     Assign a single user to a specified tenant. The user can then access tenant data and perform
    authorized actions.

    Args:
        tenant_id (str): The unique identifier of the tenant. Example: customer-service.
        username (str): The unique name of a user. Example: swillis.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | AssignUserToTenantResponse400 | AssignUserToTenantResponse403 | AssignUserToTenantResponse404 | AssignUserToTenantResponse500 | AssignUserToTenantResponse503]
    """
    kwargs = _get_kwargs(tenant_id=tenant_id, username=username)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(tenant_id: str, username: str, *, client: AuthenticatedClient | Client, **kwargs) -> Any:
    """Assign a user to a tenant

 Assign a single user to a specified tenant. The user can then access tenant data and perform
authorized actions.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    username (str): The unique name of a user. Example: swillis.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignUserToTenantResponse400 | AssignUserToTenantResponse403 | AssignUserToTenantResponse404 | AssignUserToTenantResponse500 | AssignUserToTenantResponse503]"""
    response = await asyncio_detailed(tenant_id=tenant_id, username=username, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
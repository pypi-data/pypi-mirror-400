from http import HTTPStatus
from typing import Any, cast
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.assign_client_to_tenant_response_400 import AssignClientToTenantResponse400
from ...models.assign_client_to_tenant_response_403 import AssignClientToTenantResponse403
from ...models.assign_client_to_tenant_response_404 import AssignClientToTenantResponse404
from ...models.assign_client_to_tenant_response_500 import AssignClientToTenantResponse500
from ...models.assign_client_to_tenant_response_503 import AssignClientToTenantResponse503
from ...types import Response

def _get_kwargs(tenant_id: str, client_id: str) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {'method': 'put', 'url': '/tenants/{tenant_id}/clients/{client_id}'.format(tenant_id=tenant_id, client_id=client_id)}
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | AssignClientToTenantResponse400 | AssignClientToTenantResponse403 | AssignClientToTenantResponse404 | AssignClientToTenantResponse500 | AssignClientToTenantResponse503 | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 400:
        response_400 = AssignClientToTenantResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 403:
        response_403 = AssignClientToTenantResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = AssignClientToTenantResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = AssignClientToTenantResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = AssignClientToTenantResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | AssignClientToTenantResponse400 | AssignClientToTenantResponse403 | AssignClientToTenantResponse404 | AssignClientToTenantResponse500 | AssignClientToTenantResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(tenant_id: str, client_id: str, *, client: AuthenticatedClient | Client) -> Response[Any | AssignClientToTenantResponse400 | AssignClientToTenantResponse403 | AssignClientToTenantResponse404 | AssignClientToTenantResponse500 | AssignClientToTenantResponse503]:
    """Assign a client to a tenant

     Assign the client to the specified tenant.
    The client can then access tenant data and perform authorized actions.

    Args:
        tenant_id (str): The unique identifier of the tenant. Example: customer-service.
        client_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | AssignClientToTenantResponse400 | AssignClientToTenantResponse403 | AssignClientToTenantResponse404 | AssignClientToTenantResponse500 | AssignClientToTenantResponse503]
    """
    kwargs = _get_kwargs(tenant_id=tenant_id, client_id=client_id)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(tenant_id: str, client_id: str, *, client: AuthenticatedClient | Client, **kwargs) -> Any:
    """Assign a client to a tenant

 Assign the client to the specified tenant.
The client can then access tenant data and perform authorized actions.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    client_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignClientToTenantResponse400 | AssignClientToTenantResponse403 | AssignClientToTenantResponse404 | AssignClientToTenantResponse500 | AssignClientToTenantResponse503]"""
    response = sync_detailed(tenant_id=tenant_id, client_id=client_id, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(tenant_id: str, client_id: str, *, client: AuthenticatedClient | Client) -> Response[Any | AssignClientToTenantResponse400 | AssignClientToTenantResponse403 | AssignClientToTenantResponse404 | AssignClientToTenantResponse500 | AssignClientToTenantResponse503]:
    """Assign a client to a tenant

     Assign the client to the specified tenant.
    The client can then access tenant data and perform authorized actions.

    Args:
        tenant_id (str): The unique identifier of the tenant. Example: customer-service.
        client_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | AssignClientToTenantResponse400 | AssignClientToTenantResponse403 | AssignClientToTenantResponse404 | AssignClientToTenantResponse500 | AssignClientToTenantResponse503]
    """
    kwargs = _get_kwargs(tenant_id=tenant_id, client_id=client_id)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(tenant_id: str, client_id: str, *, client: AuthenticatedClient | Client, **kwargs) -> Any:
    """Assign a client to a tenant

 Assign the client to the specified tenant.
The client can then access tenant data and perform authorized actions.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    client_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignClientToTenantResponse400 | AssignClientToTenantResponse403 | AssignClientToTenantResponse404 | AssignClientToTenantResponse500 | AssignClientToTenantResponse503]"""
    response = await asyncio_detailed(tenant_id=tenant_id, client_id=client_id, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
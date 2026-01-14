from http import HTTPStatus
from typing import Any, cast
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.delete_tenant_cluster_variable_response_400 import DeleteTenantClusterVariableResponse400
from ...models.delete_tenant_cluster_variable_response_401 import DeleteTenantClusterVariableResponse401
from ...models.delete_tenant_cluster_variable_response_403 import DeleteTenantClusterVariableResponse403
from ...models.delete_tenant_cluster_variable_response_404 import DeleteTenantClusterVariableResponse404
from ...models.delete_tenant_cluster_variable_response_500 import DeleteTenantClusterVariableResponse500
from ...types import Response

def _get_kwargs(tenant_id: str, name: str) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {'method': 'delete', 'url': '/cluster-variables/tenants/{tenant_id}/{name}'.format(tenant_id=tenant_id, name=name)}
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | DeleteTenantClusterVariableResponse400 | DeleteTenantClusterVariableResponse401 | DeleteTenantClusterVariableResponse403 | DeleteTenantClusterVariableResponse404 | DeleteTenantClusterVariableResponse500 | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 400:
        response_400 = DeleteTenantClusterVariableResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = DeleteTenantClusterVariableResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = DeleteTenantClusterVariableResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = DeleteTenantClusterVariableResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = DeleteTenantClusterVariableResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | DeleteTenantClusterVariableResponse400 | DeleteTenantClusterVariableResponse401 | DeleteTenantClusterVariableResponse403 | DeleteTenantClusterVariableResponse404 | DeleteTenantClusterVariableResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(tenant_id: str, name: str, *, client: AuthenticatedClient | Client) -> Response[Any | DeleteTenantClusterVariableResponse400 | DeleteTenantClusterVariableResponse401 | DeleteTenantClusterVariableResponse403 | DeleteTenantClusterVariableResponse404 | DeleteTenantClusterVariableResponse500]:
    """Delete a tenant-scoped cluster variable

    Args:
        tenant_id (str): The unique identifier of the tenant. Example: customer-service.
        name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | DeleteTenantClusterVariableResponse400 | DeleteTenantClusterVariableResponse401 | DeleteTenantClusterVariableResponse403 | DeleteTenantClusterVariableResponse404 | DeleteTenantClusterVariableResponse500]
    """
    kwargs = _get_kwargs(tenant_id=tenant_id, name=name)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(tenant_id: str, name: str, *, client: AuthenticatedClient | Client, **kwargs) -> Any:
    """Delete a tenant-scoped cluster variable

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    name (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteTenantClusterVariableResponse400 | DeleteTenantClusterVariableResponse401 | DeleteTenantClusterVariableResponse403 | DeleteTenantClusterVariableResponse404 | DeleteTenantClusterVariableResponse500]"""
    response = sync_detailed(tenant_id=tenant_id, name=name, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(tenant_id: str, name: str, *, client: AuthenticatedClient | Client) -> Response[Any | DeleteTenantClusterVariableResponse400 | DeleteTenantClusterVariableResponse401 | DeleteTenantClusterVariableResponse403 | DeleteTenantClusterVariableResponse404 | DeleteTenantClusterVariableResponse500]:
    """Delete a tenant-scoped cluster variable

    Args:
        tenant_id (str): The unique identifier of the tenant. Example: customer-service.
        name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | DeleteTenantClusterVariableResponse400 | DeleteTenantClusterVariableResponse401 | DeleteTenantClusterVariableResponse403 | DeleteTenantClusterVariableResponse404 | DeleteTenantClusterVariableResponse500]
    """
    kwargs = _get_kwargs(tenant_id=tenant_id, name=name)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(tenant_id: str, name: str, *, client: AuthenticatedClient | Client, **kwargs) -> Any:
    """Delete a tenant-scoped cluster variable

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    name (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteTenantClusterVariableResponse400 | DeleteTenantClusterVariableResponse401 | DeleteTenantClusterVariableResponse403 | DeleteTenantClusterVariableResponse404 | DeleteTenantClusterVariableResponse500]"""
    response = await asyncio_detailed(tenant_id=tenant_id, name=name, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
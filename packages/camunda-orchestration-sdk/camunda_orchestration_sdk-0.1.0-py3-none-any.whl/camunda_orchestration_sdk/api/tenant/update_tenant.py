from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.update_tenant_data import UpdateTenantData
from ...models.update_tenant_response_200 import UpdateTenantResponse200
from ...models.update_tenant_response_400 import UpdateTenantResponse400
from ...models.update_tenant_response_403 import UpdateTenantResponse403
from ...models.update_tenant_response_404 import UpdateTenantResponse404
from ...models.update_tenant_response_500 import UpdateTenantResponse500
from ...models.update_tenant_response_503 import UpdateTenantResponse503
from ...types import Response

def _get_kwargs(tenant_id: str, *, body: UpdateTenantData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'put', 'url': '/tenants/{tenant_id}'.format(tenant_id=tenant_id)}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> UpdateTenantResponse200 | UpdateTenantResponse400 | UpdateTenantResponse403 | UpdateTenantResponse404 | UpdateTenantResponse500 | UpdateTenantResponse503 | None:
    if response.status_code == 200:
        response_200 = UpdateTenantResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = UpdateTenantResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 403:
        response_403 = UpdateTenantResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = UpdateTenantResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = UpdateTenantResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = UpdateTenantResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[UpdateTenantResponse200 | UpdateTenantResponse400 | UpdateTenantResponse403 | UpdateTenantResponse404 | UpdateTenantResponse500 | UpdateTenantResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(tenant_id: str, *, client: AuthenticatedClient | Client, body: UpdateTenantData) -> Response[UpdateTenantResponse200 | UpdateTenantResponse400 | UpdateTenantResponse403 | UpdateTenantResponse404 | UpdateTenantResponse500 | UpdateTenantResponse503]:
    """Update tenant

     Updates an existing tenant.

    Args:
        tenant_id (str): The unique identifier of the tenant. Example: customer-service.
        body (UpdateTenantData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UpdateTenantResponse200 | UpdateTenantResponse400 | UpdateTenantResponse403 | UpdateTenantResponse404 | UpdateTenantResponse500 | UpdateTenantResponse503]
    """
    kwargs = _get_kwargs(tenant_id=tenant_id, body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(tenant_id: str, *, client: AuthenticatedClient | Client, body: UpdateTenantData, **kwargs) -> UpdateTenantResponse200:
    """Update tenant

 Updates an existing tenant.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    body (UpdateTenantData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[UpdateTenantResponse200 | UpdateTenantResponse400 | UpdateTenantResponse403 | UpdateTenantResponse404 | UpdateTenantResponse500 | UpdateTenantResponse503]"""
    response = sync_detailed(tenant_id=tenant_id, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(tenant_id: str, *, client: AuthenticatedClient | Client, body: UpdateTenantData) -> Response[UpdateTenantResponse200 | UpdateTenantResponse400 | UpdateTenantResponse403 | UpdateTenantResponse404 | UpdateTenantResponse500 | UpdateTenantResponse503]:
    """Update tenant

     Updates an existing tenant.

    Args:
        tenant_id (str): The unique identifier of the tenant. Example: customer-service.
        body (UpdateTenantData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UpdateTenantResponse200 | UpdateTenantResponse400 | UpdateTenantResponse403 | UpdateTenantResponse404 | UpdateTenantResponse500 | UpdateTenantResponse503]
    """
    kwargs = _get_kwargs(tenant_id=tenant_id, body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(tenant_id: str, *, client: AuthenticatedClient | Client, body: UpdateTenantData, **kwargs) -> UpdateTenantResponse200:
    """Update tenant

 Updates an existing tenant.

Args:
    tenant_id (str): The unique identifier of the tenant. Example: customer-service.
    body (UpdateTenantData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[UpdateTenantResponse200 | UpdateTenantResponse400 | UpdateTenantResponse403 | UpdateTenantResponse404 | UpdateTenantResponse500 | UpdateTenantResponse503]"""
    response = await asyncio_detailed(tenant_id=tenant_id, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
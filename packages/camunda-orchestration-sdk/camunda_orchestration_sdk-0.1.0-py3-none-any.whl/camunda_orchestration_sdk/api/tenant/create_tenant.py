from http import HTTPStatus
from typing import Any, cast
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_tenant_data import CreateTenantData
from ...models.create_tenant_response_201 import CreateTenantResponse201
from ...models.create_tenant_response_400 import CreateTenantResponse400
from ...models.create_tenant_response_403 import CreateTenantResponse403
from ...models.create_tenant_response_404 import CreateTenantResponse404
from ...models.create_tenant_response_500 import CreateTenantResponse500
from ...models.create_tenant_response_503 import CreateTenantResponse503
from ...types import Response

def _get_kwargs(*, body: CreateTenantData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/tenants'}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | CreateTenantResponse201 | CreateTenantResponse400 | CreateTenantResponse403 | CreateTenantResponse404 | CreateTenantResponse500 | CreateTenantResponse503 | None:
    if response.status_code == 201:
        response_201 = CreateTenantResponse201.from_dict(response.json())
        return response_201
    if response.status_code == 400:
        response_400 = CreateTenantResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 403:
        response_403 = CreateTenantResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = CreateTenantResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 409:
        response_409 = cast(Any, None)
        return response_409
    if response.status_code == 500:
        response_500 = CreateTenantResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = CreateTenantResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | CreateTenantResponse201 | CreateTenantResponse400 | CreateTenantResponse403 | CreateTenantResponse404 | CreateTenantResponse500 | CreateTenantResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(*, client: AuthenticatedClient | Client, body: CreateTenantData) -> Response[Any | CreateTenantResponse201 | CreateTenantResponse400 | CreateTenantResponse403 | CreateTenantResponse404 | CreateTenantResponse500 | CreateTenantResponse503]:
    """Create tenant

     Creates a new tenant.

    Args:
        body (CreateTenantData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | CreateTenantResponse201 | CreateTenantResponse400 | CreateTenantResponse403 | CreateTenantResponse404 | CreateTenantResponse500 | CreateTenantResponse503]
    """
    kwargs = _get_kwargs(body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(*, client: AuthenticatedClient | Client, body: CreateTenantData, **kwargs) -> Any:
    """Create tenant

 Creates a new tenant.

Args:
    body (CreateTenantData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | CreateTenantResponse201 | CreateTenantResponse400 | CreateTenantResponse403 | CreateTenantResponse404 | CreateTenantResponse500 | CreateTenantResponse503]"""
    response = sync_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(*, client: AuthenticatedClient | Client, body: CreateTenantData) -> Response[Any | CreateTenantResponse201 | CreateTenantResponse400 | CreateTenantResponse403 | CreateTenantResponse404 | CreateTenantResponse500 | CreateTenantResponse503]:
    """Create tenant

     Creates a new tenant.

    Args:
        body (CreateTenantData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | CreateTenantResponse201 | CreateTenantResponse400 | CreateTenantResponse403 | CreateTenantResponse404 | CreateTenantResponse500 | CreateTenantResponse503]
    """
    kwargs = _get_kwargs(body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(*, client: AuthenticatedClient | Client, body: CreateTenantData, **kwargs) -> Any:
    """Create tenant

 Creates a new tenant.

Args:
    body (CreateTenantData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | CreateTenantResponse201 | CreateTenantResponse400 | CreateTenantResponse403 | CreateTenantResponse404 | CreateTenantResponse500 | CreateTenantResponse503]"""
    response = await asyncio_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
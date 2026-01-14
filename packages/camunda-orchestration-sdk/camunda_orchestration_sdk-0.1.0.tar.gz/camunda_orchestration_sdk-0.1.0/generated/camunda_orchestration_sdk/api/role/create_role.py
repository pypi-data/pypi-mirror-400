from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_role_data import CreateRoleData
from ...models.create_role_response_201 import CreateRoleResponse201
from ...models.create_role_response_400 import CreateRoleResponse400
from ...models.create_role_response_401 import CreateRoleResponse401
from ...models.create_role_response_403 import CreateRoleResponse403
from ...models.create_role_response_500 import CreateRoleResponse500
from ...models.create_role_response_503 import CreateRoleResponse503
from ...types import Response

def _get_kwargs(*, body: CreateRoleData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/roles'}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> CreateRoleResponse201 | CreateRoleResponse400 | CreateRoleResponse401 | CreateRoleResponse403 | CreateRoleResponse500 | CreateRoleResponse503 | None:
    if response.status_code == 201:
        response_201 = CreateRoleResponse201.from_dict(response.json())
        return response_201
    if response.status_code == 400:
        response_400 = CreateRoleResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = CreateRoleResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = CreateRoleResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 500:
        response_500 = CreateRoleResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = CreateRoleResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[CreateRoleResponse201 | CreateRoleResponse400 | CreateRoleResponse401 | CreateRoleResponse403 | CreateRoleResponse500 | CreateRoleResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(*, client: AuthenticatedClient | Client, body: CreateRoleData) -> Response[CreateRoleResponse201 | CreateRoleResponse400 | CreateRoleResponse401 | CreateRoleResponse403 | CreateRoleResponse500 | CreateRoleResponse503]:
    """Create role

     Create a new role.

    Args:
        body (CreateRoleData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateRoleResponse201 | CreateRoleResponse400 | CreateRoleResponse401 | CreateRoleResponse403 | CreateRoleResponse500 | CreateRoleResponse503]
    """
    kwargs = _get_kwargs(body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(*, client: AuthenticatedClient | Client, body: CreateRoleData, **kwargs) -> CreateRoleResponse201:
    """Create role

 Create a new role.

Args:
    body (CreateRoleData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateRoleResponse201 | CreateRoleResponse400 | CreateRoleResponse401 | CreateRoleResponse403 | CreateRoleResponse500 | CreateRoleResponse503]"""
    response = sync_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(*, client: AuthenticatedClient | Client, body: CreateRoleData) -> Response[CreateRoleResponse201 | CreateRoleResponse400 | CreateRoleResponse401 | CreateRoleResponse403 | CreateRoleResponse500 | CreateRoleResponse503]:
    """Create role

     Create a new role.

    Args:
        body (CreateRoleData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateRoleResponse201 | CreateRoleResponse400 | CreateRoleResponse401 | CreateRoleResponse403 | CreateRoleResponse500 | CreateRoleResponse503]
    """
    kwargs = _get_kwargs(body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(*, client: AuthenticatedClient | Client, body: CreateRoleData, **kwargs) -> CreateRoleResponse201:
    """Create role

 Create a new role.

Args:
    body (CreateRoleData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateRoleResponse201 | CreateRoleResponse400 | CreateRoleResponse401 | CreateRoleResponse403 | CreateRoleResponse500 | CreateRoleResponse503]"""
    response = await asyncio_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
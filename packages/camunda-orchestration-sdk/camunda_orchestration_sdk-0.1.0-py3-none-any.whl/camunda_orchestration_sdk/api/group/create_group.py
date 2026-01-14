from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_group_data import CreateGroupData
from ...models.create_group_response_201 import CreateGroupResponse201
from ...models.create_group_response_400 import CreateGroupResponse400
from ...models.create_group_response_401 import CreateGroupResponse401
from ...models.create_group_response_403 import CreateGroupResponse403
from ...models.create_group_response_500 import CreateGroupResponse500
from ...models.create_group_response_503 import CreateGroupResponse503
from ...types import Response

def _get_kwargs(*, body: CreateGroupData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/groups'}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> CreateGroupResponse201 | CreateGroupResponse400 | CreateGroupResponse401 | CreateGroupResponse403 | CreateGroupResponse500 | CreateGroupResponse503 | None:
    if response.status_code == 201:
        response_201 = CreateGroupResponse201.from_dict(response.json())
        return response_201
    if response.status_code == 400:
        response_400 = CreateGroupResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = CreateGroupResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = CreateGroupResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 500:
        response_500 = CreateGroupResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = CreateGroupResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[CreateGroupResponse201 | CreateGroupResponse400 | CreateGroupResponse401 | CreateGroupResponse403 | CreateGroupResponse500 | CreateGroupResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(*, client: AuthenticatedClient | Client, body: CreateGroupData) -> Response[CreateGroupResponse201 | CreateGroupResponse400 | CreateGroupResponse401 | CreateGroupResponse403 | CreateGroupResponse500 | CreateGroupResponse503]:
    """Create group

     Create a new group.

    Args:
        body (CreateGroupData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateGroupResponse201 | CreateGroupResponse400 | CreateGroupResponse401 | CreateGroupResponse403 | CreateGroupResponse500 | CreateGroupResponse503]
    """
    kwargs = _get_kwargs(body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(*, client: AuthenticatedClient | Client, body: CreateGroupData, **kwargs) -> CreateGroupResponse201:
    """Create group

 Create a new group.

Args:
    body (CreateGroupData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateGroupResponse201 | CreateGroupResponse400 | CreateGroupResponse401 | CreateGroupResponse403 | CreateGroupResponse500 | CreateGroupResponse503]"""
    response = sync_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(*, client: AuthenticatedClient | Client, body: CreateGroupData) -> Response[CreateGroupResponse201 | CreateGroupResponse400 | CreateGroupResponse401 | CreateGroupResponse403 | CreateGroupResponse500 | CreateGroupResponse503]:
    """Create group

     Create a new group.

    Args:
        body (CreateGroupData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateGroupResponse201 | CreateGroupResponse400 | CreateGroupResponse401 | CreateGroupResponse403 | CreateGroupResponse500 | CreateGroupResponse503]
    """
    kwargs = _get_kwargs(body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(*, client: AuthenticatedClient | Client, body: CreateGroupData, **kwargs) -> CreateGroupResponse201:
    """Create group

 Create a new group.

Args:
    body (CreateGroupData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateGroupResponse201 | CreateGroupResponse400 | CreateGroupResponse401 | CreateGroupResponse403 | CreateGroupResponse500 | CreateGroupResponse503]"""
    response = await asyncio_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
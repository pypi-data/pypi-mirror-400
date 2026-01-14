from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_group_response_200 import GetGroupResponse200
from ...models.get_group_response_401 import GetGroupResponse401
from ...models.get_group_response_403 import GetGroupResponse403
from ...models.get_group_response_404 import GetGroupResponse404
from ...models.get_group_response_500 import GetGroupResponse500
from ...types import Response

def _get_kwargs(group_id: str) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {'method': 'get', 'url': '/groups/{group_id}'.format(group_id=group_id)}
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetGroupResponse200 | GetGroupResponse401 | GetGroupResponse403 | GetGroupResponse404 | GetGroupResponse500 | None:
    if response.status_code == 200:
        response_200 = GetGroupResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 401:
        response_401 = GetGroupResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = GetGroupResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = GetGroupResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = GetGroupResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GetGroupResponse200 | GetGroupResponse401 | GetGroupResponse403 | GetGroupResponse404 | GetGroupResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(group_id: str, *, client: AuthenticatedClient | Client) -> Response[GetGroupResponse200 | GetGroupResponse401 | GetGroupResponse403 | GetGroupResponse404 | GetGroupResponse500]:
    """Get group

     Get a group by its ID.

    Args:
        group_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetGroupResponse200 | GetGroupResponse401 | GetGroupResponse403 | GetGroupResponse404 | GetGroupResponse500]
    """
    kwargs = _get_kwargs(group_id=group_id)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(group_id: str, *, client: AuthenticatedClient | Client, **kwargs) -> GetGroupResponse200:
    """Get group

 Get a group by its ID.

Args:
    group_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetGroupResponse200 | GetGroupResponse401 | GetGroupResponse403 | GetGroupResponse404 | GetGroupResponse500]"""
    response = sync_detailed(group_id=group_id, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(group_id: str, *, client: AuthenticatedClient | Client) -> Response[GetGroupResponse200 | GetGroupResponse401 | GetGroupResponse403 | GetGroupResponse404 | GetGroupResponse500]:
    """Get group

     Get a group by its ID.

    Args:
        group_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetGroupResponse200 | GetGroupResponse401 | GetGroupResponse403 | GetGroupResponse404 | GetGroupResponse500]
    """
    kwargs = _get_kwargs(group_id=group_id)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(group_id: str, *, client: AuthenticatedClient | Client, **kwargs) -> GetGroupResponse200:
    """Get group

 Get a group by its ID.

Args:
    group_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetGroupResponse200 | GetGroupResponse401 | GetGroupResponse403 | GetGroupResponse404 | GetGroupResponse500]"""
    response = await asyncio_detailed(group_id=group_id, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
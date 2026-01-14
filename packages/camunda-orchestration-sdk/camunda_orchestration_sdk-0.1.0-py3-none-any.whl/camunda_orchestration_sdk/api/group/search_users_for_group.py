from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.search_users_for_group_data import SearchUsersForGroupData
from ...models.search_users_for_group_response_200 import SearchUsersForGroupResponse200
from ...models.search_users_for_group_response_400 import SearchUsersForGroupResponse400
from ...models.search_users_for_group_response_401 import SearchUsersForGroupResponse401
from ...models.search_users_for_group_response_403 import SearchUsersForGroupResponse403
from ...models.search_users_for_group_response_404 import SearchUsersForGroupResponse404
from ...models.search_users_for_group_response_500 import SearchUsersForGroupResponse500
from ...types import Response

def _get_kwargs(group_id: str, *, body: SearchUsersForGroupData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/groups/{group_id}/users/search'.format(group_id=group_id)}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> SearchUsersForGroupResponse200 | SearchUsersForGroupResponse400 | SearchUsersForGroupResponse401 | SearchUsersForGroupResponse403 | SearchUsersForGroupResponse404 | SearchUsersForGroupResponse500 | None:
    if response.status_code == 200:
        response_200 = SearchUsersForGroupResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = SearchUsersForGroupResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = SearchUsersForGroupResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = SearchUsersForGroupResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = SearchUsersForGroupResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = SearchUsersForGroupResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[SearchUsersForGroupResponse200 | SearchUsersForGroupResponse400 | SearchUsersForGroupResponse401 | SearchUsersForGroupResponse403 | SearchUsersForGroupResponse404 | SearchUsersForGroupResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(group_id: str, *, client: AuthenticatedClient | Client, body: SearchUsersForGroupData) -> Response[SearchUsersForGroupResponse200 | SearchUsersForGroupResponse400 | SearchUsersForGroupResponse401 | SearchUsersForGroupResponse403 | SearchUsersForGroupResponse404 | SearchUsersForGroupResponse500]:
    """Search group users

     Search users assigned to a group.

    Args:
        group_id (str):
        body (SearchUsersForGroupData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchUsersForGroupResponse200 | SearchUsersForGroupResponse400 | SearchUsersForGroupResponse401 | SearchUsersForGroupResponse403 | SearchUsersForGroupResponse404 | SearchUsersForGroupResponse500]
    """
    kwargs = _get_kwargs(group_id=group_id, body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(group_id: str, *, client: AuthenticatedClient | Client, body: SearchUsersForGroupData, **kwargs) -> SearchUsersForGroupResponse200:
    """Search group users

 Search users assigned to a group.

Args:
    group_id (str):
    body (SearchUsersForGroupData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchUsersForGroupResponse200 | SearchUsersForGroupResponse400 | SearchUsersForGroupResponse401 | SearchUsersForGroupResponse403 | SearchUsersForGroupResponse404 | SearchUsersForGroupResponse500]"""
    response = sync_detailed(group_id=group_id, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(group_id: str, *, client: AuthenticatedClient | Client, body: SearchUsersForGroupData) -> Response[SearchUsersForGroupResponse200 | SearchUsersForGroupResponse400 | SearchUsersForGroupResponse401 | SearchUsersForGroupResponse403 | SearchUsersForGroupResponse404 | SearchUsersForGroupResponse500]:
    """Search group users

     Search users assigned to a group.

    Args:
        group_id (str):
        body (SearchUsersForGroupData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchUsersForGroupResponse200 | SearchUsersForGroupResponse400 | SearchUsersForGroupResponse401 | SearchUsersForGroupResponse403 | SearchUsersForGroupResponse404 | SearchUsersForGroupResponse500]
    """
    kwargs = _get_kwargs(group_id=group_id, body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(group_id: str, *, client: AuthenticatedClient | Client, body: SearchUsersForGroupData, **kwargs) -> SearchUsersForGroupResponse200:
    """Search group users

 Search users assigned to a group.

Args:
    group_id (str):
    body (SearchUsersForGroupData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchUsersForGroupResponse200 | SearchUsersForGroupResponse400 | SearchUsersForGroupResponse401 | SearchUsersForGroupResponse403 | SearchUsersForGroupResponse404 | SearchUsersForGroupResponse500]"""
    response = await asyncio_detailed(group_id=group_id, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
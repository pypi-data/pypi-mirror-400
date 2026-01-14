from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.search_users_for_role_data import SearchUsersForRoleData
from ...models.search_users_for_role_response_200 import SearchUsersForRoleResponse200
from ...models.search_users_for_role_response_400 import SearchUsersForRoleResponse400
from ...models.search_users_for_role_response_401 import SearchUsersForRoleResponse401
from ...models.search_users_for_role_response_403 import SearchUsersForRoleResponse403
from ...models.search_users_for_role_response_404 import SearchUsersForRoleResponse404
from ...models.search_users_for_role_response_500 import SearchUsersForRoleResponse500
from ...types import Response

def _get_kwargs(role_id: str, *, body: SearchUsersForRoleData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/roles/{role_id}/users/search'.format(role_id=role_id)}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> SearchUsersForRoleResponse200 | SearchUsersForRoleResponse400 | SearchUsersForRoleResponse401 | SearchUsersForRoleResponse403 | SearchUsersForRoleResponse404 | SearchUsersForRoleResponse500 | None:
    if response.status_code == 200:
        response_200 = SearchUsersForRoleResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = SearchUsersForRoleResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = SearchUsersForRoleResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = SearchUsersForRoleResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = SearchUsersForRoleResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = SearchUsersForRoleResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[SearchUsersForRoleResponse200 | SearchUsersForRoleResponse400 | SearchUsersForRoleResponse401 | SearchUsersForRoleResponse403 | SearchUsersForRoleResponse404 | SearchUsersForRoleResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(role_id: str, *, client: AuthenticatedClient | Client, body: SearchUsersForRoleData) -> Response[SearchUsersForRoleResponse200 | SearchUsersForRoleResponse400 | SearchUsersForRoleResponse401 | SearchUsersForRoleResponse403 | SearchUsersForRoleResponse404 | SearchUsersForRoleResponse500]:
    """Search role users

     Search users with assigned role.

    Args:
        role_id (str):
        body (SearchUsersForRoleData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchUsersForRoleResponse200 | SearchUsersForRoleResponse400 | SearchUsersForRoleResponse401 | SearchUsersForRoleResponse403 | SearchUsersForRoleResponse404 | SearchUsersForRoleResponse500]
    """
    kwargs = _get_kwargs(role_id=role_id, body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(role_id: str, *, client: AuthenticatedClient | Client, body: SearchUsersForRoleData, **kwargs) -> SearchUsersForRoleResponse200:
    """Search role users

 Search users with assigned role.

Args:
    role_id (str):
    body (SearchUsersForRoleData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchUsersForRoleResponse200 | SearchUsersForRoleResponse400 | SearchUsersForRoleResponse401 | SearchUsersForRoleResponse403 | SearchUsersForRoleResponse404 | SearchUsersForRoleResponse500]"""
    response = sync_detailed(role_id=role_id, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(role_id: str, *, client: AuthenticatedClient | Client, body: SearchUsersForRoleData) -> Response[SearchUsersForRoleResponse200 | SearchUsersForRoleResponse400 | SearchUsersForRoleResponse401 | SearchUsersForRoleResponse403 | SearchUsersForRoleResponse404 | SearchUsersForRoleResponse500]:
    """Search role users

     Search users with assigned role.

    Args:
        role_id (str):
        body (SearchUsersForRoleData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchUsersForRoleResponse200 | SearchUsersForRoleResponse400 | SearchUsersForRoleResponse401 | SearchUsersForRoleResponse403 | SearchUsersForRoleResponse404 | SearchUsersForRoleResponse500]
    """
    kwargs = _get_kwargs(role_id=role_id, body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(role_id: str, *, client: AuthenticatedClient | Client, body: SearchUsersForRoleData, **kwargs) -> SearchUsersForRoleResponse200:
    """Search role users

 Search users with assigned role.

Args:
    role_id (str):
    body (SearchUsersForRoleData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchUsersForRoleResponse200 | SearchUsersForRoleResponse400 | SearchUsersForRoleResponse401 | SearchUsersForRoleResponse403 | SearchUsersForRoleResponse404 | SearchUsersForRoleResponse500]"""
    response = await asyncio_detailed(role_id=role_id, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
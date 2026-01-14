from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.search_groups_for_role_data import SearchGroupsForRoleData
from ...models.search_groups_for_role_response_200 import SearchGroupsForRoleResponse200
from ...models.search_groups_for_role_response_400 import SearchGroupsForRoleResponse400
from ...models.search_groups_for_role_response_401 import SearchGroupsForRoleResponse401
from ...models.search_groups_for_role_response_403 import SearchGroupsForRoleResponse403
from ...models.search_groups_for_role_response_404 import SearchGroupsForRoleResponse404
from ...models.search_groups_for_role_response_500 import SearchGroupsForRoleResponse500
from ...types import Response

def _get_kwargs(role_id: str, *, body: SearchGroupsForRoleData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/roles/{role_id}/groups/search'.format(role_id=role_id)}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> SearchGroupsForRoleResponse200 | SearchGroupsForRoleResponse400 | SearchGroupsForRoleResponse401 | SearchGroupsForRoleResponse403 | SearchGroupsForRoleResponse404 | SearchGroupsForRoleResponse500 | None:
    if response.status_code == 200:
        response_200 = SearchGroupsForRoleResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = SearchGroupsForRoleResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = SearchGroupsForRoleResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = SearchGroupsForRoleResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = SearchGroupsForRoleResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = SearchGroupsForRoleResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[SearchGroupsForRoleResponse200 | SearchGroupsForRoleResponse400 | SearchGroupsForRoleResponse401 | SearchGroupsForRoleResponse403 | SearchGroupsForRoleResponse404 | SearchGroupsForRoleResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(role_id: str, *, client: AuthenticatedClient | Client, body: SearchGroupsForRoleData) -> Response[SearchGroupsForRoleResponse200 | SearchGroupsForRoleResponse400 | SearchGroupsForRoleResponse401 | SearchGroupsForRoleResponse403 | SearchGroupsForRoleResponse404 | SearchGroupsForRoleResponse500]:
    """Search role groups

     Search groups with assigned role.

    Args:
        role_id (str):
        body (SearchGroupsForRoleData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchGroupsForRoleResponse200 | SearchGroupsForRoleResponse400 | SearchGroupsForRoleResponse401 | SearchGroupsForRoleResponse403 | SearchGroupsForRoleResponse404 | SearchGroupsForRoleResponse500]
    """
    kwargs = _get_kwargs(role_id=role_id, body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(role_id: str, *, client: AuthenticatedClient | Client, body: SearchGroupsForRoleData, **kwargs) -> SearchGroupsForRoleResponse200:
    """Search role groups

 Search groups with assigned role.

Args:
    role_id (str):
    body (SearchGroupsForRoleData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchGroupsForRoleResponse200 | SearchGroupsForRoleResponse400 | SearchGroupsForRoleResponse401 | SearchGroupsForRoleResponse403 | SearchGroupsForRoleResponse404 | SearchGroupsForRoleResponse500]"""
    response = sync_detailed(role_id=role_id, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(role_id: str, *, client: AuthenticatedClient | Client, body: SearchGroupsForRoleData) -> Response[SearchGroupsForRoleResponse200 | SearchGroupsForRoleResponse400 | SearchGroupsForRoleResponse401 | SearchGroupsForRoleResponse403 | SearchGroupsForRoleResponse404 | SearchGroupsForRoleResponse500]:
    """Search role groups

     Search groups with assigned role.

    Args:
        role_id (str):
        body (SearchGroupsForRoleData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchGroupsForRoleResponse200 | SearchGroupsForRoleResponse400 | SearchGroupsForRoleResponse401 | SearchGroupsForRoleResponse403 | SearchGroupsForRoleResponse404 | SearchGroupsForRoleResponse500]
    """
    kwargs = _get_kwargs(role_id=role_id, body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(role_id: str, *, client: AuthenticatedClient | Client, body: SearchGroupsForRoleData, **kwargs) -> SearchGroupsForRoleResponse200:
    """Search role groups

 Search groups with assigned role.

Args:
    role_id (str):
    body (SearchGroupsForRoleData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchGroupsForRoleResponse200 | SearchGroupsForRoleResponse400 | SearchGroupsForRoleResponse401 | SearchGroupsForRoleResponse403 | SearchGroupsForRoleResponse404 | SearchGroupsForRoleResponse500]"""
    response = await asyncio_detailed(role_id=role_id, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
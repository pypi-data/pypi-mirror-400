from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.search_roles_for_group_data import SearchRolesForGroupData
from ...models.search_roles_for_group_response_200 import SearchRolesForGroupResponse200
from ...models.search_roles_for_group_response_400 import SearchRolesForGroupResponse400
from ...models.search_roles_for_group_response_401 import SearchRolesForGroupResponse401
from ...models.search_roles_for_group_response_403 import SearchRolesForGroupResponse403
from ...models.search_roles_for_group_response_404 import SearchRolesForGroupResponse404
from ...models.search_roles_for_group_response_500 import SearchRolesForGroupResponse500
from ...types import Response

def _get_kwargs(group_id: str, *, body: SearchRolesForGroupData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/groups/{group_id}/roles/search'.format(group_id=group_id)}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> SearchRolesForGroupResponse200 | SearchRolesForGroupResponse400 | SearchRolesForGroupResponse401 | SearchRolesForGroupResponse403 | SearchRolesForGroupResponse404 | SearchRolesForGroupResponse500 | None:
    if response.status_code == 200:
        response_200 = SearchRolesForGroupResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = SearchRolesForGroupResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = SearchRolesForGroupResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = SearchRolesForGroupResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = SearchRolesForGroupResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = SearchRolesForGroupResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[SearchRolesForGroupResponse200 | SearchRolesForGroupResponse400 | SearchRolesForGroupResponse401 | SearchRolesForGroupResponse403 | SearchRolesForGroupResponse404 | SearchRolesForGroupResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(group_id: str, *, client: AuthenticatedClient | Client, body: SearchRolesForGroupData) -> Response[SearchRolesForGroupResponse200 | SearchRolesForGroupResponse400 | SearchRolesForGroupResponse401 | SearchRolesForGroupResponse403 | SearchRolesForGroupResponse404 | SearchRolesForGroupResponse500]:
    """Search group roles

     Search roles assigned to a group.

    Args:
        group_id (str):
        body (SearchRolesForGroupData): Role search request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchRolesForGroupResponse200 | SearchRolesForGroupResponse400 | SearchRolesForGroupResponse401 | SearchRolesForGroupResponse403 | SearchRolesForGroupResponse404 | SearchRolesForGroupResponse500]
    """
    kwargs = _get_kwargs(group_id=group_id, body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(group_id: str, *, client: AuthenticatedClient | Client, body: SearchRolesForGroupData, **kwargs) -> SearchRolesForGroupResponse200:
    """Search group roles

 Search roles assigned to a group.

Args:
    group_id (str):
    body (SearchRolesForGroupData): Role search request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchRolesForGroupResponse200 | SearchRolesForGroupResponse400 | SearchRolesForGroupResponse401 | SearchRolesForGroupResponse403 | SearchRolesForGroupResponse404 | SearchRolesForGroupResponse500]"""
    response = sync_detailed(group_id=group_id, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(group_id: str, *, client: AuthenticatedClient | Client, body: SearchRolesForGroupData) -> Response[SearchRolesForGroupResponse200 | SearchRolesForGroupResponse400 | SearchRolesForGroupResponse401 | SearchRolesForGroupResponse403 | SearchRolesForGroupResponse404 | SearchRolesForGroupResponse500]:
    """Search group roles

     Search roles assigned to a group.

    Args:
        group_id (str):
        body (SearchRolesForGroupData): Role search request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchRolesForGroupResponse200 | SearchRolesForGroupResponse400 | SearchRolesForGroupResponse401 | SearchRolesForGroupResponse403 | SearchRolesForGroupResponse404 | SearchRolesForGroupResponse500]
    """
    kwargs = _get_kwargs(group_id=group_id, body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(group_id: str, *, client: AuthenticatedClient | Client, body: SearchRolesForGroupData, **kwargs) -> SearchRolesForGroupResponse200:
    """Search group roles

 Search roles assigned to a group.

Args:
    group_id (str):
    body (SearchRolesForGroupData): Role search request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchRolesForGroupResponse200 | SearchRolesForGroupResponse400 | SearchRolesForGroupResponse401 | SearchRolesForGroupResponse403 | SearchRolesForGroupResponse404 | SearchRolesForGroupResponse500]"""
    response = await asyncio_detailed(group_id=group_id, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
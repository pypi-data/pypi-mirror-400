from http import HTTPStatus
from typing import Any, cast
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.unassign_role_from_group_response_400 import UnassignRoleFromGroupResponse400
from ...models.unassign_role_from_group_response_403 import UnassignRoleFromGroupResponse403
from ...models.unassign_role_from_group_response_404 import UnassignRoleFromGroupResponse404
from ...models.unassign_role_from_group_response_500 import UnassignRoleFromGroupResponse500
from ...models.unassign_role_from_group_response_503 import UnassignRoleFromGroupResponse503
from ...types import Response

def _get_kwargs(role_id: str, group_id: str) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {'method': 'delete', 'url': '/roles/{role_id}/groups/{group_id}'.format(role_id=role_id, group_id=group_id)}
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | UnassignRoleFromGroupResponse400 | UnassignRoleFromGroupResponse403 | UnassignRoleFromGroupResponse404 | UnassignRoleFromGroupResponse500 | UnassignRoleFromGroupResponse503 | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 400:
        response_400 = UnassignRoleFromGroupResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 403:
        response_403 = UnassignRoleFromGroupResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = UnassignRoleFromGroupResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = UnassignRoleFromGroupResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = UnassignRoleFromGroupResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | UnassignRoleFromGroupResponse400 | UnassignRoleFromGroupResponse403 | UnassignRoleFromGroupResponse404 | UnassignRoleFromGroupResponse500 | UnassignRoleFromGroupResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(role_id: str, group_id: str, *, client: AuthenticatedClient | Client) -> Response[Any | UnassignRoleFromGroupResponse400 | UnassignRoleFromGroupResponse403 | UnassignRoleFromGroupResponse404 | UnassignRoleFromGroupResponse500 | UnassignRoleFromGroupResponse503]:
    """Unassign a role from a group

     Unassigns the specified role from the group. All group members (user or client) no longer inherit
    the authorizations associated with this role.

    Args:
        role_id (str):
        group_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | UnassignRoleFromGroupResponse400 | UnassignRoleFromGroupResponse403 | UnassignRoleFromGroupResponse404 | UnassignRoleFromGroupResponse500 | UnassignRoleFromGroupResponse503]
    """
    kwargs = _get_kwargs(role_id=role_id, group_id=group_id)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(role_id: str, group_id: str, *, client: AuthenticatedClient | Client, **kwargs) -> Any:
    """Unassign a role from a group

 Unassigns the specified role from the group. All group members (user or client) no longer inherit
the authorizations associated with this role.

Args:
    role_id (str):
    group_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignRoleFromGroupResponse400 | UnassignRoleFromGroupResponse403 | UnassignRoleFromGroupResponse404 | UnassignRoleFromGroupResponse500 | UnassignRoleFromGroupResponse503]"""
    response = sync_detailed(role_id=role_id, group_id=group_id, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(role_id: str, group_id: str, *, client: AuthenticatedClient | Client) -> Response[Any | UnassignRoleFromGroupResponse400 | UnassignRoleFromGroupResponse403 | UnassignRoleFromGroupResponse404 | UnassignRoleFromGroupResponse500 | UnassignRoleFromGroupResponse503]:
    """Unassign a role from a group

     Unassigns the specified role from the group. All group members (user or client) no longer inherit
    the authorizations associated with this role.

    Args:
        role_id (str):
        group_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | UnassignRoleFromGroupResponse400 | UnassignRoleFromGroupResponse403 | UnassignRoleFromGroupResponse404 | UnassignRoleFromGroupResponse500 | UnassignRoleFromGroupResponse503]
    """
    kwargs = _get_kwargs(role_id=role_id, group_id=group_id)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(role_id: str, group_id: str, *, client: AuthenticatedClient | Client, **kwargs) -> Any:
    """Unassign a role from a group

 Unassigns the specified role from the group. All group members (user or client) no longer inherit
the authorizations associated with this role.

Args:
    role_id (str):
    group_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignRoleFromGroupResponse400 | UnassignRoleFromGroupResponse403 | UnassignRoleFromGroupResponse404 | UnassignRoleFromGroupResponse500 | UnassignRoleFromGroupResponse503]"""
    response = await asyncio_detailed(role_id=role_id, group_id=group_id, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
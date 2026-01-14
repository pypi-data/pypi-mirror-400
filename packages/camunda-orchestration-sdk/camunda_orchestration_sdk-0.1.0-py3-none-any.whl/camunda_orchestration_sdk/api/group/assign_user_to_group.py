from http import HTTPStatus
from typing import Any, cast
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.assign_user_to_group_response_400 import AssignUserToGroupResponse400
from ...models.assign_user_to_group_response_403 import AssignUserToGroupResponse403
from ...models.assign_user_to_group_response_404 import AssignUserToGroupResponse404
from ...models.assign_user_to_group_response_409 import AssignUserToGroupResponse409
from ...models.assign_user_to_group_response_500 import AssignUserToGroupResponse500
from ...models.assign_user_to_group_response_503 import AssignUserToGroupResponse503
from ...types import Response

def _get_kwargs(group_id: str, username: str) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {'method': 'put', 'url': '/groups/{group_id}/users/{username}'.format(group_id=group_id, username=username)}
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | AssignUserToGroupResponse400 | AssignUserToGroupResponse403 | AssignUserToGroupResponse404 | AssignUserToGroupResponse409 | AssignUserToGroupResponse500 | AssignUserToGroupResponse503 | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 400:
        response_400 = AssignUserToGroupResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 403:
        response_403 = AssignUserToGroupResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = AssignUserToGroupResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 409:
        response_409 = AssignUserToGroupResponse409.from_dict(response.json())
        return response_409
    if response.status_code == 500:
        response_500 = AssignUserToGroupResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = AssignUserToGroupResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | AssignUserToGroupResponse400 | AssignUserToGroupResponse403 | AssignUserToGroupResponse404 | AssignUserToGroupResponse409 | AssignUserToGroupResponse500 | AssignUserToGroupResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(group_id: str, username: str, *, client: AuthenticatedClient | Client) -> Response[Any | AssignUserToGroupResponse400 | AssignUserToGroupResponse403 | AssignUserToGroupResponse404 | AssignUserToGroupResponse409 | AssignUserToGroupResponse500 | AssignUserToGroupResponse503]:
    """Assign a user to a group

     Assigns a user to a group, making the user a member of the group.
    Group members inherit the group authorizations, roles, and tenant assignments.

    Args:
        group_id (str):
        username (str): The unique name of a user. Example: swillis.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | AssignUserToGroupResponse400 | AssignUserToGroupResponse403 | AssignUserToGroupResponse404 | AssignUserToGroupResponse409 | AssignUserToGroupResponse500 | AssignUserToGroupResponse503]
    """
    kwargs = _get_kwargs(group_id=group_id, username=username)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(group_id: str, username: str, *, client: AuthenticatedClient | Client, **kwargs) -> Any:
    """Assign a user to a group

 Assigns a user to a group, making the user a member of the group.
Group members inherit the group authorizations, roles, and tenant assignments.

Args:
    group_id (str):
    username (str): The unique name of a user. Example: swillis.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignUserToGroupResponse400 | AssignUserToGroupResponse403 | AssignUserToGroupResponse404 | AssignUserToGroupResponse409 | AssignUserToGroupResponse500 | AssignUserToGroupResponse503]"""
    response = sync_detailed(group_id=group_id, username=username, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(group_id: str, username: str, *, client: AuthenticatedClient | Client) -> Response[Any | AssignUserToGroupResponse400 | AssignUserToGroupResponse403 | AssignUserToGroupResponse404 | AssignUserToGroupResponse409 | AssignUserToGroupResponse500 | AssignUserToGroupResponse503]:
    """Assign a user to a group

     Assigns a user to a group, making the user a member of the group.
    Group members inherit the group authorizations, roles, and tenant assignments.

    Args:
        group_id (str):
        username (str): The unique name of a user. Example: swillis.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | AssignUserToGroupResponse400 | AssignUserToGroupResponse403 | AssignUserToGroupResponse404 | AssignUserToGroupResponse409 | AssignUserToGroupResponse500 | AssignUserToGroupResponse503]
    """
    kwargs = _get_kwargs(group_id=group_id, username=username)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(group_id: str, username: str, *, client: AuthenticatedClient | Client, **kwargs) -> Any:
    """Assign a user to a group

 Assigns a user to a group, making the user a member of the group.
Group members inherit the group authorizations, roles, and tenant assignments.

Args:
    group_id (str):
    username (str): The unique name of a user. Example: swillis.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignUserToGroupResponse400 | AssignUserToGroupResponse403 | AssignUserToGroupResponse404 | AssignUserToGroupResponse409 | AssignUserToGroupResponse500 | AssignUserToGroupResponse503]"""
    response = await asyncio_detailed(group_id=group_id, username=username, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
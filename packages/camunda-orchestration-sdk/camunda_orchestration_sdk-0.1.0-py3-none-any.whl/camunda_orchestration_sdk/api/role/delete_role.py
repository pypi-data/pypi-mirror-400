from http import HTTPStatus
from typing import Any, cast
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.delete_role_response_401 import DeleteRoleResponse401
from ...models.delete_role_response_404 import DeleteRoleResponse404
from ...models.delete_role_response_500 import DeleteRoleResponse500
from ...models.delete_role_response_503 import DeleteRoleResponse503
from ...types import Response

def _get_kwargs(role_id: str) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {'method': 'delete', 'url': '/roles/{role_id}'.format(role_id=role_id)}
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | DeleteRoleResponse401 | DeleteRoleResponse404 | DeleteRoleResponse500 | DeleteRoleResponse503 | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 401:
        response_401 = DeleteRoleResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 404:
        response_404 = DeleteRoleResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = DeleteRoleResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = DeleteRoleResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | DeleteRoleResponse401 | DeleteRoleResponse404 | DeleteRoleResponse500 | DeleteRoleResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(role_id: str, *, client: AuthenticatedClient | Client) -> Response[Any | DeleteRoleResponse401 | DeleteRoleResponse404 | DeleteRoleResponse500 | DeleteRoleResponse503]:
    """Delete role

     Deletes the role with the given ID.

    Args:
        role_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | DeleteRoleResponse401 | DeleteRoleResponse404 | DeleteRoleResponse500 | DeleteRoleResponse503]
    """
    kwargs = _get_kwargs(role_id=role_id)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(role_id: str, *, client: AuthenticatedClient | Client, **kwargs) -> Any:
    """Delete role

 Deletes the role with the given ID.

Args:
    role_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteRoleResponse401 | DeleteRoleResponse404 | DeleteRoleResponse500 | DeleteRoleResponse503]"""
    response = sync_detailed(role_id=role_id, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(role_id: str, *, client: AuthenticatedClient | Client) -> Response[Any | DeleteRoleResponse401 | DeleteRoleResponse404 | DeleteRoleResponse500 | DeleteRoleResponse503]:
    """Delete role

     Deletes the role with the given ID.

    Args:
        role_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | DeleteRoleResponse401 | DeleteRoleResponse404 | DeleteRoleResponse500 | DeleteRoleResponse503]
    """
    kwargs = _get_kwargs(role_id=role_id)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(role_id: str, *, client: AuthenticatedClient | Client, **kwargs) -> Any:
    """Delete role

 Deletes the role with the given ID.

Args:
    role_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteRoleResponse401 | DeleteRoleResponse404 | DeleteRoleResponse500 | DeleteRoleResponse503]"""
    response = await asyncio_detailed(role_id=role_id, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
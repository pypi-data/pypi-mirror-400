from http import HTTPStatus
from typing import Any, cast
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.unassign_role_from_client_response_400 import UnassignRoleFromClientResponse400
from ...models.unassign_role_from_client_response_403 import UnassignRoleFromClientResponse403
from ...models.unassign_role_from_client_response_404 import UnassignRoleFromClientResponse404
from ...models.unassign_role_from_client_response_500 import UnassignRoleFromClientResponse500
from ...models.unassign_role_from_client_response_503 import UnassignRoleFromClientResponse503
from ...types import Response

def _get_kwargs(role_id: str, client_id: str) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {'method': 'delete', 'url': '/roles/{role_id}/clients/{client_id}'.format(role_id=role_id, client_id=client_id)}
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | UnassignRoleFromClientResponse400 | UnassignRoleFromClientResponse403 | UnassignRoleFromClientResponse404 | UnassignRoleFromClientResponse500 | UnassignRoleFromClientResponse503 | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 400:
        response_400 = UnassignRoleFromClientResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 403:
        response_403 = UnassignRoleFromClientResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = UnassignRoleFromClientResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = UnassignRoleFromClientResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = UnassignRoleFromClientResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | UnassignRoleFromClientResponse400 | UnassignRoleFromClientResponse403 | UnassignRoleFromClientResponse404 | UnassignRoleFromClientResponse500 | UnassignRoleFromClientResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(role_id: str, client_id: str, *, client: AuthenticatedClient | Client) -> Response[Any | UnassignRoleFromClientResponse400 | UnassignRoleFromClientResponse403 | UnassignRoleFromClientResponse404 | UnassignRoleFromClientResponse500 | UnassignRoleFromClientResponse503]:
    """Unassign a role from a client

     Unassigns the specified role from the client. The client will no longer inherit the authorizations
    associated with this role.

    Args:
        role_id (str):
        client_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | UnassignRoleFromClientResponse400 | UnassignRoleFromClientResponse403 | UnassignRoleFromClientResponse404 | UnassignRoleFromClientResponse500 | UnassignRoleFromClientResponse503]
    """
    kwargs = _get_kwargs(role_id=role_id, client_id=client_id)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(role_id: str, client_id: str, *, client: AuthenticatedClient | Client, **kwargs) -> Any:
    """Unassign a role from a client

 Unassigns the specified role from the client. The client will no longer inherit the authorizations
associated with this role.

Args:
    role_id (str):
    client_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignRoleFromClientResponse400 | UnassignRoleFromClientResponse403 | UnassignRoleFromClientResponse404 | UnassignRoleFromClientResponse500 | UnassignRoleFromClientResponse503]"""
    response = sync_detailed(role_id=role_id, client_id=client_id, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(role_id: str, client_id: str, *, client: AuthenticatedClient | Client) -> Response[Any | UnassignRoleFromClientResponse400 | UnassignRoleFromClientResponse403 | UnassignRoleFromClientResponse404 | UnassignRoleFromClientResponse500 | UnassignRoleFromClientResponse503]:
    """Unassign a role from a client

     Unassigns the specified role from the client. The client will no longer inherit the authorizations
    associated with this role.

    Args:
        role_id (str):
        client_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | UnassignRoleFromClientResponse400 | UnassignRoleFromClientResponse403 | UnassignRoleFromClientResponse404 | UnassignRoleFromClientResponse500 | UnassignRoleFromClientResponse503]
    """
    kwargs = _get_kwargs(role_id=role_id, client_id=client_id)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(role_id: str, client_id: str, *, client: AuthenticatedClient | Client, **kwargs) -> Any:
    """Unassign a role from a client

 Unassigns the specified role from the client. The client will no longer inherit the authorizations
associated with this role.

Args:
    role_id (str):
    client_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignRoleFromClientResponse400 | UnassignRoleFromClientResponse403 | UnassignRoleFromClientResponse404 | UnassignRoleFromClientResponse500 | UnassignRoleFromClientResponse503]"""
    response = await asyncio_detailed(role_id=role_id, client_id=client_id, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
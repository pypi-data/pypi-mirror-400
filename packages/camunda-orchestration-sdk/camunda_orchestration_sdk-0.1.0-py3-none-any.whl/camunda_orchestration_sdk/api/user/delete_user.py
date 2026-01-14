from http import HTTPStatus
from typing import Any, cast
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.delete_user_response_400 import DeleteUserResponse400
from ...models.delete_user_response_404 import DeleteUserResponse404
from ...models.delete_user_response_500 import DeleteUserResponse500
from ...models.delete_user_response_503 import DeleteUserResponse503
from ...types import Response

def _get_kwargs(username: str) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {'method': 'delete', 'url': '/users/{username}'.format(username=username)}
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | DeleteUserResponse400 | DeleteUserResponse404 | DeleteUserResponse500 | DeleteUserResponse503 | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 400:
        response_400 = DeleteUserResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 404:
        response_404 = DeleteUserResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = DeleteUserResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = DeleteUserResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | DeleteUserResponse400 | DeleteUserResponse404 | DeleteUserResponse500 | DeleteUserResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(username: str, *, client: AuthenticatedClient | Client) -> Response[Any | DeleteUserResponse400 | DeleteUserResponse404 | DeleteUserResponse500 | DeleteUserResponse503]:
    """Delete user

     Deletes a user.

    Args:
        username (str): The unique name of a user. Example: swillis.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | DeleteUserResponse400 | DeleteUserResponse404 | DeleteUserResponse500 | DeleteUserResponse503]
    """
    kwargs = _get_kwargs(username=username)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(username: str, *, client: AuthenticatedClient | Client, **kwargs) -> Any:
    """Delete user

 Deletes a user.

Args:
    username (str): The unique name of a user. Example: swillis.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteUserResponse400 | DeleteUserResponse404 | DeleteUserResponse500 | DeleteUserResponse503]"""
    response = sync_detailed(username=username, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(username: str, *, client: AuthenticatedClient | Client) -> Response[Any | DeleteUserResponse400 | DeleteUserResponse404 | DeleteUserResponse500 | DeleteUserResponse503]:
    """Delete user

     Deletes a user.

    Args:
        username (str): The unique name of a user. Example: swillis.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | DeleteUserResponse400 | DeleteUserResponse404 | DeleteUserResponse500 | DeleteUserResponse503]
    """
    kwargs = _get_kwargs(username=username)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(username: str, *, client: AuthenticatedClient | Client, **kwargs) -> Any:
    """Delete user

 Deletes a user.

Args:
    username (str): The unique name of a user. Example: swillis.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteUserResponse400 | DeleteUserResponse404 | DeleteUserResponse500 | DeleteUserResponse503]"""
    response = await asyncio_detailed(username=username, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
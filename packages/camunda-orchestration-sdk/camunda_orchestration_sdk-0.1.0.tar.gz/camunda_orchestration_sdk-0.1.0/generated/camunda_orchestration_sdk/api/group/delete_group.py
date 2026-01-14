from http import HTTPStatus
from typing import Any, cast
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.delete_group_response_401 import DeleteGroupResponse401
from ...models.delete_group_response_404 import DeleteGroupResponse404
from ...models.delete_group_response_500 import DeleteGroupResponse500
from ...models.delete_group_response_503 import DeleteGroupResponse503
from ...types import Response

def _get_kwargs(group_id: str) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {'method': 'delete', 'url': '/groups/{group_id}'.format(group_id=group_id)}
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | DeleteGroupResponse401 | DeleteGroupResponse404 | DeleteGroupResponse500 | DeleteGroupResponse503 | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 401:
        response_401 = DeleteGroupResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 404:
        response_404 = DeleteGroupResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = DeleteGroupResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = DeleteGroupResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | DeleteGroupResponse401 | DeleteGroupResponse404 | DeleteGroupResponse500 | DeleteGroupResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(group_id: str, *, client: AuthenticatedClient | Client) -> Response[Any | DeleteGroupResponse401 | DeleteGroupResponse404 | DeleteGroupResponse500 | DeleteGroupResponse503]:
    """Delete group

     Deletes the group with the given ID.

    Args:
        group_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | DeleteGroupResponse401 | DeleteGroupResponse404 | DeleteGroupResponse500 | DeleteGroupResponse503]
    """
    kwargs = _get_kwargs(group_id=group_id)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(group_id: str, *, client: AuthenticatedClient | Client, **kwargs) -> Any:
    """Delete group

 Deletes the group with the given ID.

Args:
    group_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteGroupResponse401 | DeleteGroupResponse404 | DeleteGroupResponse500 | DeleteGroupResponse503]"""
    response = sync_detailed(group_id=group_id, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(group_id: str, *, client: AuthenticatedClient | Client) -> Response[Any | DeleteGroupResponse401 | DeleteGroupResponse404 | DeleteGroupResponse500 | DeleteGroupResponse503]:
    """Delete group

     Deletes the group with the given ID.

    Args:
        group_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | DeleteGroupResponse401 | DeleteGroupResponse404 | DeleteGroupResponse500 | DeleteGroupResponse503]
    """
    kwargs = _get_kwargs(group_id=group_id)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(group_id: str, *, client: AuthenticatedClient | Client, **kwargs) -> Any:
    """Delete group

 Deletes the group with the given ID.

Args:
    group_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteGroupResponse401 | DeleteGroupResponse404 | DeleteGroupResponse500 | DeleteGroupResponse503]"""
    response = await asyncio_detailed(group_id=group_id, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
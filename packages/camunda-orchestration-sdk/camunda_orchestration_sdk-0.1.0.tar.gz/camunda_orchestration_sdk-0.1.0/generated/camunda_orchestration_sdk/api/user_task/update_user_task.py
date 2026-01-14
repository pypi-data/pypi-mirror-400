from http import HTTPStatus
from typing import Any, cast
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.update_user_task_data import UpdateUserTaskData
from ...models.update_user_task_response_400 import UpdateUserTaskResponse400
from ...models.update_user_task_response_404 import UpdateUserTaskResponse404
from ...models.update_user_task_response_409 import UpdateUserTaskResponse409
from ...models.update_user_task_response_500 import UpdateUserTaskResponse500
from ...models.update_user_task_response_503 import UpdateUserTaskResponse503
from ...types import Response

def _get_kwargs(user_task_key: str, *, body: UpdateUserTaskData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'patch', 'url': '/user-tasks/{user_task_key}'.format(user_task_key=user_task_key)}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | UpdateUserTaskResponse400 | UpdateUserTaskResponse404 | UpdateUserTaskResponse409 | UpdateUserTaskResponse500 | UpdateUserTaskResponse503 | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 400:
        response_400 = UpdateUserTaskResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 404:
        response_404 = UpdateUserTaskResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 409:
        response_409 = UpdateUserTaskResponse409.from_dict(response.json())
        return response_409
    if response.status_code == 500:
        response_500 = UpdateUserTaskResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = UpdateUserTaskResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | UpdateUserTaskResponse400 | UpdateUserTaskResponse404 | UpdateUserTaskResponse409 | UpdateUserTaskResponse500 | UpdateUserTaskResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(user_task_key: str, *, client: AuthenticatedClient | Client, body: UpdateUserTaskData) -> Response[Any | UpdateUserTaskResponse400 | UpdateUserTaskResponse404 | UpdateUserTaskResponse409 | UpdateUserTaskResponse500 | UpdateUserTaskResponse503]:
    """Update user task

     Update a user task with the given key.

    Args:
        user_task_key (str): System-generated key for a user task.
        body (UpdateUserTaskData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | UpdateUserTaskResponse400 | UpdateUserTaskResponse404 | UpdateUserTaskResponse409 | UpdateUserTaskResponse500 | UpdateUserTaskResponse503]
    """
    kwargs = _get_kwargs(user_task_key=user_task_key, body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(user_task_key: str, *, client: AuthenticatedClient | Client, body: UpdateUserTaskData, **kwargs) -> Any:
    """Update user task

 Update a user task with the given key.

Args:
    user_task_key (str): System-generated key for a user task.
    body (UpdateUserTaskData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UpdateUserTaskResponse400 | UpdateUserTaskResponse404 | UpdateUserTaskResponse409 | UpdateUserTaskResponse500 | UpdateUserTaskResponse503]"""
    response = sync_detailed(user_task_key=user_task_key, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(user_task_key: str, *, client: AuthenticatedClient | Client, body: UpdateUserTaskData) -> Response[Any | UpdateUserTaskResponse400 | UpdateUserTaskResponse404 | UpdateUserTaskResponse409 | UpdateUserTaskResponse500 | UpdateUserTaskResponse503]:
    """Update user task

     Update a user task with the given key.

    Args:
        user_task_key (str): System-generated key for a user task.
        body (UpdateUserTaskData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | UpdateUserTaskResponse400 | UpdateUserTaskResponse404 | UpdateUserTaskResponse409 | UpdateUserTaskResponse500 | UpdateUserTaskResponse503]
    """
    kwargs = _get_kwargs(user_task_key=user_task_key, body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(user_task_key: str, *, client: AuthenticatedClient | Client, body: UpdateUserTaskData, **kwargs) -> Any:
    """Update user task

 Update a user task with the given key.

Args:
    user_task_key (str): System-generated key for a user task.
    body (UpdateUserTaskData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UpdateUserTaskResponse400 | UpdateUserTaskResponse404 | UpdateUserTaskResponse409 | UpdateUserTaskResponse500 | UpdateUserTaskResponse503]"""
    response = await asyncio_detailed(user_task_key=user_task_key, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
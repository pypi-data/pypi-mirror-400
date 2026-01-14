from http import HTTPStatus
from typing import Any, cast
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.assign_user_task_data import AssignUserTaskData
from ...models.assign_user_task_response_400 import AssignUserTaskResponse400
from ...models.assign_user_task_response_404 import AssignUserTaskResponse404
from ...models.assign_user_task_response_409 import AssignUserTaskResponse409
from ...models.assign_user_task_response_500 import AssignUserTaskResponse500
from ...models.assign_user_task_response_503 import AssignUserTaskResponse503
from ...types import Response

def _get_kwargs(user_task_key: str, *, body: AssignUserTaskData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/user-tasks/{user_task_key}/assignment'.format(user_task_key=user_task_key)}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | AssignUserTaskResponse400 | AssignUserTaskResponse404 | AssignUserTaskResponse409 | AssignUserTaskResponse500 | AssignUserTaskResponse503 | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 400:
        response_400 = AssignUserTaskResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 404:
        response_404 = AssignUserTaskResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 409:
        response_409 = AssignUserTaskResponse409.from_dict(response.json())
        return response_409
    if response.status_code == 500:
        response_500 = AssignUserTaskResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = AssignUserTaskResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | AssignUserTaskResponse400 | AssignUserTaskResponse404 | AssignUserTaskResponse409 | AssignUserTaskResponse500 | AssignUserTaskResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(user_task_key: str, *, client: AuthenticatedClient | Client, body: AssignUserTaskData) -> Response[Any | AssignUserTaskResponse400 | AssignUserTaskResponse404 | AssignUserTaskResponse409 | AssignUserTaskResponse500 | AssignUserTaskResponse503]:
    """Assign user task

     Assigns a user task with the given key to the given assignee.

    Args:
        user_task_key (str): System-generated key for a user task.
        body (AssignUserTaskData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | AssignUserTaskResponse400 | AssignUserTaskResponse404 | AssignUserTaskResponse409 | AssignUserTaskResponse500 | AssignUserTaskResponse503]
    """
    kwargs = _get_kwargs(user_task_key=user_task_key, body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(user_task_key: str, *, client: AuthenticatedClient | Client, body: AssignUserTaskData, **kwargs) -> Any:
    """Assign user task

 Assigns a user task with the given key to the given assignee.

Args:
    user_task_key (str): System-generated key for a user task.
    body (AssignUserTaskData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignUserTaskResponse400 | AssignUserTaskResponse404 | AssignUserTaskResponse409 | AssignUserTaskResponse500 | AssignUserTaskResponse503]"""
    response = sync_detailed(user_task_key=user_task_key, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(user_task_key: str, *, client: AuthenticatedClient | Client, body: AssignUserTaskData) -> Response[Any | AssignUserTaskResponse400 | AssignUserTaskResponse404 | AssignUserTaskResponse409 | AssignUserTaskResponse500 | AssignUserTaskResponse503]:
    """Assign user task

     Assigns a user task with the given key to the given assignee.

    Args:
        user_task_key (str): System-generated key for a user task.
        body (AssignUserTaskData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | AssignUserTaskResponse400 | AssignUserTaskResponse404 | AssignUserTaskResponse409 | AssignUserTaskResponse500 | AssignUserTaskResponse503]
    """
    kwargs = _get_kwargs(user_task_key=user_task_key, body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(user_task_key: str, *, client: AuthenticatedClient | Client, body: AssignUserTaskData, **kwargs) -> Any:
    """Assign user task

 Assigns a user task with the given key to the given assignee.

Args:
    user_task_key (str): System-generated key for a user task.
    body (AssignUserTaskData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignUserTaskResponse400 | AssignUserTaskResponse404 | AssignUserTaskResponse409 | AssignUserTaskResponse500 | AssignUserTaskResponse503]"""
    response = await asyncio_detailed(user_task_key=user_task_key, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
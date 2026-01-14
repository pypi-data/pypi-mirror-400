from http import HTTPStatus
from typing import Any, cast
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_user_task_form_response_200 import GetUserTaskFormResponse200
from ...models.get_user_task_form_response_400 import GetUserTaskFormResponse400
from ...models.get_user_task_form_response_401 import GetUserTaskFormResponse401
from ...models.get_user_task_form_response_403 import GetUserTaskFormResponse403
from ...models.get_user_task_form_response_404 import GetUserTaskFormResponse404
from ...models.get_user_task_form_response_500 import GetUserTaskFormResponse500
from ...types import Response

def _get_kwargs(user_task_key: str) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {'method': 'get', 'url': '/user-tasks/{user_task_key}/form'.format(user_task_key=user_task_key)}
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | GetUserTaskFormResponse200 | GetUserTaskFormResponse400 | GetUserTaskFormResponse401 | GetUserTaskFormResponse403 | GetUserTaskFormResponse404 | GetUserTaskFormResponse500 | None:
    if response.status_code == 200:
        response_200 = GetUserTaskFormResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 400:
        response_400 = GetUserTaskFormResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = GetUserTaskFormResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = GetUserTaskFormResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = GetUserTaskFormResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = GetUserTaskFormResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | GetUserTaskFormResponse200 | GetUserTaskFormResponse400 | GetUserTaskFormResponse401 | GetUserTaskFormResponse403 | GetUserTaskFormResponse404 | GetUserTaskFormResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(user_task_key: str, *, client: AuthenticatedClient | Client) -> Response[Any | GetUserTaskFormResponse200 | GetUserTaskFormResponse400 | GetUserTaskFormResponse401 | GetUserTaskFormResponse403 | GetUserTaskFormResponse404 | GetUserTaskFormResponse500]:
    """Get user task form

     Get the form of a user task.
    Note that this endpoint will only return linked forms. This endpoint does not support embedded
    forms.

    Args:
        user_task_key (str): System-generated key for a user task.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | GetUserTaskFormResponse200 | GetUserTaskFormResponse400 | GetUserTaskFormResponse401 | GetUserTaskFormResponse403 | GetUserTaskFormResponse404 | GetUserTaskFormResponse500]
    """
    kwargs = _get_kwargs(user_task_key=user_task_key)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(user_task_key: str, *, client: AuthenticatedClient | Client, **kwargs) -> Any:
    """Get user task form

 Get the form of a user task.
Note that this endpoint will only return linked forms. This endpoint does not support embedded
forms.

Args:
    user_task_key (str): System-generated key for a user task.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | GetUserTaskFormResponse200 | GetUserTaskFormResponse400 | GetUserTaskFormResponse401 | GetUserTaskFormResponse403 | GetUserTaskFormResponse404 | GetUserTaskFormResponse500]"""
    response = sync_detailed(user_task_key=user_task_key, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(user_task_key: str, *, client: AuthenticatedClient | Client) -> Response[Any | GetUserTaskFormResponse200 | GetUserTaskFormResponse400 | GetUserTaskFormResponse401 | GetUserTaskFormResponse403 | GetUserTaskFormResponse404 | GetUserTaskFormResponse500]:
    """Get user task form

     Get the form of a user task.
    Note that this endpoint will only return linked forms. This endpoint does not support embedded
    forms.

    Args:
        user_task_key (str): System-generated key for a user task.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | GetUserTaskFormResponse200 | GetUserTaskFormResponse400 | GetUserTaskFormResponse401 | GetUserTaskFormResponse403 | GetUserTaskFormResponse404 | GetUserTaskFormResponse500]
    """
    kwargs = _get_kwargs(user_task_key=user_task_key)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(user_task_key: str, *, client: AuthenticatedClient | Client, **kwargs) -> Any:
    """Get user task form

 Get the form of a user task.
Note that this endpoint will only return linked forms. This endpoint does not support embedded
forms.

Args:
    user_task_key (str): System-generated key for a user task.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | GetUserTaskFormResponse200 | GetUserTaskFormResponse400 | GetUserTaskFormResponse401 | GetUserTaskFormResponse403 | GetUserTaskFormResponse404 | GetUserTaskFormResponse500]"""
    response = await asyncio_detailed(user_task_key=user_task_key, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
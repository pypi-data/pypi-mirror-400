from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.search_user_task_variables_data import SearchUserTaskVariablesData
from ...models.search_user_task_variables_response_200 import SearchUserTaskVariablesResponse200
from ...models.search_user_task_variables_response_400 import SearchUserTaskVariablesResponse400
from ...models.search_user_task_variables_response_500 import SearchUserTaskVariablesResponse500
from ...types import UNSET, Response, Unset

def _get_kwargs(user_task_key: str, *, body: SearchUserTaskVariablesData, truncate_values: bool | Unset=UNSET) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    params: dict[str, Any] = {}
    params['truncateValues'] = truncate_values
    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/user-tasks/{user_task_key}/variables/search'.format(user_task_key=user_task_key), 'params': params}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> SearchUserTaskVariablesResponse200 | SearchUserTaskVariablesResponse400 | SearchUserTaskVariablesResponse500 | None:
    if response.status_code == 200:
        response_200 = SearchUserTaskVariablesResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = SearchUserTaskVariablesResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 500:
        response_500 = SearchUserTaskVariablesResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[SearchUserTaskVariablesResponse200 | SearchUserTaskVariablesResponse400 | SearchUserTaskVariablesResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(user_task_key: str, *, client: AuthenticatedClient | Client, body: SearchUserTaskVariablesData, truncate_values: bool | Unset=UNSET) -> Response[SearchUserTaskVariablesResponse200 | SearchUserTaskVariablesResponse400 | SearchUserTaskVariablesResponse500]:
    """Search user task variables

     Search for user task variables based on given criteria. By default, long variable values in the
    response are truncated.

    Args:
        user_task_key (str): System-generated key for a user task.
        truncate_values (bool | Unset):
        body (SearchUserTaskVariablesData): User task search query request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchUserTaskVariablesResponse200 | SearchUserTaskVariablesResponse400 | SearchUserTaskVariablesResponse500]
    """
    kwargs = _get_kwargs(user_task_key=user_task_key, body=body, truncate_values=truncate_values)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(user_task_key: str, *, client: AuthenticatedClient | Client, body: SearchUserTaskVariablesData, truncate_values: bool | Unset=UNSET, **kwargs) -> SearchUserTaskVariablesResponse200:
    """Search user task variables

 Search for user task variables based on given criteria. By default, long variable values in the
response are truncated.

Args:
    user_task_key (str): System-generated key for a user task.
    truncate_values (bool | Unset):
    body (SearchUserTaskVariablesData): User task search query request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchUserTaskVariablesResponse200 | SearchUserTaskVariablesResponse400 | SearchUserTaskVariablesResponse500]"""
    response = sync_detailed(user_task_key=user_task_key, client=client, body=body, truncate_values=truncate_values)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(user_task_key: str, *, client: AuthenticatedClient | Client, body: SearchUserTaskVariablesData, truncate_values: bool | Unset=UNSET) -> Response[SearchUserTaskVariablesResponse200 | SearchUserTaskVariablesResponse400 | SearchUserTaskVariablesResponse500]:
    """Search user task variables

     Search for user task variables based on given criteria. By default, long variable values in the
    response are truncated.

    Args:
        user_task_key (str): System-generated key for a user task.
        truncate_values (bool | Unset):
        body (SearchUserTaskVariablesData): User task search query request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchUserTaskVariablesResponse200 | SearchUserTaskVariablesResponse400 | SearchUserTaskVariablesResponse500]
    """
    kwargs = _get_kwargs(user_task_key=user_task_key, body=body, truncate_values=truncate_values)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(user_task_key: str, *, client: AuthenticatedClient | Client, body: SearchUserTaskVariablesData, truncate_values: bool | Unset=UNSET, **kwargs) -> SearchUserTaskVariablesResponse200:
    """Search user task variables

 Search for user task variables based on given criteria. By default, long variable values in the
response are truncated.

Args:
    user_task_key (str): System-generated key for a user task.
    truncate_values (bool | Unset):
    body (SearchUserTaskVariablesData): User task search query request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchUserTaskVariablesResponse200 | SearchUserTaskVariablesResponse400 | SearchUserTaskVariablesResponse500]"""
    response = await asyncio_detailed(user_task_key=user_task_key, client=client, body=body, truncate_values=truncate_values)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
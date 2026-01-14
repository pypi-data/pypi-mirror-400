from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.search_user_task_audit_logs_data import SearchUserTaskAuditLogsData
from ...models.search_user_task_audit_logs_response_200 import SearchUserTaskAuditLogsResponse200
from ...models.search_user_task_audit_logs_response_400 import SearchUserTaskAuditLogsResponse400
from ...models.search_user_task_audit_logs_response_500 import SearchUserTaskAuditLogsResponse500
from ...types import Response

def _get_kwargs(user_task_key: str, *, body: SearchUserTaskAuditLogsData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/user-tasks/{user_task_key}/audit-logs/search'.format(user_task_key=user_task_key)}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> SearchUserTaskAuditLogsResponse200 | SearchUserTaskAuditLogsResponse400 | SearchUserTaskAuditLogsResponse500 | None:
    if response.status_code == 200:
        response_200 = SearchUserTaskAuditLogsResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = SearchUserTaskAuditLogsResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 500:
        response_500 = SearchUserTaskAuditLogsResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[SearchUserTaskAuditLogsResponse200 | SearchUserTaskAuditLogsResponse400 | SearchUserTaskAuditLogsResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(user_task_key: str, *, client: AuthenticatedClient | Client, body: SearchUserTaskAuditLogsData) -> Response[SearchUserTaskAuditLogsResponse200 | SearchUserTaskAuditLogsResponse400 | SearchUserTaskAuditLogsResponse500]:
    """Search user task audit logs

     Search for user task audit logs based on given criteria.

    Args:
        user_task_key (str): System-generated key for a user task.
        body (SearchUserTaskAuditLogsData): User task search query request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchUserTaskAuditLogsResponse200 | SearchUserTaskAuditLogsResponse400 | SearchUserTaskAuditLogsResponse500]
    """
    kwargs = _get_kwargs(user_task_key=user_task_key, body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(user_task_key: str, *, client: AuthenticatedClient | Client, body: SearchUserTaskAuditLogsData, **kwargs) -> SearchUserTaskAuditLogsResponse200:
    """Search user task audit logs

 Search for user task audit logs based on given criteria.

Args:
    user_task_key (str): System-generated key for a user task.
    body (SearchUserTaskAuditLogsData): User task search query request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchUserTaskAuditLogsResponse200 | SearchUserTaskAuditLogsResponse400 | SearchUserTaskAuditLogsResponse500]"""
    response = sync_detailed(user_task_key=user_task_key, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(user_task_key: str, *, client: AuthenticatedClient | Client, body: SearchUserTaskAuditLogsData) -> Response[SearchUserTaskAuditLogsResponse200 | SearchUserTaskAuditLogsResponse400 | SearchUserTaskAuditLogsResponse500]:
    """Search user task audit logs

     Search for user task audit logs based on given criteria.

    Args:
        user_task_key (str): System-generated key for a user task.
        body (SearchUserTaskAuditLogsData): User task search query request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchUserTaskAuditLogsResponse200 | SearchUserTaskAuditLogsResponse400 | SearchUserTaskAuditLogsResponse500]
    """
    kwargs = _get_kwargs(user_task_key=user_task_key, body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(user_task_key: str, *, client: AuthenticatedClient | Client, body: SearchUserTaskAuditLogsData, **kwargs) -> SearchUserTaskAuditLogsResponse200:
    """Search user task audit logs

 Search for user task audit logs based on given criteria.

Args:
    user_task_key (str): System-generated key for a user task.
    body (SearchUserTaskAuditLogsData): User task search query request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchUserTaskAuditLogsResponse200 | SearchUserTaskAuditLogsResponse400 | SearchUserTaskAuditLogsResponse500]"""
    response = await asyncio_detailed(user_task_key=user_task_key, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
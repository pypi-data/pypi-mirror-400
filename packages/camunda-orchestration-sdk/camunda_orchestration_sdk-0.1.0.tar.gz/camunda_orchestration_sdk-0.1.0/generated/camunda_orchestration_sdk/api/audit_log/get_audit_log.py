from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_audit_log_response_200 import GetAuditLogResponse200
from ...models.get_audit_log_response_401 import GetAuditLogResponse401
from ...models.get_audit_log_response_403 import GetAuditLogResponse403
from ...models.get_audit_log_response_404 import GetAuditLogResponse404
from ...models.get_audit_log_response_500 import GetAuditLogResponse500
from ...types import Response

def _get_kwargs(audit_log_key: str) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {'method': 'get', 'url': '/audit-logs/{audit_log_key}'.format(audit_log_key=audit_log_key)}
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetAuditLogResponse200 | GetAuditLogResponse401 | GetAuditLogResponse403 | GetAuditLogResponse404 | GetAuditLogResponse500 | None:
    if response.status_code == 200:
        response_200 = GetAuditLogResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 401:
        response_401 = GetAuditLogResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = GetAuditLogResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = GetAuditLogResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = GetAuditLogResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GetAuditLogResponse200 | GetAuditLogResponse401 | GetAuditLogResponse403 | GetAuditLogResponse404 | GetAuditLogResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(audit_log_key: str, *, client: AuthenticatedClient | Client) -> Response[GetAuditLogResponse200 | GetAuditLogResponse401 | GetAuditLogResponse403 | GetAuditLogResponse404 | GetAuditLogResponse500]:
    """Get audit log

     Get an audit log entry by auditLogKey.

    Args:
        audit_log_key (str): System-generated key for an audit log entry. Example:
            22517998136843567.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetAuditLogResponse200 | GetAuditLogResponse401 | GetAuditLogResponse403 | GetAuditLogResponse404 | GetAuditLogResponse500]
    """
    kwargs = _get_kwargs(audit_log_key=audit_log_key)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(audit_log_key: str, *, client: AuthenticatedClient | Client, **kwargs) -> GetAuditLogResponse200:
    """Get audit log

 Get an audit log entry by auditLogKey.

Args:
    audit_log_key (str): System-generated key for an audit log entry. Example:
        22517998136843567.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetAuditLogResponse200 | GetAuditLogResponse401 | GetAuditLogResponse403 | GetAuditLogResponse404 | GetAuditLogResponse500]"""
    response = sync_detailed(audit_log_key=audit_log_key, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(audit_log_key: str, *, client: AuthenticatedClient | Client) -> Response[GetAuditLogResponse200 | GetAuditLogResponse401 | GetAuditLogResponse403 | GetAuditLogResponse404 | GetAuditLogResponse500]:
    """Get audit log

     Get an audit log entry by auditLogKey.

    Args:
        audit_log_key (str): System-generated key for an audit log entry. Example:
            22517998136843567.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetAuditLogResponse200 | GetAuditLogResponse401 | GetAuditLogResponse403 | GetAuditLogResponse404 | GetAuditLogResponse500]
    """
    kwargs = _get_kwargs(audit_log_key=audit_log_key)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(audit_log_key: str, *, client: AuthenticatedClient | Client, **kwargs) -> GetAuditLogResponse200:
    """Get audit log

 Get an audit log entry by auditLogKey.

Args:
    audit_log_key (str): System-generated key for an audit log entry. Example:
        22517998136843567.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetAuditLogResponse200 | GetAuditLogResponse401 | GetAuditLogResponse403 | GetAuditLogResponse404 | GetAuditLogResponse500]"""
    response = await asyncio_detailed(audit_log_key=audit_log_key, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
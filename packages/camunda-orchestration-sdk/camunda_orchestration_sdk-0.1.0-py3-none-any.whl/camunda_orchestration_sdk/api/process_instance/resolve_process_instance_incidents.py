from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.resolve_process_instance_incidents_response_200 import ResolveProcessInstanceIncidentsResponse200
from ...models.resolve_process_instance_incidents_response_400 import ResolveProcessInstanceIncidentsResponse400
from ...models.resolve_process_instance_incidents_response_401 import ResolveProcessInstanceIncidentsResponse401
from ...models.resolve_process_instance_incidents_response_404 import ResolveProcessInstanceIncidentsResponse404
from ...models.resolve_process_instance_incidents_response_500 import ResolveProcessInstanceIncidentsResponse500
from ...models.resolve_process_instance_incidents_response_503 import ResolveProcessInstanceIncidentsResponse503
from ...types import Response

def _get_kwargs(process_instance_key: str) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/process-instances/{process_instance_key}/incident-resolution'.format(process_instance_key=process_instance_key)}
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ResolveProcessInstanceIncidentsResponse200 | ResolveProcessInstanceIncidentsResponse400 | ResolveProcessInstanceIncidentsResponse401 | ResolveProcessInstanceIncidentsResponse404 | ResolveProcessInstanceIncidentsResponse500 | ResolveProcessInstanceIncidentsResponse503 | None:
    if response.status_code == 200:
        response_200 = ResolveProcessInstanceIncidentsResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = ResolveProcessInstanceIncidentsResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = ResolveProcessInstanceIncidentsResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 404:
        response_404 = ResolveProcessInstanceIncidentsResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = ResolveProcessInstanceIncidentsResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = ResolveProcessInstanceIncidentsResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[ResolveProcessInstanceIncidentsResponse200 | ResolveProcessInstanceIncidentsResponse400 | ResolveProcessInstanceIncidentsResponse401 | ResolveProcessInstanceIncidentsResponse404 | ResolveProcessInstanceIncidentsResponse500 | ResolveProcessInstanceIncidentsResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(process_instance_key: str, *, client: AuthenticatedClient | Client) -> Response[ResolveProcessInstanceIncidentsResponse200 | ResolveProcessInstanceIncidentsResponse400 | ResolveProcessInstanceIncidentsResponse401 | ResolveProcessInstanceIncidentsResponse404 | ResolveProcessInstanceIncidentsResponse500 | ResolveProcessInstanceIncidentsResponse503]:
    """Resolve related incidents

     Creates a batch operation to resolve multiple incidents of a process instance.

    Args:
        process_instance_key (str): System-generated key for a process instance. Example:
            2251799813690746.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ResolveProcessInstanceIncidentsResponse200 | ResolveProcessInstanceIncidentsResponse400 | ResolveProcessInstanceIncidentsResponse401 | ResolveProcessInstanceIncidentsResponse404 | ResolveProcessInstanceIncidentsResponse500 | ResolveProcessInstanceIncidentsResponse503]
    """
    kwargs = _get_kwargs(process_instance_key=process_instance_key)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(process_instance_key: str, *, client: AuthenticatedClient | Client, **kwargs) -> ResolveProcessInstanceIncidentsResponse200:
    """Resolve related incidents

 Creates a batch operation to resolve multiple incidents of a process instance.

Args:
    process_instance_key (str): System-generated key for a process instance. Example:
        2251799813690746.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[ResolveProcessInstanceIncidentsResponse200 | ResolveProcessInstanceIncidentsResponse400 | ResolveProcessInstanceIncidentsResponse401 | ResolveProcessInstanceIncidentsResponse404 | ResolveProcessInstanceIncidentsResponse500 | ResolveProcessInstanceIncidentsResponse503]"""
    response = sync_detailed(process_instance_key=process_instance_key, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(process_instance_key: str, *, client: AuthenticatedClient | Client) -> Response[ResolveProcessInstanceIncidentsResponse200 | ResolveProcessInstanceIncidentsResponse400 | ResolveProcessInstanceIncidentsResponse401 | ResolveProcessInstanceIncidentsResponse404 | ResolveProcessInstanceIncidentsResponse500 | ResolveProcessInstanceIncidentsResponse503]:
    """Resolve related incidents

     Creates a batch operation to resolve multiple incidents of a process instance.

    Args:
        process_instance_key (str): System-generated key for a process instance. Example:
            2251799813690746.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ResolveProcessInstanceIncidentsResponse200 | ResolveProcessInstanceIncidentsResponse400 | ResolveProcessInstanceIncidentsResponse401 | ResolveProcessInstanceIncidentsResponse404 | ResolveProcessInstanceIncidentsResponse500 | ResolveProcessInstanceIncidentsResponse503]
    """
    kwargs = _get_kwargs(process_instance_key=process_instance_key)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(process_instance_key: str, *, client: AuthenticatedClient | Client, **kwargs) -> ResolveProcessInstanceIncidentsResponse200:
    """Resolve related incidents

 Creates a batch operation to resolve multiple incidents of a process instance.

Args:
    process_instance_key (str): System-generated key for a process instance. Example:
        2251799813690746.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[ResolveProcessInstanceIncidentsResponse200 | ResolveProcessInstanceIncidentsResponse400 | ResolveProcessInstanceIncidentsResponse401 | ResolveProcessInstanceIncidentsResponse404 | ResolveProcessInstanceIncidentsResponse500 | ResolveProcessInstanceIncidentsResponse503]"""
    response = await asyncio_detailed(process_instance_key=process_instance_key, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
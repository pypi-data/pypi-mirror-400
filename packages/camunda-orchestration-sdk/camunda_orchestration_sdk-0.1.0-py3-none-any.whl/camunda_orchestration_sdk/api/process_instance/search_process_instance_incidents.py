from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.search_process_instance_incidents_data import SearchProcessInstanceIncidentsData
from ...models.search_process_instance_incidents_response_200 import SearchProcessInstanceIncidentsResponse200
from ...models.search_process_instance_incidents_response_400 import SearchProcessInstanceIncidentsResponse400
from ...models.search_process_instance_incidents_response_401 import SearchProcessInstanceIncidentsResponse401
from ...models.search_process_instance_incidents_response_403 import SearchProcessInstanceIncidentsResponse403
from ...models.search_process_instance_incidents_response_404 import SearchProcessInstanceIncidentsResponse404
from ...models.search_process_instance_incidents_response_500 import SearchProcessInstanceIncidentsResponse500
from ...types import Response

def _get_kwargs(process_instance_key: str, *, body: SearchProcessInstanceIncidentsData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/process-instances/{process_instance_key}/incidents/search'.format(process_instance_key=process_instance_key)}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> SearchProcessInstanceIncidentsResponse200 | SearchProcessInstanceIncidentsResponse400 | SearchProcessInstanceIncidentsResponse401 | SearchProcessInstanceIncidentsResponse403 | SearchProcessInstanceIncidentsResponse404 | SearchProcessInstanceIncidentsResponse500 | None:
    if response.status_code == 200:
        response_200 = SearchProcessInstanceIncidentsResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = SearchProcessInstanceIncidentsResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = SearchProcessInstanceIncidentsResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = SearchProcessInstanceIncidentsResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = SearchProcessInstanceIncidentsResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = SearchProcessInstanceIncidentsResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[SearchProcessInstanceIncidentsResponse200 | SearchProcessInstanceIncidentsResponse400 | SearchProcessInstanceIncidentsResponse401 | SearchProcessInstanceIncidentsResponse403 | SearchProcessInstanceIncidentsResponse404 | SearchProcessInstanceIncidentsResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(process_instance_key: str, *, client: AuthenticatedClient | Client, body: SearchProcessInstanceIncidentsData) -> Response[SearchProcessInstanceIncidentsResponse200 | SearchProcessInstanceIncidentsResponse400 | SearchProcessInstanceIncidentsResponse401 | SearchProcessInstanceIncidentsResponse403 | SearchProcessInstanceIncidentsResponse404 | SearchProcessInstanceIncidentsResponse500]:
    """Search related incidents

     Search for incidents caused by the process instance or any of its called process or decision
    instances.

    Although the `processInstanceKey` is provided as a path parameter to indicate the root process
    instance,
    you may also include a `processInstanceKey` within the filter object to narrow results to specific
    child process instances. This is useful, for example, if you want to isolate incidents associated
    with
    subprocesses or called processes under the root instance while excluding incidents directly tied to
    the root.

    Args:
        process_instance_key (str): System-generated key for a process instance. Example:
            2251799813690746.
        body (SearchProcessInstanceIncidentsData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchProcessInstanceIncidentsResponse200 | SearchProcessInstanceIncidentsResponse400 | SearchProcessInstanceIncidentsResponse401 | SearchProcessInstanceIncidentsResponse403 | SearchProcessInstanceIncidentsResponse404 | SearchProcessInstanceIncidentsResponse500]
    """
    kwargs = _get_kwargs(process_instance_key=process_instance_key, body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(process_instance_key: str, *, client: AuthenticatedClient | Client, body: SearchProcessInstanceIncidentsData, **kwargs) -> SearchProcessInstanceIncidentsResponse200:
    """Search related incidents

 Search for incidents caused by the process instance or any of its called process or decision
instances.

Although the `processInstanceKey` is provided as a path parameter to indicate the root process
instance,
you may also include a `processInstanceKey` within the filter object to narrow results to specific
child process instances. This is useful, for example, if you want to isolate incidents associated
with
subprocesses or called processes under the root instance while excluding incidents directly tied to
the root.

Args:
    process_instance_key (str): System-generated key for a process instance. Example:
        2251799813690746.
    body (SearchProcessInstanceIncidentsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchProcessInstanceIncidentsResponse200 | SearchProcessInstanceIncidentsResponse400 | SearchProcessInstanceIncidentsResponse401 | SearchProcessInstanceIncidentsResponse403 | SearchProcessInstanceIncidentsResponse404 | SearchProcessInstanceIncidentsResponse500]"""
    response = sync_detailed(process_instance_key=process_instance_key, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(process_instance_key: str, *, client: AuthenticatedClient | Client, body: SearchProcessInstanceIncidentsData) -> Response[SearchProcessInstanceIncidentsResponse200 | SearchProcessInstanceIncidentsResponse400 | SearchProcessInstanceIncidentsResponse401 | SearchProcessInstanceIncidentsResponse403 | SearchProcessInstanceIncidentsResponse404 | SearchProcessInstanceIncidentsResponse500]:
    """Search related incidents

     Search for incidents caused by the process instance or any of its called process or decision
    instances.

    Although the `processInstanceKey` is provided as a path parameter to indicate the root process
    instance,
    you may also include a `processInstanceKey` within the filter object to narrow results to specific
    child process instances. This is useful, for example, if you want to isolate incidents associated
    with
    subprocesses or called processes under the root instance while excluding incidents directly tied to
    the root.

    Args:
        process_instance_key (str): System-generated key for a process instance. Example:
            2251799813690746.
        body (SearchProcessInstanceIncidentsData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchProcessInstanceIncidentsResponse200 | SearchProcessInstanceIncidentsResponse400 | SearchProcessInstanceIncidentsResponse401 | SearchProcessInstanceIncidentsResponse403 | SearchProcessInstanceIncidentsResponse404 | SearchProcessInstanceIncidentsResponse500]
    """
    kwargs = _get_kwargs(process_instance_key=process_instance_key, body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(process_instance_key: str, *, client: AuthenticatedClient | Client, body: SearchProcessInstanceIncidentsData, **kwargs) -> SearchProcessInstanceIncidentsResponse200:
    """Search related incidents

 Search for incidents caused by the process instance or any of its called process or decision
instances.

Although the `processInstanceKey` is provided as a path parameter to indicate the root process
instance,
you may also include a `processInstanceKey` within the filter object to narrow results to specific
child process instances. This is useful, for example, if you want to isolate incidents associated
with
subprocesses or called processes under the root instance while excluding incidents directly tied to
the root.

Args:
    process_instance_key (str): System-generated key for a process instance. Example:
        2251799813690746.
    body (SearchProcessInstanceIncidentsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchProcessInstanceIncidentsResponse200 | SearchProcessInstanceIncidentsResponse400 | SearchProcessInstanceIncidentsResponse401 | SearchProcessInstanceIncidentsResponse403 | SearchProcessInstanceIncidentsResponse404 | SearchProcessInstanceIncidentsResponse500]"""
    response = await asyncio_detailed(process_instance_key=process_instance_key, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_process_instance_response_200 import GetProcessInstanceResponse200
from ...models.get_process_instance_response_400 import GetProcessInstanceResponse400
from ...models.get_process_instance_response_401 import GetProcessInstanceResponse401
from ...models.get_process_instance_response_403 import GetProcessInstanceResponse403
from ...models.get_process_instance_response_404 import GetProcessInstanceResponse404
from ...models.get_process_instance_response_500 import GetProcessInstanceResponse500
from ...types import Response

def _get_kwargs(process_instance_key: str) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {'method': 'get', 'url': '/process-instances/{process_instance_key}'.format(process_instance_key=process_instance_key)}
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetProcessInstanceResponse200 | GetProcessInstanceResponse400 | GetProcessInstanceResponse401 | GetProcessInstanceResponse403 | GetProcessInstanceResponse404 | GetProcessInstanceResponse500 | None:
    if response.status_code == 200:
        response_200 = GetProcessInstanceResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = GetProcessInstanceResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = GetProcessInstanceResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = GetProcessInstanceResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = GetProcessInstanceResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = GetProcessInstanceResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GetProcessInstanceResponse200 | GetProcessInstanceResponse400 | GetProcessInstanceResponse401 | GetProcessInstanceResponse403 | GetProcessInstanceResponse404 | GetProcessInstanceResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(process_instance_key: str, *, client: AuthenticatedClient | Client) -> Response[GetProcessInstanceResponse200 | GetProcessInstanceResponse400 | GetProcessInstanceResponse401 | GetProcessInstanceResponse403 | GetProcessInstanceResponse404 | GetProcessInstanceResponse500]:
    """Get process instance

     Get the process instance by the process instance key.

    Args:
        process_instance_key (str): System-generated key for a process instance. Example:
            2251799813690746.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetProcessInstanceResponse200 | GetProcessInstanceResponse400 | GetProcessInstanceResponse401 | GetProcessInstanceResponse403 | GetProcessInstanceResponse404 | GetProcessInstanceResponse500]
    """
    kwargs = _get_kwargs(process_instance_key=process_instance_key)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(process_instance_key: str, *, client: AuthenticatedClient | Client, **kwargs) -> GetProcessInstanceResponse200:
    """Get process instance

 Get the process instance by the process instance key.

Args:
    process_instance_key (str): System-generated key for a process instance. Example:
        2251799813690746.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetProcessInstanceResponse200 | GetProcessInstanceResponse400 | GetProcessInstanceResponse401 | GetProcessInstanceResponse403 | GetProcessInstanceResponse404 | GetProcessInstanceResponse500]"""
    response = sync_detailed(process_instance_key=process_instance_key, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(process_instance_key: str, *, client: AuthenticatedClient | Client) -> Response[GetProcessInstanceResponse200 | GetProcessInstanceResponse400 | GetProcessInstanceResponse401 | GetProcessInstanceResponse403 | GetProcessInstanceResponse404 | GetProcessInstanceResponse500]:
    """Get process instance

     Get the process instance by the process instance key.

    Args:
        process_instance_key (str): System-generated key for a process instance. Example:
            2251799813690746.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetProcessInstanceResponse200 | GetProcessInstanceResponse400 | GetProcessInstanceResponse401 | GetProcessInstanceResponse403 | GetProcessInstanceResponse404 | GetProcessInstanceResponse500]
    """
    kwargs = _get_kwargs(process_instance_key=process_instance_key)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(process_instance_key: str, *, client: AuthenticatedClient | Client, **kwargs) -> GetProcessInstanceResponse200:
    """Get process instance

 Get the process instance by the process instance key.

Args:
    process_instance_key (str): System-generated key for a process instance. Example:
        2251799813690746.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetProcessInstanceResponse200 | GetProcessInstanceResponse400 | GetProcessInstanceResponse401 | GetProcessInstanceResponse403 | GetProcessInstanceResponse404 | GetProcessInstanceResponse500]"""
    response = await asyncio_detailed(process_instance_key=process_instance_key, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
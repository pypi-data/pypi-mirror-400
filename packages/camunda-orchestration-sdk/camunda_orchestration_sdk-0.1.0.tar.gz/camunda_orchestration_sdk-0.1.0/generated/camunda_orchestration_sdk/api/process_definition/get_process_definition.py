from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_process_definition_response_200 import GetProcessDefinitionResponse200
from ...models.get_process_definition_response_400 import GetProcessDefinitionResponse400
from ...models.get_process_definition_response_401 import GetProcessDefinitionResponse401
from ...models.get_process_definition_response_403 import GetProcessDefinitionResponse403
from ...models.get_process_definition_response_404 import GetProcessDefinitionResponse404
from ...models.get_process_definition_response_500 import GetProcessDefinitionResponse500
from ...types import Response

def _get_kwargs(process_definition_key: str) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {'method': 'get', 'url': '/process-definitions/{process_definition_key}'.format(process_definition_key=process_definition_key)}
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetProcessDefinitionResponse200 | GetProcessDefinitionResponse400 | GetProcessDefinitionResponse401 | GetProcessDefinitionResponse403 | GetProcessDefinitionResponse404 | GetProcessDefinitionResponse500 | None:
    if response.status_code == 200:
        response_200 = GetProcessDefinitionResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = GetProcessDefinitionResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = GetProcessDefinitionResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = GetProcessDefinitionResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = GetProcessDefinitionResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = GetProcessDefinitionResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GetProcessDefinitionResponse200 | GetProcessDefinitionResponse400 | GetProcessDefinitionResponse401 | GetProcessDefinitionResponse403 | GetProcessDefinitionResponse404 | GetProcessDefinitionResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(process_definition_key: str, *, client: AuthenticatedClient | Client) -> Response[GetProcessDefinitionResponse200 | GetProcessDefinitionResponse400 | GetProcessDefinitionResponse401 | GetProcessDefinitionResponse403 | GetProcessDefinitionResponse404 | GetProcessDefinitionResponse500]:
    """Get process definition

     Returns process definition as JSON.

    Args:
        process_definition_key (str): System-generated key for a deployed process definition.
            Example: 2251799813686749.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetProcessDefinitionResponse200 | GetProcessDefinitionResponse400 | GetProcessDefinitionResponse401 | GetProcessDefinitionResponse403 | GetProcessDefinitionResponse404 | GetProcessDefinitionResponse500]
    """
    kwargs = _get_kwargs(process_definition_key=process_definition_key)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(process_definition_key: str, *, client: AuthenticatedClient | Client, **kwargs) -> GetProcessDefinitionResponse200:
    """Get process definition

 Returns process definition as JSON.

Args:
    process_definition_key (str): System-generated key for a deployed process definition.
        Example: 2251799813686749.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetProcessDefinitionResponse200 | GetProcessDefinitionResponse400 | GetProcessDefinitionResponse401 | GetProcessDefinitionResponse403 | GetProcessDefinitionResponse404 | GetProcessDefinitionResponse500]"""
    response = sync_detailed(process_definition_key=process_definition_key, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(process_definition_key: str, *, client: AuthenticatedClient | Client) -> Response[GetProcessDefinitionResponse200 | GetProcessDefinitionResponse400 | GetProcessDefinitionResponse401 | GetProcessDefinitionResponse403 | GetProcessDefinitionResponse404 | GetProcessDefinitionResponse500]:
    """Get process definition

     Returns process definition as JSON.

    Args:
        process_definition_key (str): System-generated key for a deployed process definition.
            Example: 2251799813686749.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetProcessDefinitionResponse200 | GetProcessDefinitionResponse400 | GetProcessDefinitionResponse401 | GetProcessDefinitionResponse403 | GetProcessDefinitionResponse404 | GetProcessDefinitionResponse500]
    """
    kwargs = _get_kwargs(process_definition_key=process_definition_key)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(process_definition_key: str, *, client: AuthenticatedClient | Client, **kwargs) -> GetProcessDefinitionResponse200:
    """Get process definition

 Returns process definition as JSON.

Args:
    process_definition_key (str): System-generated key for a deployed process definition.
        Example: 2251799813686749.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetProcessDefinitionResponse200 | GetProcessDefinitionResponse400 | GetProcessDefinitionResponse401 | GetProcessDefinitionResponse403 | GetProcessDefinitionResponse404 | GetProcessDefinitionResponse500]"""
    response = await asyncio_detailed(process_definition_key=process_definition_key, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
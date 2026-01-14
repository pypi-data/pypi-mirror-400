from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_variable_response_200 import GetVariableResponse200
from ...models.get_variable_response_400 import GetVariableResponse400
from ...models.get_variable_response_401 import GetVariableResponse401
from ...models.get_variable_response_403 import GetVariableResponse403
from ...models.get_variable_response_404 import GetVariableResponse404
from ...models.get_variable_response_500 import GetVariableResponse500
from ...types import Response

def _get_kwargs(variable_key: str) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {'method': 'get', 'url': '/variables/{variable_key}'.format(variable_key=variable_key)}
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetVariableResponse200 | GetVariableResponse400 | GetVariableResponse401 | GetVariableResponse403 | GetVariableResponse404 | GetVariableResponse500 | None:
    if response.status_code == 200:
        response_200 = GetVariableResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = GetVariableResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = GetVariableResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = GetVariableResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = GetVariableResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = GetVariableResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GetVariableResponse200 | GetVariableResponse400 | GetVariableResponse401 | GetVariableResponse403 | GetVariableResponse404 | GetVariableResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(variable_key: str, *, client: AuthenticatedClient | Client) -> Response[GetVariableResponse200 | GetVariableResponse400 | GetVariableResponse401 | GetVariableResponse403 | GetVariableResponse404 | GetVariableResponse500]:
    """Get variable

     Get the variable by the variable key.

    Args:
        variable_key (str): System-generated key for a variable. Example: 2251799813683287.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetVariableResponse200 | GetVariableResponse400 | GetVariableResponse401 | GetVariableResponse403 | GetVariableResponse404 | GetVariableResponse500]
    """
    kwargs = _get_kwargs(variable_key=variable_key)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(variable_key: str, *, client: AuthenticatedClient | Client, **kwargs) -> GetVariableResponse200:
    """Get variable

 Get the variable by the variable key.

Args:
    variable_key (str): System-generated key for a variable. Example: 2251799813683287.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetVariableResponse200 | GetVariableResponse400 | GetVariableResponse401 | GetVariableResponse403 | GetVariableResponse404 | GetVariableResponse500]"""
    response = sync_detailed(variable_key=variable_key, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(variable_key: str, *, client: AuthenticatedClient | Client) -> Response[GetVariableResponse200 | GetVariableResponse400 | GetVariableResponse401 | GetVariableResponse403 | GetVariableResponse404 | GetVariableResponse500]:
    """Get variable

     Get the variable by the variable key.

    Args:
        variable_key (str): System-generated key for a variable. Example: 2251799813683287.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetVariableResponse200 | GetVariableResponse400 | GetVariableResponse401 | GetVariableResponse403 | GetVariableResponse404 | GetVariableResponse500]
    """
    kwargs = _get_kwargs(variable_key=variable_key)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(variable_key: str, *, client: AuthenticatedClient | Client, **kwargs) -> GetVariableResponse200:
    """Get variable

 Get the variable by the variable key.

Args:
    variable_key (str): System-generated key for a variable. Example: 2251799813683287.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetVariableResponse200 | GetVariableResponse400 | GetVariableResponse401 | GetVariableResponse403 | GetVariableResponse404 | GetVariableResponse500]"""
    response = await asyncio_detailed(variable_key=variable_key, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_element_instance_response_200 import GetElementInstanceResponse200
from ...models.get_element_instance_response_400 import GetElementInstanceResponse400
from ...models.get_element_instance_response_401 import GetElementInstanceResponse401
from ...models.get_element_instance_response_403 import GetElementInstanceResponse403
from ...models.get_element_instance_response_404 import GetElementInstanceResponse404
from ...models.get_element_instance_response_500 import GetElementInstanceResponse500
from ...types import Response

def _get_kwargs(element_instance_key: str) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {'method': 'get', 'url': '/element-instances/{element_instance_key}'.format(element_instance_key=element_instance_key)}
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetElementInstanceResponse200 | GetElementInstanceResponse400 | GetElementInstanceResponse401 | GetElementInstanceResponse403 | GetElementInstanceResponse404 | GetElementInstanceResponse500 | None:
    if response.status_code == 200:
        response_200 = GetElementInstanceResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = GetElementInstanceResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = GetElementInstanceResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = GetElementInstanceResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = GetElementInstanceResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = GetElementInstanceResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GetElementInstanceResponse200 | GetElementInstanceResponse400 | GetElementInstanceResponse401 | GetElementInstanceResponse403 | GetElementInstanceResponse404 | GetElementInstanceResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(element_instance_key: str, *, client: AuthenticatedClient | Client) -> Response[GetElementInstanceResponse200 | GetElementInstanceResponse400 | GetElementInstanceResponse401 | GetElementInstanceResponse403 | GetElementInstanceResponse404 | GetElementInstanceResponse500]:
    """Get element instance

     Returns element instance as JSON.

    Args:
        element_instance_key (str): System-generated key for a element instance. Example:
            2251799813686789.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetElementInstanceResponse200 | GetElementInstanceResponse400 | GetElementInstanceResponse401 | GetElementInstanceResponse403 | GetElementInstanceResponse404 | GetElementInstanceResponse500]
    """
    kwargs = _get_kwargs(element_instance_key=element_instance_key)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(element_instance_key: str, *, client: AuthenticatedClient | Client, **kwargs) -> GetElementInstanceResponse200:
    """Get element instance

 Returns element instance as JSON.

Args:
    element_instance_key (str): System-generated key for a element instance. Example:
        2251799813686789.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetElementInstanceResponse200 | GetElementInstanceResponse400 | GetElementInstanceResponse401 | GetElementInstanceResponse403 | GetElementInstanceResponse404 | GetElementInstanceResponse500]"""
    response = sync_detailed(element_instance_key=element_instance_key, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(element_instance_key: str, *, client: AuthenticatedClient | Client) -> Response[GetElementInstanceResponse200 | GetElementInstanceResponse400 | GetElementInstanceResponse401 | GetElementInstanceResponse403 | GetElementInstanceResponse404 | GetElementInstanceResponse500]:
    """Get element instance

     Returns element instance as JSON.

    Args:
        element_instance_key (str): System-generated key for a element instance. Example:
            2251799813686789.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetElementInstanceResponse200 | GetElementInstanceResponse400 | GetElementInstanceResponse401 | GetElementInstanceResponse403 | GetElementInstanceResponse404 | GetElementInstanceResponse500]
    """
    kwargs = _get_kwargs(element_instance_key=element_instance_key)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(element_instance_key: str, *, client: AuthenticatedClient | Client, **kwargs) -> GetElementInstanceResponse200:
    """Get element instance

 Returns element instance as JSON.

Args:
    element_instance_key (str): System-generated key for a element instance. Example:
        2251799813686789.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetElementInstanceResponse200 | GetElementInstanceResponse400 | GetElementInstanceResponse401 | GetElementInstanceResponse403 | GetElementInstanceResponse404 | GetElementInstanceResponse500]"""
    response = await asyncio_detailed(element_instance_key=element_instance_key, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
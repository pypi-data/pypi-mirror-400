from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_authorization_response_200 import GetAuthorizationResponse200
from ...models.get_authorization_response_401 import GetAuthorizationResponse401
from ...models.get_authorization_response_403 import GetAuthorizationResponse403
from ...models.get_authorization_response_404 import GetAuthorizationResponse404
from ...models.get_authorization_response_500 import GetAuthorizationResponse500
from ...types import Response

def _get_kwargs(authorization_key: str) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {'method': 'get', 'url': '/authorizations/{authorization_key}'.format(authorization_key=authorization_key)}
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetAuthorizationResponse200 | GetAuthorizationResponse401 | GetAuthorizationResponse403 | GetAuthorizationResponse404 | GetAuthorizationResponse500 | None:
    if response.status_code == 200:
        response_200 = GetAuthorizationResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 401:
        response_401 = GetAuthorizationResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = GetAuthorizationResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = GetAuthorizationResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = GetAuthorizationResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GetAuthorizationResponse200 | GetAuthorizationResponse401 | GetAuthorizationResponse403 | GetAuthorizationResponse404 | GetAuthorizationResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(authorization_key: str, *, client: AuthenticatedClient | Client) -> Response[GetAuthorizationResponse200 | GetAuthorizationResponse401 | GetAuthorizationResponse403 | GetAuthorizationResponse404 | GetAuthorizationResponse500]:
    """Get authorization

     Get authorization by the given key.

    Args:
        authorization_key (str): System-generated key for an authorization. Example:
            2251799813684332.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetAuthorizationResponse200 | GetAuthorizationResponse401 | GetAuthorizationResponse403 | GetAuthorizationResponse404 | GetAuthorizationResponse500]
    """
    kwargs = _get_kwargs(authorization_key=authorization_key)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(authorization_key: str, *, client: AuthenticatedClient | Client, **kwargs) -> GetAuthorizationResponse200:
    """Get authorization

 Get authorization by the given key.

Args:
    authorization_key (str): System-generated key for an authorization. Example:
        2251799813684332.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetAuthorizationResponse200 | GetAuthorizationResponse401 | GetAuthorizationResponse403 | GetAuthorizationResponse404 | GetAuthorizationResponse500]"""
    response = sync_detailed(authorization_key=authorization_key, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(authorization_key: str, *, client: AuthenticatedClient | Client) -> Response[GetAuthorizationResponse200 | GetAuthorizationResponse401 | GetAuthorizationResponse403 | GetAuthorizationResponse404 | GetAuthorizationResponse500]:
    """Get authorization

     Get authorization by the given key.

    Args:
        authorization_key (str): System-generated key for an authorization. Example:
            2251799813684332.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetAuthorizationResponse200 | GetAuthorizationResponse401 | GetAuthorizationResponse403 | GetAuthorizationResponse404 | GetAuthorizationResponse500]
    """
    kwargs = _get_kwargs(authorization_key=authorization_key)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(authorization_key: str, *, client: AuthenticatedClient | Client, **kwargs) -> GetAuthorizationResponse200:
    """Get authorization

 Get authorization by the given key.

Args:
    authorization_key (str): System-generated key for an authorization. Example:
        2251799813684332.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetAuthorizationResponse200 | GetAuthorizationResponse401 | GetAuthorizationResponse403 | GetAuthorizationResponse404 | GetAuthorizationResponse500]"""
    response = await asyncio_detailed(authorization_key=authorization_key, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.search_authorizations_data import SearchAuthorizationsData
from ...models.search_authorizations_response_200 import SearchAuthorizationsResponse200
from ...models.search_authorizations_response_400 import SearchAuthorizationsResponse400
from ...models.search_authorizations_response_401 import SearchAuthorizationsResponse401
from ...models.search_authorizations_response_403 import SearchAuthorizationsResponse403
from ...models.search_authorizations_response_500 import SearchAuthorizationsResponse500
from ...types import Response

def _get_kwargs(*, body: SearchAuthorizationsData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/authorizations/search'}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> SearchAuthorizationsResponse200 | SearchAuthorizationsResponse400 | SearchAuthorizationsResponse401 | SearchAuthorizationsResponse403 | SearchAuthorizationsResponse500 | None:
    if response.status_code == 200:
        response_200 = SearchAuthorizationsResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = SearchAuthorizationsResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = SearchAuthorizationsResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = SearchAuthorizationsResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 500:
        response_500 = SearchAuthorizationsResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[SearchAuthorizationsResponse200 | SearchAuthorizationsResponse400 | SearchAuthorizationsResponse401 | SearchAuthorizationsResponse403 | SearchAuthorizationsResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(*, client: AuthenticatedClient | Client, body: SearchAuthorizationsData) -> Response[SearchAuthorizationsResponse200 | SearchAuthorizationsResponse400 | SearchAuthorizationsResponse401 | SearchAuthorizationsResponse403 | SearchAuthorizationsResponse500]:
    """Search authorizations

     Search for authorizations based on given criteria.

    Args:
        body (SearchAuthorizationsData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchAuthorizationsResponse200 | SearchAuthorizationsResponse400 | SearchAuthorizationsResponse401 | SearchAuthorizationsResponse403 | SearchAuthorizationsResponse500]
    """
    kwargs = _get_kwargs(body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(*, client: AuthenticatedClient | Client, body: SearchAuthorizationsData, **kwargs) -> SearchAuthorizationsResponse200:
    """Search authorizations

 Search for authorizations based on given criteria.

Args:
    body (SearchAuthorizationsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchAuthorizationsResponse200 | SearchAuthorizationsResponse400 | SearchAuthorizationsResponse401 | SearchAuthorizationsResponse403 | SearchAuthorizationsResponse500]"""
    response = sync_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(*, client: AuthenticatedClient | Client, body: SearchAuthorizationsData) -> Response[SearchAuthorizationsResponse200 | SearchAuthorizationsResponse400 | SearchAuthorizationsResponse401 | SearchAuthorizationsResponse403 | SearchAuthorizationsResponse500]:
    """Search authorizations

     Search for authorizations based on given criteria.

    Args:
        body (SearchAuthorizationsData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchAuthorizationsResponse200 | SearchAuthorizationsResponse400 | SearchAuthorizationsResponse401 | SearchAuthorizationsResponse403 | SearchAuthorizationsResponse500]
    """
    kwargs = _get_kwargs(body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(*, client: AuthenticatedClient | Client, body: SearchAuthorizationsData, **kwargs) -> SearchAuthorizationsResponse200:
    """Search authorizations

 Search for authorizations based on given criteria.

Args:
    body (SearchAuthorizationsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchAuthorizationsResponse200 | SearchAuthorizationsResponse400 | SearchAuthorizationsResponse401 | SearchAuthorizationsResponse403 | SearchAuthorizationsResponse500]"""
    response = await asyncio_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
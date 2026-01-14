from http import HTTPStatus
from typing import Any, cast
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.search_roles_data import SearchRolesData
from ...models.search_roles_response_200 import SearchRolesResponse200
from ...models.search_roles_response_400 import SearchRolesResponse400
from ...models.search_roles_response_401 import SearchRolesResponse401
from ...models.search_roles_response_403 import SearchRolesResponse403
from ...types import Response

def _get_kwargs(*, body: SearchRolesData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/roles/search'}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | SearchRolesResponse200 | SearchRolesResponse400 | SearchRolesResponse401 | SearchRolesResponse403 | None:
    if response.status_code == 200:
        response_200 = SearchRolesResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = SearchRolesResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = SearchRolesResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = SearchRolesResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 500:
        response_500 = cast(Any, None)
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | SearchRolesResponse200 | SearchRolesResponse400 | SearchRolesResponse401 | SearchRolesResponse403]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(*, client: AuthenticatedClient | Client, body: SearchRolesData) -> Response[Any | SearchRolesResponse200 | SearchRolesResponse400 | SearchRolesResponse401 | SearchRolesResponse403]:
    """Search roles

     Search for roles based on given criteria.

    Args:
        body (SearchRolesData): Role search request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | SearchRolesResponse200 | SearchRolesResponse400 | SearchRolesResponse401 | SearchRolesResponse403]
    """
    kwargs = _get_kwargs(body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(*, client: AuthenticatedClient | Client, body: SearchRolesData, **kwargs) -> Any:
    """Search roles

 Search for roles based on given criteria.

Args:
    body (SearchRolesData): Role search request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | SearchRolesResponse200 | SearchRolesResponse400 | SearchRolesResponse401 | SearchRolesResponse403]"""
    response = sync_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(*, client: AuthenticatedClient | Client, body: SearchRolesData) -> Response[Any | SearchRolesResponse200 | SearchRolesResponse400 | SearchRolesResponse401 | SearchRolesResponse403]:
    """Search roles

     Search for roles based on given criteria.

    Args:
        body (SearchRolesData): Role search request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | SearchRolesResponse200 | SearchRolesResponse400 | SearchRolesResponse401 | SearchRolesResponse403]
    """
    kwargs = _get_kwargs(body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(*, client: AuthenticatedClient | Client, body: SearchRolesData, **kwargs) -> Any:
    """Search roles

 Search for roles based on given criteria.

Args:
    body (SearchRolesData): Role search request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | SearchRolesResponse200 | SearchRolesResponse400 | SearchRolesResponse401 | SearchRolesResponse403]"""
    response = await asyncio_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
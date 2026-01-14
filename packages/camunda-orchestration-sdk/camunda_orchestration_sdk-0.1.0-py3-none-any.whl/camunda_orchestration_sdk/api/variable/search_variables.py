from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.search_variables_data import SearchVariablesData
from ...models.search_variables_response_200 import SearchVariablesResponse200
from ...models.search_variables_response_400 import SearchVariablesResponse400
from ...models.search_variables_response_401 import SearchVariablesResponse401
from ...models.search_variables_response_403 import SearchVariablesResponse403
from ...models.search_variables_response_500 import SearchVariablesResponse500
from ...types import UNSET, Response, Unset

def _get_kwargs(*, body: SearchVariablesData, truncate_values: bool | Unset=UNSET) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    params: dict[str, Any] = {}
    params['truncateValues'] = truncate_values
    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/variables/search', 'params': params}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> SearchVariablesResponse200 | SearchVariablesResponse400 | SearchVariablesResponse401 | SearchVariablesResponse403 | SearchVariablesResponse500 | None:
    if response.status_code == 200:
        response_200 = SearchVariablesResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = SearchVariablesResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = SearchVariablesResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = SearchVariablesResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 500:
        response_500 = SearchVariablesResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[SearchVariablesResponse200 | SearchVariablesResponse400 | SearchVariablesResponse401 | SearchVariablesResponse403 | SearchVariablesResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(*, client: AuthenticatedClient | Client, body: SearchVariablesData, truncate_values: bool | Unset=UNSET) -> Response[SearchVariablesResponse200 | SearchVariablesResponse400 | SearchVariablesResponse401 | SearchVariablesResponse403 | SearchVariablesResponse500]:
    """Search variables

     Search for process and local variables based on given criteria. By default, long variable values in
    the response are truncated.

    Args:
        truncate_values (bool | Unset):
        body (SearchVariablesData): Variable search query request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchVariablesResponse200 | SearchVariablesResponse400 | SearchVariablesResponse401 | SearchVariablesResponse403 | SearchVariablesResponse500]
    """
    kwargs = _get_kwargs(body=body, truncate_values=truncate_values)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(*, client: AuthenticatedClient | Client, body: SearchVariablesData, truncate_values: bool | Unset=UNSET, **kwargs) -> SearchVariablesResponse200:
    """Search variables

 Search for process and local variables based on given criteria. By default, long variable values in
the response are truncated.

Args:
    truncate_values (bool | Unset):
    body (SearchVariablesData): Variable search query request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchVariablesResponse200 | SearchVariablesResponse400 | SearchVariablesResponse401 | SearchVariablesResponse403 | SearchVariablesResponse500]"""
    response = sync_detailed(client=client, body=body, truncate_values=truncate_values)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(*, client: AuthenticatedClient | Client, body: SearchVariablesData, truncate_values: bool | Unset=UNSET) -> Response[SearchVariablesResponse200 | SearchVariablesResponse400 | SearchVariablesResponse401 | SearchVariablesResponse403 | SearchVariablesResponse500]:
    """Search variables

     Search for process and local variables based on given criteria. By default, long variable values in
    the response are truncated.

    Args:
        truncate_values (bool | Unset):
        body (SearchVariablesData): Variable search query request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchVariablesResponse200 | SearchVariablesResponse400 | SearchVariablesResponse401 | SearchVariablesResponse403 | SearchVariablesResponse500]
    """
    kwargs = _get_kwargs(body=body, truncate_values=truncate_values)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(*, client: AuthenticatedClient | Client, body: SearchVariablesData, truncate_values: bool | Unset=UNSET, **kwargs) -> SearchVariablesResponse200:
    """Search variables

 Search for process and local variables based on given criteria. By default, long variable values in
the response are truncated.

Args:
    truncate_values (bool | Unset):
    body (SearchVariablesData): Variable search query request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchVariablesResponse200 | SearchVariablesResponse400 | SearchVariablesResponse401 | SearchVariablesResponse403 | SearchVariablesResponse500]"""
    response = await asyncio_detailed(client=client, body=body, truncate_values=truncate_values)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
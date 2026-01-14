from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.search_batch_operations_data import SearchBatchOperationsData
from ...models.search_batch_operations_response_200 import SearchBatchOperationsResponse200
from ...models.search_batch_operations_response_400 import SearchBatchOperationsResponse400
from ...models.search_batch_operations_response_500 import SearchBatchOperationsResponse500
from ...types import Response

def _get_kwargs(*, body: SearchBatchOperationsData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/batch-operations/search'}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> SearchBatchOperationsResponse200 | SearchBatchOperationsResponse400 | SearchBatchOperationsResponse500 | None:
    if response.status_code == 200:
        response_200 = SearchBatchOperationsResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = SearchBatchOperationsResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 500:
        response_500 = SearchBatchOperationsResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[SearchBatchOperationsResponse200 | SearchBatchOperationsResponse400 | SearchBatchOperationsResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(*, client: AuthenticatedClient | Client, body: SearchBatchOperationsData) -> Response[SearchBatchOperationsResponse200 | SearchBatchOperationsResponse400 | SearchBatchOperationsResponse500]:
    """Search batch operations

     Search for batch operations based on given criteria.

    Args:
        body (SearchBatchOperationsData): Batch operation search request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchBatchOperationsResponse200 | SearchBatchOperationsResponse400 | SearchBatchOperationsResponse500]
    """
    kwargs = _get_kwargs(body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(*, client: AuthenticatedClient | Client, body: SearchBatchOperationsData, **kwargs) -> SearchBatchOperationsResponse200:
    """Search batch operations

 Search for batch operations based on given criteria.

Args:
    body (SearchBatchOperationsData): Batch operation search request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchBatchOperationsResponse200 | SearchBatchOperationsResponse400 | SearchBatchOperationsResponse500]"""
    response = sync_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(*, client: AuthenticatedClient | Client, body: SearchBatchOperationsData) -> Response[SearchBatchOperationsResponse200 | SearchBatchOperationsResponse400 | SearchBatchOperationsResponse500]:
    """Search batch operations

     Search for batch operations based on given criteria.

    Args:
        body (SearchBatchOperationsData): Batch operation search request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchBatchOperationsResponse200 | SearchBatchOperationsResponse400 | SearchBatchOperationsResponse500]
    """
    kwargs = _get_kwargs(body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(*, client: AuthenticatedClient | Client, body: SearchBatchOperationsData, **kwargs) -> SearchBatchOperationsResponse200:
    """Search batch operations

 Search for batch operations based on given criteria.

Args:
    body (SearchBatchOperationsData): Batch operation search request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchBatchOperationsResponse200 | SearchBatchOperationsResponse400 | SearchBatchOperationsResponse500]"""
    response = await asyncio_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
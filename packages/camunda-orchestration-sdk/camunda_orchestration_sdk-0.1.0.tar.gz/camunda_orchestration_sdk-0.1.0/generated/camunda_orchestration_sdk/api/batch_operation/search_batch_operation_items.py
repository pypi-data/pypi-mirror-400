from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.search_batch_operation_items_data import SearchBatchOperationItemsData
from ...models.search_batch_operation_items_response_200 import SearchBatchOperationItemsResponse200
from ...models.search_batch_operation_items_response_400 import SearchBatchOperationItemsResponse400
from ...models.search_batch_operation_items_response_500 import SearchBatchOperationItemsResponse500
from ...types import Response

def _get_kwargs(*, body: SearchBatchOperationItemsData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/batch-operation-items/search'}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> SearchBatchOperationItemsResponse200 | SearchBatchOperationItemsResponse400 | SearchBatchOperationItemsResponse500 | None:
    if response.status_code == 200:
        response_200 = SearchBatchOperationItemsResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = SearchBatchOperationItemsResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 500:
        response_500 = SearchBatchOperationItemsResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[SearchBatchOperationItemsResponse200 | SearchBatchOperationItemsResponse400 | SearchBatchOperationItemsResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(*, client: AuthenticatedClient | Client, body: SearchBatchOperationItemsData) -> Response[SearchBatchOperationItemsResponse200 | SearchBatchOperationItemsResponse400 | SearchBatchOperationItemsResponse500]:
    """Search batch operation items

     Search for batch operation items based on given criteria.

    Args:
        body (SearchBatchOperationItemsData): Batch operation item search request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchBatchOperationItemsResponse200 | SearchBatchOperationItemsResponse400 | SearchBatchOperationItemsResponse500]
    """
    kwargs = _get_kwargs(body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(*, client: AuthenticatedClient | Client, body: SearchBatchOperationItemsData, **kwargs) -> SearchBatchOperationItemsResponse200:
    """Search batch operation items

 Search for batch operation items based on given criteria.

Args:
    body (SearchBatchOperationItemsData): Batch operation item search request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchBatchOperationItemsResponse200 | SearchBatchOperationItemsResponse400 | SearchBatchOperationItemsResponse500]"""
    response = sync_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(*, client: AuthenticatedClient | Client, body: SearchBatchOperationItemsData) -> Response[SearchBatchOperationItemsResponse200 | SearchBatchOperationItemsResponse400 | SearchBatchOperationItemsResponse500]:
    """Search batch operation items

     Search for batch operation items based on given criteria.

    Args:
        body (SearchBatchOperationItemsData): Batch operation item search request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchBatchOperationItemsResponse200 | SearchBatchOperationItemsResponse400 | SearchBatchOperationItemsResponse500]
    """
    kwargs = _get_kwargs(body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(*, client: AuthenticatedClient | Client, body: SearchBatchOperationItemsData, **kwargs) -> SearchBatchOperationItemsResponse200:
    """Search batch operation items

 Search for batch operation items based on given criteria.

Args:
    body (SearchBatchOperationItemsData): Batch operation item search request.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchBatchOperationItemsResponse200 | SearchBatchOperationItemsResponse400 | SearchBatchOperationItemsResponse500]"""
    response = await asyncio_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_batch_operation_response_200 import GetBatchOperationResponse200
from ...models.get_batch_operation_response_400 import GetBatchOperationResponse400
from ...models.get_batch_operation_response_404 import GetBatchOperationResponse404
from ...models.get_batch_operation_response_500 import GetBatchOperationResponse500
from ...types import Response

def _get_kwargs(batch_operation_key: str) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {'method': 'get', 'url': '/batch-operations/{batch_operation_key}'.format(batch_operation_key=batch_operation_key)}
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetBatchOperationResponse200 | GetBatchOperationResponse400 | GetBatchOperationResponse404 | GetBatchOperationResponse500 | None:
    if response.status_code == 200:
        response_200 = GetBatchOperationResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = GetBatchOperationResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 404:
        response_404 = GetBatchOperationResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = GetBatchOperationResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GetBatchOperationResponse200 | GetBatchOperationResponse400 | GetBatchOperationResponse404 | GetBatchOperationResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(batch_operation_key: str, *, client: AuthenticatedClient | Client) -> Response[GetBatchOperationResponse200 | GetBatchOperationResponse400 | GetBatchOperationResponse404 | GetBatchOperationResponse500]:
    """Get batch operation

     Get batch operation by key.

    Args:
        batch_operation_key (str): System-generated key for an batch operation. Example:
            2251799813684321.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetBatchOperationResponse200 | GetBatchOperationResponse400 | GetBatchOperationResponse404 | GetBatchOperationResponse500]
    """
    kwargs = _get_kwargs(batch_operation_key=batch_operation_key)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(batch_operation_key: str, *, client: AuthenticatedClient | Client, **kwargs) -> GetBatchOperationResponse200:
    """Get batch operation

 Get batch operation by key.

Args:
    batch_operation_key (str): System-generated key for an batch operation. Example:
        2251799813684321.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetBatchOperationResponse200 | GetBatchOperationResponse400 | GetBatchOperationResponse404 | GetBatchOperationResponse500]"""
    response = sync_detailed(batch_operation_key=batch_operation_key, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(batch_operation_key: str, *, client: AuthenticatedClient | Client) -> Response[GetBatchOperationResponse200 | GetBatchOperationResponse400 | GetBatchOperationResponse404 | GetBatchOperationResponse500]:
    """Get batch operation

     Get batch operation by key.

    Args:
        batch_operation_key (str): System-generated key for an batch operation. Example:
            2251799813684321.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetBatchOperationResponse200 | GetBatchOperationResponse400 | GetBatchOperationResponse404 | GetBatchOperationResponse500]
    """
    kwargs = _get_kwargs(batch_operation_key=batch_operation_key)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(batch_operation_key: str, *, client: AuthenticatedClient | Client, **kwargs) -> GetBatchOperationResponse200:
    """Get batch operation

 Get batch operation by key.

Args:
    batch_operation_key (str): System-generated key for an batch operation. Example:
        2251799813684321.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetBatchOperationResponse200 | GetBatchOperationResponse400 | GetBatchOperationResponse404 | GetBatchOperationResponse500]"""
    response = await asyncio_detailed(batch_operation_key=batch_operation_key, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
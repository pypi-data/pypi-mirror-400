from http import HTTPStatus
from typing import Any, cast
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.resume_batch_operation_response_400 import ResumeBatchOperationResponse400
from ...models.resume_batch_operation_response_403 import ResumeBatchOperationResponse403
from ...models.resume_batch_operation_response_404 import ResumeBatchOperationResponse404
from ...models.resume_batch_operation_response_500 import ResumeBatchOperationResponse500
from ...models.resume_batch_operation_response_503 import ResumeBatchOperationResponse503
from ...types import Response

def _get_kwargs(batch_operation_key: str, *, body: Any) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/batch-operations/{batch_operation_key}/resumption'.format(batch_operation_key=batch_operation_key)}
    _kwargs['json'] = body
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | ResumeBatchOperationResponse400 | ResumeBatchOperationResponse403 | ResumeBatchOperationResponse404 | ResumeBatchOperationResponse500 | ResumeBatchOperationResponse503 | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 400:
        response_400 = ResumeBatchOperationResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 403:
        response_403 = ResumeBatchOperationResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = ResumeBatchOperationResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = ResumeBatchOperationResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = ResumeBatchOperationResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | ResumeBatchOperationResponse400 | ResumeBatchOperationResponse403 | ResumeBatchOperationResponse404 | ResumeBatchOperationResponse500 | ResumeBatchOperationResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(batch_operation_key: str, *, client: AuthenticatedClient | Client, body: Any) -> Response[Any | ResumeBatchOperationResponse400 | ResumeBatchOperationResponse403 | ResumeBatchOperationResponse404 | ResumeBatchOperationResponse500 | ResumeBatchOperationResponse503]:
    """Resume Batch operation

     Resumes a suspended batch operation.
    This is done asynchronously, the progress can be tracked using the batch operation status endpoint
    (/batch-operations/{batchOperationKey}).

    Args:
        batch_operation_key (str): System-generated key for an batch operation. Example:
            2251799813684321.
        body (Any):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ResumeBatchOperationResponse400 | ResumeBatchOperationResponse403 | ResumeBatchOperationResponse404 | ResumeBatchOperationResponse500 | ResumeBatchOperationResponse503]
    """
    kwargs = _get_kwargs(batch_operation_key=batch_operation_key, body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(batch_operation_key: str, *, client: AuthenticatedClient | Client, body: Any, **kwargs) -> Any:
    """Resume Batch operation

 Resumes a suspended batch operation.
This is done asynchronously, the progress can be tracked using the batch operation status endpoint
(/batch-operations/{batchOperationKey}).

Args:
    batch_operation_key (str): System-generated key for an batch operation. Example:
        2251799813684321.
    body (Any):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | ResumeBatchOperationResponse400 | ResumeBatchOperationResponse403 | ResumeBatchOperationResponse404 | ResumeBatchOperationResponse500 | ResumeBatchOperationResponse503]"""
    response = sync_detailed(batch_operation_key=batch_operation_key, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(batch_operation_key: str, *, client: AuthenticatedClient | Client, body: Any) -> Response[Any | ResumeBatchOperationResponse400 | ResumeBatchOperationResponse403 | ResumeBatchOperationResponse404 | ResumeBatchOperationResponse500 | ResumeBatchOperationResponse503]:
    """Resume Batch operation

     Resumes a suspended batch operation.
    This is done asynchronously, the progress can be tracked using the batch operation status endpoint
    (/batch-operations/{batchOperationKey}).

    Args:
        batch_operation_key (str): System-generated key for an batch operation. Example:
            2251799813684321.
        body (Any):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ResumeBatchOperationResponse400 | ResumeBatchOperationResponse403 | ResumeBatchOperationResponse404 | ResumeBatchOperationResponse500 | ResumeBatchOperationResponse503]
    """
    kwargs = _get_kwargs(batch_operation_key=batch_operation_key, body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(batch_operation_key: str, *, client: AuthenticatedClient | Client, body: Any, **kwargs) -> Any:
    """Resume Batch operation

 Resumes a suspended batch operation.
This is done asynchronously, the progress can be tracked using the batch operation status endpoint
(/batch-operations/{batchOperationKey}).

Args:
    batch_operation_key (str): System-generated key for an batch operation. Example:
        2251799813684321.
    body (Any):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | ResumeBatchOperationResponse400 | ResumeBatchOperationResponse403 | ResumeBatchOperationResponse404 | ResumeBatchOperationResponse500 | ResumeBatchOperationResponse503]"""
    response = await asyncio_detailed(batch_operation_key=batch_operation_key, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
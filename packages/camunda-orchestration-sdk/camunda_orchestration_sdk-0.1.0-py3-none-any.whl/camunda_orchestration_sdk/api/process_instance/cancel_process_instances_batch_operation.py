from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.cancel_process_instances_batch_operation_data import CancelProcessInstancesBatchOperationData
from ...models.cancel_process_instances_batch_operation_response_200 import CancelProcessInstancesBatchOperationResponse200
from ...models.cancel_process_instances_batch_operation_response_400 import CancelProcessInstancesBatchOperationResponse400
from ...models.cancel_process_instances_batch_operation_response_401 import CancelProcessInstancesBatchOperationResponse401
from ...models.cancel_process_instances_batch_operation_response_403 import CancelProcessInstancesBatchOperationResponse403
from ...models.cancel_process_instances_batch_operation_response_500 import CancelProcessInstancesBatchOperationResponse500
from ...types import Response

def _get_kwargs(*, body: CancelProcessInstancesBatchOperationData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/process-instances/cancellation'}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> CancelProcessInstancesBatchOperationResponse200 | CancelProcessInstancesBatchOperationResponse400 | CancelProcessInstancesBatchOperationResponse401 | CancelProcessInstancesBatchOperationResponse403 | CancelProcessInstancesBatchOperationResponse500 | None:
    if response.status_code == 200:
        response_200 = CancelProcessInstancesBatchOperationResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = CancelProcessInstancesBatchOperationResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = CancelProcessInstancesBatchOperationResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = CancelProcessInstancesBatchOperationResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 500:
        response_500 = CancelProcessInstancesBatchOperationResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[CancelProcessInstancesBatchOperationResponse200 | CancelProcessInstancesBatchOperationResponse400 | CancelProcessInstancesBatchOperationResponse401 | CancelProcessInstancesBatchOperationResponse403 | CancelProcessInstancesBatchOperationResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(*, client: AuthenticatedClient | Client, body: CancelProcessInstancesBatchOperationData) -> Response[CancelProcessInstancesBatchOperationResponse200 | CancelProcessInstancesBatchOperationResponse400 | CancelProcessInstancesBatchOperationResponse401 | CancelProcessInstancesBatchOperationResponse403 | CancelProcessInstancesBatchOperationResponse500]:
    """Cancel process instances (batch)

     Cancels multiple running process instances.
    Since only ACTIVE root instances can be cancelled, any given filters for state and
    parentProcessInstanceKey are ignored and overridden during this batch operation.
    This is done asynchronously, the progress can be tracked using the batchOperationKey from the
    response and the batch operation status endpoint (/batch-operations/{batchOperationKey}).

    Args:
        body (CancelProcessInstancesBatchOperationData): The process instance filter that defines
            which process instances should be canceled.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CancelProcessInstancesBatchOperationResponse200 | CancelProcessInstancesBatchOperationResponse400 | CancelProcessInstancesBatchOperationResponse401 | CancelProcessInstancesBatchOperationResponse403 | CancelProcessInstancesBatchOperationResponse500]
    """
    kwargs = _get_kwargs(body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(*, client: AuthenticatedClient | Client, body: CancelProcessInstancesBatchOperationData, **kwargs) -> CancelProcessInstancesBatchOperationResponse200:
    """Cancel process instances (batch)

 Cancels multiple running process instances.
Since only ACTIVE root instances can be cancelled, any given filters for state and
parentProcessInstanceKey are ignored and overridden during this batch operation.
This is done asynchronously, the progress can be tracked using the batchOperationKey from the
response and the batch operation status endpoint (/batch-operations/{batchOperationKey}).

Args:
    body (CancelProcessInstancesBatchOperationData): The process instance filter that defines
        which process instances should be canceled.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CancelProcessInstancesBatchOperationResponse200 | CancelProcessInstancesBatchOperationResponse400 | CancelProcessInstancesBatchOperationResponse401 | CancelProcessInstancesBatchOperationResponse403 | CancelProcessInstancesBatchOperationResponse500]"""
    response = sync_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(*, client: AuthenticatedClient | Client, body: CancelProcessInstancesBatchOperationData) -> Response[CancelProcessInstancesBatchOperationResponse200 | CancelProcessInstancesBatchOperationResponse400 | CancelProcessInstancesBatchOperationResponse401 | CancelProcessInstancesBatchOperationResponse403 | CancelProcessInstancesBatchOperationResponse500]:
    """Cancel process instances (batch)

     Cancels multiple running process instances.
    Since only ACTIVE root instances can be cancelled, any given filters for state and
    parentProcessInstanceKey are ignored and overridden during this batch operation.
    This is done asynchronously, the progress can be tracked using the batchOperationKey from the
    response and the batch operation status endpoint (/batch-operations/{batchOperationKey}).

    Args:
        body (CancelProcessInstancesBatchOperationData): The process instance filter that defines
            which process instances should be canceled.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CancelProcessInstancesBatchOperationResponse200 | CancelProcessInstancesBatchOperationResponse400 | CancelProcessInstancesBatchOperationResponse401 | CancelProcessInstancesBatchOperationResponse403 | CancelProcessInstancesBatchOperationResponse500]
    """
    kwargs = _get_kwargs(body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(*, client: AuthenticatedClient | Client, body: CancelProcessInstancesBatchOperationData, **kwargs) -> CancelProcessInstancesBatchOperationResponse200:
    """Cancel process instances (batch)

 Cancels multiple running process instances.
Since only ACTIVE root instances can be cancelled, any given filters for state and
parentProcessInstanceKey are ignored and overridden during this batch operation.
This is done asynchronously, the progress can be tracked using the batchOperationKey from the
response and the batch operation status endpoint (/batch-operations/{batchOperationKey}).

Args:
    body (CancelProcessInstancesBatchOperationData): The process instance filter that defines
        which process instances should be canceled.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CancelProcessInstancesBatchOperationResponse200 | CancelProcessInstancesBatchOperationResponse400 | CancelProcessInstancesBatchOperationResponse401 | CancelProcessInstancesBatchOperationResponse403 | CancelProcessInstancesBatchOperationResponse500]"""
    response = await asyncio_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
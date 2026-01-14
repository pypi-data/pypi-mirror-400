from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.delete_process_instances_batch_operation_data import DeleteProcessInstancesBatchOperationData
from ...models.delete_process_instances_batch_operation_response_200 import DeleteProcessInstancesBatchOperationResponse200
from ...models.delete_process_instances_batch_operation_response_400 import DeleteProcessInstancesBatchOperationResponse400
from ...models.delete_process_instances_batch_operation_response_401 import DeleteProcessInstancesBatchOperationResponse401
from ...models.delete_process_instances_batch_operation_response_403 import DeleteProcessInstancesBatchOperationResponse403
from ...models.delete_process_instances_batch_operation_response_500 import DeleteProcessInstancesBatchOperationResponse500
from ...types import Response

def _get_kwargs(*, body: DeleteProcessInstancesBatchOperationData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/process-instances/deletion'}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> DeleteProcessInstancesBatchOperationResponse200 | DeleteProcessInstancesBatchOperationResponse400 | DeleteProcessInstancesBatchOperationResponse401 | DeleteProcessInstancesBatchOperationResponse403 | DeleteProcessInstancesBatchOperationResponse500 | None:
    if response.status_code == 200:
        response_200 = DeleteProcessInstancesBatchOperationResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = DeleteProcessInstancesBatchOperationResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = DeleteProcessInstancesBatchOperationResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = DeleteProcessInstancesBatchOperationResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 500:
        response_500 = DeleteProcessInstancesBatchOperationResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[DeleteProcessInstancesBatchOperationResponse200 | DeleteProcessInstancesBatchOperationResponse400 | DeleteProcessInstancesBatchOperationResponse401 | DeleteProcessInstancesBatchOperationResponse403 | DeleteProcessInstancesBatchOperationResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(*, client: AuthenticatedClient | Client, body: DeleteProcessInstancesBatchOperationData) -> Response[DeleteProcessInstancesBatchOperationResponse200 | DeleteProcessInstancesBatchOperationResponse400 | DeleteProcessInstancesBatchOperationResponse401 | DeleteProcessInstancesBatchOperationResponse403 | DeleteProcessInstancesBatchOperationResponse500]:
    """Delete process instances (batch)

     Delete multiple process instances. This will delete the historic data from secondary storage.
    Only process instances in a final state (COMPLETED or TERMINATED) can be deleted.
    This is done asynchronously, the progress can be tracked using the batchOperationKey from the
    response and the batch operation status endpoint (/batch-operations/{batchOperationKey}).

    Args:
        body (DeleteProcessInstancesBatchOperationData): The process instance filter that defines
            which process instances should be deleted.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeleteProcessInstancesBatchOperationResponse200 | DeleteProcessInstancesBatchOperationResponse400 | DeleteProcessInstancesBatchOperationResponse401 | DeleteProcessInstancesBatchOperationResponse403 | DeleteProcessInstancesBatchOperationResponse500]
    """
    kwargs = _get_kwargs(body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(*, client: AuthenticatedClient | Client, body: DeleteProcessInstancesBatchOperationData, **kwargs) -> DeleteProcessInstancesBatchOperationResponse200:
    """Delete process instances (batch)

 Delete multiple process instances. This will delete the historic data from secondary storage.
Only process instances in a final state (COMPLETED or TERMINATED) can be deleted.
This is done asynchronously, the progress can be tracked using the batchOperationKey from the
response and the batch operation status endpoint (/batch-operations/{batchOperationKey}).

Args:
    body (DeleteProcessInstancesBatchOperationData): The process instance filter that defines
        which process instances should be deleted.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[DeleteProcessInstancesBatchOperationResponse200 | DeleteProcessInstancesBatchOperationResponse400 | DeleteProcessInstancesBatchOperationResponse401 | DeleteProcessInstancesBatchOperationResponse403 | DeleteProcessInstancesBatchOperationResponse500]"""
    response = sync_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(*, client: AuthenticatedClient | Client, body: DeleteProcessInstancesBatchOperationData) -> Response[DeleteProcessInstancesBatchOperationResponse200 | DeleteProcessInstancesBatchOperationResponse400 | DeleteProcessInstancesBatchOperationResponse401 | DeleteProcessInstancesBatchOperationResponse403 | DeleteProcessInstancesBatchOperationResponse500]:
    """Delete process instances (batch)

     Delete multiple process instances. This will delete the historic data from secondary storage.
    Only process instances in a final state (COMPLETED or TERMINATED) can be deleted.
    This is done asynchronously, the progress can be tracked using the batchOperationKey from the
    response and the batch operation status endpoint (/batch-operations/{batchOperationKey}).

    Args:
        body (DeleteProcessInstancesBatchOperationData): The process instance filter that defines
            which process instances should be deleted.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeleteProcessInstancesBatchOperationResponse200 | DeleteProcessInstancesBatchOperationResponse400 | DeleteProcessInstancesBatchOperationResponse401 | DeleteProcessInstancesBatchOperationResponse403 | DeleteProcessInstancesBatchOperationResponse500]
    """
    kwargs = _get_kwargs(body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(*, client: AuthenticatedClient | Client, body: DeleteProcessInstancesBatchOperationData, **kwargs) -> DeleteProcessInstancesBatchOperationResponse200:
    """Delete process instances (batch)

 Delete multiple process instances. This will delete the historic data from secondary storage.
Only process instances in a final state (COMPLETED or TERMINATED) can be deleted.
This is done asynchronously, the progress can be tracked using the batchOperationKey from the
response and the batch operation status endpoint (/batch-operations/{batchOperationKey}).

Args:
    body (DeleteProcessInstancesBatchOperationData): The process instance filter that defines
        which process instances should be deleted.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[DeleteProcessInstancesBatchOperationResponse200 | DeleteProcessInstancesBatchOperationResponse400 | DeleteProcessInstancesBatchOperationResponse401 | DeleteProcessInstancesBatchOperationResponse403 | DeleteProcessInstancesBatchOperationResponse500]"""
    response = await asyncio_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
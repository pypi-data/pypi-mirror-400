from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.modify_process_instances_batch_operation_data import ModifyProcessInstancesBatchOperationData
from ...models.modify_process_instances_batch_operation_response_200 import ModifyProcessInstancesBatchOperationResponse200
from ...models.modify_process_instances_batch_operation_response_400 import ModifyProcessInstancesBatchOperationResponse400
from ...models.modify_process_instances_batch_operation_response_401 import ModifyProcessInstancesBatchOperationResponse401
from ...models.modify_process_instances_batch_operation_response_403 import ModifyProcessInstancesBatchOperationResponse403
from ...models.modify_process_instances_batch_operation_response_500 import ModifyProcessInstancesBatchOperationResponse500
from ...types import Response

def _get_kwargs(*, body: ModifyProcessInstancesBatchOperationData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/process-instances/modification'}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ModifyProcessInstancesBatchOperationResponse200 | ModifyProcessInstancesBatchOperationResponse400 | ModifyProcessInstancesBatchOperationResponse401 | ModifyProcessInstancesBatchOperationResponse403 | ModifyProcessInstancesBatchOperationResponse500 | None:
    if response.status_code == 200:
        response_200 = ModifyProcessInstancesBatchOperationResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = ModifyProcessInstancesBatchOperationResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = ModifyProcessInstancesBatchOperationResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = ModifyProcessInstancesBatchOperationResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 500:
        response_500 = ModifyProcessInstancesBatchOperationResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[ModifyProcessInstancesBatchOperationResponse200 | ModifyProcessInstancesBatchOperationResponse400 | ModifyProcessInstancesBatchOperationResponse401 | ModifyProcessInstancesBatchOperationResponse403 | ModifyProcessInstancesBatchOperationResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(*, client: AuthenticatedClient | Client, body: ModifyProcessInstancesBatchOperationData) -> Response[ModifyProcessInstancesBatchOperationResponse200 | ModifyProcessInstancesBatchOperationResponse400 | ModifyProcessInstancesBatchOperationResponse401 | ModifyProcessInstancesBatchOperationResponse403 | ModifyProcessInstancesBatchOperationResponse500]:
    """Modify process instances (batch)

     Modify multiple process instances.
    Since only process instances with ACTIVE state can be modified, any given
    filters for state are ignored and overridden during this batch operation.
    In contrast to single modification operation, it is not possible to add variable instructions or
    modify by element key.
    It is only possible to use the element id of the source and target.
    This is done asynchronously, the progress can be tracked using the batchOperationKey from the
    response and the batch operation status endpoint (/batch-operations/{batchOperationKey}).

    Args:
        body (ModifyProcessInstancesBatchOperationData): The process instance filter to define on
            which process instances tokens should be moved,
            and new element instances should be activated or terminated.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ModifyProcessInstancesBatchOperationResponse200 | ModifyProcessInstancesBatchOperationResponse400 | ModifyProcessInstancesBatchOperationResponse401 | ModifyProcessInstancesBatchOperationResponse403 | ModifyProcessInstancesBatchOperationResponse500]
    """
    kwargs = _get_kwargs(body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(*, client: AuthenticatedClient | Client, body: ModifyProcessInstancesBatchOperationData, **kwargs) -> ModifyProcessInstancesBatchOperationResponse200:
    """Modify process instances (batch)

 Modify multiple process instances.
Since only process instances with ACTIVE state can be modified, any given
filters for state are ignored and overridden during this batch operation.
In contrast to single modification operation, it is not possible to add variable instructions or
modify by element key.
It is only possible to use the element id of the source and target.
This is done asynchronously, the progress can be tracked using the batchOperationKey from the
response and the batch operation status endpoint (/batch-operations/{batchOperationKey}).

Args:
    body (ModifyProcessInstancesBatchOperationData): The process instance filter to define on
        which process instances tokens should be moved,
        and new element instances should be activated or terminated.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[ModifyProcessInstancesBatchOperationResponse200 | ModifyProcessInstancesBatchOperationResponse400 | ModifyProcessInstancesBatchOperationResponse401 | ModifyProcessInstancesBatchOperationResponse403 | ModifyProcessInstancesBatchOperationResponse500]"""
    response = sync_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(*, client: AuthenticatedClient | Client, body: ModifyProcessInstancesBatchOperationData) -> Response[ModifyProcessInstancesBatchOperationResponse200 | ModifyProcessInstancesBatchOperationResponse400 | ModifyProcessInstancesBatchOperationResponse401 | ModifyProcessInstancesBatchOperationResponse403 | ModifyProcessInstancesBatchOperationResponse500]:
    """Modify process instances (batch)

     Modify multiple process instances.
    Since only process instances with ACTIVE state can be modified, any given
    filters for state are ignored and overridden during this batch operation.
    In contrast to single modification operation, it is not possible to add variable instructions or
    modify by element key.
    It is only possible to use the element id of the source and target.
    This is done asynchronously, the progress can be tracked using the batchOperationKey from the
    response and the batch operation status endpoint (/batch-operations/{batchOperationKey}).

    Args:
        body (ModifyProcessInstancesBatchOperationData): The process instance filter to define on
            which process instances tokens should be moved,
            and new element instances should be activated or terminated.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ModifyProcessInstancesBatchOperationResponse200 | ModifyProcessInstancesBatchOperationResponse400 | ModifyProcessInstancesBatchOperationResponse401 | ModifyProcessInstancesBatchOperationResponse403 | ModifyProcessInstancesBatchOperationResponse500]
    """
    kwargs = _get_kwargs(body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(*, client: AuthenticatedClient | Client, body: ModifyProcessInstancesBatchOperationData, **kwargs) -> ModifyProcessInstancesBatchOperationResponse200:
    """Modify process instances (batch)

 Modify multiple process instances.
Since only process instances with ACTIVE state can be modified, any given
filters for state are ignored and overridden during this batch operation.
In contrast to single modification operation, it is not possible to add variable instructions or
modify by element key.
It is only possible to use the element id of the source and target.
This is done asynchronously, the progress can be tracked using the batchOperationKey from the
response and the batch operation status endpoint (/batch-operations/{batchOperationKey}).

Args:
    body (ModifyProcessInstancesBatchOperationData): The process instance filter to define on
        which process instances tokens should be moved,
        and new element instances should be activated or terminated.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[ModifyProcessInstancesBatchOperationResponse200 | ModifyProcessInstancesBatchOperationResponse400 | ModifyProcessInstancesBatchOperationResponse401 | ModifyProcessInstancesBatchOperationResponse403 | ModifyProcessInstancesBatchOperationResponse500]"""
    response = await asyncio_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
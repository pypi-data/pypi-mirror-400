from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.migrate_process_instances_batch_operation_data import MigrateProcessInstancesBatchOperationData
from ...models.migrate_process_instances_batch_operation_response_200 import MigrateProcessInstancesBatchOperationResponse200
from ...models.migrate_process_instances_batch_operation_response_400 import MigrateProcessInstancesBatchOperationResponse400
from ...models.migrate_process_instances_batch_operation_response_401 import MigrateProcessInstancesBatchOperationResponse401
from ...models.migrate_process_instances_batch_operation_response_403 import MigrateProcessInstancesBatchOperationResponse403
from ...models.migrate_process_instances_batch_operation_response_500 import MigrateProcessInstancesBatchOperationResponse500
from ...types import Response

def _get_kwargs(*, body: MigrateProcessInstancesBatchOperationData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/process-instances/migration'}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> MigrateProcessInstancesBatchOperationResponse200 | MigrateProcessInstancesBatchOperationResponse400 | MigrateProcessInstancesBatchOperationResponse401 | MigrateProcessInstancesBatchOperationResponse403 | MigrateProcessInstancesBatchOperationResponse500 | None:
    if response.status_code == 200:
        response_200 = MigrateProcessInstancesBatchOperationResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = MigrateProcessInstancesBatchOperationResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = MigrateProcessInstancesBatchOperationResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = MigrateProcessInstancesBatchOperationResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 500:
        response_500 = MigrateProcessInstancesBatchOperationResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[MigrateProcessInstancesBatchOperationResponse200 | MigrateProcessInstancesBatchOperationResponse400 | MigrateProcessInstancesBatchOperationResponse401 | MigrateProcessInstancesBatchOperationResponse403 | MigrateProcessInstancesBatchOperationResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(*, client: AuthenticatedClient | Client, body: MigrateProcessInstancesBatchOperationData) -> Response[MigrateProcessInstancesBatchOperationResponse200 | MigrateProcessInstancesBatchOperationResponse400 | MigrateProcessInstancesBatchOperationResponse401 | MigrateProcessInstancesBatchOperationResponse403 | MigrateProcessInstancesBatchOperationResponse500]:
    """Migrate process instances (batch)

     Migrate multiple process instances.
    Since only process instances with ACTIVE state can be migrated, any given
    filters for state are ignored and overridden during this batch operation.
    This is done asynchronously, the progress can be tracked using the batchOperationKey from the
    response and the batch operation status endpoint (/batch-operations/{batchOperationKey}).

    Args:
        body (MigrateProcessInstancesBatchOperationData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[MigrateProcessInstancesBatchOperationResponse200 | MigrateProcessInstancesBatchOperationResponse400 | MigrateProcessInstancesBatchOperationResponse401 | MigrateProcessInstancesBatchOperationResponse403 | MigrateProcessInstancesBatchOperationResponse500]
    """
    kwargs = _get_kwargs(body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(*, client: AuthenticatedClient | Client, body: MigrateProcessInstancesBatchOperationData, **kwargs) -> MigrateProcessInstancesBatchOperationResponse200:
    """Migrate process instances (batch)

 Migrate multiple process instances.
Since only process instances with ACTIVE state can be migrated, any given
filters for state are ignored and overridden during this batch operation.
This is done asynchronously, the progress can be tracked using the batchOperationKey from the
response and the batch operation status endpoint (/batch-operations/{batchOperationKey}).

Args:
    body (MigrateProcessInstancesBatchOperationData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[MigrateProcessInstancesBatchOperationResponse200 | MigrateProcessInstancesBatchOperationResponse400 | MigrateProcessInstancesBatchOperationResponse401 | MigrateProcessInstancesBatchOperationResponse403 | MigrateProcessInstancesBatchOperationResponse500]"""
    response = sync_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(*, client: AuthenticatedClient | Client, body: MigrateProcessInstancesBatchOperationData) -> Response[MigrateProcessInstancesBatchOperationResponse200 | MigrateProcessInstancesBatchOperationResponse400 | MigrateProcessInstancesBatchOperationResponse401 | MigrateProcessInstancesBatchOperationResponse403 | MigrateProcessInstancesBatchOperationResponse500]:
    """Migrate process instances (batch)

     Migrate multiple process instances.
    Since only process instances with ACTIVE state can be migrated, any given
    filters for state are ignored and overridden during this batch operation.
    This is done asynchronously, the progress can be tracked using the batchOperationKey from the
    response and the batch operation status endpoint (/batch-operations/{batchOperationKey}).

    Args:
        body (MigrateProcessInstancesBatchOperationData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[MigrateProcessInstancesBatchOperationResponse200 | MigrateProcessInstancesBatchOperationResponse400 | MigrateProcessInstancesBatchOperationResponse401 | MigrateProcessInstancesBatchOperationResponse403 | MigrateProcessInstancesBatchOperationResponse500]
    """
    kwargs = _get_kwargs(body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(*, client: AuthenticatedClient | Client, body: MigrateProcessInstancesBatchOperationData, **kwargs) -> MigrateProcessInstancesBatchOperationResponse200:
    """Migrate process instances (batch)

 Migrate multiple process instances.
Since only process instances with ACTIVE state can be migrated, any given
filters for state are ignored and overridden during this batch operation.
This is done asynchronously, the progress can be tracked using the batchOperationKey from the
response and the batch operation status endpoint (/batch-operations/{batchOperationKey}).

Args:
    body (MigrateProcessInstancesBatchOperationData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[MigrateProcessInstancesBatchOperationResponse200 | MigrateProcessInstancesBatchOperationResponse400 | MigrateProcessInstancesBatchOperationResponse401 | MigrateProcessInstancesBatchOperationResponse403 | MigrateProcessInstancesBatchOperationResponse500]"""
    response = await asyncio_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
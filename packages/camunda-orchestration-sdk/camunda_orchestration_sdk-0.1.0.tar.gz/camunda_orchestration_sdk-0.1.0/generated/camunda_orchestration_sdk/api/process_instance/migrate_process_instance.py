from http import HTTPStatus
from typing import Any, cast
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.migrate_process_instance_data import MigrateProcessInstanceData
from ...models.migrate_process_instance_response_400 import MigrateProcessInstanceResponse400
from ...models.migrate_process_instance_response_404 import MigrateProcessInstanceResponse404
from ...models.migrate_process_instance_response_409 import MigrateProcessInstanceResponse409
from ...models.migrate_process_instance_response_500 import MigrateProcessInstanceResponse500
from ...models.migrate_process_instance_response_503 import MigrateProcessInstanceResponse503
from ...types import Response

def _get_kwargs(process_instance_key: str, *, body: MigrateProcessInstanceData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/process-instances/{process_instance_key}/migration'.format(process_instance_key=process_instance_key)}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | MigrateProcessInstanceResponse400 | MigrateProcessInstanceResponse404 | MigrateProcessInstanceResponse409 | MigrateProcessInstanceResponse500 | MigrateProcessInstanceResponse503 | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 400:
        response_400 = MigrateProcessInstanceResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 404:
        response_404 = MigrateProcessInstanceResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 409:
        response_409 = MigrateProcessInstanceResponse409.from_dict(response.json())
        return response_409
    if response.status_code == 500:
        response_500 = MigrateProcessInstanceResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = MigrateProcessInstanceResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | MigrateProcessInstanceResponse400 | MigrateProcessInstanceResponse404 | MigrateProcessInstanceResponse409 | MigrateProcessInstanceResponse500 | MigrateProcessInstanceResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(process_instance_key: str, *, client: AuthenticatedClient | Client, body: MigrateProcessInstanceData) -> Response[Any | MigrateProcessInstanceResponse400 | MigrateProcessInstanceResponse404 | MigrateProcessInstanceResponse409 | MigrateProcessInstanceResponse500 | MigrateProcessInstanceResponse503]:
    """Migrate process instance

     Migrates a process instance to a new process definition.
    This request can contain multiple mapping instructions to define mapping between the active
    process instance's elements and target process definition elements.

    Use this to upgrade a process instance to a new version of a process or to
    a different process definition, e.g. to keep your running instances up-to-date with the
    latest process improvements.

    Args:
        process_instance_key (str): System-generated key for a process instance. Example:
            2251799813690746.
        body (MigrateProcessInstanceData): The migration instructions describe how to migrate a
            process instance from one process definition to another.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | MigrateProcessInstanceResponse400 | MigrateProcessInstanceResponse404 | MigrateProcessInstanceResponse409 | MigrateProcessInstanceResponse500 | MigrateProcessInstanceResponse503]
    """
    kwargs = _get_kwargs(process_instance_key=process_instance_key, body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(process_instance_key: str, *, client: AuthenticatedClient | Client, body: MigrateProcessInstanceData, **kwargs) -> Any:
    """Migrate process instance

 Migrates a process instance to a new process definition.
This request can contain multiple mapping instructions to define mapping between the active
process instance's elements and target process definition elements.

Use this to upgrade a process instance to a new version of a process or to
a different process definition, e.g. to keep your running instances up-to-date with the
latest process improvements.

Args:
    process_instance_key (str): System-generated key for a process instance. Example:
        2251799813690746.
    body (MigrateProcessInstanceData): The migration instructions describe how to migrate a
        process instance from one process definition to another.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | MigrateProcessInstanceResponse400 | MigrateProcessInstanceResponse404 | MigrateProcessInstanceResponse409 | MigrateProcessInstanceResponse500 | MigrateProcessInstanceResponse503]"""
    response = sync_detailed(process_instance_key=process_instance_key, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(process_instance_key: str, *, client: AuthenticatedClient | Client, body: MigrateProcessInstanceData) -> Response[Any | MigrateProcessInstanceResponse400 | MigrateProcessInstanceResponse404 | MigrateProcessInstanceResponse409 | MigrateProcessInstanceResponse500 | MigrateProcessInstanceResponse503]:
    """Migrate process instance

     Migrates a process instance to a new process definition.
    This request can contain multiple mapping instructions to define mapping between the active
    process instance's elements and target process definition elements.

    Use this to upgrade a process instance to a new version of a process or to
    a different process definition, e.g. to keep your running instances up-to-date with the
    latest process improvements.

    Args:
        process_instance_key (str): System-generated key for a process instance. Example:
            2251799813690746.
        body (MigrateProcessInstanceData): The migration instructions describe how to migrate a
            process instance from one process definition to another.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | MigrateProcessInstanceResponse400 | MigrateProcessInstanceResponse404 | MigrateProcessInstanceResponse409 | MigrateProcessInstanceResponse500 | MigrateProcessInstanceResponse503]
    """
    kwargs = _get_kwargs(process_instance_key=process_instance_key, body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(process_instance_key: str, *, client: AuthenticatedClient | Client, body: MigrateProcessInstanceData, **kwargs) -> Any:
    """Migrate process instance

 Migrates a process instance to a new process definition.
This request can contain multiple mapping instructions to define mapping between the active
process instance's elements and target process definition elements.

Use this to upgrade a process instance to a new version of a process or to
a different process definition, e.g. to keep your running instances up-to-date with the
latest process improvements.

Args:
    process_instance_key (str): System-generated key for a process instance. Example:
        2251799813690746.
    body (MigrateProcessInstanceData): The migration instructions describe how to migrate a
        process instance from one process definition to another.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | MigrateProcessInstanceResponse400 | MigrateProcessInstanceResponse404 | MigrateProcessInstanceResponse409 | MigrateProcessInstanceResponse500 | MigrateProcessInstanceResponse503]"""
    response = await asyncio_detailed(process_instance_key=process_instance_key, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_process_instance_response_200 import CreateProcessInstanceResponse200
from ...models.create_process_instance_response_400 import CreateProcessInstanceResponse400
from ...models.create_process_instance_response_500 import CreateProcessInstanceResponse500
from ...models.create_process_instance_response_503 import CreateProcessInstanceResponse503
from ...models.create_process_instance_response_504 import CreateProcessInstanceResponse504
from ...models.processcreationbyid import Processcreationbyid
from ...models.processcreationbykey import Processcreationbykey
from ...types import Response

def _get_kwargs(*, body: Processcreationbyid | Processcreationbykey) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/process-instances'}
    _kwargs['json']: dict[str, Any]
    if isinstance(body, Processcreationbyid):
        _kwargs['json'] = body.to_dict()
    else:
        _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> CreateProcessInstanceResponse200 | CreateProcessInstanceResponse400 | CreateProcessInstanceResponse500 | CreateProcessInstanceResponse503 | CreateProcessInstanceResponse504 | None:
    if response.status_code == 200:
        response_200 = CreateProcessInstanceResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = CreateProcessInstanceResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 500:
        response_500 = CreateProcessInstanceResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = CreateProcessInstanceResponse503.from_dict(response.json())
        return response_503
    if response.status_code == 504:
        response_504 = CreateProcessInstanceResponse504.from_dict(response.json())
        return response_504
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[CreateProcessInstanceResponse200 | CreateProcessInstanceResponse400 | CreateProcessInstanceResponse500 | CreateProcessInstanceResponse503 | CreateProcessInstanceResponse504]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(*, client: AuthenticatedClient | Client, body: Processcreationbyid | Processcreationbykey) -> Response[CreateProcessInstanceResponse200 | CreateProcessInstanceResponse400 | CreateProcessInstanceResponse500 | CreateProcessInstanceResponse503 | CreateProcessInstanceResponse504]:
    """Create process instance

     Creates and starts an instance of the specified process.
    The process definition to use to create the instance can be specified either using its unique key
    (as returned by Deploy resources), or using the BPMN process id and a version.

    Waits for the completion of the process instance before returning a result
    when awaitCompletion is enabled.

    Args:
        body (Processcreationbyid | Processcreationbykey): Instructions for creating a process
            instance. The process definition can be specified
            either by id or by key.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateProcessInstanceResponse200 | CreateProcessInstanceResponse400 | CreateProcessInstanceResponse500 | CreateProcessInstanceResponse503 | CreateProcessInstanceResponse504]
    """
    kwargs = _get_kwargs(body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(*, client: AuthenticatedClient | Client, body: Processcreationbyid | Processcreationbykey, **kwargs) -> CreateProcessInstanceResponse200:
    """Create process instance

 Creates and starts an instance of the specified process.
The process definition to use to create the instance can be specified either using its unique key
(as returned by Deploy resources), or using the BPMN process id and a version.

Waits for the completion of the process instance before returning a result
when awaitCompletion is enabled.

Args:
    body (Processcreationbyid | Processcreationbykey): Instructions for creating a process
        instance. The process definition can be specified
        either by id or by key.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateProcessInstanceResponse200 | CreateProcessInstanceResponse400 | CreateProcessInstanceResponse500 | CreateProcessInstanceResponse503 | CreateProcessInstanceResponse504]"""
    response = sync_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(*, client: AuthenticatedClient | Client, body: Processcreationbyid | Processcreationbykey) -> Response[CreateProcessInstanceResponse200 | CreateProcessInstanceResponse400 | CreateProcessInstanceResponse500 | CreateProcessInstanceResponse503 | CreateProcessInstanceResponse504]:
    """Create process instance

     Creates and starts an instance of the specified process.
    The process definition to use to create the instance can be specified either using its unique key
    (as returned by Deploy resources), or using the BPMN process id and a version.

    Waits for the completion of the process instance before returning a result
    when awaitCompletion is enabled.

    Args:
        body (Processcreationbyid | Processcreationbykey): Instructions for creating a process
            instance. The process definition can be specified
            either by id or by key.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateProcessInstanceResponse200 | CreateProcessInstanceResponse400 | CreateProcessInstanceResponse500 | CreateProcessInstanceResponse503 | CreateProcessInstanceResponse504]
    """
    kwargs = _get_kwargs(body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(*, client: AuthenticatedClient | Client, body: Processcreationbyid | Processcreationbykey, **kwargs) -> CreateProcessInstanceResponse200:
    """Create process instance

 Creates and starts an instance of the specified process.
The process definition to use to create the instance can be specified either using its unique key
(as returned by Deploy resources), or using the BPMN process id and a version.

Waits for the completion of the process instance before returning a result
when awaitCompletion is enabled.

Args:
    body (Processcreationbyid | Processcreationbykey): Instructions for creating a process
        instance. The process definition can be specified
        either by id or by key.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateProcessInstanceResponse200 | CreateProcessInstanceResponse400 | CreateProcessInstanceResponse500 | CreateProcessInstanceResponse503 | CreateProcessInstanceResponse504]"""
    response = await asyncio_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
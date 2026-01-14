from http import HTTPStatus
from typing import Any, cast
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.modify_process_instance_data import ModifyProcessInstanceData
from ...models.modify_process_instance_response_400 import ModifyProcessInstanceResponse400
from ...models.modify_process_instance_response_404 import ModifyProcessInstanceResponse404
from ...models.modify_process_instance_response_500 import ModifyProcessInstanceResponse500
from ...models.modify_process_instance_response_503 import ModifyProcessInstanceResponse503
from ...types import Response

def _get_kwargs(process_instance_key: str, *, body: ModifyProcessInstanceData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/process-instances/{process_instance_key}/modification'.format(process_instance_key=process_instance_key)}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | ModifyProcessInstanceResponse400 | ModifyProcessInstanceResponse404 | ModifyProcessInstanceResponse500 | ModifyProcessInstanceResponse503 | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 400:
        response_400 = ModifyProcessInstanceResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 404:
        response_404 = ModifyProcessInstanceResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = ModifyProcessInstanceResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = ModifyProcessInstanceResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | ModifyProcessInstanceResponse400 | ModifyProcessInstanceResponse404 | ModifyProcessInstanceResponse500 | ModifyProcessInstanceResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(process_instance_key: str, *, client: AuthenticatedClient | Client, body: ModifyProcessInstanceData) -> Response[Any | ModifyProcessInstanceResponse400 | ModifyProcessInstanceResponse404 | ModifyProcessInstanceResponse500 | ModifyProcessInstanceResponse503]:
    """Modify process instance

     Modifies a running process instance.
    This request can contain multiple instructions to activate an element of the process or
    to terminate an active instance of an element.

    Use this to repair a process instance that is stuck on an element or took an unintended path.
    For example, because an external system is not available or doesn't respond as expected.

    Args:
        process_instance_key (str): System-generated key for a process instance. Example:
            2251799813690746.
        body (ModifyProcessInstanceData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ModifyProcessInstanceResponse400 | ModifyProcessInstanceResponse404 | ModifyProcessInstanceResponse500 | ModifyProcessInstanceResponse503]
    """
    kwargs = _get_kwargs(process_instance_key=process_instance_key, body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(process_instance_key: str, *, client: AuthenticatedClient | Client, body: ModifyProcessInstanceData, **kwargs) -> Any:
    """Modify process instance

 Modifies a running process instance.
This request can contain multiple instructions to activate an element of the process or
to terminate an active instance of an element.

Use this to repair a process instance that is stuck on an element or took an unintended path.
For example, because an external system is not available or doesn't respond as expected.

Args:
    process_instance_key (str): System-generated key for a process instance. Example:
        2251799813690746.
    body (ModifyProcessInstanceData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | ModifyProcessInstanceResponse400 | ModifyProcessInstanceResponse404 | ModifyProcessInstanceResponse500 | ModifyProcessInstanceResponse503]"""
    response = sync_detailed(process_instance_key=process_instance_key, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(process_instance_key: str, *, client: AuthenticatedClient | Client, body: ModifyProcessInstanceData) -> Response[Any | ModifyProcessInstanceResponse400 | ModifyProcessInstanceResponse404 | ModifyProcessInstanceResponse500 | ModifyProcessInstanceResponse503]:
    """Modify process instance

     Modifies a running process instance.
    This request can contain multiple instructions to activate an element of the process or
    to terminate an active instance of an element.

    Use this to repair a process instance that is stuck on an element or took an unintended path.
    For example, because an external system is not available or doesn't respond as expected.

    Args:
        process_instance_key (str): System-generated key for a process instance. Example:
            2251799813690746.
        body (ModifyProcessInstanceData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ModifyProcessInstanceResponse400 | ModifyProcessInstanceResponse404 | ModifyProcessInstanceResponse500 | ModifyProcessInstanceResponse503]
    """
    kwargs = _get_kwargs(process_instance_key=process_instance_key, body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(process_instance_key: str, *, client: AuthenticatedClient | Client, body: ModifyProcessInstanceData, **kwargs) -> Any:
    """Modify process instance

 Modifies a running process instance.
This request can contain multiple instructions to activate an element of the process or
to terminate an active instance of an element.

Use this to repair a process instance that is stuck on an element or took an unintended path.
For example, because an external system is not available or doesn't respond as expected.

Args:
    process_instance_key (str): System-generated key for a process instance. Example:
        2251799813690746.
    body (ModifyProcessInstanceData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | ModifyProcessInstanceResponse400 | ModifyProcessInstanceResponse404 | ModifyProcessInstanceResponse500 | ModifyProcessInstanceResponse503]"""
    response = await asyncio_detailed(process_instance_key=process_instance_key, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
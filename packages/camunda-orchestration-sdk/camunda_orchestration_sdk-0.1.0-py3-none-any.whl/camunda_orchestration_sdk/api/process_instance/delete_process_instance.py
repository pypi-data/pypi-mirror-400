from http import HTTPStatus
from typing import Any, cast
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.delete_process_instance_data_type_0 import DeleteProcessInstanceDataType0
from ...models.delete_process_instance_response_401 import DeleteProcessInstanceResponse401
from ...models.delete_process_instance_response_403 import DeleteProcessInstanceResponse403
from ...models.delete_process_instance_response_404 import DeleteProcessInstanceResponse404
from ...models.delete_process_instance_response_409 import DeleteProcessInstanceResponse409
from ...models.delete_process_instance_response_500 import DeleteProcessInstanceResponse500
from ...models.delete_process_instance_response_503 import DeleteProcessInstanceResponse503
from ...types import Response

def _get_kwargs(process_instance_key: str, *, body: DeleteProcessInstanceDataType0 | None) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/process-instances/{process_instance_key}/deletion'.format(process_instance_key=process_instance_key)}
    _kwargs['json']: dict[str, Any] | None
    if isinstance(body, DeleteProcessInstanceDataType0):
        _kwargs['json'] = body.to_dict()
    else:
        _kwargs['json'] = body
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | DeleteProcessInstanceResponse401 | DeleteProcessInstanceResponse403 | DeleteProcessInstanceResponse404 | DeleteProcessInstanceResponse409 | DeleteProcessInstanceResponse500 | DeleteProcessInstanceResponse503 | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 401:
        response_401 = DeleteProcessInstanceResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = DeleteProcessInstanceResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = DeleteProcessInstanceResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 409:
        response_409 = DeleteProcessInstanceResponse409.from_dict(response.json())
        return response_409
    if response.status_code == 500:
        response_500 = DeleteProcessInstanceResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = DeleteProcessInstanceResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | DeleteProcessInstanceResponse401 | DeleteProcessInstanceResponse403 | DeleteProcessInstanceResponse404 | DeleteProcessInstanceResponse409 | DeleteProcessInstanceResponse500 | DeleteProcessInstanceResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(process_instance_key: str, *, client: AuthenticatedClient | Client, body: DeleteProcessInstanceDataType0 | None) -> Response[Any | DeleteProcessInstanceResponse401 | DeleteProcessInstanceResponse403 | DeleteProcessInstanceResponse404 | DeleteProcessInstanceResponse409 | DeleteProcessInstanceResponse500 | DeleteProcessInstanceResponse503]:
    """Delete process instance

     Deletes a process instance. Only instances that are completed or terminated can be deleted.

    Args:
        process_instance_key (str): System-generated key for a process instance. Example:
            2251799813690746.
        body (DeleteProcessInstanceDataType0 | None):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | DeleteProcessInstanceResponse401 | DeleteProcessInstanceResponse403 | DeleteProcessInstanceResponse404 | DeleteProcessInstanceResponse409 | DeleteProcessInstanceResponse500 | DeleteProcessInstanceResponse503]
    """
    kwargs = _get_kwargs(process_instance_key=process_instance_key, body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(process_instance_key: str, *, client: AuthenticatedClient | Client, body: DeleteProcessInstanceDataType0 | None, **kwargs) -> Any:
    """Delete process instance

 Deletes a process instance. Only instances that are completed or terminated can be deleted.

Args:
    process_instance_key (str): System-generated key for a process instance. Example:
        2251799813690746.
    body (DeleteProcessInstanceDataType0 | None):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteProcessInstanceResponse401 | DeleteProcessInstanceResponse403 | DeleteProcessInstanceResponse404 | DeleteProcessInstanceResponse409 | DeleteProcessInstanceResponse500 | DeleteProcessInstanceResponse503]"""
    response = sync_detailed(process_instance_key=process_instance_key, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(process_instance_key: str, *, client: AuthenticatedClient | Client, body: DeleteProcessInstanceDataType0 | None) -> Response[Any | DeleteProcessInstanceResponse401 | DeleteProcessInstanceResponse403 | DeleteProcessInstanceResponse404 | DeleteProcessInstanceResponse409 | DeleteProcessInstanceResponse500 | DeleteProcessInstanceResponse503]:
    """Delete process instance

     Deletes a process instance. Only instances that are completed or terminated can be deleted.

    Args:
        process_instance_key (str): System-generated key for a process instance. Example:
            2251799813690746.
        body (DeleteProcessInstanceDataType0 | None):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | DeleteProcessInstanceResponse401 | DeleteProcessInstanceResponse403 | DeleteProcessInstanceResponse404 | DeleteProcessInstanceResponse409 | DeleteProcessInstanceResponse500 | DeleteProcessInstanceResponse503]
    """
    kwargs = _get_kwargs(process_instance_key=process_instance_key, body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(process_instance_key: str, *, client: AuthenticatedClient | Client, body: DeleteProcessInstanceDataType0 | None, **kwargs) -> Any:
    """Delete process instance

 Deletes a process instance. Only instances that are completed or terminated can be deleted.

Args:
    process_instance_key (str): System-generated key for a process instance. Example:
        2251799813690746.
    body (DeleteProcessInstanceDataType0 | None):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteProcessInstanceResponse401 | DeleteProcessInstanceResponse403 | DeleteProcessInstanceResponse404 | DeleteProcessInstanceResponse409 | DeleteProcessInstanceResponse500 | DeleteProcessInstanceResponse503]"""
    response = await asyncio_detailed(process_instance_key=process_instance_key, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
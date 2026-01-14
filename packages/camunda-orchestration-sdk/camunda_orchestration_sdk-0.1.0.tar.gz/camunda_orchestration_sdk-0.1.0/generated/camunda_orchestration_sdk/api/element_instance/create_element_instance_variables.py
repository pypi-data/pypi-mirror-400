from http import HTTPStatus
from typing import Any, cast
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_element_instance_variables_data import CreateElementInstanceVariablesData
from ...models.create_element_instance_variables_response_400 import CreateElementInstanceVariablesResponse400
from ...models.create_element_instance_variables_response_500 import CreateElementInstanceVariablesResponse500
from ...models.create_element_instance_variables_response_503 import CreateElementInstanceVariablesResponse503
from ...types import Response

def _get_kwargs(element_instance_key: str, *, body: CreateElementInstanceVariablesData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'put', 'url': '/element-instances/{element_instance_key}/variables'.format(element_instance_key=element_instance_key)}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | CreateElementInstanceVariablesResponse400 | CreateElementInstanceVariablesResponse500 | CreateElementInstanceVariablesResponse503 | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 400:
        response_400 = CreateElementInstanceVariablesResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 500:
        response_500 = CreateElementInstanceVariablesResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = CreateElementInstanceVariablesResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | CreateElementInstanceVariablesResponse400 | CreateElementInstanceVariablesResponse500 | CreateElementInstanceVariablesResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(element_instance_key: str, *, client: AuthenticatedClient | Client, body: CreateElementInstanceVariablesData) -> Response[Any | CreateElementInstanceVariablesResponse400 | CreateElementInstanceVariablesResponse500 | CreateElementInstanceVariablesResponse503]:
    """Update element instance variables

     Updates all the variables of a particular scope (for example, process instance, element instance)
    with the given variable data.
    Specify the element instance in the `elementInstanceKey` parameter.

    Args:
        element_instance_key (str): System-generated key for a element instance. Example:
            2251799813686789.
        body (CreateElementInstanceVariablesData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | CreateElementInstanceVariablesResponse400 | CreateElementInstanceVariablesResponse500 | CreateElementInstanceVariablesResponse503]
    """
    kwargs = _get_kwargs(element_instance_key=element_instance_key, body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(element_instance_key: str, *, client: AuthenticatedClient | Client, body: CreateElementInstanceVariablesData, **kwargs) -> Any:
    """Update element instance variables

 Updates all the variables of a particular scope (for example, process instance, element instance)
with the given variable data.
Specify the element instance in the `elementInstanceKey` parameter.

Args:
    element_instance_key (str): System-generated key for a element instance. Example:
        2251799813686789.
    body (CreateElementInstanceVariablesData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | CreateElementInstanceVariablesResponse400 | CreateElementInstanceVariablesResponse500 | CreateElementInstanceVariablesResponse503]"""
    response = sync_detailed(element_instance_key=element_instance_key, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(element_instance_key: str, *, client: AuthenticatedClient | Client, body: CreateElementInstanceVariablesData) -> Response[Any | CreateElementInstanceVariablesResponse400 | CreateElementInstanceVariablesResponse500 | CreateElementInstanceVariablesResponse503]:
    """Update element instance variables

     Updates all the variables of a particular scope (for example, process instance, element instance)
    with the given variable data.
    Specify the element instance in the `elementInstanceKey` parameter.

    Args:
        element_instance_key (str): System-generated key for a element instance. Example:
            2251799813686789.
        body (CreateElementInstanceVariablesData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | CreateElementInstanceVariablesResponse400 | CreateElementInstanceVariablesResponse500 | CreateElementInstanceVariablesResponse503]
    """
    kwargs = _get_kwargs(element_instance_key=element_instance_key, body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(element_instance_key: str, *, client: AuthenticatedClient | Client, body: CreateElementInstanceVariablesData, **kwargs) -> Any:
    """Update element instance variables

 Updates all the variables of a particular scope (for example, process instance, element instance)
with the given variable data.
Specify the element instance in the `elementInstanceKey` parameter.

Args:
    element_instance_key (str): System-generated key for a element instance. Example:
        2251799813686789.
    body (CreateElementInstanceVariablesData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | CreateElementInstanceVariablesResponse400 | CreateElementInstanceVariablesResponse500 | CreateElementInstanceVariablesResponse503]"""
    response = await asyncio_detailed(element_instance_key=element_instance_key, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
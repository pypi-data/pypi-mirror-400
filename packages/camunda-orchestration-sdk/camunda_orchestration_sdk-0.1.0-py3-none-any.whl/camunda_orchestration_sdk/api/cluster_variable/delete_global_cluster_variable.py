from http import HTTPStatus
from typing import Any, cast
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.delete_global_cluster_variable_response_400 import DeleteGlobalClusterVariableResponse400
from ...models.delete_global_cluster_variable_response_401 import DeleteGlobalClusterVariableResponse401
from ...models.delete_global_cluster_variable_response_403 import DeleteGlobalClusterVariableResponse403
from ...models.delete_global_cluster_variable_response_404 import DeleteGlobalClusterVariableResponse404
from ...models.delete_global_cluster_variable_response_500 import DeleteGlobalClusterVariableResponse500
from ...types import Response

def _get_kwargs(name: str) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {'method': 'delete', 'url': '/cluster-variables/global/{name}'.format(name=name)}
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | DeleteGlobalClusterVariableResponse400 | DeleteGlobalClusterVariableResponse401 | DeleteGlobalClusterVariableResponse403 | DeleteGlobalClusterVariableResponse404 | DeleteGlobalClusterVariableResponse500 | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 400:
        response_400 = DeleteGlobalClusterVariableResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = DeleteGlobalClusterVariableResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = DeleteGlobalClusterVariableResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = DeleteGlobalClusterVariableResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = DeleteGlobalClusterVariableResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | DeleteGlobalClusterVariableResponse400 | DeleteGlobalClusterVariableResponse401 | DeleteGlobalClusterVariableResponse403 | DeleteGlobalClusterVariableResponse404 | DeleteGlobalClusterVariableResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(name: str, *, client: AuthenticatedClient | Client) -> Response[Any | DeleteGlobalClusterVariableResponse400 | DeleteGlobalClusterVariableResponse401 | DeleteGlobalClusterVariableResponse403 | DeleteGlobalClusterVariableResponse404 | DeleteGlobalClusterVariableResponse500]:
    """Delete a global-scoped cluster variable

    Args:
        name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | DeleteGlobalClusterVariableResponse400 | DeleteGlobalClusterVariableResponse401 | DeleteGlobalClusterVariableResponse403 | DeleteGlobalClusterVariableResponse404 | DeleteGlobalClusterVariableResponse500]
    """
    kwargs = _get_kwargs(name=name)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(name: str, *, client: AuthenticatedClient | Client, **kwargs) -> Any:
    """Delete a global-scoped cluster variable

Args:
    name (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteGlobalClusterVariableResponse400 | DeleteGlobalClusterVariableResponse401 | DeleteGlobalClusterVariableResponse403 | DeleteGlobalClusterVariableResponse404 | DeleteGlobalClusterVariableResponse500]"""
    response = sync_detailed(name=name, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(name: str, *, client: AuthenticatedClient | Client) -> Response[Any | DeleteGlobalClusterVariableResponse400 | DeleteGlobalClusterVariableResponse401 | DeleteGlobalClusterVariableResponse403 | DeleteGlobalClusterVariableResponse404 | DeleteGlobalClusterVariableResponse500]:
    """Delete a global-scoped cluster variable

    Args:
        name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | DeleteGlobalClusterVariableResponse400 | DeleteGlobalClusterVariableResponse401 | DeleteGlobalClusterVariableResponse403 | DeleteGlobalClusterVariableResponse404 | DeleteGlobalClusterVariableResponse500]
    """
    kwargs = _get_kwargs(name=name)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(name: str, *, client: AuthenticatedClient | Client, **kwargs) -> Any:
    """Delete a global-scoped cluster variable

Args:
    name (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteGlobalClusterVariableResponse400 | DeleteGlobalClusterVariableResponse401 | DeleteGlobalClusterVariableResponse403 | DeleteGlobalClusterVariableResponse404 | DeleteGlobalClusterVariableResponse500]"""
    response = await asyncio_detailed(name=name, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
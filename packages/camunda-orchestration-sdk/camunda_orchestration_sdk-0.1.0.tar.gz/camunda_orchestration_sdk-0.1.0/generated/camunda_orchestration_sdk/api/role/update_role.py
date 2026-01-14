from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.update_role_data import UpdateRoleData
from ...models.update_role_response_200 import UpdateRoleResponse200
from ...models.update_role_response_400 import UpdateRoleResponse400
from ...models.update_role_response_401 import UpdateRoleResponse401
from ...models.update_role_response_404 import UpdateRoleResponse404
from ...models.update_role_response_500 import UpdateRoleResponse500
from ...models.update_role_response_503 import UpdateRoleResponse503
from ...types import Response

def _get_kwargs(role_id: str, *, body: UpdateRoleData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'put', 'url': '/roles/{role_id}'.format(role_id=role_id)}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> UpdateRoleResponse200 | UpdateRoleResponse400 | UpdateRoleResponse401 | UpdateRoleResponse404 | UpdateRoleResponse500 | UpdateRoleResponse503 | None:
    if response.status_code == 200:
        response_200 = UpdateRoleResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = UpdateRoleResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = UpdateRoleResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 404:
        response_404 = UpdateRoleResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = UpdateRoleResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = UpdateRoleResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[UpdateRoleResponse200 | UpdateRoleResponse400 | UpdateRoleResponse401 | UpdateRoleResponse404 | UpdateRoleResponse500 | UpdateRoleResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(role_id: str, *, client: AuthenticatedClient | Client, body: UpdateRoleData) -> Response[UpdateRoleResponse200 | UpdateRoleResponse400 | UpdateRoleResponse401 | UpdateRoleResponse404 | UpdateRoleResponse500 | UpdateRoleResponse503]:
    """Update role

     Update a role with the given ID.

    Args:
        role_id (str):
        body (UpdateRoleData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UpdateRoleResponse200 | UpdateRoleResponse400 | UpdateRoleResponse401 | UpdateRoleResponse404 | UpdateRoleResponse500 | UpdateRoleResponse503]
    """
    kwargs = _get_kwargs(role_id=role_id, body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(role_id: str, *, client: AuthenticatedClient | Client, body: UpdateRoleData, **kwargs) -> UpdateRoleResponse200:
    """Update role

 Update a role with the given ID.

Args:
    role_id (str):
    body (UpdateRoleData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[UpdateRoleResponse200 | UpdateRoleResponse400 | UpdateRoleResponse401 | UpdateRoleResponse404 | UpdateRoleResponse500 | UpdateRoleResponse503]"""
    response = sync_detailed(role_id=role_id, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(role_id: str, *, client: AuthenticatedClient | Client, body: UpdateRoleData) -> Response[UpdateRoleResponse200 | UpdateRoleResponse400 | UpdateRoleResponse401 | UpdateRoleResponse404 | UpdateRoleResponse500 | UpdateRoleResponse503]:
    """Update role

     Update a role with the given ID.

    Args:
        role_id (str):
        body (UpdateRoleData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UpdateRoleResponse200 | UpdateRoleResponse400 | UpdateRoleResponse401 | UpdateRoleResponse404 | UpdateRoleResponse500 | UpdateRoleResponse503]
    """
    kwargs = _get_kwargs(role_id=role_id, body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(role_id: str, *, client: AuthenticatedClient | Client, body: UpdateRoleData, **kwargs) -> UpdateRoleResponse200:
    """Update role

 Update a role with the given ID.

Args:
    role_id (str):
    body (UpdateRoleData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[UpdateRoleResponse200 | UpdateRoleResponse400 | UpdateRoleResponse401 | UpdateRoleResponse404 | UpdateRoleResponse500 | UpdateRoleResponse503]"""
    response = await asyncio_detailed(role_id=role_id, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
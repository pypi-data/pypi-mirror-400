from http import HTTPStatus
from typing import Any, cast
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.assign_role_to_client_response_400 import AssignRoleToClientResponse400
from ...models.assign_role_to_client_response_403 import AssignRoleToClientResponse403
from ...models.assign_role_to_client_response_404 import AssignRoleToClientResponse404
from ...models.assign_role_to_client_response_409 import AssignRoleToClientResponse409
from ...models.assign_role_to_client_response_500 import AssignRoleToClientResponse500
from ...models.assign_role_to_client_response_503 import AssignRoleToClientResponse503
from ...types import Response

def _get_kwargs(role_id: str, client_id: str) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {'method': 'put', 'url': '/roles/{role_id}/clients/{client_id}'.format(role_id=role_id, client_id=client_id)}
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | AssignRoleToClientResponse400 | AssignRoleToClientResponse403 | AssignRoleToClientResponse404 | AssignRoleToClientResponse409 | AssignRoleToClientResponse500 | AssignRoleToClientResponse503 | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 400:
        response_400 = AssignRoleToClientResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 403:
        response_403 = AssignRoleToClientResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = AssignRoleToClientResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 409:
        response_409 = AssignRoleToClientResponse409.from_dict(response.json())
        return response_409
    if response.status_code == 500:
        response_500 = AssignRoleToClientResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = AssignRoleToClientResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | AssignRoleToClientResponse400 | AssignRoleToClientResponse403 | AssignRoleToClientResponse404 | AssignRoleToClientResponse409 | AssignRoleToClientResponse500 | AssignRoleToClientResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(role_id: str, client_id: str, *, client: AuthenticatedClient | Client) -> Response[Any | AssignRoleToClientResponse400 | AssignRoleToClientResponse403 | AssignRoleToClientResponse404 | AssignRoleToClientResponse409 | AssignRoleToClientResponse500 | AssignRoleToClientResponse503]:
    """Assign a role to a client

     Assigns the specified role to the client. The client will inherit the authorizations associated with
    this role.

    Args:
        role_id (str):
        client_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | AssignRoleToClientResponse400 | AssignRoleToClientResponse403 | AssignRoleToClientResponse404 | AssignRoleToClientResponse409 | AssignRoleToClientResponse500 | AssignRoleToClientResponse503]
    """
    kwargs = _get_kwargs(role_id=role_id, client_id=client_id)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(role_id: str, client_id: str, *, client: AuthenticatedClient | Client, **kwargs) -> Any:
    """Assign a role to a client

 Assigns the specified role to the client. The client will inherit the authorizations associated with
this role.

Args:
    role_id (str):
    client_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignRoleToClientResponse400 | AssignRoleToClientResponse403 | AssignRoleToClientResponse404 | AssignRoleToClientResponse409 | AssignRoleToClientResponse500 | AssignRoleToClientResponse503]"""
    response = sync_detailed(role_id=role_id, client_id=client_id, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(role_id: str, client_id: str, *, client: AuthenticatedClient | Client) -> Response[Any | AssignRoleToClientResponse400 | AssignRoleToClientResponse403 | AssignRoleToClientResponse404 | AssignRoleToClientResponse409 | AssignRoleToClientResponse500 | AssignRoleToClientResponse503]:
    """Assign a role to a client

     Assigns the specified role to the client. The client will inherit the authorizations associated with
    this role.

    Args:
        role_id (str):
        client_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | AssignRoleToClientResponse400 | AssignRoleToClientResponse403 | AssignRoleToClientResponse404 | AssignRoleToClientResponse409 | AssignRoleToClientResponse500 | AssignRoleToClientResponse503]
    """
    kwargs = _get_kwargs(role_id=role_id, client_id=client_id)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(role_id: str, client_id: str, *, client: AuthenticatedClient | Client, **kwargs) -> Any:
    """Assign a role to a client

 Assigns the specified role to the client. The client will inherit the authorizations associated with
this role.

Args:
    role_id (str):
    client_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | AssignRoleToClientResponse400 | AssignRoleToClientResponse403 | AssignRoleToClientResponse404 | AssignRoleToClientResponse409 | AssignRoleToClientResponse500 | AssignRoleToClientResponse503]"""
    response = await asyncio_detailed(role_id=role_id, client_id=client_id, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
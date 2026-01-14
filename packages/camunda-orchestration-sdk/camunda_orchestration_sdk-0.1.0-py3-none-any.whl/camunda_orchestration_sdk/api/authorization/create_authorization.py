from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_authorization_response_201 import CreateAuthorizationResponse201
from ...models.create_authorization_response_400 import CreateAuthorizationResponse400
from ...models.create_authorization_response_401 import CreateAuthorizationResponse401
from ...models.create_authorization_response_403 import CreateAuthorizationResponse403
from ...models.create_authorization_response_404 import CreateAuthorizationResponse404
from ...models.create_authorization_response_500 import CreateAuthorizationResponse500
from ...models.create_authorization_response_503 import CreateAuthorizationResponse503
from ...models.object_ import Object
from ...models.object_1 import Object1
from ...types import Response

def _get_kwargs(*, body: Object | Object1) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/authorizations'}
    _kwargs['json']: dict[str, Any]
    if isinstance(body, Object):
        _kwargs['json'] = body.to_dict()
    else:
        _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> CreateAuthorizationResponse201 | CreateAuthorizationResponse400 | CreateAuthorizationResponse401 | CreateAuthorizationResponse403 | CreateAuthorizationResponse404 | CreateAuthorizationResponse500 | CreateAuthorizationResponse503 | None:
    if response.status_code == 201:
        response_201 = CreateAuthorizationResponse201.from_dict(response.json())
        return response_201
    if response.status_code == 400:
        response_400 = CreateAuthorizationResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = CreateAuthorizationResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = CreateAuthorizationResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = CreateAuthorizationResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = CreateAuthorizationResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = CreateAuthorizationResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[CreateAuthorizationResponse201 | CreateAuthorizationResponse400 | CreateAuthorizationResponse401 | CreateAuthorizationResponse403 | CreateAuthorizationResponse404 | CreateAuthorizationResponse500 | CreateAuthorizationResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(*, client: AuthenticatedClient | Client, body: Object | Object1) -> Response[CreateAuthorizationResponse201 | CreateAuthorizationResponse400 | CreateAuthorizationResponse401 | CreateAuthorizationResponse403 | CreateAuthorizationResponse404 | CreateAuthorizationResponse500 | CreateAuthorizationResponse503]:
    """Create authorization

     Create the authorization.

    Args:
        body (Object | Object1): Defines an authorization request.
            Either an id-based or a property-based authorization can be provided.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateAuthorizationResponse201 | CreateAuthorizationResponse400 | CreateAuthorizationResponse401 | CreateAuthorizationResponse403 | CreateAuthorizationResponse404 | CreateAuthorizationResponse500 | CreateAuthorizationResponse503]
    """
    kwargs = _get_kwargs(body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(*, client: AuthenticatedClient | Client, body: Object | Object1, **kwargs) -> CreateAuthorizationResponse201:
    """Create authorization

 Create the authorization.

Args:
    body (Object | Object1): Defines an authorization request.
        Either an id-based or a property-based authorization can be provided.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateAuthorizationResponse201 | CreateAuthorizationResponse400 | CreateAuthorizationResponse401 | CreateAuthorizationResponse403 | CreateAuthorizationResponse404 | CreateAuthorizationResponse500 | CreateAuthorizationResponse503]"""
    response = sync_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(*, client: AuthenticatedClient | Client, body: Object | Object1) -> Response[CreateAuthorizationResponse201 | CreateAuthorizationResponse400 | CreateAuthorizationResponse401 | CreateAuthorizationResponse403 | CreateAuthorizationResponse404 | CreateAuthorizationResponse500 | CreateAuthorizationResponse503]:
    """Create authorization

     Create the authorization.

    Args:
        body (Object | Object1): Defines an authorization request.
            Either an id-based or a property-based authorization can be provided.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateAuthorizationResponse201 | CreateAuthorizationResponse400 | CreateAuthorizationResponse401 | CreateAuthorizationResponse403 | CreateAuthorizationResponse404 | CreateAuthorizationResponse500 | CreateAuthorizationResponse503]
    """
    kwargs = _get_kwargs(body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(*, client: AuthenticatedClient | Client, body: Object | Object1, **kwargs) -> CreateAuthorizationResponse201:
    """Create authorization

 Create the authorization.

Args:
    body (Object | Object1): Defines an authorization request.
        Either an id-based or a property-based authorization can be provided.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateAuthorizationResponse201 | CreateAuthorizationResponse400 | CreateAuthorizationResponse401 | CreateAuthorizationResponse403 | CreateAuthorizationResponse404 | CreateAuthorizationResponse500 | CreateAuthorizationResponse503]"""
    response = await asyncio_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
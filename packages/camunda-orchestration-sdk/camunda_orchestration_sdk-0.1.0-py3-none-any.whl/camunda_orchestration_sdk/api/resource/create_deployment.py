from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_deployment_data import CreateDeploymentData
from ...models.create_deployment_response_200 import CreateDeploymentResponse200
from ...models.create_deployment_response_400 import CreateDeploymentResponse400
from ...models.create_deployment_response_503 import CreateDeploymentResponse503
from ...types import Response

def _get_kwargs(*, body: CreateDeploymentData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/deployments'}
    _kwargs['files'] = body.to_multipart()
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> CreateDeploymentResponse200 | CreateDeploymentResponse400 | CreateDeploymentResponse503 | None:
    if response.status_code == 200:
        response_200 = CreateDeploymentResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = CreateDeploymentResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 503:
        response_503 = CreateDeploymentResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[CreateDeploymentResponse200 | CreateDeploymentResponse400 | CreateDeploymentResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(*, client: AuthenticatedClient | Client, body: CreateDeploymentData) -> Response[CreateDeploymentResponse200 | CreateDeploymentResponse400 | CreateDeploymentResponse503]:
    """Deploy resources

     Deploys one or more resources (e.g. processes, decision models, or forms).
    This is an atomic call, i.e. either all resources are deployed or none of them are.

    Args:
        body (CreateDeploymentData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateDeploymentResponse200 | CreateDeploymentResponse400 | CreateDeploymentResponse503]
    """
    kwargs = _get_kwargs(body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(*, client: AuthenticatedClient | Client, body: CreateDeploymentData, **kwargs) -> CreateDeploymentResponse200:
    """Deploy resources

 Deploys one or more resources (e.g. processes, decision models, or forms).
This is an atomic call, i.e. either all resources are deployed or none of them are.

Args:
    body (CreateDeploymentData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateDeploymentResponse200 | CreateDeploymentResponse400 | CreateDeploymentResponse503]"""
    response = sync_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(*, client: AuthenticatedClient | Client, body: CreateDeploymentData) -> Response[CreateDeploymentResponse200 | CreateDeploymentResponse400 | CreateDeploymentResponse503]:
    """Deploy resources

     Deploys one or more resources (e.g. processes, decision models, or forms).
    This is an atomic call, i.e. either all resources are deployed or none of them are.

    Args:
        body (CreateDeploymentData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateDeploymentResponse200 | CreateDeploymentResponse400 | CreateDeploymentResponse503]
    """
    kwargs = _get_kwargs(body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(*, client: AuthenticatedClient | Client, body: CreateDeploymentData, **kwargs) -> CreateDeploymentResponse200:
    """Deploy resources

 Deploys one or more resources (e.g. processes, decision models, or forms).
This is an atomic call, i.e. either all resources are deployed or none of them are.

Args:
    body (CreateDeploymentData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateDeploymentResponse200 | CreateDeploymentResponse400 | CreateDeploymentResponse503]"""
    response = await asyncio_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.search_decision_instances_data import SearchDecisionInstancesData
from ...models.search_decision_instances_response_200 import SearchDecisionInstancesResponse200
from ...models.search_decision_instances_response_400 import SearchDecisionInstancesResponse400
from ...models.search_decision_instances_response_401 import SearchDecisionInstancesResponse401
from ...models.search_decision_instances_response_403 import SearchDecisionInstancesResponse403
from ...models.search_decision_instances_response_500 import SearchDecisionInstancesResponse500
from ...types import Response

def _get_kwargs(*, body: SearchDecisionInstancesData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/decision-instances/search'}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> SearchDecisionInstancesResponse200 | SearchDecisionInstancesResponse400 | SearchDecisionInstancesResponse401 | SearchDecisionInstancesResponse403 | SearchDecisionInstancesResponse500 | None:
    if response.status_code == 200:
        response_200 = SearchDecisionInstancesResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = SearchDecisionInstancesResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = SearchDecisionInstancesResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = SearchDecisionInstancesResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 500:
        response_500 = SearchDecisionInstancesResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[SearchDecisionInstancesResponse200 | SearchDecisionInstancesResponse400 | SearchDecisionInstancesResponse401 | SearchDecisionInstancesResponse403 | SearchDecisionInstancesResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(*, client: AuthenticatedClient | Client, body: SearchDecisionInstancesData) -> Response[SearchDecisionInstancesResponse200 | SearchDecisionInstancesResponse400 | SearchDecisionInstancesResponse401 | SearchDecisionInstancesResponse403 | SearchDecisionInstancesResponse500]:
    """Search decision instances

     Search for decision instances based on given criteria.

    Args:
        body (SearchDecisionInstancesData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchDecisionInstancesResponse200 | SearchDecisionInstancesResponse400 | SearchDecisionInstancesResponse401 | SearchDecisionInstancesResponse403 | SearchDecisionInstancesResponse500]
    """
    kwargs = _get_kwargs(body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(*, client: AuthenticatedClient | Client, body: SearchDecisionInstancesData, **kwargs) -> SearchDecisionInstancesResponse200:
    """Search decision instances

 Search for decision instances based on given criteria.

Args:
    body (SearchDecisionInstancesData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchDecisionInstancesResponse200 | SearchDecisionInstancesResponse400 | SearchDecisionInstancesResponse401 | SearchDecisionInstancesResponse403 | SearchDecisionInstancesResponse500]"""
    response = sync_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(*, client: AuthenticatedClient | Client, body: SearchDecisionInstancesData) -> Response[SearchDecisionInstancesResponse200 | SearchDecisionInstancesResponse400 | SearchDecisionInstancesResponse401 | SearchDecisionInstancesResponse403 | SearchDecisionInstancesResponse500]:
    """Search decision instances

     Search for decision instances based on given criteria.

    Args:
        body (SearchDecisionInstancesData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchDecisionInstancesResponse200 | SearchDecisionInstancesResponse400 | SearchDecisionInstancesResponse401 | SearchDecisionInstancesResponse403 | SearchDecisionInstancesResponse500]
    """
    kwargs = _get_kwargs(body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(*, client: AuthenticatedClient | Client, body: SearchDecisionInstancesData, **kwargs) -> SearchDecisionInstancesResponse200:
    """Search decision instances

 Search for decision instances based on given criteria.

Args:
    body (SearchDecisionInstancesData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchDecisionInstancesResponse200 | SearchDecisionInstancesResponse400 | SearchDecisionInstancesResponse401 | SearchDecisionInstancesResponse403 | SearchDecisionInstancesResponse500]"""
    response = await asyncio_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
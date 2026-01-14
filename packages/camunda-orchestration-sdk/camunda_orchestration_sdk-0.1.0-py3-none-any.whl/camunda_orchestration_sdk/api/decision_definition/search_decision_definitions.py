from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.search_decision_definitions_data import SearchDecisionDefinitionsData
from ...models.search_decision_definitions_response_200 import SearchDecisionDefinitionsResponse200
from ...models.search_decision_definitions_response_400 import SearchDecisionDefinitionsResponse400
from ...models.search_decision_definitions_response_401 import SearchDecisionDefinitionsResponse401
from ...models.search_decision_definitions_response_403 import SearchDecisionDefinitionsResponse403
from ...models.search_decision_definitions_response_500 import SearchDecisionDefinitionsResponse500
from ...types import Response

def _get_kwargs(*, body: SearchDecisionDefinitionsData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/decision-definitions/search'}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> SearchDecisionDefinitionsResponse200 | SearchDecisionDefinitionsResponse400 | SearchDecisionDefinitionsResponse401 | SearchDecisionDefinitionsResponse403 | SearchDecisionDefinitionsResponse500 | None:
    if response.status_code == 200:
        response_200 = SearchDecisionDefinitionsResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = SearchDecisionDefinitionsResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = SearchDecisionDefinitionsResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = SearchDecisionDefinitionsResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 500:
        response_500 = SearchDecisionDefinitionsResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[SearchDecisionDefinitionsResponse200 | SearchDecisionDefinitionsResponse400 | SearchDecisionDefinitionsResponse401 | SearchDecisionDefinitionsResponse403 | SearchDecisionDefinitionsResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(*, client: AuthenticatedClient | Client, body: SearchDecisionDefinitionsData) -> Response[SearchDecisionDefinitionsResponse200 | SearchDecisionDefinitionsResponse400 | SearchDecisionDefinitionsResponse401 | SearchDecisionDefinitionsResponse403 | SearchDecisionDefinitionsResponse500]:
    """Search decision definitions

     Search for decision definitions based on given criteria.

    Args:
        body (SearchDecisionDefinitionsData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchDecisionDefinitionsResponse200 | SearchDecisionDefinitionsResponse400 | SearchDecisionDefinitionsResponse401 | SearchDecisionDefinitionsResponse403 | SearchDecisionDefinitionsResponse500]
    """
    kwargs = _get_kwargs(body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(*, client: AuthenticatedClient | Client, body: SearchDecisionDefinitionsData, **kwargs) -> SearchDecisionDefinitionsResponse200:
    """Search decision definitions

 Search for decision definitions based on given criteria.

Args:
    body (SearchDecisionDefinitionsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchDecisionDefinitionsResponse200 | SearchDecisionDefinitionsResponse400 | SearchDecisionDefinitionsResponse401 | SearchDecisionDefinitionsResponse403 | SearchDecisionDefinitionsResponse500]"""
    response = sync_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(*, client: AuthenticatedClient | Client, body: SearchDecisionDefinitionsData) -> Response[SearchDecisionDefinitionsResponse200 | SearchDecisionDefinitionsResponse400 | SearchDecisionDefinitionsResponse401 | SearchDecisionDefinitionsResponse403 | SearchDecisionDefinitionsResponse500]:
    """Search decision definitions

     Search for decision definitions based on given criteria.

    Args:
        body (SearchDecisionDefinitionsData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchDecisionDefinitionsResponse200 | SearchDecisionDefinitionsResponse400 | SearchDecisionDefinitionsResponse401 | SearchDecisionDefinitionsResponse403 | SearchDecisionDefinitionsResponse500]
    """
    kwargs = _get_kwargs(body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(*, client: AuthenticatedClient | Client, body: SearchDecisionDefinitionsData, **kwargs) -> SearchDecisionDefinitionsResponse200:
    """Search decision definitions

 Search for decision definitions based on given criteria.

Args:
    body (SearchDecisionDefinitionsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchDecisionDefinitionsResponse200 | SearchDecisionDefinitionsResponse400 | SearchDecisionDefinitionsResponse401 | SearchDecisionDefinitionsResponse403 | SearchDecisionDefinitionsResponse500]"""
    response = await asyncio_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
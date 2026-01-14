from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.search_mapping_rule_data import SearchMappingRuleData
from ...models.search_mapping_rule_response_200 import SearchMappingRuleResponse200
from ...models.search_mapping_rule_response_400 import SearchMappingRuleResponse400
from ...models.search_mapping_rule_response_401 import SearchMappingRuleResponse401
from ...models.search_mapping_rule_response_403 import SearchMappingRuleResponse403
from ...models.search_mapping_rule_response_500 import SearchMappingRuleResponse500
from ...types import Response

def _get_kwargs(*, body: SearchMappingRuleData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/mapping-rules/search'}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> SearchMappingRuleResponse200 | SearchMappingRuleResponse400 | SearchMappingRuleResponse401 | SearchMappingRuleResponse403 | SearchMappingRuleResponse500 | None:
    if response.status_code == 200:
        response_200 = SearchMappingRuleResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = SearchMappingRuleResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = SearchMappingRuleResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = SearchMappingRuleResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 500:
        response_500 = SearchMappingRuleResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[SearchMappingRuleResponse200 | SearchMappingRuleResponse400 | SearchMappingRuleResponse401 | SearchMappingRuleResponse403 | SearchMappingRuleResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(*, client: AuthenticatedClient | Client, body: SearchMappingRuleData) -> Response[SearchMappingRuleResponse200 | SearchMappingRuleResponse400 | SearchMappingRuleResponse401 | SearchMappingRuleResponse403 | SearchMappingRuleResponse500]:
    """Search mapping rules

     Search for mapping rules based on given criteria.

    Args:
        body (SearchMappingRuleData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchMappingRuleResponse200 | SearchMappingRuleResponse400 | SearchMappingRuleResponse401 | SearchMappingRuleResponse403 | SearchMappingRuleResponse500]
    """
    kwargs = _get_kwargs(body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(*, client: AuthenticatedClient | Client, body: SearchMappingRuleData, **kwargs) -> SearchMappingRuleResponse200:
    """Search mapping rules

 Search for mapping rules based on given criteria.

Args:
    body (SearchMappingRuleData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchMappingRuleResponse200 | SearchMappingRuleResponse400 | SearchMappingRuleResponse401 | SearchMappingRuleResponse403 | SearchMappingRuleResponse500]"""
    response = sync_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(*, client: AuthenticatedClient | Client, body: SearchMappingRuleData) -> Response[SearchMappingRuleResponse200 | SearchMappingRuleResponse400 | SearchMappingRuleResponse401 | SearchMappingRuleResponse403 | SearchMappingRuleResponse500]:
    """Search mapping rules

     Search for mapping rules based on given criteria.

    Args:
        body (SearchMappingRuleData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchMappingRuleResponse200 | SearchMappingRuleResponse400 | SearchMappingRuleResponse401 | SearchMappingRuleResponse403 | SearchMappingRuleResponse500]
    """
    kwargs = _get_kwargs(body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(*, client: AuthenticatedClient | Client, body: SearchMappingRuleData, **kwargs) -> SearchMappingRuleResponse200:
    """Search mapping rules

 Search for mapping rules based on given criteria.

Args:
    body (SearchMappingRuleData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchMappingRuleResponse200 | SearchMappingRuleResponse400 | SearchMappingRuleResponse401 | SearchMappingRuleResponse403 | SearchMappingRuleResponse500]"""
    response = await asyncio_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
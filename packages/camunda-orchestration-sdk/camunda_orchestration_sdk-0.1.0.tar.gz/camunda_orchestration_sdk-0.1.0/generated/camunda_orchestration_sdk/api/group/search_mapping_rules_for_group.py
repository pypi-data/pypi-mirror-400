from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.search_mapping_rules_for_group_data import SearchMappingRulesForGroupData
from ...models.search_mapping_rules_for_group_response_200 import SearchMappingRulesForGroupResponse200
from ...models.search_mapping_rules_for_group_response_400 import SearchMappingRulesForGroupResponse400
from ...models.search_mapping_rules_for_group_response_401 import SearchMappingRulesForGroupResponse401
from ...models.search_mapping_rules_for_group_response_403 import SearchMappingRulesForGroupResponse403
from ...models.search_mapping_rules_for_group_response_404 import SearchMappingRulesForGroupResponse404
from ...models.search_mapping_rules_for_group_response_500 import SearchMappingRulesForGroupResponse500
from ...types import Response

def _get_kwargs(group_id: str, *, body: SearchMappingRulesForGroupData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/groups/{group_id}/mapping-rules/search'.format(group_id=group_id)}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> SearchMappingRulesForGroupResponse200 | SearchMappingRulesForGroupResponse400 | SearchMappingRulesForGroupResponse401 | SearchMappingRulesForGroupResponse403 | SearchMappingRulesForGroupResponse404 | SearchMappingRulesForGroupResponse500 | None:
    if response.status_code == 200:
        response_200 = SearchMappingRulesForGroupResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = SearchMappingRulesForGroupResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = SearchMappingRulesForGroupResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = SearchMappingRulesForGroupResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = SearchMappingRulesForGroupResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = SearchMappingRulesForGroupResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[SearchMappingRulesForGroupResponse200 | SearchMappingRulesForGroupResponse400 | SearchMappingRulesForGroupResponse401 | SearchMappingRulesForGroupResponse403 | SearchMappingRulesForGroupResponse404 | SearchMappingRulesForGroupResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(group_id: str, *, client: AuthenticatedClient | Client, body: SearchMappingRulesForGroupData) -> Response[SearchMappingRulesForGroupResponse200 | SearchMappingRulesForGroupResponse400 | SearchMappingRulesForGroupResponse401 | SearchMappingRulesForGroupResponse403 | SearchMappingRulesForGroupResponse404 | SearchMappingRulesForGroupResponse500]:
    """Search group mapping rules

     Search mapping rules assigned to a group.

    Args:
        group_id (str):
        body (SearchMappingRulesForGroupData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchMappingRulesForGroupResponse200 | SearchMappingRulesForGroupResponse400 | SearchMappingRulesForGroupResponse401 | SearchMappingRulesForGroupResponse403 | SearchMappingRulesForGroupResponse404 | SearchMappingRulesForGroupResponse500]
    """
    kwargs = _get_kwargs(group_id=group_id, body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(group_id: str, *, client: AuthenticatedClient | Client, body: SearchMappingRulesForGroupData, **kwargs) -> SearchMappingRulesForGroupResponse200:
    """Search group mapping rules

 Search mapping rules assigned to a group.

Args:
    group_id (str):
    body (SearchMappingRulesForGroupData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchMappingRulesForGroupResponse200 | SearchMappingRulesForGroupResponse400 | SearchMappingRulesForGroupResponse401 | SearchMappingRulesForGroupResponse403 | SearchMappingRulesForGroupResponse404 | SearchMappingRulesForGroupResponse500]"""
    response = sync_detailed(group_id=group_id, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(group_id: str, *, client: AuthenticatedClient | Client, body: SearchMappingRulesForGroupData) -> Response[SearchMappingRulesForGroupResponse200 | SearchMappingRulesForGroupResponse400 | SearchMappingRulesForGroupResponse401 | SearchMappingRulesForGroupResponse403 | SearchMappingRulesForGroupResponse404 | SearchMappingRulesForGroupResponse500]:
    """Search group mapping rules

     Search mapping rules assigned to a group.

    Args:
        group_id (str):
        body (SearchMappingRulesForGroupData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchMappingRulesForGroupResponse200 | SearchMappingRulesForGroupResponse400 | SearchMappingRulesForGroupResponse401 | SearchMappingRulesForGroupResponse403 | SearchMappingRulesForGroupResponse404 | SearchMappingRulesForGroupResponse500]
    """
    kwargs = _get_kwargs(group_id=group_id, body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(group_id: str, *, client: AuthenticatedClient | Client, body: SearchMappingRulesForGroupData, **kwargs) -> SearchMappingRulesForGroupResponse200:
    """Search group mapping rules

 Search mapping rules assigned to a group.

Args:
    group_id (str):
    body (SearchMappingRulesForGroupData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchMappingRulesForGroupResponse200 | SearchMappingRulesForGroupResponse400 | SearchMappingRulesForGroupResponse401 | SearchMappingRulesForGroupResponse403 | SearchMappingRulesForGroupResponse404 | SearchMappingRulesForGroupResponse500]"""
    response = await asyncio_detailed(group_id=group_id, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
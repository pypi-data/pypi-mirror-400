from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.search_mapping_rules_for_role_data import SearchMappingRulesForRoleData
from ...models.search_mapping_rules_for_role_response_200 import SearchMappingRulesForRoleResponse200
from ...models.search_mapping_rules_for_role_response_400 import SearchMappingRulesForRoleResponse400
from ...models.search_mapping_rules_for_role_response_401 import SearchMappingRulesForRoleResponse401
from ...models.search_mapping_rules_for_role_response_403 import SearchMappingRulesForRoleResponse403
from ...models.search_mapping_rules_for_role_response_404 import SearchMappingRulesForRoleResponse404
from ...models.search_mapping_rules_for_role_response_500 import SearchMappingRulesForRoleResponse500
from ...types import Response

def _get_kwargs(role_id: str, *, body: SearchMappingRulesForRoleData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/roles/{role_id}/mapping-rules/search'.format(role_id=role_id)}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> SearchMappingRulesForRoleResponse200 | SearchMappingRulesForRoleResponse400 | SearchMappingRulesForRoleResponse401 | SearchMappingRulesForRoleResponse403 | SearchMappingRulesForRoleResponse404 | SearchMappingRulesForRoleResponse500 | None:
    if response.status_code == 200:
        response_200 = SearchMappingRulesForRoleResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = SearchMappingRulesForRoleResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = SearchMappingRulesForRoleResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = SearchMappingRulesForRoleResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = SearchMappingRulesForRoleResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = SearchMappingRulesForRoleResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[SearchMappingRulesForRoleResponse200 | SearchMappingRulesForRoleResponse400 | SearchMappingRulesForRoleResponse401 | SearchMappingRulesForRoleResponse403 | SearchMappingRulesForRoleResponse404 | SearchMappingRulesForRoleResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(role_id: str, *, client: AuthenticatedClient | Client, body: SearchMappingRulesForRoleData) -> Response[SearchMappingRulesForRoleResponse200 | SearchMappingRulesForRoleResponse400 | SearchMappingRulesForRoleResponse401 | SearchMappingRulesForRoleResponse403 | SearchMappingRulesForRoleResponse404 | SearchMappingRulesForRoleResponse500]:
    """Search role mapping rules

     Search mapping rules with assigned role.

    Args:
        role_id (str):
        body (SearchMappingRulesForRoleData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchMappingRulesForRoleResponse200 | SearchMappingRulesForRoleResponse400 | SearchMappingRulesForRoleResponse401 | SearchMappingRulesForRoleResponse403 | SearchMappingRulesForRoleResponse404 | SearchMappingRulesForRoleResponse500]
    """
    kwargs = _get_kwargs(role_id=role_id, body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(role_id: str, *, client: AuthenticatedClient | Client, body: SearchMappingRulesForRoleData, **kwargs) -> SearchMappingRulesForRoleResponse200:
    """Search role mapping rules

 Search mapping rules with assigned role.

Args:
    role_id (str):
    body (SearchMappingRulesForRoleData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchMappingRulesForRoleResponse200 | SearchMappingRulesForRoleResponse400 | SearchMappingRulesForRoleResponse401 | SearchMappingRulesForRoleResponse403 | SearchMappingRulesForRoleResponse404 | SearchMappingRulesForRoleResponse500]"""
    response = sync_detailed(role_id=role_id, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(role_id: str, *, client: AuthenticatedClient | Client, body: SearchMappingRulesForRoleData) -> Response[SearchMappingRulesForRoleResponse200 | SearchMappingRulesForRoleResponse400 | SearchMappingRulesForRoleResponse401 | SearchMappingRulesForRoleResponse403 | SearchMappingRulesForRoleResponse404 | SearchMappingRulesForRoleResponse500]:
    """Search role mapping rules

     Search mapping rules with assigned role.

    Args:
        role_id (str):
        body (SearchMappingRulesForRoleData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchMappingRulesForRoleResponse200 | SearchMappingRulesForRoleResponse400 | SearchMappingRulesForRoleResponse401 | SearchMappingRulesForRoleResponse403 | SearchMappingRulesForRoleResponse404 | SearchMappingRulesForRoleResponse500]
    """
    kwargs = _get_kwargs(role_id=role_id, body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(role_id: str, *, client: AuthenticatedClient | Client, body: SearchMappingRulesForRoleData, **kwargs) -> SearchMappingRulesForRoleResponse200:
    """Search role mapping rules

 Search mapping rules with assigned role.

Args:
    role_id (str):
    body (SearchMappingRulesForRoleData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchMappingRulesForRoleResponse200 | SearchMappingRulesForRoleResponse400 | SearchMappingRulesForRoleResponse401 | SearchMappingRulesForRoleResponse403 | SearchMappingRulesForRoleResponse404 | SearchMappingRulesForRoleResponse500]"""
    response = await asyncio_detailed(role_id=role_id, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
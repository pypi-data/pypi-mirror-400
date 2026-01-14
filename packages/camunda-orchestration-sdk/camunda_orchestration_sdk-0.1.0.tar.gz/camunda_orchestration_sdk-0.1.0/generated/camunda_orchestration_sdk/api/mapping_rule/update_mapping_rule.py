from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.update_mapping_rule_data import UpdateMappingRuleData
from ...models.update_mapping_rule_response_200 import UpdateMappingRuleResponse200
from ...models.update_mapping_rule_response_400 import UpdateMappingRuleResponse400
from ...models.update_mapping_rule_response_403 import UpdateMappingRuleResponse403
from ...models.update_mapping_rule_response_404 import UpdateMappingRuleResponse404
from ...models.update_mapping_rule_response_500 import UpdateMappingRuleResponse500
from ...models.update_mapping_rule_response_503 import UpdateMappingRuleResponse503
from ...types import Response

def _get_kwargs(mapping_rule_id: str, *, body: UpdateMappingRuleData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'put', 'url': '/mapping-rules/{mapping_rule_id}'.format(mapping_rule_id=mapping_rule_id)}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> UpdateMappingRuleResponse200 | UpdateMappingRuleResponse400 | UpdateMappingRuleResponse403 | UpdateMappingRuleResponse404 | UpdateMappingRuleResponse500 | UpdateMappingRuleResponse503 | None:
    if response.status_code == 200:
        response_200 = UpdateMappingRuleResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = UpdateMappingRuleResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 403:
        response_403 = UpdateMappingRuleResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = UpdateMappingRuleResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = UpdateMappingRuleResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = UpdateMappingRuleResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[UpdateMappingRuleResponse200 | UpdateMappingRuleResponse400 | UpdateMappingRuleResponse403 | UpdateMappingRuleResponse404 | UpdateMappingRuleResponse500 | UpdateMappingRuleResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(mapping_rule_id: str, *, client: AuthenticatedClient | Client, body: UpdateMappingRuleData) -> Response[UpdateMappingRuleResponse200 | UpdateMappingRuleResponse400 | UpdateMappingRuleResponse403 | UpdateMappingRuleResponse404 | UpdateMappingRuleResponse500 | UpdateMappingRuleResponse503]:
    """Update mapping rule

     Update a mapping rule.

    Args:
        mapping_rule_id (str):
        body (UpdateMappingRuleData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UpdateMappingRuleResponse200 | UpdateMappingRuleResponse400 | UpdateMappingRuleResponse403 | UpdateMappingRuleResponse404 | UpdateMappingRuleResponse500 | UpdateMappingRuleResponse503]
    """
    kwargs = _get_kwargs(mapping_rule_id=mapping_rule_id, body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(mapping_rule_id: str, *, client: AuthenticatedClient | Client, body: UpdateMappingRuleData, **kwargs) -> UpdateMappingRuleResponse200:
    """Update mapping rule

 Update a mapping rule.

Args:
    mapping_rule_id (str):
    body (UpdateMappingRuleData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[UpdateMappingRuleResponse200 | UpdateMappingRuleResponse400 | UpdateMappingRuleResponse403 | UpdateMappingRuleResponse404 | UpdateMappingRuleResponse500 | UpdateMappingRuleResponse503]"""
    response = sync_detailed(mapping_rule_id=mapping_rule_id, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(mapping_rule_id: str, *, client: AuthenticatedClient | Client, body: UpdateMappingRuleData) -> Response[UpdateMappingRuleResponse200 | UpdateMappingRuleResponse400 | UpdateMappingRuleResponse403 | UpdateMappingRuleResponse404 | UpdateMappingRuleResponse500 | UpdateMappingRuleResponse503]:
    """Update mapping rule

     Update a mapping rule.

    Args:
        mapping_rule_id (str):
        body (UpdateMappingRuleData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UpdateMappingRuleResponse200 | UpdateMappingRuleResponse400 | UpdateMappingRuleResponse403 | UpdateMappingRuleResponse404 | UpdateMappingRuleResponse500 | UpdateMappingRuleResponse503]
    """
    kwargs = _get_kwargs(mapping_rule_id=mapping_rule_id, body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(mapping_rule_id: str, *, client: AuthenticatedClient | Client, body: UpdateMappingRuleData, **kwargs) -> UpdateMappingRuleResponse200:
    """Update mapping rule

 Update a mapping rule.

Args:
    mapping_rule_id (str):
    body (UpdateMappingRuleData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[UpdateMappingRuleResponse200 | UpdateMappingRuleResponse400 | UpdateMappingRuleResponse403 | UpdateMappingRuleResponse404 | UpdateMappingRuleResponse500 | UpdateMappingRuleResponse503]"""
    response = await asyncio_detailed(mapping_rule_id=mapping_rule_id, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
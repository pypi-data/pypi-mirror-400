from http import HTTPStatus
from typing import Any, cast
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.unassign_mapping_rule_from_group_response_400 import UnassignMappingRuleFromGroupResponse400
from ...models.unassign_mapping_rule_from_group_response_403 import UnassignMappingRuleFromGroupResponse403
from ...models.unassign_mapping_rule_from_group_response_404 import UnassignMappingRuleFromGroupResponse404
from ...models.unassign_mapping_rule_from_group_response_500 import UnassignMappingRuleFromGroupResponse500
from ...models.unassign_mapping_rule_from_group_response_503 import UnassignMappingRuleFromGroupResponse503
from ...types import Response

def _get_kwargs(group_id: str, mapping_rule_id: str) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {'method': 'delete', 'url': '/groups/{group_id}/mapping-rules/{mapping_rule_id}'.format(group_id=group_id, mapping_rule_id=mapping_rule_id)}
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | UnassignMappingRuleFromGroupResponse400 | UnassignMappingRuleFromGroupResponse403 | UnassignMappingRuleFromGroupResponse404 | UnassignMappingRuleFromGroupResponse500 | UnassignMappingRuleFromGroupResponse503 | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 400:
        response_400 = UnassignMappingRuleFromGroupResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 403:
        response_403 = UnassignMappingRuleFromGroupResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = UnassignMappingRuleFromGroupResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = UnassignMappingRuleFromGroupResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = UnassignMappingRuleFromGroupResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | UnassignMappingRuleFromGroupResponse400 | UnassignMappingRuleFromGroupResponse403 | UnassignMappingRuleFromGroupResponse404 | UnassignMappingRuleFromGroupResponse500 | UnassignMappingRuleFromGroupResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(group_id: str, mapping_rule_id: str, *, client: AuthenticatedClient | Client) -> Response[Any | UnassignMappingRuleFromGroupResponse400 | UnassignMappingRuleFromGroupResponse403 | UnassignMappingRuleFromGroupResponse404 | UnassignMappingRuleFromGroupResponse500 | UnassignMappingRuleFromGroupResponse503]:
    """Unassign a mapping rule from a group

     Unassigns a mapping rule from a group.

    Args:
        group_id (str):
        mapping_rule_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | UnassignMappingRuleFromGroupResponse400 | UnassignMappingRuleFromGroupResponse403 | UnassignMappingRuleFromGroupResponse404 | UnassignMappingRuleFromGroupResponse500 | UnassignMappingRuleFromGroupResponse503]
    """
    kwargs = _get_kwargs(group_id=group_id, mapping_rule_id=mapping_rule_id)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(group_id: str, mapping_rule_id: str, *, client: AuthenticatedClient | Client, **kwargs) -> Any:
    """Unassign a mapping rule from a group

 Unassigns a mapping rule from a group.

Args:
    group_id (str):
    mapping_rule_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignMappingRuleFromGroupResponse400 | UnassignMappingRuleFromGroupResponse403 | UnassignMappingRuleFromGroupResponse404 | UnassignMappingRuleFromGroupResponse500 | UnassignMappingRuleFromGroupResponse503]"""
    response = sync_detailed(group_id=group_id, mapping_rule_id=mapping_rule_id, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(group_id: str, mapping_rule_id: str, *, client: AuthenticatedClient | Client) -> Response[Any | UnassignMappingRuleFromGroupResponse400 | UnassignMappingRuleFromGroupResponse403 | UnassignMappingRuleFromGroupResponse404 | UnassignMappingRuleFromGroupResponse500 | UnassignMappingRuleFromGroupResponse503]:
    """Unassign a mapping rule from a group

     Unassigns a mapping rule from a group.

    Args:
        group_id (str):
        mapping_rule_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | UnassignMappingRuleFromGroupResponse400 | UnassignMappingRuleFromGroupResponse403 | UnassignMappingRuleFromGroupResponse404 | UnassignMappingRuleFromGroupResponse500 | UnassignMappingRuleFromGroupResponse503]
    """
    kwargs = _get_kwargs(group_id=group_id, mapping_rule_id=mapping_rule_id)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(group_id: str, mapping_rule_id: str, *, client: AuthenticatedClient | Client, **kwargs) -> Any:
    """Unassign a mapping rule from a group

 Unassigns a mapping rule from a group.

Args:
    group_id (str):
    mapping_rule_id (str):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | UnassignMappingRuleFromGroupResponse400 | UnassignMappingRuleFromGroupResponse403 | UnassignMappingRuleFromGroupResponse404 | UnassignMappingRuleFromGroupResponse500 | UnassignMappingRuleFromGroupResponse503]"""
    response = await asyncio_detailed(group_id=group_id, mapping_rule_id=mapping_rule_id, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
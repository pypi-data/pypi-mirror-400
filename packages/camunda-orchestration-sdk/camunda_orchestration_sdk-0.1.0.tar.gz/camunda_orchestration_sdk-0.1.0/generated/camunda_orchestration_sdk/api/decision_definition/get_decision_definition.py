from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_decision_definition_response_200 import GetDecisionDefinitionResponse200
from ...models.get_decision_definition_response_400 import GetDecisionDefinitionResponse400
from ...models.get_decision_definition_response_401 import GetDecisionDefinitionResponse401
from ...models.get_decision_definition_response_403 import GetDecisionDefinitionResponse403
from ...models.get_decision_definition_response_404 import GetDecisionDefinitionResponse404
from ...models.get_decision_definition_response_500 import GetDecisionDefinitionResponse500
from ...types import Response

def _get_kwargs(decision_definition_key: str) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {'method': 'get', 'url': '/decision-definitions/{decision_definition_key}'.format(decision_definition_key=decision_definition_key)}
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetDecisionDefinitionResponse200 | GetDecisionDefinitionResponse400 | GetDecisionDefinitionResponse401 | GetDecisionDefinitionResponse403 | GetDecisionDefinitionResponse404 | GetDecisionDefinitionResponse500 | None:
    if response.status_code == 200:
        response_200 = GetDecisionDefinitionResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = GetDecisionDefinitionResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = GetDecisionDefinitionResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = GetDecisionDefinitionResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = GetDecisionDefinitionResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = GetDecisionDefinitionResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GetDecisionDefinitionResponse200 | GetDecisionDefinitionResponse400 | GetDecisionDefinitionResponse401 | GetDecisionDefinitionResponse403 | GetDecisionDefinitionResponse404 | GetDecisionDefinitionResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(decision_definition_key: str, *, client: AuthenticatedClient | Client) -> Response[GetDecisionDefinitionResponse200 | GetDecisionDefinitionResponse400 | GetDecisionDefinitionResponse401 | GetDecisionDefinitionResponse403 | GetDecisionDefinitionResponse404 | GetDecisionDefinitionResponse500]:
    """Get decision definition

     Returns a decision definition by key.

    Args:
        decision_definition_key (str): System-generated key for a decision definition. Example:
            2251799813326547.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetDecisionDefinitionResponse200 | GetDecisionDefinitionResponse400 | GetDecisionDefinitionResponse401 | GetDecisionDefinitionResponse403 | GetDecisionDefinitionResponse404 | GetDecisionDefinitionResponse500]
    """
    kwargs = _get_kwargs(decision_definition_key=decision_definition_key)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(decision_definition_key: str, *, client: AuthenticatedClient | Client, **kwargs) -> GetDecisionDefinitionResponse200:
    """Get decision definition

 Returns a decision definition by key.

Args:
    decision_definition_key (str): System-generated key for a decision definition. Example:
        2251799813326547.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetDecisionDefinitionResponse200 | GetDecisionDefinitionResponse400 | GetDecisionDefinitionResponse401 | GetDecisionDefinitionResponse403 | GetDecisionDefinitionResponse404 | GetDecisionDefinitionResponse500]"""
    response = sync_detailed(decision_definition_key=decision_definition_key, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(decision_definition_key: str, *, client: AuthenticatedClient | Client) -> Response[GetDecisionDefinitionResponse200 | GetDecisionDefinitionResponse400 | GetDecisionDefinitionResponse401 | GetDecisionDefinitionResponse403 | GetDecisionDefinitionResponse404 | GetDecisionDefinitionResponse500]:
    """Get decision definition

     Returns a decision definition by key.

    Args:
        decision_definition_key (str): System-generated key for a decision definition. Example:
            2251799813326547.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetDecisionDefinitionResponse200 | GetDecisionDefinitionResponse400 | GetDecisionDefinitionResponse401 | GetDecisionDefinitionResponse403 | GetDecisionDefinitionResponse404 | GetDecisionDefinitionResponse500]
    """
    kwargs = _get_kwargs(decision_definition_key=decision_definition_key)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(decision_definition_key: str, *, client: AuthenticatedClient | Client, **kwargs) -> GetDecisionDefinitionResponse200:
    """Get decision definition

 Returns a decision definition by key.

Args:
    decision_definition_key (str): System-generated key for a decision definition. Example:
        2251799813326547.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetDecisionDefinitionResponse200 | GetDecisionDefinitionResponse400 | GetDecisionDefinitionResponse401 | GetDecisionDefinitionResponse403 | GetDecisionDefinitionResponse404 | GetDecisionDefinitionResponse500]"""
    response = await asyncio_detailed(decision_definition_key=decision_definition_key, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
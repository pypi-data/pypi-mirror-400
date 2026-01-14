from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_decision_instance_response_200 import GetDecisionInstanceResponse200
from ...models.get_decision_instance_response_400 import GetDecisionInstanceResponse400
from ...models.get_decision_instance_response_401 import GetDecisionInstanceResponse401
from ...models.get_decision_instance_response_403 import GetDecisionInstanceResponse403
from ...models.get_decision_instance_response_404 import GetDecisionInstanceResponse404
from ...models.get_decision_instance_response_500 import GetDecisionInstanceResponse500
from ...types import Response

def _get_kwargs(decision_evaluation_instance_key: str) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {'method': 'get', 'url': '/decision-instances/{decision_evaluation_instance_key}'.format(decision_evaluation_instance_key=decision_evaluation_instance_key)}
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetDecisionInstanceResponse200 | GetDecisionInstanceResponse400 | GetDecisionInstanceResponse401 | GetDecisionInstanceResponse403 | GetDecisionInstanceResponse404 | GetDecisionInstanceResponse500 | None:
    if response.status_code == 200:
        response_200 = GetDecisionInstanceResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = GetDecisionInstanceResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = GetDecisionInstanceResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = GetDecisionInstanceResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = GetDecisionInstanceResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = GetDecisionInstanceResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GetDecisionInstanceResponse200 | GetDecisionInstanceResponse400 | GetDecisionInstanceResponse401 | GetDecisionInstanceResponse403 | GetDecisionInstanceResponse404 | GetDecisionInstanceResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(decision_evaluation_instance_key: str, *, client: AuthenticatedClient | Client) -> Response[GetDecisionInstanceResponse200 | GetDecisionInstanceResponse400 | GetDecisionInstanceResponse401 | GetDecisionInstanceResponse403 | GetDecisionInstanceResponse404 | GetDecisionInstanceResponse500]:
    """Get decision instance

     Returns a decision instance.

    Args:
        decision_evaluation_instance_key (str): System-generated key for a deployed decision
            instance. Example: 22517998136843567.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetDecisionInstanceResponse200 | GetDecisionInstanceResponse400 | GetDecisionInstanceResponse401 | GetDecisionInstanceResponse403 | GetDecisionInstanceResponse404 | GetDecisionInstanceResponse500]
    """
    kwargs = _get_kwargs(decision_evaluation_instance_key=decision_evaluation_instance_key)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(decision_evaluation_instance_key: str, *, client: AuthenticatedClient | Client, **kwargs) -> GetDecisionInstanceResponse200:
    """Get decision instance

 Returns a decision instance.

Args:
    decision_evaluation_instance_key (str): System-generated key for a deployed decision
        instance. Example: 22517998136843567.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetDecisionInstanceResponse200 | GetDecisionInstanceResponse400 | GetDecisionInstanceResponse401 | GetDecisionInstanceResponse403 | GetDecisionInstanceResponse404 | GetDecisionInstanceResponse500]"""
    response = sync_detailed(decision_evaluation_instance_key=decision_evaluation_instance_key, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(decision_evaluation_instance_key: str, *, client: AuthenticatedClient | Client) -> Response[GetDecisionInstanceResponse200 | GetDecisionInstanceResponse400 | GetDecisionInstanceResponse401 | GetDecisionInstanceResponse403 | GetDecisionInstanceResponse404 | GetDecisionInstanceResponse500]:
    """Get decision instance

     Returns a decision instance.

    Args:
        decision_evaluation_instance_key (str): System-generated key for a deployed decision
            instance. Example: 22517998136843567.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetDecisionInstanceResponse200 | GetDecisionInstanceResponse400 | GetDecisionInstanceResponse401 | GetDecisionInstanceResponse403 | GetDecisionInstanceResponse404 | GetDecisionInstanceResponse500]
    """
    kwargs = _get_kwargs(decision_evaluation_instance_key=decision_evaluation_instance_key)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(decision_evaluation_instance_key: str, *, client: AuthenticatedClient | Client, **kwargs) -> GetDecisionInstanceResponse200:
    """Get decision instance

 Returns a decision instance.

Args:
    decision_evaluation_instance_key (str): System-generated key for a deployed decision
        instance. Example: 22517998136843567.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetDecisionInstanceResponse200 | GetDecisionInstanceResponse400 | GetDecisionInstanceResponse401 | GetDecisionInstanceResponse403 | GetDecisionInstanceResponse404 | GetDecisionInstanceResponse500]"""
    response = await asyncio_detailed(decision_evaluation_instance_key=decision_evaluation_instance_key, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
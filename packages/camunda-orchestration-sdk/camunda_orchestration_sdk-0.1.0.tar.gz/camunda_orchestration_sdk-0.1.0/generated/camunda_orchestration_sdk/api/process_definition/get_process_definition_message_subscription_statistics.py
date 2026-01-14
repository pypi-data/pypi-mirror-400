from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_process_definition_message_subscription_statistics_data import GetProcessDefinitionMessageSubscriptionStatisticsData
from ...models.get_process_definition_message_subscription_statistics_response_200 import GetProcessDefinitionMessageSubscriptionStatisticsResponse200
from ...models.get_process_definition_message_subscription_statistics_response_400 import GetProcessDefinitionMessageSubscriptionStatisticsResponse400
from ...models.get_process_definition_message_subscription_statistics_response_401 import GetProcessDefinitionMessageSubscriptionStatisticsResponse401
from ...models.get_process_definition_message_subscription_statistics_response_403 import GetProcessDefinitionMessageSubscriptionStatisticsResponse403
from ...models.get_process_definition_message_subscription_statistics_response_500 import GetProcessDefinitionMessageSubscriptionStatisticsResponse500
from ...types import Response

def _get_kwargs(*, body: GetProcessDefinitionMessageSubscriptionStatisticsData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/process-definitions/statistics/message-subscriptions'}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetProcessDefinitionMessageSubscriptionStatisticsResponse200 | GetProcessDefinitionMessageSubscriptionStatisticsResponse400 | GetProcessDefinitionMessageSubscriptionStatisticsResponse401 | GetProcessDefinitionMessageSubscriptionStatisticsResponse403 | GetProcessDefinitionMessageSubscriptionStatisticsResponse500 | None:
    if response.status_code == 200:
        response_200 = GetProcessDefinitionMessageSubscriptionStatisticsResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = GetProcessDefinitionMessageSubscriptionStatisticsResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = GetProcessDefinitionMessageSubscriptionStatisticsResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = GetProcessDefinitionMessageSubscriptionStatisticsResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 500:
        response_500 = GetProcessDefinitionMessageSubscriptionStatisticsResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GetProcessDefinitionMessageSubscriptionStatisticsResponse200 | GetProcessDefinitionMessageSubscriptionStatisticsResponse400 | GetProcessDefinitionMessageSubscriptionStatisticsResponse401 | GetProcessDefinitionMessageSubscriptionStatisticsResponse403 | GetProcessDefinitionMessageSubscriptionStatisticsResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(*, client: AuthenticatedClient | Client, body: GetProcessDefinitionMessageSubscriptionStatisticsData) -> Response[GetProcessDefinitionMessageSubscriptionStatisticsResponse200 | GetProcessDefinitionMessageSubscriptionStatisticsResponse400 | GetProcessDefinitionMessageSubscriptionStatisticsResponse401 | GetProcessDefinitionMessageSubscriptionStatisticsResponse403 | GetProcessDefinitionMessageSubscriptionStatisticsResponse500]:
    """Get message subscription statistics

     Get message subscription statistics, grouped by process definition.

    Args:
        body (GetProcessDefinitionMessageSubscriptionStatisticsData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetProcessDefinitionMessageSubscriptionStatisticsResponse200 | GetProcessDefinitionMessageSubscriptionStatisticsResponse400 | GetProcessDefinitionMessageSubscriptionStatisticsResponse401 | GetProcessDefinitionMessageSubscriptionStatisticsResponse403 | GetProcessDefinitionMessageSubscriptionStatisticsResponse500]
    """
    kwargs = _get_kwargs(body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(*, client: AuthenticatedClient | Client, body: GetProcessDefinitionMessageSubscriptionStatisticsData, **kwargs) -> GetProcessDefinitionMessageSubscriptionStatisticsResponse200:
    """Get message subscription statistics

 Get message subscription statistics, grouped by process definition.

Args:
    body (GetProcessDefinitionMessageSubscriptionStatisticsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetProcessDefinitionMessageSubscriptionStatisticsResponse200 | GetProcessDefinitionMessageSubscriptionStatisticsResponse400 | GetProcessDefinitionMessageSubscriptionStatisticsResponse401 | GetProcessDefinitionMessageSubscriptionStatisticsResponse403 | GetProcessDefinitionMessageSubscriptionStatisticsResponse500]"""
    response = sync_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(*, client: AuthenticatedClient | Client, body: GetProcessDefinitionMessageSubscriptionStatisticsData) -> Response[GetProcessDefinitionMessageSubscriptionStatisticsResponse200 | GetProcessDefinitionMessageSubscriptionStatisticsResponse400 | GetProcessDefinitionMessageSubscriptionStatisticsResponse401 | GetProcessDefinitionMessageSubscriptionStatisticsResponse403 | GetProcessDefinitionMessageSubscriptionStatisticsResponse500]:
    """Get message subscription statistics

     Get message subscription statistics, grouped by process definition.

    Args:
        body (GetProcessDefinitionMessageSubscriptionStatisticsData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetProcessDefinitionMessageSubscriptionStatisticsResponse200 | GetProcessDefinitionMessageSubscriptionStatisticsResponse400 | GetProcessDefinitionMessageSubscriptionStatisticsResponse401 | GetProcessDefinitionMessageSubscriptionStatisticsResponse403 | GetProcessDefinitionMessageSubscriptionStatisticsResponse500]
    """
    kwargs = _get_kwargs(body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(*, client: AuthenticatedClient | Client, body: GetProcessDefinitionMessageSubscriptionStatisticsData, **kwargs) -> GetProcessDefinitionMessageSubscriptionStatisticsResponse200:
    """Get message subscription statistics

 Get message subscription statistics, grouped by process definition.

Args:
    body (GetProcessDefinitionMessageSubscriptionStatisticsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetProcessDefinitionMessageSubscriptionStatisticsResponse200 | GetProcessDefinitionMessageSubscriptionStatisticsResponse400 | GetProcessDefinitionMessageSubscriptionStatisticsResponse401 | GetProcessDefinitionMessageSubscriptionStatisticsResponse403 | GetProcessDefinitionMessageSubscriptionStatisticsResponse500]"""
    response = await asyncio_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
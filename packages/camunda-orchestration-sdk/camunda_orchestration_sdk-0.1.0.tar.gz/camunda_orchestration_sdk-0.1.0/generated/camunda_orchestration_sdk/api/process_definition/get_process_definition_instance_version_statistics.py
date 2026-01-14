from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_process_definition_instance_version_statistics_data import GetProcessDefinitionInstanceVersionStatisticsData
from ...models.get_process_definition_instance_version_statistics_response_200 import GetProcessDefinitionInstanceVersionStatisticsResponse200
from ...models.get_process_definition_instance_version_statistics_response_400 import GetProcessDefinitionInstanceVersionStatisticsResponse400
from ...models.get_process_definition_instance_version_statistics_response_401 import GetProcessDefinitionInstanceVersionStatisticsResponse401
from ...models.get_process_definition_instance_version_statistics_response_403 import GetProcessDefinitionInstanceVersionStatisticsResponse403
from ...models.get_process_definition_instance_version_statistics_response_500 import GetProcessDefinitionInstanceVersionStatisticsResponse500
from ...types import Response

def _get_kwargs(process_definition_id: str, *, body: GetProcessDefinitionInstanceVersionStatisticsData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/process-definitions/{process_definition_id}/statistics/process-instances'.format(process_definition_id=process_definition_id)}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetProcessDefinitionInstanceVersionStatisticsResponse200 | GetProcessDefinitionInstanceVersionStatisticsResponse400 | GetProcessDefinitionInstanceVersionStatisticsResponse401 | GetProcessDefinitionInstanceVersionStatisticsResponse403 | GetProcessDefinitionInstanceVersionStatisticsResponse500 | None:
    if response.status_code == 200:
        response_200 = GetProcessDefinitionInstanceVersionStatisticsResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = GetProcessDefinitionInstanceVersionStatisticsResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = GetProcessDefinitionInstanceVersionStatisticsResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = GetProcessDefinitionInstanceVersionStatisticsResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 500:
        response_500 = GetProcessDefinitionInstanceVersionStatisticsResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GetProcessDefinitionInstanceVersionStatisticsResponse200 | GetProcessDefinitionInstanceVersionStatisticsResponse400 | GetProcessDefinitionInstanceVersionStatisticsResponse401 | GetProcessDefinitionInstanceVersionStatisticsResponse403 | GetProcessDefinitionInstanceVersionStatisticsResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(process_definition_id: str, *, client: AuthenticatedClient | Client, body: GetProcessDefinitionInstanceVersionStatisticsData) -> Response[GetProcessDefinitionInstanceVersionStatisticsResponse200 | GetProcessDefinitionInstanceVersionStatisticsResponse400 | GetProcessDefinitionInstanceVersionStatisticsResponse401 | GetProcessDefinitionInstanceVersionStatisticsResponse403 | GetProcessDefinitionInstanceVersionStatisticsResponse500]:
    """Get process instance statistics by version

     Get statistics about process instances, grouped by version for a given process definition.

    Args:
        process_definition_id (str): Id of a process definition, from the model. Only ids of
            process definitions that are deployed are useful. Example: new-account-onboarding-
            workflow.
        body (GetProcessDefinitionInstanceVersionStatisticsData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetProcessDefinitionInstanceVersionStatisticsResponse200 | GetProcessDefinitionInstanceVersionStatisticsResponse400 | GetProcessDefinitionInstanceVersionStatisticsResponse401 | GetProcessDefinitionInstanceVersionStatisticsResponse403 | GetProcessDefinitionInstanceVersionStatisticsResponse500]
    """
    kwargs = _get_kwargs(process_definition_id=process_definition_id, body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(process_definition_id: str, *, client: AuthenticatedClient | Client, body: GetProcessDefinitionInstanceVersionStatisticsData, **kwargs) -> GetProcessDefinitionInstanceVersionStatisticsResponse200:
    """Get process instance statistics by version

 Get statistics about process instances, grouped by version for a given process definition.

Args:
    process_definition_id (str): Id of a process definition, from the model. Only ids of
        process definitions that are deployed are useful. Example: new-account-onboarding-
        workflow.
    body (GetProcessDefinitionInstanceVersionStatisticsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetProcessDefinitionInstanceVersionStatisticsResponse200 | GetProcessDefinitionInstanceVersionStatisticsResponse400 | GetProcessDefinitionInstanceVersionStatisticsResponse401 | GetProcessDefinitionInstanceVersionStatisticsResponse403 | GetProcessDefinitionInstanceVersionStatisticsResponse500]"""
    response = sync_detailed(process_definition_id=process_definition_id, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(process_definition_id: str, *, client: AuthenticatedClient | Client, body: GetProcessDefinitionInstanceVersionStatisticsData) -> Response[GetProcessDefinitionInstanceVersionStatisticsResponse200 | GetProcessDefinitionInstanceVersionStatisticsResponse400 | GetProcessDefinitionInstanceVersionStatisticsResponse401 | GetProcessDefinitionInstanceVersionStatisticsResponse403 | GetProcessDefinitionInstanceVersionStatisticsResponse500]:
    """Get process instance statistics by version

     Get statistics about process instances, grouped by version for a given process definition.

    Args:
        process_definition_id (str): Id of a process definition, from the model. Only ids of
            process definitions that are deployed are useful. Example: new-account-onboarding-
            workflow.
        body (GetProcessDefinitionInstanceVersionStatisticsData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetProcessDefinitionInstanceVersionStatisticsResponse200 | GetProcessDefinitionInstanceVersionStatisticsResponse400 | GetProcessDefinitionInstanceVersionStatisticsResponse401 | GetProcessDefinitionInstanceVersionStatisticsResponse403 | GetProcessDefinitionInstanceVersionStatisticsResponse500]
    """
    kwargs = _get_kwargs(process_definition_id=process_definition_id, body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(process_definition_id: str, *, client: AuthenticatedClient | Client, body: GetProcessDefinitionInstanceVersionStatisticsData, **kwargs) -> GetProcessDefinitionInstanceVersionStatisticsResponse200:
    """Get process instance statistics by version

 Get statistics about process instances, grouped by version for a given process definition.

Args:
    process_definition_id (str): Id of a process definition, from the model. Only ids of
        process definitions that are deployed are useful. Example: new-account-onboarding-
        workflow.
    body (GetProcessDefinitionInstanceVersionStatisticsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetProcessDefinitionInstanceVersionStatisticsResponse200 | GetProcessDefinitionInstanceVersionStatisticsResponse400 | GetProcessDefinitionInstanceVersionStatisticsResponse401 | GetProcessDefinitionInstanceVersionStatisticsResponse403 | GetProcessDefinitionInstanceVersionStatisticsResponse500]"""
    response = await asyncio_detailed(process_definition_id=process_definition_id, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
from http import HTTPStatus
from typing import Any, cast
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.resolve_incident_data import ResolveIncidentData
from ...models.resolve_incident_response_400 import ResolveIncidentResponse400
from ...models.resolve_incident_response_404 import ResolveIncidentResponse404
from ...models.resolve_incident_response_500 import ResolveIncidentResponse500
from ...models.resolve_incident_response_503 import ResolveIncidentResponse503
from ...types import Response

def _get_kwargs(incident_key: str, *, body: ResolveIncidentData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/incidents/{incident_key}/resolution'.format(incident_key=incident_key)}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | ResolveIncidentResponse400 | ResolveIncidentResponse404 | ResolveIncidentResponse500 | ResolveIncidentResponse503 | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 400:
        response_400 = ResolveIncidentResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 404:
        response_404 = ResolveIncidentResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = ResolveIncidentResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = ResolveIncidentResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | ResolveIncidentResponse400 | ResolveIncidentResponse404 | ResolveIncidentResponse500 | ResolveIncidentResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(incident_key: str, *, client: AuthenticatedClient | Client, body: ResolveIncidentData) -> Response[Any | ResolveIncidentResponse400 | ResolveIncidentResponse404 | ResolveIncidentResponse500 | ResolveIncidentResponse503]:
    """Resolve incident

     Marks the incident as resolved; most likely a call to Update job will be necessary
    to reset the job's retries, followed by this call.

    Args:
        incident_key (str): System-generated key for a incident. Example: 2251799813689432.
        body (ResolveIncidentData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ResolveIncidentResponse400 | ResolveIncidentResponse404 | ResolveIncidentResponse500 | ResolveIncidentResponse503]
    """
    kwargs = _get_kwargs(incident_key=incident_key, body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(incident_key: str, *, client: AuthenticatedClient | Client, body: ResolveIncidentData, **kwargs) -> Any:
    """Resolve incident

 Marks the incident as resolved; most likely a call to Update job will be necessary
to reset the job's retries, followed by this call.

Args:
    incident_key (str): System-generated key for a incident. Example: 2251799813689432.
    body (ResolveIncidentData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | ResolveIncidentResponse400 | ResolveIncidentResponse404 | ResolveIncidentResponse500 | ResolveIncidentResponse503]"""
    response = sync_detailed(incident_key=incident_key, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(incident_key: str, *, client: AuthenticatedClient | Client, body: ResolveIncidentData) -> Response[Any | ResolveIncidentResponse400 | ResolveIncidentResponse404 | ResolveIncidentResponse500 | ResolveIncidentResponse503]:
    """Resolve incident

     Marks the incident as resolved; most likely a call to Update job will be necessary
    to reset the job's retries, followed by this call.

    Args:
        incident_key (str): System-generated key for a incident. Example: 2251799813689432.
        body (ResolveIncidentData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ResolveIncidentResponse400 | ResolveIncidentResponse404 | ResolveIncidentResponse500 | ResolveIncidentResponse503]
    """
    kwargs = _get_kwargs(incident_key=incident_key, body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(incident_key: str, *, client: AuthenticatedClient | Client, body: ResolveIncidentData, **kwargs) -> Any:
    """Resolve incident

 Marks the incident as resolved; most likely a call to Update job will be necessary
to reset the job's retries, followed by this call.

Args:
    incident_key (str): System-generated key for a incident. Example: 2251799813689432.
    body (ResolveIncidentData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | ResolveIncidentResponse400 | ResolveIncidentResponse404 | ResolveIncidentResponse500 | ResolveIncidentResponse503]"""
    response = await asyncio_detailed(incident_key=incident_key, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
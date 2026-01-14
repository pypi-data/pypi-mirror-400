from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.search_element_instance_incidents_data import SearchElementInstanceIncidentsData
from ...models.search_element_instance_incidents_response_200 import SearchElementInstanceIncidentsResponse200
from ...models.search_element_instance_incidents_response_400 import SearchElementInstanceIncidentsResponse400
from ...models.search_element_instance_incidents_response_401 import SearchElementInstanceIncidentsResponse401
from ...models.search_element_instance_incidents_response_403 import SearchElementInstanceIncidentsResponse403
from ...models.search_element_instance_incidents_response_404 import SearchElementInstanceIncidentsResponse404
from ...models.search_element_instance_incidents_response_500 import SearchElementInstanceIncidentsResponse500
from ...types import Response

def _get_kwargs(element_instance_key: str, *, body: SearchElementInstanceIncidentsData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/element-instances/{element_instance_key}/incidents/search'.format(element_instance_key=element_instance_key)}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> SearchElementInstanceIncidentsResponse200 | SearchElementInstanceIncidentsResponse400 | SearchElementInstanceIncidentsResponse401 | SearchElementInstanceIncidentsResponse403 | SearchElementInstanceIncidentsResponse404 | SearchElementInstanceIncidentsResponse500 | None:
    if response.status_code == 200:
        response_200 = SearchElementInstanceIncidentsResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = SearchElementInstanceIncidentsResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = SearchElementInstanceIncidentsResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = SearchElementInstanceIncidentsResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = SearchElementInstanceIncidentsResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = SearchElementInstanceIncidentsResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[SearchElementInstanceIncidentsResponse200 | SearchElementInstanceIncidentsResponse400 | SearchElementInstanceIncidentsResponse401 | SearchElementInstanceIncidentsResponse403 | SearchElementInstanceIncidentsResponse404 | SearchElementInstanceIncidentsResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(element_instance_key: str, *, client: AuthenticatedClient | Client, body: SearchElementInstanceIncidentsData) -> Response[SearchElementInstanceIncidentsResponse200 | SearchElementInstanceIncidentsResponse400 | SearchElementInstanceIncidentsResponse401 | SearchElementInstanceIncidentsResponse403 | SearchElementInstanceIncidentsResponse404 | SearchElementInstanceIncidentsResponse500]:
    """Search for incidents of a specific element instance

     Search for incidents caused by the specified element instance, including incidents of any child
    instances created from this element instance.

    Although the `elementInstanceKey` is provided as a path parameter to indicate the root element
    instance,
    you may also include an `elementInstanceKey` within the filter object to narrow results to specific
    child element instances. This is useful, for example, if you want to isolate incidents associated
    with
    nested or subordinate elements within the given element instance while excluding incidents directly
    tied
    to the root element itself.

    Args:
        element_instance_key (str): System-generated key for a element instance. Example:
            2251799813686789.
        body (SearchElementInstanceIncidentsData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchElementInstanceIncidentsResponse200 | SearchElementInstanceIncidentsResponse400 | SearchElementInstanceIncidentsResponse401 | SearchElementInstanceIncidentsResponse403 | SearchElementInstanceIncidentsResponse404 | SearchElementInstanceIncidentsResponse500]
    """
    kwargs = _get_kwargs(element_instance_key=element_instance_key, body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(element_instance_key: str, *, client: AuthenticatedClient | Client, body: SearchElementInstanceIncidentsData, **kwargs) -> SearchElementInstanceIncidentsResponse200:
    """Search for incidents of a specific element instance

 Search for incidents caused by the specified element instance, including incidents of any child
instances created from this element instance.

Although the `elementInstanceKey` is provided as a path parameter to indicate the root element
instance,
you may also include an `elementInstanceKey` within the filter object to narrow results to specific
child element instances. This is useful, for example, if you want to isolate incidents associated
with
nested or subordinate elements within the given element instance while excluding incidents directly
tied
to the root element itself.

Args:
    element_instance_key (str): System-generated key for a element instance. Example:
        2251799813686789.
    body (SearchElementInstanceIncidentsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchElementInstanceIncidentsResponse200 | SearchElementInstanceIncidentsResponse400 | SearchElementInstanceIncidentsResponse401 | SearchElementInstanceIncidentsResponse403 | SearchElementInstanceIncidentsResponse404 | SearchElementInstanceIncidentsResponse500]"""
    response = sync_detailed(element_instance_key=element_instance_key, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(element_instance_key: str, *, client: AuthenticatedClient | Client, body: SearchElementInstanceIncidentsData) -> Response[SearchElementInstanceIncidentsResponse200 | SearchElementInstanceIncidentsResponse400 | SearchElementInstanceIncidentsResponse401 | SearchElementInstanceIncidentsResponse403 | SearchElementInstanceIncidentsResponse404 | SearchElementInstanceIncidentsResponse500]:
    """Search for incidents of a specific element instance

     Search for incidents caused by the specified element instance, including incidents of any child
    instances created from this element instance.

    Although the `elementInstanceKey` is provided as a path parameter to indicate the root element
    instance,
    you may also include an `elementInstanceKey` within the filter object to narrow results to specific
    child element instances. This is useful, for example, if you want to isolate incidents associated
    with
    nested or subordinate elements within the given element instance while excluding incidents directly
    tied
    to the root element itself.

    Args:
        element_instance_key (str): System-generated key for a element instance. Example:
            2251799813686789.
        body (SearchElementInstanceIncidentsData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SearchElementInstanceIncidentsResponse200 | SearchElementInstanceIncidentsResponse400 | SearchElementInstanceIncidentsResponse401 | SearchElementInstanceIncidentsResponse403 | SearchElementInstanceIncidentsResponse404 | SearchElementInstanceIncidentsResponse500]
    """
    kwargs = _get_kwargs(element_instance_key=element_instance_key, body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(element_instance_key: str, *, client: AuthenticatedClient | Client, body: SearchElementInstanceIncidentsData, **kwargs) -> SearchElementInstanceIncidentsResponse200:
    """Search for incidents of a specific element instance

 Search for incidents caused by the specified element instance, including incidents of any child
instances created from this element instance.

Although the `elementInstanceKey` is provided as a path parameter to indicate the root element
instance,
you may also include an `elementInstanceKey` within the filter object to narrow results to specific
child element instances. This is useful, for example, if you want to isolate incidents associated
with
nested or subordinate elements within the given element instance while excluding incidents directly
tied
to the root element itself.

Args:
    element_instance_key (str): System-generated key for a element instance. Example:
        2251799813686789.
    body (SearchElementInstanceIncidentsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[SearchElementInstanceIncidentsResponse200 | SearchElementInstanceIncidentsResponse400 | SearchElementInstanceIncidentsResponse401 | SearchElementInstanceIncidentsResponse403 | SearchElementInstanceIncidentsResponse404 | SearchElementInstanceIncidentsResponse500]"""
    response = await asyncio_detailed(element_instance_key=element_instance_key, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
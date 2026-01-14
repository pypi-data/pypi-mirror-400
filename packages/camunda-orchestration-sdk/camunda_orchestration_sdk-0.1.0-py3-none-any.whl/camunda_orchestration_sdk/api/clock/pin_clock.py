from http import HTTPStatus
from typing import Any, cast
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.pin_clock_data import PinClockData
from ...models.pin_clock_response_400 import PinClockResponse400
from ...models.pin_clock_response_500 import PinClockResponse500
from ...models.pin_clock_response_503 import PinClockResponse503
from ...types import Response

def _get_kwargs(*, body: PinClockData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'put', 'url': '/clock'}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | PinClockResponse400 | PinClockResponse500 | PinClockResponse503 | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 400:
        response_400 = PinClockResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 500:
        response_500 = PinClockResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = PinClockResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | PinClockResponse400 | PinClockResponse500 | PinClockResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(*, client: AuthenticatedClient | Client, body: PinClockData) -> Response[Any | PinClockResponse400 | PinClockResponse500 | PinClockResponse503]:
    """Pin internal clock (alpha)

     Set a precise, static time for the Zeebe engine's internal clock.
    When the clock is pinned, it remains at the specified time and does not advance.
    To change the time, the clock must be pinned again with a new timestamp.

    This endpoint is an alpha feature and may be subject to change
    in future releases.

    Args:
        body (PinClockData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | PinClockResponse400 | PinClockResponse500 | PinClockResponse503]
    """
    kwargs = _get_kwargs(body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(*, client: AuthenticatedClient | Client, body: PinClockData, **kwargs) -> Any:
    """Pin internal clock (alpha)

 Set a precise, static time for the Zeebe engine's internal clock.
When the clock is pinned, it remains at the specified time and does not advance.
To change the time, the clock must be pinned again with a new timestamp.

This endpoint is an alpha feature and may be subject to change
in future releases.

Args:
    body (PinClockData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | PinClockResponse400 | PinClockResponse500 | PinClockResponse503]"""
    response = sync_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(*, client: AuthenticatedClient | Client, body: PinClockData) -> Response[Any | PinClockResponse400 | PinClockResponse500 | PinClockResponse503]:
    """Pin internal clock (alpha)

     Set a precise, static time for the Zeebe engine's internal clock.
    When the clock is pinned, it remains at the specified time and does not advance.
    To change the time, the clock must be pinned again with a new timestamp.

    This endpoint is an alpha feature and may be subject to change
    in future releases.

    Args:
        body (PinClockData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | PinClockResponse400 | PinClockResponse500 | PinClockResponse503]
    """
    kwargs = _get_kwargs(body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(*, client: AuthenticatedClient | Client, body: PinClockData, **kwargs) -> Any:
    """Pin internal clock (alpha)

 Set a precise, static time for the Zeebe engine's internal clock.
When the clock is pinned, it remains at the specified time and does not advance.
To change the time, the clock must be pinned again with a new timestamp.

This endpoint is an alpha feature and may be subject to change
in future releases.

Args:
    body (PinClockData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | PinClockResponse400 | PinClockResponse500 | PinClockResponse503]"""
    response = await asyncio_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
from http import HTTPStatus
from typing import Any, cast
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.reset_clock_response_500 import ResetClockResponse500
from ...models.reset_clock_response_503 import ResetClockResponse503
from ...types import Response

def _get_kwargs() -> dict[str, Any]:
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/clock/reset'}
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | ResetClockResponse500 | ResetClockResponse503 | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 500:
        response_500 = ResetClockResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = ResetClockResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | ResetClockResponse500 | ResetClockResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(*, client: AuthenticatedClient | Client) -> Response[Any | ResetClockResponse500 | ResetClockResponse503]:
    """Reset internal clock (alpha)

     Resets the Zeebe engine's internal clock to the current system time, enabling it to tick in real-
    time.
    This operation is useful for returning the clock to
    normal behavior after it has been pinned to a specific time.

    This endpoint is an alpha feature and may be subject to change
    in future releases.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ResetClockResponse500 | ResetClockResponse503]
    """
    kwargs = _get_kwargs()
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(*, client: AuthenticatedClient | Client, **kwargs) -> Any:
    """Reset internal clock (alpha)

 Resets the Zeebe engine's internal clock to the current system time, enabling it to tick in real-
time.
This operation is useful for returning the clock to
normal behavior after it has been pinned to a specific time.

This endpoint is an alpha feature and may be subject to change
in future releases.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | ResetClockResponse500 | ResetClockResponse503]"""
    response = sync_detailed(client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(*, client: AuthenticatedClient | Client) -> Response[Any | ResetClockResponse500 | ResetClockResponse503]:
    """Reset internal clock (alpha)

     Resets the Zeebe engine's internal clock to the current system time, enabling it to tick in real-
    time.
    This operation is useful for returning the clock to
    normal behavior after it has been pinned to a specific time.

    This endpoint is an alpha feature and may be subject to change
    in future releases.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ResetClockResponse500 | ResetClockResponse503]
    """
    kwargs = _get_kwargs()
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(*, client: AuthenticatedClient | Client, **kwargs) -> Any:
    """Reset internal clock (alpha)

 Resets the Zeebe engine's internal clock to the current system time, enabling it to tick in real-
time.
This operation is useful for returning the clock to
normal behavior after it has been pinned to a specific time.

This endpoint is an alpha feature and may be subject to change
in future releases.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | ResetClockResponse500 | ResetClockResponse503]"""
    response = await asyncio_detailed(client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.evaluate_conditionals_data import EvaluateConditionalsData
from ...models.evaluate_conditionals_response_200 import EvaluateConditionalsResponse200
from ...models.evaluate_conditionals_response_400 import EvaluateConditionalsResponse400
from ...models.evaluate_conditionals_response_403 import EvaluateConditionalsResponse403
from ...models.evaluate_conditionals_response_404 import EvaluateConditionalsResponse404
from ...models.evaluate_conditionals_response_500 import EvaluateConditionalsResponse500
from ...models.evaluate_conditionals_response_503 import EvaluateConditionalsResponse503
from ...types import Response

def _get_kwargs(*, body: EvaluateConditionalsData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/conditionals/evaluation'}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> EvaluateConditionalsResponse200 | EvaluateConditionalsResponse400 | EvaluateConditionalsResponse403 | EvaluateConditionalsResponse404 | EvaluateConditionalsResponse500 | EvaluateConditionalsResponse503 | None:
    if response.status_code == 200:
        response_200 = EvaluateConditionalsResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = EvaluateConditionalsResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 403:
        response_403 = EvaluateConditionalsResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = EvaluateConditionalsResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = EvaluateConditionalsResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = EvaluateConditionalsResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[EvaluateConditionalsResponse200 | EvaluateConditionalsResponse400 | EvaluateConditionalsResponse403 | EvaluateConditionalsResponse404 | EvaluateConditionalsResponse500 | EvaluateConditionalsResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(*, client: AuthenticatedClient | Client, body: EvaluateConditionalsData) -> Response[EvaluateConditionalsResponse200 | EvaluateConditionalsResponse400 | EvaluateConditionalsResponse403 | EvaluateConditionalsResponse404 | EvaluateConditionalsResponse500 | EvaluateConditionalsResponse503]:
    """Evaluate root level conditional start events

     Evaluates root-level conditional start events for process definitions.
    If the evaluation is successful, it will return the keys of all created process instances, along
    with their associated process definition key.
    Multiple root-level conditional start events of the same process definition can trigger if their
    conditions evaluate to true.

    Args:
        body (EvaluateConditionalsData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[EvaluateConditionalsResponse200 | EvaluateConditionalsResponse400 | EvaluateConditionalsResponse403 | EvaluateConditionalsResponse404 | EvaluateConditionalsResponse500 | EvaluateConditionalsResponse503]
    """
    kwargs = _get_kwargs(body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(*, client: AuthenticatedClient | Client, body: EvaluateConditionalsData, **kwargs) -> EvaluateConditionalsResponse200:
    """Evaluate root level conditional start events

 Evaluates root-level conditional start events for process definitions.
If the evaluation is successful, it will return the keys of all created process instances, along
with their associated process definition key.
Multiple root-level conditional start events of the same process definition can trigger if their
conditions evaluate to true.

Args:
    body (EvaluateConditionalsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[EvaluateConditionalsResponse200 | EvaluateConditionalsResponse400 | EvaluateConditionalsResponse403 | EvaluateConditionalsResponse404 | EvaluateConditionalsResponse500 | EvaluateConditionalsResponse503]"""
    response = sync_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(*, client: AuthenticatedClient | Client, body: EvaluateConditionalsData) -> Response[EvaluateConditionalsResponse200 | EvaluateConditionalsResponse400 | EvaluateConditionalsResponse403 | EvaluateConditionalsResponse404 | EvaluateConditionalsResponse500 | EvaluateConditionalsResponse503]:
    """Evaluate root level conditional start events

     Evaluates root-level conditional start events for process definitions.
    If the evaluation is successful, it will return the keys of all created process instances, along
    with their associated process definition key.
    Multiple root-level conditional start events of the same process definition can trigger if their
    conditions evaluate to true.

    Args:
        body (EvaluateConditionalsData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[EvaluateConditionalsResponse200 | EvaluateConditionalsResponse400 | EvaluateConditionalsResponse403 | EvaluateConditionalsResponse404 | EvaluateConditionalsResponse500 | EvaluateConditionalsResponse503]
    """
    kwargs = _get_kwargs(body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(*, client: AuthenticatedClient | Client, body: EvaluateConditionalsData, **kwargs) -> EvaluateConditionalsResponse200:
    """Evaluate root level conditional start events

 Evaluates root-level conditional start events for process definitions.
If the evaluation is successful, it will return the keys of all created process instances, along
with their associated process definition key.
Multiple root-level conditional start events of the same process definition can trigger if their
conditions evaluate to true.

Args:
    body (EvaluateConditionalsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[EvaluateConditionalsResponse200 | EvaluateConditionalsResponse400 | EvaluateConditionalsResponse403 | EvaluateConditionalsResponse404 | EvaluateConditionalsResponse500 | EvaluateConditionalsResponse503]"""
    response = await asyncio_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
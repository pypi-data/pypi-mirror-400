from http import HTTPStatus
from typing import Any, cast
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.decisionevaluationby_id import DecisionevaluationbyID
from ...models.decisionevaluationbykey import Decisionevaluationbykey
from ...models.evaluate_decision_response_200 import EvaluateDecisionResponse200
from ...models.evaluate_decision_response_400 import EvaluateDecisionResponse400
from ...models.evaluate_decision_response_500 import EvaluateDecisionResponse500
from ...models.evaluate_decision_response_503 import EvaluateDecisionResponse503
from ...types import Response

def _get_kwargs(*, body: DecisionevaluationbyID | Decisionevaluationbykey) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/decision-definitions/evaluation'}
    _kwargs['json']: dict[str, Any]
    if isinstance(body, DecisionevaluationbyID):
        _kwargs['json'] = body.to_dict()
    else:
        _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | EvaluateDecisionResponse200 | EvaluateDecisionResponse400 | EvaluateDecisionResponse500 | EvaluateDecisionResponse503 | None:
    if response.status_code == 200:
        response_200 = EvaluateDecisionResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = EvaluateDecisionResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404
    if response.status_code == 500:
        response_500 = EvaluateDecisionResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = EvaluateDecisionResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | EvaluateDecisionResponse200 | EvaluateDecisionResponse400 | EvaluateDecisionResponse500 | EvaluateDecisionResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(*, client: AuthenticatedClient | Client, body: DecisionevaluationbyID | Decisionevaluationbykey) -> Response[Any | EvaluateDecisionResponse200 | EvaluateDecisionResponse400 | EvaluateDecisionResponse500 | EvaluateDecisionResponse503]:
    """Evaluate decision

     Evaluates a decision.
    You specify the decision to evaluate either by using its unique key (as returned by
    DeployResource), or using the decision ID. When using the decision ID, the latest deployed
    version of the decision is used.

    Args:
        body (DecisionevaluationbyID | Decisionevaluationbykey):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | EvaluateDecisionResponse200 | EvaluateDecisionResponse400 | EvaluateDecisionResponse500 | EvaluateDecisionResponse503]
    """
    kwargs = _get_kwargs(body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(*, client: AuthenticatedClient | Client, body: DecisionevaluationbyID | Decisionevaluationbykey, **kwargs) -> Any:
    """Evaluate decision

 Evaluates a decision.
You specify the decision to evaluate either by using its unique key (as returned by
DeployResource), or using the decision ID. When using the decision ID, the latest deployed
version of the decision is used.

Args:
    body (DecisionevaluationbyID | Decisionevaluationbykey):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | EvaluateDecisionResponse200 | EvaluateDecisionResponse400 | EvaluateDecisionResponse500 | EvaluateDecisionResponse503]"""
    response = sync_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(*, client: AuthenticatedClient | Client, body: DecisionevaluationbyID | Decisionevaluationbykey) -> Response[Any | EvaluateDecisionResponse200 | EvaluateDecisionResponse400 | EvaluateDecisionResponse500 | EvaluateDecisionResponse503]:
    """Evaluate decision

     Evaluates a decision.
    You specify the decision to evaluate either by using its unique key (as returned by
    DeployResource), or using the decision ID. When using the decision ID, the latest deployed
    version of the decision is used.

    Args:
        body (DecisionevaluationbyID | Decisionevaluationbykey):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | EvaluateDecisionResponse200 | EvaluateDecisionResponse400 | EvaluateDecisionResponse500 | EvaluateDecisionResponse503]
    """
    kwargs = _get_kwargs(body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(*, client: AuthenticatedClient | Client, body: DecisionevaluationbyID | Decisionevaluationbykey, **kwargs) -> Any:
    """Evaluate decision

 Evaluates a decision.
You specify the decision to evaluate either by using its unique key (as returned by
DeployResource), or using the decision ID. When using the decision ID, the latest deployed
version of the decision is used.

Args:
    body (DecisionevaluationbyID | Decisionevaluationbykey):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | EvaluateDecisionResponse200 | EvaluateDecisionResponse400 | EvaluateDecisionResponse500 | EvaluateDecisionResponse503]"""
    response = await asyncio_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
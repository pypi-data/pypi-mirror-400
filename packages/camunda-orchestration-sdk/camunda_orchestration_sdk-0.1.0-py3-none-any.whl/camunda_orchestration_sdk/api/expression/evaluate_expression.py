from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.evaluate_expression_data import EvaluateExpressionData
from ...models.evaluate_expression_response_200 import EvaluateExpressionResponse200
from ...models.evaluate_expression_response_400 import EvaluateExpressionResponse400
from ...models.evaluate_expression_response_401 import EvaluateExpressionResponse401
from ...models.evaluate_expression_response_403 import EvaluateExpressionResponse403
from ...models.evaluate_expression_response_500 import EvaluateExpressionResponse500
from ...types import Response

def _get_kwargs(*, body: EvaluateExpressionData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/expression/evaluation'}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> EvaluateExpressionResponse200 | EvaluateExpressionResponse400 | EvaluateExpressionResponse401 | EvaluateExpressionResponse403 | EvaluateExpressionResponse500 | None:
    if response.status_code == 200:
        response_200 = EvaluateExpressionResponse200.from_dict(response.json())
        return response_200
    if response.status_code == 400:
        response_400 = EvaluateExpressionResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = EvaluateExpressionResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = EvaluateExpressionResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 500:
        response_500 = EvaluateExpressionResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[EvaluateExpressionResponse200 | EvaluateExpressionResponse400 | EvaluateExpressionResponse401 | EvaluateExpressionResponse403 | EvaluateExpressionResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(*, client: AuthenticatedClient | Client, body: EvaluateExpressionData) -> Response[EvaluateExpressionResponse200 | EvaluateExpressionResponse400 | EvaluateExpressionResponse401 | EvaluateExpressionResponse403 | EvaluateExpressionResponse500]:
    """Evaluate an expression

     Evaluates a FEEL expression and returns the result. Supports references to tenant scoped cluster
    variables when a tenant ID is provided.

    Args:
        body (EvaluateExpressionData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[EvaluateExpressionResponse200 | EvaluateExpressionResponse400 | EvaluateExpressionResponse401 | EvaluateExpressionResponse403 | EvaluateExpressionResponse500]
    """
    kwargs = _get_kwargs(body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(*, client: AuthenticatedClient | Client, body: EvaluateExpressionData, **kwargs) -> EvaluateExpressionResponse200:
    """Evaluate an expression

 Evaluates a FEEL expression and returns the result. Supports references to tenant scoped cluster
variables when a tenant ID is provided.

Args:
    body (EvaluateExpressionData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[EvaluateExpressionResponse200 | EvaluateExpressionResponse400 | EvaluateExpressionResponse401 | EvaluateExpressionResponse403 | EvaluateExpressionResponse500]"""
    response = sync_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(*, client: AuthenticatedClient | Client, body: EvaluateExpressionData) -> Response[EvaluateExpressionResponse200 | EvaluateExpressionResponse400 | EvaluateExpressionResponse401 | EvaluateExpressionResponse403 | EvaluateExpressionResponse500]:
    """Evaluate an expression

     Evaluates a FEEL expression and returns the result. Supports references to tenant scoped cluster
    variables when a tenant ID is provided.

    Args:
        body (EvaluateExpressionData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[EvaluateExpressionResponse200 | EvaluateExpressionResponse400 | EvaluateExpressionResponse401 | EvaluateExpressionResponse403 | EvaluateExpressionResponse500]
    """
    kwargs = _get_kwargs(body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(*, client: AuthenticatedClient | Client, body: EvaluateExpressionData, **kwargs) -> EvaluateExpressionResponse200:
    """Evaluate an expression

 Evaluates a FEEL expression and returns the result. Supports references to tenant scoped cluster
variables when a tenant ID is provided.

Args:
    body (EvaluateExpressionData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[EvaluateExpressionResponse200 | EvaluateExpressionResponse400 | EvaluateExpressionResponse401 | EvaluateExpressionResponse403 | EvaluateExpressionResponse500]"""
    response = await asyncio_detailed(client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
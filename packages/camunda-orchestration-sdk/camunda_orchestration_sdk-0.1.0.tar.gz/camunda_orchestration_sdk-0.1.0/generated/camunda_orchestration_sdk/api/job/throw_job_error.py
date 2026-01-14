from http import HTTPStatus
from typing import Any, cast
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.throw_job_error_data import ThrowJobErrorData
from ...models.throw_job_error_response_400 import ThrowJobErrorResponse400
from ...models.throw_job_error_response_404 import ThrowJobErrorResponse404
from ...models.throw_job_error_response_409 import ThrowJobErrorResponse409
from ...models.throw_job_error_response_500 import ThrowJobErrorResponse500
from ...models.throw_job_error_response_503 import ThrowJobErrorResponse503
from ...types import Response

def _get_kwargs(job_key: str, *, body: ThrowJobErrorData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/jobs/{job_key}/error'.format(job_key=job_key)}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | ThrowJobErrorResponse400 | ThrowJobErrorResponse404 | ThrowJobErrorResponse409 | ThrowJobErrorResponse500 | ThrowJobErrorResponse503 | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 400:
        response_400 = ThrowJobErrorResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 404:
        response_404 = ThrowJobErrorResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 409:
        response_409 = ThrowJobErrorResponse409.from_dict(response.json())
        return response_409
    if response.status_code == 500:
        response_500 = ThrowJobErrorResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = ThrowJobErrorResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | ThrowJobErrorResponse400 | ThrowJobErrorResponse404 | ThrowJobErrorResponse409 | ThrowJobErrorResponse500 | ThrowJobErrorResponse503]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(job_key: str, *, client: AuthenticatedClient | Client, body: ThrowJobErrorData) -> Response[Any | ThrowJobErrorResponse400 | ThrowJobErrorResponse404 | ThrowJobErrorResponse409 | ThrowJobErrorResponse500 | ThrowJobErrorResponse503]:
    """Throw error for job

     Reports a business error (i.e. non-technical) that occurs while processing a job.

    Args:
        job_key (str): System-generated key for a job. Example: 2251799813653498.
        body (ThrowJobErrorData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ThrowJobErrorResponse400 | ThrowJobErrorResponse404 | ThrowJobErrorResponse409 | ThrowJobErrorResponse500 | ThrowJobErrorResponse503]
    """
    kwargs = _get_kwargs(job_key=job_key, body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(job_key: str, *, client: AuthenticatedClient | Client, body: ThrowJobErrorData, **kwargs) -> Any:
    """Throw error for job

 Reports a business error (i.e. non-technical) that occurs while processing a job.

Args:
    job_key (str): System-generated key for a job. Example: 2251799813653498.
    body (ThrowJobErrorData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | ThrowJobErrorResponse400 | ThrowJobErrorResponse404 | ThrowJobErrorResponse409 | ThrowJobErrorResponse500 | ThrowJobErrorResponse503]"""
    response = sync_detailed(job_key=job_key, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(job_key: str, *, client: AuthenticatedClient | Client, body: ThrowJobErrorData) -> Response[Any | ThrowJobErrorResponse400 | ThrowJobErrorResponse404 | ThrowJobErrorResponse409 | ThrowJobErrorResponse500 | ThrowJobErrorResponse503]:
    """Throw error for job

     Reports a business error (i.e. non-technical) that occurs while processing a job.

    Args:
        job_key (str): System-generated key for a job. Example: 2251799813653498.
        body (ThrowJobErrorData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ThrowJobErrorResponse400 | ThrowJobErrorResponse404 | ThrowJobErrorResponse409 | ThrowJobErrorResponse500 | ThrowJobErrorResponse503]
    """
    kwargs = _get_kwargs(job_key=job_key, body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(job_key: str, *, client: AuthenticatedClient | Client, body: ThrowJobErrorData, **kwargs) -> Any:
    """Throw error for job

 Reports a business error (i.e. non-technical) that occurs while processing a job.

Args:
    job_key (str): System-generated key for a job. Example: 2251799813653498.
    body (ThrowJobErrorData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | ThrowJobErrorResponse400 | ThrowJobErrorResponse404 | ThrowJobErrorResponse409 | ThrowJobErrorResponse500 | ThrowJobErrorResponse503]"""
    response = await asyncio_detailed(job_key=job_key, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
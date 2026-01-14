from http import HTTPStatus
from io import BytesIO
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_document_response_404 import GetDocumentResponse404
from ...models.get_document_response_500 import GetDocumentResponse500
from ...types import UNSET, File, Response, Unset

def _get_kwargs(document_id: str, *, store_id: str | Unset=UNSET, content_hash: str | Unset=UNSET) -> dict[str, Any]:
    params: dict[str, Any] = {}
    params['storeId'] = store_id
    params['contentHash'] = content_hash
    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}
    _kwargs: dict[str, Any] = {'method': 'get', 'url': '/documents/{document_id}'.format(document_id=document_id), 'params': params}
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> File | GetDocumentResponse404 | GetDocumentResponse500 | None:
    if response.status_code == 200:
        response_200 = File(payload=BytesIO(response.content))
        return response_200
    if response.status_code == 404:
        response_404 = GetDocumentResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = GetDocumentResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[File | GetDocumentResponse404 | GetDocumentResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(document_id: str, *, client: AuthenticatedClient | Client, store_id: str | Unset=UNSET, content_hash: str | Unset=UNSET) -> Response[File | GetDocumentResponse404 | GetDocumentResponse500]:
    """Download document

     Download a document from the Camunda 8 cluster.

    Note that this is currently supported for document stores of type: AWS, GCP, in-memory (non-
    production), local (non-production)

    Args:
        document_id (str): Document Id that uniquely identifies a document.
        store_id (str | Unset):
        content_hash (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[File | GetDocumentResponse404 | GetDocumentResponse500]
    """
    kwargs = _get_kwargs(document_id=document_id, store_id=store_id, content_hash=content_hash)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(document_id: str, *, client: AuthenticatedClient | Client, store_id: str | Unset=UNSET, content_hash: str | Unset=UNSET, **kwargs) -> File:
    """Download document

 Download a document from the Camunda 8 cluster.

Note that this is currently supported for document stores of type: AWS, GCP, in-memory (non-
production), local (non-production)

Args:
    document_id (str): Document Id that uniquely identifies a document.
    store_id (str | Unset):
    content_hash (str | Unset):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[File | GetDocumentResponse404 | GetDocumentResponse500]"""
    response = sync_detailed(document_id=document_id, client=client, store_id=store_id, content_hash=content_hash)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(document_id: str, *, client: AuthenticatedClient | Client, store_id: str | Unset=UNSET, content_hash: str | Unset=UNSET) -> Response[File | GetDocumentResponse404 | GetDocumentResponse500]:
    """Download document

     Download a document from the Camunda 8 cluster.

    Note that this is currently supported for document stores of type: AWS, GCP, in-memory (non-
    production), local (non-production)

    Args:
        document_id (str): Document Id that uniquely identifies a document.
        store_id (str | Unset):
        content_hash (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[File | GetDocumentResponse404 | GetDocumentResponse500]
    """
    kwargs = _get_kwargs(document_id=document_id, store_id=store_id, content_hash=content_hash)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(document_id: str, *, client: AuthenticatedClient | Client, store_id: str | Unset=UNSET, content_hash: str | Unset=UNSET, **kwargs) -> File:
    """Download document

 Download a document from the Camunda 8 cluster.

Note that this is currently supported for document stores of type: AWS, GCP, in-memory (non-
production), local (non-production)

Args:
    document_id (str): Document Id that uniquely identifies a document.
    store_id (str | Unset):
    content_hash (str | Unset):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[File | GetDocumentResponse404 | GetDocumentResponse500]"""
    response = await asyncio_detailed(document_id=document_id, client=client, store_id=store_id, content_hash=content_hash)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
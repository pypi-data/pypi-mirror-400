from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_document_data import CreateDocumentData
from ...models.create_document_response_201 import CreateDocumentResponse201
from ...models.create_document_response_400 import CreateDocumentResponse400
from ...models.create_document_response_415 import CreateDocumentResponse415
from ...types import UNSET, Response, Unset

def _get_kwargs(*, body: CreateDocumentData, store_id: str | Unset=UNSET, document_id: str | Unset=UNSET) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    params: dict[str, Any] = {}
    params['storeId'] = store_id
    params['documentId'] = document_id
    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/documents', 'params': params}
    _kwargs['files'] = body.to_multipart()
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> CreateDocumentResponse201 | CreateDocumentResponse400 | CreateDocumentResponse415 | None:
    if response.status_code == 201:
        response_201 = CreateDocumentResponse201.from_dict(response.json())
        return response_201
    if response.status_code == 400:
        response_400 = CreateDocumentResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 415:
        response_415 = CreateDocumentResponse415.from_dict(response.json())
        return response_415
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[CreateDocumentResponse201 | CreateDocumentResponse400 | CreateDocumentResponse415]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(*, client: AuthenticatedClient | Client, body: CreateDocumentData, store_id: str | Unset=UNSET, document_id: str | Unset=UNSET) -> Response[CreateDocumentResponse201 | CreateDocumentResponse400 | CreateDocumentResponse415]:
    """Upload document

     Upload a document to the Camunda 8 cluster.

    Note that this is currently supported for document stores of type: AWS, GCP, in-memory (non-
    production), local (non-production)

    Args:
        store_id (str | Unset):
        document_id (str | Unset): Document Id that uniquely identifies a document.
        body (CreateDocumentData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateDocumentResponse201 | CreateDocumentResponse400 | CreateDocumentResponse415]
    """
    kwargs = _get_kwargs(body=body, store_id=store_id, document_id=document_id)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(*, client: AuthenticatedClient | Client, body: CreateDocumentData, store_id: str | Unset=UNSET, document_id: str | Unset=UNSET, **kwargs) -> CreateDocumentResponse201:
    """Upload document

 Upload a document to the Camunda 8 cluster.

Note that this is currently supported for document stores of type: AWS, GCP, in-memory (non-
production), local (non-production)

Args:
    store_id (str | Unset):
    document_id (str | Unset): Document Id that uniquely identifies a document.
    body (CreateDocumentData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateDocumentResponse201 | CreateDocumentResponse400 | CreateDocumentResponse415]"""
    response = sync_detailed(client=client, body=body, store_id=store_id, document_id=document_id)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(*, client: AuthenticatedClient | Client, body: CreateDocumentData, store_id: str | Unset=UNSET, document_id: str | Unset=UNSET) -> Response[CreateDocumentResponse201 | CreateDocumentResponse400 | CreateDocumentResponse415]:
    """Upload document

     Upload a document to the Camunda 8 cluster.

    Note that this is currently supported for document stores of type: AWS, GCP, in-memory (non-
    production), local (non-production)

    Args:
        store_id (str | Unset):
        document_id (str | Unset): Document Id that uniquely identifies a document.
        body (CreateDocumentData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateDocumentResponse201 | CreateDocumentResponse400 | CreateDocumentResponse415]
    """
    kwargs = _get_kwargs(body=body, store_id=store_id, document_id=document_id)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(*, client: AuthenticatedClient | Client, body: CreateDocumentData, store_id: str | Unset=UNSET, document_id: str | Unset=UNSET, **kwargs) -> CreateDocumentResponse201:
    """Upload document

 Upload a document to the Camunda 8 cluster.

Note that this is currently supported for document stores of type: AWS, GCP, in-memory (non-
production), local (non-production)

Args:
    store_id (str | Unset):
    document_id (str | Unset): Document Id that uniquely identifies a document.
    body (CreateDocumentData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateDocumentResponse201 | CreateDocumentResponse400 | CreateDocumentResponse415]"""
    response = await asyncio_detailed(client=client, body=body, store_id=store_id, document_id=document_id)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
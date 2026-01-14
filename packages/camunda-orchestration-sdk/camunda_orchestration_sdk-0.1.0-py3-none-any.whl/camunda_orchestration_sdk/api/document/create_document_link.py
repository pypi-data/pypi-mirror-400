from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_document_link_data import CreateDocumentLinkData
from ...models.create_document_link_response_201 import CreateDocumentLinkResponse201
from ...models.create_document_link_response_400 import CreateDocumentLinkResponse400
from ...types import UNSET, Response, Unset

def _get_kwargs(document_id: str, *, body: CreateDocumentLinkData, store_id: str | Unset=UNSET, content_hash: str | Unset=UNSET) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    params: dict[str, Any] = {}
    params['storeId'] = store_id
    params['contentHash'] = content_hash
    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/documents/{document_id}/links'.format(document_id=document_id), 'params': params}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> CreateDocumentLinkResponse201 | CreateDocumentLinkResponse400 | None:
    if response.status_code == 201:
        response_201 = CreateDocumentLinkResponse201.from_dict(response.json())
        return response_201
    if response.status_code == 400:
        response_400 = CreateDocumentLinkResponse400.from_dict(response.json())
        return response_400
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[CreateDocumentLinkResponse201 | CreateDocumentLinkResponse400]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(document_id: str, *, client: AuthenticatedClient | Client, body: CreateDocumentLinkData, store_id: str | Unset=UNSET, content_hash: str | Unset=UNSET) -> Response[CreateDocumentLinkResponse201 | CreateDocumentLinkResponse400]:
    """Create document link

     Create a link to a document in the Camunda 8 cluster.

    Note that this is currently supported for document stores of type: AWS, GCP

    Args:
        document_id (str): Document Id that uniquely identifies a document.
        store_id (str | Unset):
        content_hash (str | Unset):
        body (CreateDocumentLinkData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateDocumentLinkResponse201 | CreateDocumentLinkResponse400]
    """
    kwargs = _get_kwargs(document_id=document_id, body=body, store_id=store_id, content_hash=content_hash)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(document_id: str, *, client: AuthenticatedClient | Client, body: CreateDocumentLinkData, store_id: str | Unset=UNSET, content_hash: str | Unset=UNSET, **kwargs) -> CreateDocumentLinkResponse201:
    """Create document link

 Create a link to a document in the Camunda 8 cluster.

Note that this is currently supported for document stores of type: AWS, GCP

Args:
    document_id (str): Document Id that uniquely identifies a document.
    store_id (str | Unset):
    content_hash (str | Unset):
    body (CreateDocumentLinkData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateDocumentLinkResponse201 | CreateDocumentLinkResponse400]"""
    response = sync_detailed(document_id=document_id, client=client, body=body, store_id=store_id, content_hash=content_hash)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(document_id: str, *, client: AuthenticatedClient | Client, body: CreateDocumentLinkData, store_id: str | Unset=UNSET, content_hash: str | Unset=UNSET) -> Response[CreateDocumentLinkResponse201 | CreateDocumentLinkResponse400]:
    """Create document link

     Create a link to a document in the Camunda 8 cluster.

    Note that this is currently supported for document stores of type: AWS, GCP

    Args:
        document_id (str): Document Id that uniquely identifies a document.
        store_id (str | Unset):
        content_hash (str | Unset):
        body (CreateDocumentLinkData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateDocumentLinkResponse201 | CreateDocumentLinkResponse400]
    """
    kwargs = _get_kwargs(document_id=document_id, body=body, store_id=store_id, content_hash=content_hash)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(document_id: str, *, client: AuthenticatedClient | Client, body: CreateDocumentLinkData, store_id: str | Unset=UNSET, content_hash: str | Unset=UNSET, **kwargs) -> CreateDocumentLinkResponse201:
    """Create document link

 Create a link to a document in the Camunda 8 cluster.

Note that this is currently supported for document stores of type: AWS, GCP

Args:
    document_id (str): Document Id that uniquely identifies a document.
    store_id (str | Unset):
    content_hash (str | Unset):
    body (CreateDocumentLinkData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateDocumentLinkResponse201 | CreateDocumentLinkResponse400]"""
    response = await asyncio_detailed(document_id=document_id, client=client, body=body, store_id=store_id, content_hash=content_hash)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
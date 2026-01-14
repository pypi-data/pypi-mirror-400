from http import HTTPStatus
from typing import Any, cast
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.delete_document_response_404 import DeleteDocumentResponse404
from ...models.delete_document_response_500 import DeleteDocumentResponse500
from ...types import UNSET, Response, Unset

def _get_kwargs(document_id: str, *, store_id: str | Unset=UNSET) -> dict[str, Any]:
    params: dict[str, Any] = {}
    params['storeId'] = store_id
    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}
    _kwargs: dict[str, Any] = {'method': 'delete', 'url': '/documents/{document_id}'.format(document_id=document_id), 'params': params}
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | DeleteDocumentResponse404 | DeleteDocumentResponse500 | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 404:
        response_404 = DeleteDocumentResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = DeleteDocumentResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | DeleteDocumentResponse404 | DeleteDocumentResponse500]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(document_id: str, *, client: AuthenticatedClient | Client, store_id: str | Unset=UNSET) -> Response[Any | DeleteDocumentResponse404 | DeleteDocumentResponse500]:
    """Delete document

     Delete a document from the Camunda 8 cluster.

    Note that this is currently supported for document stores of type: AWS, GCP, in-memory (non-
    production), local (non-production)

    Args:
        document_id (str): Document Id that uniquely identifies a document.
        store_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | DeleteDocumentResponse404 | DeleteDocumentResponse500]
    """
    kwargs = _get_kwargs(document_id=document_id, store_id=store_id)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(document_id: str, *, client: AuthenticatedClient | Client, store_id: str | Unset=UNSET, **kwargs) -> Any:
    """Delete document

 Delete a document from the Camunda 8 cluster.

Note that this is currently supported for document stores of type: AWS, GCP, in-memory (non-
production), local (non-production)

Args:
    document_id (str): Document Id that uniquely identifies a document.
    store_id (str | Unset):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteDocumentResponse404 | DeleteDocumentResponse500]"""
    response = sync_detailed(document_id=document_id, client=client, store_id=store_id)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(document_id: str, *, client: AuthenticatedClient | Client, store_id: str | Unset=UNSET) -> Response[Any | DeleteDocumentResponse404 | DeleteDocumentResponse500]:
    """Delete document

     Delete a document from the Camunda 8 cluster.

    Note that this is currently supported for document stores of type: AWS, GCP, in-memory (non-
    production), local (non-production)

    Args:
        document_id (str): Document Id that uniquely identifies a document.
        store_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | DeleteDocumentResponse404 | DeleteDocumentResponse500]
    """
    kwargs = _get_kwargs(document_id=document_id, store_id=store_id)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(document_id: str, *, client: AuthenticatedClient | Client, store_id: str | Unset=UNSET, **kwargs) -> Any:
    """Delete document

 Delete a document from the Camunda 8 cluster.

Note that this is currently supported for document stores of type: AWS, GCP, in-memory (non-
production), local (non-production)

Args:
    document_id (str): Document Id that uniquely identifies a document.
    store_id (str | Unset):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[Any | DeleteDocumentResponse404 | DeleteDocumentResponse500]"""
    response = await asyncio_detailed(document_id=document_id, client=client, store_id=store_id)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
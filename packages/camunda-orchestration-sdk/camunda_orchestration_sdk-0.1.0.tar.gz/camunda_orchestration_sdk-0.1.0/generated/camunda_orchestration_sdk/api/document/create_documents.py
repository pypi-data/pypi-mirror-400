from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_documents_data import CreateDocumentsData
from ...models.create_documents_response_201 import CreateDocumentsResponse201
from ...models.create_documents_response_207 import CreateDocumentsResponse207
from ...models.create_documents_response_400 import CreateDocumentsResponse400
from ...models.create_documents_response_415 import CreateDocumentsResponse415
from ...types import UNSET, Response, Unset

def _get_kwargs(*, body: CreateDocumentsData, store_id: str | Unset=UNSET) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    params: dict[str, Any] = {}
    params['storeId'] = store_id
    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/documents/batch', 'params': params}
    _kwargs['files'] = body.to_multipart()
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> CreateDocumentsResponse201 | CreateDocumentsResponse207 | CreateDocumentsResponse400 | CreateDocumentsResponse415 | None:
    if response.status_code == 201:
        response_201 = CreateDocumentsResponse201.from_dict(response.json())
        return response_201
    if response.status_code == 207:
        response_207 = CreateDocumentsResponse207.from_dict(response.json())
        return response_207
    if response.status_code == 400:
        response_400 = CreateDocumentsResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 415:
        response_415 = CreateDocumentsResponse415.from_dict(response.json())
        return response_415
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[CreateDocumentsResponse201 | CreateDocumentsResponse207 | CreateDocumentsResponse400 | CreateDocumentsResponse415]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(*, client: AuthenticatedClient | Client, body: CreateDocumentsData, store_id: str | Unset=UNSET) -> Response[CreateDocumentsResponse201 | CreateDocumentsResponse207 | CreateDocumentsResponse400 | CreateDocumentsResponse415]:
    """Upload multiple documents

     Upload multiple documents to the Camunda 8 cluster.

    The caller must provide a file name for each document, which will be used in case of a multi-status
    response
    to identify which documents failed to upload. The file name can be provided in the `Content-
    Disposition` header
    of the file part or in the `fileName` field of the metadata. You can add a parallel array of
    metadata objects. These
    are matched with the files based on index, and must have the same length as the files array.
    To pass homogenous metadata for all files, spread the metadata over the metadata array.
    A filename value provided explicitly via the metadata array in the request overrides the `Content-
    Disposition` header
    of the file part.

    In case of a multi-status response, the response body will contain a list of
    `DocumentBatchProblemDetail` objects,
    each of which contains the file name of the document that failed to upload and the reason for the
    failure.
    The client can choose to retry the whole batch or individual documents based on the response.

    Note that this is currently supported for document stores of type: AWS, GCP, in-memory (non-
    production), local (non-production)

    Args:
        store_id (str | Unset):
        body (CreateDocumentsData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateDocumentsResponse201 | CreateDocumentsResponse207 | CreateDocumentsResponse400 | CreateDocumentsResponse415]
    """
    kwargs = _get_kwargs(body=body, store_id=store_id)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(*, client: AuthenticatedClient | Client, body: CreateDocumentsData, store_id: str | Unset=UNSET, **kwargs) -> CreateDocumentsResponse201:
    """Upload multiple documents

 Upload multiple documents to the Camunda 8 cluster.

The caller must provide a file name for each document, which will be used in case of a multi-status
response
to identify which documents failed to upload. The file name can be provided in the `Content-
Disposition` header
of the file part or in the `fileName` field of the metadata. You can add a parallel array of
metadata objects. These
are matched with the files based on index, and must have the same length as the files array.
To pass homogenous metadata for all files, spread the metadata over the metadata array.
A filename value provided explicitly via the metadata array in the request overrides the `Content-
Disposition` header
of the file part.

In case of a multi-status response, the response body will contain a list of
`DocumentBatchProblemDetail` objects,
each of which contains the file name of the document that failed to upload and the reason for the
failure.
The client can choose to retry the whole batch or individual documents based on the response.

Note that this is currently supported for document stores of type: AWS, GCP, in-memory (non-
production), local (non-production)

Args:
    store_id (str | Unset):
    body (CreateDocumentsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateDocumentsResponse201 | CreateDocumentsResponse207 | CreateDocumentsResponse400 | CreateDocumentsResponse415]"""
    response = sync_detailed(client=client, body=body, store_id=store_id)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(*, client: AuthenticatedClient | Client, body: CreateDocumentsData, store_id: str | Unset=UNSET) -> Response[CreateDocumentsResponse201 | CreateDocumentsResponse207 | CreateDocumentsResponse400 | CreateDocumentsResponse415]:
    """Upload multiple documents

     Upload multiple documents to the Camunda 8 cluster.

    The caller must provide a file name for each document, which will be used in case of a multi-status
    response
    to identify which documents failed to upload. The file name can be provided in the `Content-
    Disposition` header
    of the file part or in the `fileName` field of the metadata. You can add a parallel array of
    metadata objects. These
    are matched with the files based on index, and must have the same length as the files array.
    To pass homogenous metadata for all files, spread the metadata over the metadata array.
    A filename value provided explicitly via the metadata array in the request overrides the `Content-
    Disposition` header
    of the file part.

    In case of a multi-status response, the response body will contain a list of
    `DocumentBatchProblemDetail` objects,
    each of which contains the file name of the document that failed to upload and the reason for the
    failure.
    The client can choose to retry the whole batch or individual documents based on the response.

    Note that this is currently supported for document stores of type: AWS, GCP, in-memory (non-
    production), local (non-production)

    Args:
        store_id (str | Unset):
        body (CreateDocumentsData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateDocumentsResponse201 | CreateDocumentsResponse207 | CreateDocumentsResponse400 | CreateDocumentsResponse415]
    """
    kwargs = _get_kwargs(body=body, store_id=store_id)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(*, client: AuthenticatedClient | Client, body: CreateDocumentsData, store_id: str | Unset=UNSET, **kwargs) -> CreateDocumentsResponse201:
    """Upload multiple documents

 Upload multiple documents to the Camunda 8 cluster.

The caller must provide a file name for each document, which will be used in case of a multi-status
response
to identify which documents failed to upload. The file name can be provided in the `Content-
Disposition` header
of the file part or in the `fileName` field of the metadata. You can add a parallel array of
metadata objects. These
are matched with the files based on index, and must have the same length as the files array.
To pass homogenous metadata for all files, spread the metadata over the metadata array.
A filename value provided explicitly via the metadata array in the request overrides the `Content-
Disposition` header
of the file part.

In case of a multi-status response, the response body will contain a list of
`DocumentBatchProblemDetail` objects,
each of which contains the file name of the document that failed to upload and the reason for the
failure.
The client can choose to retry the whole batch or individual documents based on the response.

Note that this is currently supported for document stores of type: AWS, GCP, in-memory (non-
production), local (non-production)

Args:
    store_id (str | Unset):
    body (CreateDocumentsData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[CreateDocumentsResponse201 | CreateDocumentsResponse207 | CreateDocumentsResponse400 | CreateDocumentsResponse415]"""
    response = await asyncio_detailed(client=client, body=body, store_id=store_id)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
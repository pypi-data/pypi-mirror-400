from http import HTTPStatus
from typing import Any, cast
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.activate_ad_hoc_sub_process_activities_data import ActivateAdHocSubProcessActivitiesData
from ...models.activate_ad_hoc_sub_process_activities_response_400 import ActivateAdHocSubProcessActivitiesResponse400
from ...models.activate_ad_hoc_sub_process_activities_response_401 import ActivateAdHocSubProcessActivitiesResponse401
from ...models.activate_ad_hoc_sub_process_activities_response_403 import ActivateAdHocSubProcessActivitiesResponse403
from ...models.activate_ad_hoc_sub_process_activities_response_404 import ActivateAdHocSubProcessActivitiesResponse404
from ...models.activate_ad_hoc_sub_process_activities_response_500 import ActivateAdHocSubProcessActivitiesResponse500
from ...models.activate_ad_hoc_sub_process_activities_response_503 import ActivateAdHocSubProcessActivitiesResponse503
from ...types import Response

def _get_kwargs(ad_hoc_sub_process_instance_key: str, *, body: ActivateAdHocSubProcessActivitiesData) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    _kwargs: dict[str, Any] = {'method': 'post', 'url': '/element-instances/ad-hoc-activities/{ad_hoc_sub_process_instance_key}/activation'.format(ad_hoc_sub_process_instance_key=ad_hoc_sub_process_instance_key)}
    _kwargs['json'] = body.to_dict()
    headers['Content-Type'] = 'application/json'
    _kwargs['headers'] = headers
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ActivateAdHocSubProcessActivitiesResponse400 | ActivateAdHocSubProcessActivitiesResponse401 | ActivateAdHocSubProcessActivitiesResponse403 | ActivateAdHocSubProcessActivitiesResponse404 | ActivateAdHocSubProcessActivitiesResponse500 | ActivateAdHocSubProcessActivitiesResponse503 | Any | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 400:
        response_400 = ActivateAdHocSubProcessActivitiesResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = ActivateAdHocSubProcessActivitiesResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = ActivateAdHocSubProcessActivitiesResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = ActivateAdHocSubProcessActivitiesResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = ActivateAdHocSubProcessActivitiesResponse500.from_dict(response.json())
        return response_500
    if response.status_code == 503:
        response_503 = ActivateAdHocSubProcessActivitiesResponse503.from_dict(response.json())
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[ActivateAdHocSubProcessActivitiesResponse400 | ActivateAdHocSubProcessActivitiesResponse401 | ActivateAdHocSubProcessActivitiesResponse403 | ActivateAdHocSubProcessActivitiesResponse404 | ActivateAdHocSubProcessActivitiesResponse500 | ActivateAdHocSubProcessActivitiesResponse503 | Any]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(ad_hoc_sub_process_instance_key: str, *, client: AuthenticatedClient | Client, body: ActivateAdHocSubProcessActivitiesData) -> Response[ActivateAdHocSubProcessActivitiesResponse400 | ActivateAdHocSubProcessActivitiesResponse401 | ActivateAdHocSubProcessActivitiesResponse403 | ActivateAdHocSubProcessActivitiesResponse404 | ActivateAdHocSubProcessActivitiesResponse500 | ActivateAdHocSubProcessActivitiesResponse503 | Any]:
    """Activate activities within an ad-hoc sub-process

     Activates selected activities within an ad-hoc sub-process identified by element ID.
    The provided element IDs must exist within the ad-hoc sub-process instance identified by the
    provided adHocSubProcessInstanceKey.

    Args:
        ad_hoc_sub_process_instance_key (str): System-generated key for a element instance.
            Example: 2251799813686789.
        body (ActivateAdHocSubProcessActivitiesData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ActivateAdHocSubProcessActivitiesResponse400 | ActivateAdHocSubProcessActivitiesResponse401 | ActivateAdHocSubProcessActivitiesResponse403 | ActivateAdHocSubProcessActivitiesResponse404 | ActivateAdHocSubProcessActivitiesResponse500 | ActivateAdHocSubProcessActivitiesResponse503 | Any]
    """
    kwargs = _get_kwargs(ad_hoc_sub_process_instance_key=ad_hoc_sub_process_instance_key, body=body)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(ad_hoc_sub_process_instance_key: str, *, client: AuthenticatedClient | Client, body: ActivateAdHocSubProcessActivitiesData, **kwargs) -> ActivateAdHocSubProcessActivitiesResponse400:
    """Activate activities within an ad-hoc sub-process

 Activates selected activities within an ad-hoc sub-process identified by element ID.
The provided element IDs must exist within the ad-hoc sub-process instance identified by the
provided adHocSubProcessInstanceKey.

Args:
    ad_hoc_sub_process_instance_key (str): System-generated key for a element instance.
        Example: 2251799813686789.
    body (ActivateAdHocSubProcessActivitiesData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[ActivateAdHocSubProcessActivitiesResponse400 | ActivateAdHocSubProcessActivitiesResponse401 | ActivateAdHocSubProcessActivitiesResponse403 | ActivateAdHocSubProcessActivitiesResponse404 | ActivateAdHocSubProcessActivitiesResponse500 | ActivateAdHocSubProcessActivitiesResponse503 | Any]"""
    response = sync_detailed(ad_hoc_sub_process_instance_key=ad_hoc_sub_process_instance_key, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(ad_hoc_sub_process_instance_key: str, *, client: AuthenticatedClient | Client, body: ActivateAdHocSubProcessActivitiesData) -> Response[ActivateAdHocSubProcessActivitiesResponse400 | ActivateAdHocSubProcessActivitiesResponse401 | ActivateAdHocSubProcessActivitiesResponse403 | ActivateAdHocSubProcessActivitiesResponse404 | ActivateAdHocSubProcessActivitiesResponse500 | ActivateAdHocSubProcessActivitiesResponse503 | Any]:
    """Activate activities within an ad-hoc sub-process

     Activates selected activities within an ad-hoc sub-process identified by element ID.
    The provided element IDs must exist within the ad-hoc sub-process instance identified by the
    provided adHocSubProcessInstanceKey.

    Args:
        ad_hoc_sub_process_instance_key (str): System-generated key for a element instance.
            Example: 2251799813686789.
        body (ActivateAdHocSubProcessActivitiesData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ActivateAdHocSubProcessActivitiesResponse400 | ActivateAdHocSubProcessActivitiesResponse401 | ActivateAdHocSubProcessActivitiesResponse403 | ActivateAdHocSubProcessActivitiesResponse404 | ActivateAdHocSubProcessActivitiesResponse500 | ActivateAdHocSubProcessActivitiesResponse503 | Any]
    """
    kwargs = _get_kwargs(ad_hoc_sub_process_instance_key=ad_hoc_sub_process_instance_key, body=body)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(ad_hoc_sub_process_instance_key: str, *, client: AuthenticatedClient | Client, body: ActivateAdHocSubProcessActivitiesData, **kwargs) -> ActivateAdHocSubProcessActivitiesResponse400:
    """Activate activities within an ad-hoc sub-process

 Activates selected activities within an ad-hoc sub-process identified by element ID.
The provided element IDs must exist within the ad-hoc sub-process instance identified by the
provided adHocSubProcessInstanceKey.

Args:
    ad_hoc_sub_process_instance_key (str): System-generated key for a element instance.
        Example: 2251799813686789.
    body (ActivateAdHocSubProcessActivitiesData):

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[ActivateAdHocSubProcessActivitiesResponse400 | ActivateAdHocSubProcessActivitiesResponse401 | ActivateAdHocSubProcessActivitiesResponse403 | ActivateAdHocSubProcessActivitiesResponse404 | ActivateAdHocSubProcessActivitiesResponse500 | ActivateAdHocSubProcessActivitiesResponse503 | Any]"""
    response = await asyncio_detailed(ad_hoc_sub_process_instance_key=ad_hoc_sub_process_instance_key, client=client, body=body)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
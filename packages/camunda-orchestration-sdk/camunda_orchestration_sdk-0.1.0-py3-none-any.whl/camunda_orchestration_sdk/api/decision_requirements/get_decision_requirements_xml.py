from http import HTTPStatus
from typing import Any
import httpx
from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_decision_requirements_xml_response_400 import GetDecisionRequirementsXMLResponse400
from ...models.get_decision_requirements_xml_response_401 import GetDecisionRequirementsXMLResponse401
from ...models.get_decision_requirements_xml_response_403 import GetDecisionRequirementsXMLResponse403
from ...models.get_decision_requirements_xml_response_404 import GetDecisionRequirementsXMLResponse404
from ...models.get_decision_requirements_xml_response_500 import GetDecisionRequirementsXMLResponse500
from ...types import Response

def _get_kwargs(decision_requirements_key: str) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {'method': 'get', 'url': '/decision-requirements/{decision_requirements_key}/xml'.format(decision_requirements_key=decision_requirements_key)}
    return _kwargs

def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetDecisionRequirementsXMLResponse400 | GetDecisionRequirementsXMLResponse401 | GetDecisionRequirementsXMLResponse403 | GetDecisionRequirementsXMLResponse404 | GetDecisionRequirementsXMLResponse500 | str | None:
    if response.status_code == 200:
        response_200 = response.text
        return response_200
    if response.status_code == 400:
        response_400 = GetDecisionRequirementsXMLResponse400.from_dict(response.json())
        return response_400
    if response.status_code == 401:
        response_401 = GetDecisionRequirementsXMLResponse401.from_dict(response.json())
        return response_401
    if response.status_code == 403:
        response_403 = GetDecisionRequirementsXMLResponse403.from_dict(response.json())
        return response_403
    if response.status_code == 404:
        response_404 = GetDecisionRequirementsXMLResponse404.from_dict(response.json())
        return response_404
    if response.status_code == 500:
        response_500 = GetDecisionRequirementsXMLResponse500.from_dict(response.json())
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None

def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GetDecisionRequirementsXMLResponse400 | GetDecisionRequirementsXMLResponse401 | GetDecisionRequirementsXMLResponse403 | GetDecisionRequirementsXMLResponse404 | GetDecisionRequirementsXMLResponse500 | str]:
    return Response(status_code=HTTPStatus(response.status_code), content=response.content, headers=response.headers, parsed=_parse_response(client=client, response=response))

def sync_detailed(decision_requirements_key: str, *, client: AuthenticatedClient | Client) -> Response[GetDecisionRequirementsXMLResponse400 | GetDecisionRequirementsXMLResponse401 | GetDecisionRequirementsXMLResponse403 | GetDecisionRequirementsXMLResponse404 | GetDecisionRequirementsXMLResponse500 | str]:
    """Get decision requirements XML

     Returns decision requirements as XML.

    Args:
        decision_requirements_key (str): System-generated key for a deployed decision requirements
            definition. Example: 2251799813683346.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetDecisionRequirementsXMLResponse400 | GetDecisionRequirementsXMLResponse401 | GetDecisionRequirementsXMLResponse403 | GetDecisionRequirementsXMLResponse404 | GetDecisionRequirementsXMLResponse500 | str]
    """
    kwargs = _get_kwargs(decision_requirements_key=decision_requirements_key)
    response = client.get_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

def sync(decision_requirements_key: str, *, client: AuthenticatedClient | Client, **kwargs) -> GetDecisionRequirementsXMLResponse400:
    """Get decision requirements XML

 Returns decision requirements as XML.

Args:
    decision_requirements_key (str): System-generated key for a deployed decision requirements
        definition. Example: 2251799813683346.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetDecisionRequirementsXMLResponse400 | GetDecisionRequirementsXMLResponse401 | GetDecisionRequirementsXMLResponse403 | GetDecisionRequirementsXMLResponse404 | GetDecisionRequirementsXMLResponse500 | str]"""
    response = sync_detailed(decision_requirements_key=decision_requirements_key, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed

async def asyncio_detailed(decision_requirements_key: str, *, client: AuthenticatedClient | Client) -> Response[GetDecisionRequirementsXMLResponse400 | GetDecisionRequirementsXMLResponse401 | GetDecisionRequirementsXMLResponse403 | GetDecisionRequirementsXMLResponse404 | GetDecisionRequirementsXMLResponse500 | str]:
    """Get decision requirements XML

     Returns decision requirements as XML.

    Args:
        decision_requirements_key (str): System-generated key for a deployed decision requirements
            definition. Example: 2251799813683346.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetDecisionRequirementsXMLResponse400 | GetDecisionRequirementsXMLResponse401 | GetDecisionRequirementsXMLResponse403 | GetDecisionRequirementsXMLResponse404 | GetDecisionRequirementsXMLResponse500 | str]
    """
    kwargs = _get_kwargs(decision_requirements_key=decision_requirements_key)
    response = await client.get_async_httpx_client().request(**kwargs)
    return _build_response(client=client, response=response)

async def asyncio(decision_requirements_key: str, *, client: AuthenticatedClient | Client, **kwargs) -> GetDecisionRequirementsXMLResponse400:
    """Get decision requirements XML

 Returns decision requirements as XML.

Args:
    decision_requirements_key (str): System-generated key for a deployed decision requirements
        definition. Example: 2251799813683346.

Raises:
    errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
    httpx.TimeoutException: If the request takes longer than Client.timeout.

Returns:
    Response[GetDecisionRequirementsXMLResponse400 | GetDecisionRequirementsXMLResponse401 | GetDecisionRequirementsXMLResponse403 | GetDecisionRequirementsXMLResponse404 | GetDecisionRequirementsXMLResponse500 | str]"""
    response = await asyncio_detailed(decision_requirements_key=decision_requirements_key, client=client)
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return response.parsed
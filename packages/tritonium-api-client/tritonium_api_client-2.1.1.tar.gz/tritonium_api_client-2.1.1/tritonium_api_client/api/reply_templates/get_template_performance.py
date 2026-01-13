from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error_response import ErrorResponse
from ...models.get_template_performance_response_200 import GetTemplatePerformanceResponse200
from ...types import UNSET, Unset
from typing import cast
from typing import Union



def _get_kwargs(
    *,
    days: Union[Unset, int] = 90,
    template_id: Union[Unset, str] = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["days"] = days

    params["template_id"] = template_id


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/reply-templates/performance",
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[ErrorResponse, GetTemplatePerformanceResponse200]]:
    if response.status_code == 200:
        response_200 = GetTemplatePerformanceResponse200.from_dict(response.json())



        return response_200

    if response.status_code == 401:
        response_401 = ErrorResponse.from_dict(response.json())



        return response_401

    if response.status_code == 403:
        response_403 = ErrorResponse.from_dict(response.json())



        return response_403

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[ErrorResponse, GetTemplatePerformanceResponse200]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    days: Union[Unset, int] = 90,
    template_id: Union[Unset, str] = UNSET,

) -> Response[Union[ErrorResponse, GetTemplatePerformanceResponse200]]:
    """ List reply template performance metrics.

    Args:
        days (Union[Unset, int]):  Default: 90.
        template_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, GetTemplatePerformanceResponse200]]
     """


    kwargs = _get_kwargs(
        days=days,
template_id=template_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: AuthenticatedClient,
    days: Union[Unset, int] = 90,
    template_id: Union[Unset, str] = UNSET,

) -> Optional[Union[ErrorResponse, GetTemplatePerformanceResponse200]]:
    """ List reply template performance metrics.

    Args:
        days (Union[Unset, int]):  Default: 90.
        template_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, GetTemplatePerformanceResponse200]
     """


    return sync_detailed(
        client=client,
days=days,
template_id=template_id,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    days: Union[Unset, int] = 90,
    template_id: Union[Unset, str] = UNSET,

) -> Response[Union[ErrorResponse, GetTemplatePerformanceResponse200]]:
    """ List reply template performance metrics.

    Args:
        days (Union[Unset, int]):  Default: 90.
        template_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, GetTemplatePerformanceResponse200]]
     """


    kwargs = _get_kwargs(
        days=days,
template_id=template_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient,
    days: Union[Unset, int] = 90,
    template_id: Union[Unset, str] = UNSET,

) -> Optional[Union[ErrorResponse, GetTemplatePerformanceResponse200]]:
    """ List reply template performance metrics.

    Args:
        days (Union[Unset, int]):  Default: 90.
        template_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, GetTemplatePerformanceResponse200]
     """


    return (await asyncio_detailed(
        client=client,
days=days,
template_id=template_id,

    )).parsed

from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error_response import ErrorResponse
from ...models.get_competitors_response_200 import GetCompetitorsResponse200
from typing import cast



def _get_kwargs(
    app_uuid: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/apps/{app_uuid}/competitors".format(app_uuid=app_uuid,),
    }


    return _kwargs



def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[ErrorResponse, GetCompetitorsResponse200]]:
    if response.status_code == 200:
        response_200 = GetCompetitorsResponse200.from_dict(response.json())



        return response_200

    if response.status_code == 401:
        response_401 = ErrorResponse.from_dict(response.json())



        return response_401

    if response.status_code == 403:
        response_403 = ErrorResponse.from_dict(response.json())



        return response_403

    if response.status_code == 404:
        response_404 = ErrorResponse.from_dict(response.json())



        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[ErrorResponse, GetCompetitorsResponse200]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    app_uuid: str,
    *,
    client: AuthenticatedClient,

) -> Response[Union[ErrorResponse, GetCompetitorsResponse200]]:
    """ List competitor apps registered for benchmarking.

    Args:
        app_uuid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, GetCompetitorsResponse200]]
     """


    kwargs = _get_kwargs(
        app_uuid=app_uuid,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    app_uuid: str,
    *,
    client: AuthenticatedClient,

) -> Optional[Union[ErrorResponse, GetCompetitorsResponse200]]:
    """ List competitor apps registered for benchmarking.

    Args:
        app_uuid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, GetCompetitorsResponse200]
     """


    return sync_detailed(
        app_uuid=app_uuid,
client=client,

    ).parsed

async def asyncio_detailed(
    app_uuid: str,
    *,
    client: AuthenticatedClient,

) -> Response[Union[ErrorResponse, GetCompetitorsResponse200]]:
    """ List competitor apps registered for benchmarking.

    Args:
        app_uuid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, GetCompetitorsResponse200]]
     """


    kwargs = _get_kwargs(
        app_uuid=app_uuid,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    app_uuid: str,
    *,
    client: AuthenticatedClient,

) -> Optional[Union[ErrorResponse, GetCompetitorsResponse200]]:
    """ List competitor apps registered for benchmarking.

    Args:
        app_uuid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, GetCompetitorsResponse200]
     """


    return (await asyncio_detailed(
        app_uuid=app_uuid,
client=client,

    )).parsed

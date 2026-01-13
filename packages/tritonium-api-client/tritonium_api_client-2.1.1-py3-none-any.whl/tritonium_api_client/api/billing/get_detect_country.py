from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error_response import ErrorResponse
from ...models.get_detect_country_response_200 import GetDetectCountryResponse200
from typing import cast



def _get_kwargs(
    
) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/billing/detect-country",
    }


    return _kwargs



def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[ErrorResponse, GetDetectCountryResponse200]]:
    if response.status_code == 200:
        response_200 = GetDetectCountryResponse200.from_dict(response.json())



        return response_200

    if response.status_code == 401:
        response_401 = ErrorResponse.from_dict(response.json())



        return response_401

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[ErrorResponse, GetDetectCountryResponse200]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,

) -> Response[Union[ErrorResponse, GetDetectCountryResponse200]]:
    """ Detect user's country from IP address.

     Detects the user's country based on their IP address for display purposes. Note: Final pricing is
    always determined by card country, not IP location.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, GetDetectCountryResponse200]]
     """


    kwargs = _get_kwargs(
        
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: AuthenticatedClient,

) -> Optional[Union[ErrorResponse, GetDetectCountryResponse200]]:
    """ Detect user's country from IP address.

     Detects the user's country based on their IP address for display purposes. Note: Final pricing is
    always determined by card country, not IP location.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, GetDetectCountryResponse200]
     """


    return sync_detailed(
        client=client,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient,

) -> Response[Union[ErrorResponse, GetDetectCountryResponse200]]:
    """ Detect user's country from IP address.

     Detects the user's country based on their IP address for display purposes. Note: Final pricing is
    always determined by card country, not IP location.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, GetDetectCountryResponse200]]
     """


    kwargs = _get_kwargs(
        
    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient,

) -> Optional[Union[ErrorResponse, GetDetectCountryResponse200]]:
    """ Detect user's country from IP address.

     Detects the user's country based on their IP address for display purposes. Note: Final pricing is
    always determined by card country, not IP location.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, GetDetectCountryResponse200]
     """


    return (await asyncio_detailed(
        client=client,

    )).parsed

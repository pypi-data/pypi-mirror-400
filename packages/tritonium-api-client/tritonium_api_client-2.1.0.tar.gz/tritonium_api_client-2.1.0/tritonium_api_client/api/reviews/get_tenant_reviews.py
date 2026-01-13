from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error_response import ErrorResponse
from ...models.get_tenant_reviews_response_200 import GetTenantReviewsResponse200
from ...types import UNSET, Unset
from typing import cast
from typing import Union



def _get_kwargs(
    *,
    limit: Union[Unset, int] = UNSET,
    cursor: Union[Unset, str] = UNSET,
    app_uuid: Union[Unset, str] = UNSET,
    sentiment: Union[Unset, str] = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["limit"] = limit

    params["cursor"] = cursor

    params["app_uuid"] = app_uuid

    params["sentiment"] = sentiment


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/reviews",
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[ErrorResponse, GetTenantReviewsResponse200]]:
    if response.status_code == 200:
        response_200 = GetTenantReviewsResponse200.from_dict(response.json())



        return response_200

    if response.status_code == 401:
        response_401 = ErrorResponse.from_dict(response.json())



        return response_401

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[ErrorResponse, GetTenantReviewsResponse200]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = UNSET,
    cursor: Union[Unset, str] = UNSET,
    app_uuid: Union[Unset, str] = UNSET,
    sentiment: Union[Unset, str] = UNSET,

) -> Response[Union[ErrorResponse, GetTenantReviewsResponse200]]:
    """ Discover reviews across all connected apps.

    Args:
        limit (Union[Unset, int]):
        cursor (Union[Unset, str]):
        app_uuid (Union[Unset, str]):
        sentiment (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, GetTenantReviewsResponse200]]
     """


    kwargs = _get_kwargs(
        limit=limit,
cursor=cursor,
app_uuid=app_uuid,
sentiment=sentiment,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = UNSET,
    cursor: Union[Unset, str] = UNSET,
    app_uuid: Union[Unset, str] = UNSET,
    sentiment: Union[Unset, str] = UNSET,

) -> Optional[Union[ErrorResponse, GetTenantReviewsResponse200]]:
    """ Discover reviews across all connected apps.

    Args:
        limit (Union[Unset, int]):
        cursor (Union[Unset, str]):
        app_uuid (Union[Unset, str]):
        sentiment (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, GetTenantReviewsResponse200]
     """


    return sync_detailed(
        client=client,
limit=limit,
cursor=cursor,
app_uuid=app_uuid,
sentiment=sentiment,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = UNSET,
    cursor: Union[Unset, str] = UNSET,
    app_uuid: Union[Unset, str] = UNSET,
    sentiment: Union[Unset, str] = UNSET,

) -> Response[Union[ErrorResponse, GetTenantReviewsResponse200]]:
    """ Discover reviews across all connected apps.

    Args:
        limit (Union[Unset, int]):
        cursor (Union[Unset, str]):
        app_uuid (Union[Unset, str]):
        sentiment (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, GetTenantReviewsResponse200]]
     """


    kwargs = _get_kwargs(
        limit=limit,
cursor=cursor,
app_uuid=app_uuid,
sentiment=sentiment,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = UNSET,
    cursor: Union[Unset, str] = UNSET,
    app_uuid: Union[Unset, str] = UNSET,
    sentiment: Union[Unset, str] = UNSET,

) -> Optional[Union[ErrorResponse, GetTenantReviewsResponse200]]:
    """ Discover reviews across all connected apps.

    Args:
        limit (Union[Unset, int]):
        cursor (Union[Unset, str]):
        app_uuid (Union[Unset, str]):
        sentiment (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, GetTenantReviewsResponse200]
     """


    return (await asyncio_detailed(
        client=client,
limit=limit,
cursor=cursor,
app_uuid=app_uuid,
sentiment=sentiment,

    )).parsed

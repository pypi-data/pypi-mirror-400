from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error_response import ErrorResponse
from ...models.get_app_segments_response_200 import GetAppSegmentsResponse200
from ...models.get_app_segments_sort import GetAppSegmentsSort
from ...types import UNSET, Unset
from typing import cast
from typing import Union



def _get_kwargs(
    app_uuid: str,
    *,
    segment_type: Union[Unset, str] = UNSET,
    sort: Union[Unset, GetAppSegmentsSort] = UNSET,
    limit: Union[Unset, int] = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["segment_type"] = segment_type

    json_sort: Union[Unset, str] = UNSET
    if not isinstance(sort, Unset):
        json_sort = sort.value

    params["sort"] = json_sort

    params["limit"] = limit


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/apps/{app_uuid}/segments".format(app_uuid=app_uuid,),
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[ErrorResponse, GetAppSegmentsResponse200]]:
    if response.status_code == 200:
        response_200 = GetAppSegmentsResponse200.from_dict(response.json())



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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[ErrorResponse, GetAppSegmentsResponse200]]:
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
    segment_type: Union[Unset, str] = UNSET,
    sort: Union[Unset, GetAppSegmentsSort] = UNSET,
    limit: Union[Unset, int] = UNSET,

) -> Response[Union[ErrorResponse, GetAppSegmentsResponse200]]:
    """ List reviewer segments for an app.

    Args:
        app_uuid (str):
        segment_type (Union[Unset, str]):
        sort (Union[Unset, GetAppSegmentsSort]):
        limit (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, GetAppSegmentsResponse200]]
     """


    kwargs = _get_kwargs(
        app_uuid=app_uuid,
segment_type=segment_type,
sort=sort,
limit=limit,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    app_uuid: str,
    *,
    client: AuthenticatedClient,
    segment_type: Union[Unset, str] = UNSET,
    sort: Union[Unset, GetAppSegmentsSort] = UNSET,
    limit: Union[Unset, int] = UNSET,

) -> Optional[Union[ErrorResponse, GetAppSegmentsResponse200]]:
    """ List reviewer segments for an app.

    Args:
        app_uuid (str):
        segment_type (Union[Unset, str]):
        sort (Union[Unset, GetAppSegmentsSort]):
        limit (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, GetAppSegmentsResponse200]
     """


    return sync_detailed(
        app_uuid=app_uuid,
client=client,
segment_type=segment_type,
sort=sort,
limit=limit,

    ).parsed

async def asyncio_detailed(
    app_uuid: str,
    *,
    client: AuthenticatedClient,
    segment_type: Union[Unset, str] = UNSET,
    sort: Union[Unset, GetAppSegmentsSort] = UNSET,
    limit: Union[Unset, int] = UNSET,

) -> Response[Union[ErrorResponse, GetAppSegmentsResponse200]]:
    """ List reviewer segments for an app.

    Args:
        app_uuid (str):
        segment_type (Union[Unset, str]):
        sort (Union[Unset, GetAppSegmentsSort]):
        limit (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, GetAppSegmentsResponse200]]
     """


    kwargs = _get_kwargs(
        app_uuid=app_uuid,
segment_type=segment_type,
sort=sort,
limit=limit,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    app_uuid: str,
    *,
    client: AuthenticatedClient,
    segment_type: Union[Unset, str] = UNSET,
    sort: Union[Unset, GetAppSegmentsSort] = UNSET,
    limit: Union[Unset, int] = UNSET,

) -> Optional[Union[ErrorResponse, GetAppSegmentsResponse200]]:
    """ List reviewer segments for an app.

    Args:
        app_uuid (str):
        segment_type (Union[Unset, str]):
        sort (Union[Unset, GetAppSegmentsSort]):
        limit (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, GetAppSegmentsResponse200]
     """


    return (await asyncio_detailed(
        app_uuid=app_uuid,
client=client,
segment_type=segment_type,
sort=sort,
limit=limit,

    )).parsed

from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error_response import ErrorResponse
from ...models.get_ratings_history_order import GetRatingsHistoryOrder
from ...models.get_ratings_history_response_200 import GetRatingsHistoryResponse200
from ...types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import Union
import datetime



def _get_kwargs(
    app_uuid: str,
    *,
    limit: Union[Unset, int] = UNSET,
    cursor: Union[Unset, str] = UNSET,
    order: Union[Unset, GetRatingsHistoryOrder] = UNSET,
    platform: Union[Unset, str] = UNSET,
    start_date: Union[Unset, datetime.date] = UNSET,
    end_date: Union[Unset, datetime.date] = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["limit"] = limit

    params["cursor"] = cursor

    json_order: Union[Unset, str] = UNSET
    if not isinstance(order, Unset):
        json_order = order.value

    params["order"] = json_order

    params["platform"] = platform

    json_start_date: Union[Unset, str] = UNSET
    if not isinstance(start_date, Unset):
        json_start_date = start_date.isoformat()
    params["start_date"] = json_start_date

    json_end_date: Union[Unset, str] = UNSET
    if not isinstance(end_date, Unset):
        json_end_date = end_date.isoformat()
    params["end_date"] = json_end_date


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/apps/{app_uuid}/ratings/history".format(app_uuid=app_uuid,),
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[ErrorResponse, GetRatingsHistoryResponse200]]:
    if response.status_code == 200:
        response_200 = GetRatingsHistoryResponse200.from_dict(response.json())



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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[ErrorResponse, GetRatingsHistoryResponse200]]:
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
    limit: Union[Unset, int] = UNSET,
    cursor: Union[Unset, str] = UNSET,
    order: Union[Unset, GetRatingsHistoryOrder] = UNSET,
    platform: Union[Unset, str] = UNSET,
    start_date: Union[Unset, datetime.date] = UNSET,
    end_date: Union[Unset, datetime.date] = UNSET,

) -> Response[Union[ErrorResponse, GetRatingsHistoryResponse200]]:
    """ Historical rating snapshots for an app.

    Args:
        app_uuid (str):
        limit (Union[Unset, int]):
        cursor (Union[Unset, str]):
        order (Union[Unset, GetRatingsHistoryOrder]):
        platform (Union[Unset, str]):
        start_date (Union[Unset, datetime.date]):
        end_date (Union[Unset, datetime.date]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, GetRatingsHistoryResponse200]]
     """


    kwargs = _get_kwargs(
        app_uuid=app_uuid,
limit=limit,
cursor=cursor,
order=order,
platform=platform,
start_date=start_date,
end_date=end_date,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    app_uuid: str,
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = UNSET,
    cursor: Union[Unset, str] = UNSET,
    order: Union[Unset, GetRatingsHistoryOrder] = UNSET,
    platform: Union[Unset, str] = UNSET,
    start_date: Union[Unset, datetime.date] = UNSET,
    end_date: Union[Unset, datetime.date] = UNSET,

) -> Optional[Union[ErrorResponse, GetRatingsHistoryResponse200]]:
    """ Historical rating snapshots for an app.

    Args:
        app_uuid (str):
        limit (Union[Unset, int]):
        cursor (Union[Unset, str]):
        order (Union[Unset, GetRatingsHistoryOrder]):
        platform (Union[Unset, str]):
        start_date (Union[Unset, datetime.date]):
        end_date (Union[Unset, datetime.date]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, GetRatingsHistoryResponse200]
     """


    return sync_detailed(
        app_uuid=app_uuid,
client=client,
limit=limit,
cursor=cursor,
order=order,
platform=platform,
start_date=start_date,
end_date=end_date,

    ).parsed

async def asyncio_detailed(
    app_uuid: str,
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = UNSET,
    cursor: Union[Unset, str] = UNSET,
    order: Union[Unset, GetRatingsHistoryOrder] = UNSET,
    platform: Union[Unset, str] = UNSET,
    start_date: Union[Unset, datetime.date] = UNSET,
    end_date: Union[Unset, datetime.date] = UNSET,

) -> Response[Union[ErrorResponse, GetRatingsHistoryResponse200]]:
    """ Historical rating snapshots for an app.

    Args:
        app_uuid (str):
        limit (Union[Unset, int]):
        cursor (Union[Unset, str]):
        order (Union[Unset, GetRatingsHistoryOrder]):
        platform (Union[Unset, str]):
        start_date (Union[Unset, datetime.date]):
        end_date (Union[Unset, datetime.date]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, GetRatingsHistoryResponse200]]
     """


    kwargs = _get_kwargs(
        app_uuid=app_uuid,
limit=limit,
cursor=cursor,
order=order,
platform=platform,
start_date=start_date,
end_date=end_date,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    app_uuid: str,
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = UNSET,
    cursor: Union[Unset, str] = UNSET,
    order: Union[Unset, GetRatingsHistoryOrder] = UNSET,
    platform: Union[Unset, str] = UNSET,
    start_date: Union[Unset, datetime.date] = UNSET,
    end_date: Union[Unset, datetime.date] = UNSET,

) -> Optional[Union[ErrorResponse, GetRatingsHistoryResponse200]]:
    """ Historical rating snapshots for an app.

    Args:
        app_uuid (str):
        limit (Union[Unset, int]):
        cursor (Union[Unset, str]):
        order (Union[Unset, GetRatingsHistoryOrder]):
        platform (Union[Unset, str]):
        start_date (Union[Unset, datetime.date]):
        end_date (Union[Unset, datetime.date]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, GetRatingsHistoryResponse200]
     """


    return (await asyncio_detailed(
        app_uuid=app_uuid,
client=client,
limit=limit,
cursor=cursor,
order=order,
platform=platform,
start_date=start_date,
end_date=end_date,

    )).parsed

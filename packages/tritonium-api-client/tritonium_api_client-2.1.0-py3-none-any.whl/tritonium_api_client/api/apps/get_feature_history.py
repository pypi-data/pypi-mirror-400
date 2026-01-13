from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error_response import ErrorResponse
from ...models.get_feature_history_response_200 import GetFeatureHistoryResponse200
from ...types import UNSET, Unset
from typing import cast
from typing import Union



def _get_kwargs(
    app_uuid: str,
    *,
    limit: Union[Unset, int] = UNSET,
    cursor: Union[Unset, str] = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["limit"] = limit

    params["cursor"] = cursor


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/apps/{app_uuid}/features/history".format(app_uuid=app_uuid,),
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[ErrorResponse, GetFeatureHistoryResponse200]]:
    if response.status_code == 200:
        response_200 = GetFeatureHistoryResponse200.from_dict(response.json())



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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[ErrorResponse, GetFeatureHistoryResponse200]]:
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

) -> Response[Union[ErrorResponse, GetFeatureHistoryResponse200]]:
    """ Historical feature impact entries for an app release.

    Args:
        app_uuid (str):
        limit (Union[Unset, int]):
        cursor (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, GetFeatureHistoryResponse200]]
     """


    kwargs = _get_kwargs(
        app_uuid=app_uuid,
limit=limit,
cursor=cursor,

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

) -> Optional[Union[ErrorResponse, GetFeatureHistoryResponse200]]:
    """ Historical feature impact entries for an app release.

    Args:
        app_uuid (str):
        limit (Union[Unset, int]):
        cursor (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, GetFeatureHistoryResponse200]
     """


    return sync_detailed(
        app_uuid=app_uuid,
client=client,
limit=limit,
cursor=cursor,

    ).parsed

async def asyncio_detailed(
    app_uuid: str,
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = UNSET,
    cursor: Union[Unset, str] = UNSET,

) -> Response[Union[ErrorResponse, GetFeatureHistoryResponse200]]:
    """ Historical feature impact entries for an app release.

    Args:
        app_uuid (str):
        limit (Union[Unset, int]):
        cursor (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, GetFeatureHistoryResponse200]]
     """


    kwargs = _get_kwargs(
        app_uuid=app_uuid,
limit=limit,
cursor=cursor,

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

) -> Optional[Union[ErrorResponse, GetFeatureHistoryResponse200]]:
    """ Historical feature impact entries for an app release.

    Args:
        app_uuid (str):
        limit (Union[Unset, int]):
        cursor (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, GetFeatureHistoryResponse200]
     """


    return (await asyncio_detailed(
        app_uuid=app_uuid,
client=client,
limit=limit,
cursor=cursor,

    )).parsed

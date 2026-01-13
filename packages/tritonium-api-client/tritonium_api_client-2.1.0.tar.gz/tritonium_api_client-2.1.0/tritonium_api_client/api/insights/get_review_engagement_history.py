from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error_response import ErrorResponse
from ...models.get_review_engagement_history_response_200 import GetReviewEngagementHistoryResponse200
from typing import cast



def _get_kwargs(
    review_id: str,
    *,
    app_uuid: str,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["app_uuid"] = app_uuid


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/reviews/{review_id}/engagement/history".format(review_id=review_id,),
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[ErrorResponse, GetReviewEngagementHistoryResponse200]]:
    if response.status_code == 200:
        response_200 = GetReviewEngagementHistoryResponse200.from_dict(response.json())



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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[ErrorResponse, GetReviewEngagementHistoryResponse200]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    review_id: str,
    *,
    client: AuthenticatedClient,
    app_uuid: str,

) -> Response[Union[ErrorResponse, GetReviewEngagementHistoryResponse200]]:
    """ Retrieve engagement history for a review.

    Args:
        review_id (str):
        app_uuid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, GetReviewEngagementHistoryResponse200]]
     """


    kwargs = _get_kwargs(
        review_id=review_id,
app_uuid=app_uuid,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    review_id: str,
    *,
    client: AuthenticatedClient,
    app_uuid: str,

) -> Optional[Union[ErrorResponse, GetReviewEngagementHistoryResponse200]]:
    """ Retrieve engagement history for a review.

    Args:
        review_id (str):
        app_uuid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, GetReviewEngagementHistoryResponse200]
     """


    return sync_detailed(
        review_id=review_id,
client=client,
app_uuid=app_uuid,

    ).parsed

async def asyncio_detailed(
    review_id: str,
    *,
    client: AuthenticatedClient,
    app_uuid: str,

) -> Response[Union[ErrorResponse, GetReviewEngagementHistoryResponse200]]:
    """ Retrieve engagement history for a review.

    Args:
        review_id (str):
        app_uuid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, GetReviewEngagementHistoryResponse200]]
     """


    kwargs = _get_kwargs(
        review_id=review_id,
app_uuid=app_uuid,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    review_id: str,
    *,
    client: AuthenticatedClient,
    app_uuid: str,

) -> Optional[Union[ErrorResponse, GetReviewEngagementHistoryResponse200]]:
    """ Retrieve engagement history for a review.

    Args:
        review_id (str):
        app_uuid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, GetReviewEngagementHistoryResponse200]
     """


    return (await asyncio_detailed(
        review_id=review_id,
client=client,
app_uuid=app_uuid,

    )).parsed

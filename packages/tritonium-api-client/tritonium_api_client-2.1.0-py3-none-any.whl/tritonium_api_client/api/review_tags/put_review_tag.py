from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error_response import ErrorResponse
from ...models.put_review_tag_response_200 import PutReviewTagResponse200
from ...models.update_review_tag_request import UpdateReviewTagRequest
from typing import cast
from uuid import UUID



def _get_kwargs(
    tag_id: UUID,
    *,
    body: UpdateReviewTagRequest,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/api/v1/review-tags/{tag_id}".format(tag_id=tag_id,),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[ErrorResponse, PutReviewTagResponse200]]:
    if response.status_code == 200:
        response_200 = PutReviewTagResponse200.from_dict(response.json())



        return response_200

    if response.status_code == 401:
        response_401 = ErrorResponse.from_dict(response.json())



        return response_401

    if response.status_code == 404:
        response_404 = ErrorResponse.from_dict(response.json())



        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[ErrorResponse, PutReviewTagResponse200]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    tag_id: UUID,
    *,
    client: AuthenticatedClient,
    body: UpdateReviewTagRequest,

) -> Response[Union[ErrorResponse, PutReviewTagResponse200]]:
    """ Update a review tag.

    Args:
        tag_id (UUID):
        body (UpdateReviewTagRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, PutReviewTagResponse200]]
     """


    kwargs = _get_kwargs(
        tag_id=tag_id,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    tag_id: UUID,
    *,
    client: AuthenticatedClient,
    body: UpdateReviewTagRequest,

) -> Optional[Union[ErrorResponse, PutReviewTagResponse200]]:
    """ Update a review tag.

    Args:
        tag_id (UUID):
        body (UpdateReviewTagRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, PutReviewTagResponse200]
     """


    return sync_detailed(
        tag_id=tag_id,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    tag_id: UUID,
    *,
    client: AuthenticatedClient,
    body: UpdateReviewTagRequest,

) -> Response[Union[ErrorResponse, PutReviewTagResponse200]]:
    """ Update a review tag.

    Args:
        tag_id (UUID):
        body (UpdateReviewTagRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, PutReviewTagResponse200]]
     """


    kwargs = _get_kwargs(
        tag_id=tag_id,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    tag_id: UUID,
    *,
    client: AuthenticatedClient,
    body: UpdateReviewTagRequest,

) -> Optional[Union[ErrorResponse, PutReviewTagResponse200]]:
    """ Update a review tag.

    Args:
        tag_id (UUID):
        body (UpdateReviewTagRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, PutReviewTagResponse200]
     """


    return (await asyncio_detailed(
        tag_id=tag_id,
client=client,
body=body,

    )).parsed

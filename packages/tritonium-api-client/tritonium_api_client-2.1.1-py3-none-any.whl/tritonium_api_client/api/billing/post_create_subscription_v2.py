from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error_response import ErrorResponse
from ...models.post_create_subscription_v2_body import PostCreateSubscriptionV2Body
from ...models.post_create_subscription_v2_response_200 import PostCreateSubscriptionV2Response200
from typing import cast



def _get_kwargs(
    *,
    body: PostCreateSubscriptionV2Body,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/billing/create-subscription-v2",
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[ErrorResponse, PostCreateSubscriptionV2Response200]]:
    if response.status_code == 200:
        response_200 = PostCreateSubscriptionV2Response200.from_dict(response.json())



        return response_200

    if response.status_code == 400:
        response_400 = ErrorResponse.from_dict(response.json())



        return response_400

    if response.status_code == 402:
        response_402 = ErrorResponse.from_dict(response.json())



        return response_402

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[ErrorResponse, PostCreateSubscriptionV2Response200]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: PostCreateSubscriptionV2Body,

) -> Response[Union[ErrorResponse, PostCreateSubscriptionV2Response200]]:
    """ Create per-integration subscription.

    Args:
        body (PostCreateSubscriptionV2Body):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, PostCreateSubscriptionV2Response200]]
     """


    kwargs = _get_kwargs(
        body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: AuthenticatedClient,
    body: PostCreateSubscriptionV2Body,

) -> Optional[Union[ErrorResponse, PostCreateSubscriptionV2Response200]]:
    """ Create per-integration subscription.

    Args:
        body (PostCreateSubscriptionV2Body):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, PostCreateSubscriptionV2Response200]
     """


    return sync_detailed(
        client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: PostCreateSubscriptionV2Body,

) -> Response[Union[ErrorResponse, PostCreateSubscriptionV2Response200]]:
    """ Create per-integration subscription.

    Args:
        body (PostCreateSubscriptionV2Body):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, PostCreateSubscriptionV2Response200]]
     """


    kwargs = _get_kwargs(
        body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient,
    body: PostCreateSubscriptionV2Body,

) -> Optional[Union[ErrorResponse, PostCreateSubscriptionV2Response200]]:
    """ Create per-integration subscription.

    Args:
        body (PostCreateSubscriptionV2Body):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, PostCreateSubscriptionV2Response200]
     """


    return (await asyncio_detailed(
        client=client,
body=body,

    )).parsed

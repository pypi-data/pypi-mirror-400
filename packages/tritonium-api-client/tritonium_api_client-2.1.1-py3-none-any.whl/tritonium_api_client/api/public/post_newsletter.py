from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error_response import ErrorResponse
from ...models.newsletter_request import NewsletterRequest
from ...models.post_newsletter_response_200 import PostNewsletterResponse200
from ...models.post_newsletter_response_429 import PostNewsletterResponse429
from typing import cast



def _get_kwargs(
    *,
    body: NewsletterRequest,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/newsletter",
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[ErrorResponse, PostNewsletterResponse200, PostNewsletterResponse429]]:
    if response.status_code == 200:
        response_200 = PostNewsletterResponse200.from_dict(response.json())



        return response_200

    if response.status_code == 400:
        response_400 = ErrorResponse.from_dict(response.json())



        return response_400

    if response.status_code == 429:
        response_429 = PostNewsletterResponse429.from_dict(response.json())



        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[ErrorResponse, PostNewsletterResponse200, PostNewsletterResponse429]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: NewsletterRequest,

) -> Response[Union[ErrorResponse, PostNewsletterResponse200, PostNewsletterResponse429]]:
    """ Subscribe to the newsletter.

     Captures newsletter subscription requests. Rate limited to 10 requests per IP per hour.

    Args:
        body (NewsletterRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, PostNewsletterResponse200, PostNewsletterResponse429]]
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
    client: Union[AuthenticatedClient, Client],
    body: NewsletterRequest,

) -> Optional[Union[ErrorResponse, PostNewsletterResponse200, PostNewsletterResponse429]]:
    """ Subscribe to the newsletter.

     Captures newsletter subscription requests. Rate limited to 10 requests per IP per hour.

    Args:
        body (NewsletterRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, PostNewsletterResponse200, PostNewsletterResponse429]
     """


    return sync_detailed(
        client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: NewsletterRequest,

) -> Response[Union[ErrorResponse, PostNewsletterResponse200, PostNewsletterResponse429]]:
    """ Subscribe to the newsletter.

     Captures newsletter subscription requests. Rate limited to 10 requests per IP per hour.

    Args:
        body (NewsletterRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, PostNewsletterResponse200, PostNewsletterResponse429]]
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
    client: Union[AuthenticatedClient, Client],
    body: NewsletterRequest,

) -> Optional[Union[ErrorResponse, PostNewsletterResponse200, PostNewsletterResponse429]]:
    """ Subscribe to the newsletter.

     Captures newsletter subscription requests. Rate limited to 10 requests per IP per hour.

    Args:
        body (NewsletterRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, PostNewsletterResponse200, PostNewsletterResponse429]
     """


    return (await asyncio_detailed(
        client=client,
body=body,

    )).parsed

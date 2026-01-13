from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.contact_request import ContactRequest
from ...models.error_response import ErrorResponse
from ...models.generic_success import GenericSuccess
from ...models.post_contact_response_429 import PostContactResponse429
from typing import cast



def _get_kwargs(
    *,
    body: ContactRequest,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/contact",
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[ErrorResponse, GenericSuccess, PostContactResponse429]]:
    if response.status_code == 202:
        response_202 = GenericSuccess.from_dict(response.json())



        return response_202

    if response.status_code == 400:
        response_400 = ErrorResponse.from_dict(response.json())



        return response_400

    if response.status_code == 429:
        response_429 = PostContactResponse429.from_dict(response.json())



        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[ErrorResponse, GenericSuccess, PostContactResponse429]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ContactRequest,

) -> Response[Union[ErrorResponse, GenericSuccess, PostContactResponse429]]:
    """ Submit a contact form inquiry.

     Captures contact form submissions from the marketing website. Rate limited to 5 requests per IP per
    hour.

    Args:
        body (ContactRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, GenericSuccess, PostContactResponse429]]
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
    body: ContactRequest,

) -> Optional[Union[ErrorResponse, GenericSuccess, PostContactResponse429]]:
    """ Submit a contact form inquiry.

     Captures contact form submissions from the marketing website. Rate limited to 5 requests per IP per
    hour.

    Args:
        body (ContactRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, GenericSuccess, PostContactResponse429]
     """


    return sync_detailed(
        client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ContactRequest,

) -> Response[Union[ErrorResponse, GenericSuccess, PostContactResponse429]]:
    """ Submit a contact form inquiry.

     Captures contact form submissions from the marketing website. Rate limited to 5 requests per IP per
    hour.

    Args:
        body (ContactRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, GenericSuccess, PostContactResponse429]]
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
    body: ContactRequest,

) -> Optional[Union[ErrorResponse, GenericSuccess, PostContactResponse429]]:
    """ Submit a contact form inquiry.

     Captures contact form submissions from the marketing website. Rate limited to 5 requests per IP per
    hour.

    Args:
        body (ContactRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, GenericSuccess, PostContactResponse429]
     """


    return (await asyncio_detailed(
        client=client,
body=body,

    )).parsed

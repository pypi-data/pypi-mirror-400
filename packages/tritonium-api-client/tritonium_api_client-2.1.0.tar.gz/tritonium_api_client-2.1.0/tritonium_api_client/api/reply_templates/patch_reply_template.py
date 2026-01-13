from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error_response import ErrorResponse
from ...models.reply_template import ReplyTemplate
from ...models.reply_template_patch_request import ReplyTemplatePatchRequest
from typing import cast



def _get_kwargs(
    template_id: str,
    *,
    body: ReplyTemplatePatchRequest,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/api/v1/reply-templates/{template_id}".format(template_id=template_id,),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[ErrorResponse, ReplyTemplate]]:
    if response.status_code == 200:
        response_200 = ReplyTemplate.from_dict(response.json())



        return response_200

    if response.status_code == 400:
        response_400 = ErrorResponse.from_dict(response.json())



        return response_400

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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[ErrorResponse, ReplyTemplate]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    template_id: str,
    *,
    client: AuthenticatedClient,
    body: ReplyTemplatePatchRequest,

) -> Response[Union[ErrorResponse, ReplyTemplate]]:
    """ Patch fields on a reply template.

    Args:
        template_id (str):
        body (ReplyTemplatePatchRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, ReplyTemplate]]
     """


    kwargs = _get_kwargs(
        template_id=template_id,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    template_id: str,
    *,
    client: AuthenticatedClient,
    body: ReplyTemplatePatchRequest,

) -> Optional[Union[ErrorResponse, ReplyTemplate]]:
    """ Patch fields on a reply template.

    Args:
        template_id (str):
        body (ReplyTemplatePatchRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, ReplyTemplate]
     """


    return sync_detailed(
        template_id=template_id,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    template_id: str,
    *,
    client: AuthenticatedClient,
    body: ReplyTemplatePatchRequest,

) -> Response[Union[ErrorResponse, ReplyTemplate]]:
    """ Patch fields on a reply template.

    Args:
        template_id (str):
        body (ReplyTemplatePatchRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, ReplyTemplate]]
     """


    kwargs = _get_kwargs(
        template_id=template_id,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    template_id: str,
    *,
    client: AuthenticatedClient,
    body: ReplyTemplatePatchRequest,

) -> Optional[Union[ErrorResponse, ReplyTemplate]]:
    """ Patch fields on a reply template.

    Args:
        template_id (str):
        body (ReplyTemplatePatchRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, ReplyTemplate]
     """


    return (await asyncio_detailed(
        template_id=template_id,
client=client,
body=body,

    )).parsed

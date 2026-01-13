from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.draft_approve_request import DraftApproveRequest
from ...models.error_response import ErrorResponse
from ...models.generic_success import GenericSuccess
from typing import cast



def _get_kwargs(
    draft_id: str,
    *,
    body: DraftApproveRequest,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/reply-drafts/{draft_id}/approve".format(draft_id=draft_id,),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[ErrorResponse, GenericSuccess]]:
    if response.status_code == 200:
        response_200 = GenericSuccess.from_dict(response.json())



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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[ErrorResponse, GenericSuccess]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    draft_id: str,
    *,
    client: AuthenticatedClient,
    body: DraftApproveRequest,

) -> Response[Union[ErrorResponse, GenericSuccess]]:
    """ Approve a pending draft for posting.

     Approves the draft and optionally posts it immediately to the app store. The auto_post parameter
    controls whether to post immediately or queue for later.

    Args:
        draft_id (str):
        body (DraftApproveRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, GenericSuccess]]
     """


    kwargs = _get_kwargs(
        draft_id=draft_id,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    draft_id: str,
    *,
    client: AuthenticatedClient,
    body: DraftApproveRequest,

) -> Optional[Union[ErrorResponse, GenericSuccess]]:
    """ Approve a pending draft for posting.

     Approves the draft and optionally posts it immediately to the app store. The auto_post parameter
    controls whether to post immediately or queue for later.

    Args:
        draft_id (str):
        body (DraftApproveRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, GenericSuccess]
     """


    return sync_detailed(
        draft_id=draft_id,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    draft_id: str,
    *,
    client: AuthenticatedClient,
    body: DraftApproveRequest,

) -> Response[Union[ErrorResponse, GenericSuccess]]:
    """ Approve a pending draft for posting.

     Approves the draft and optionally posts it immediately to the app store. The auto_post parameter
    controls whether to post immediately or queue for later.

    Args:
        draft_id (str):
        body (DraftApproveRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, GenericSuccess]]
     """


    kwargs = _get_kwargs(
        draft_id=draft_id,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    draft_id: str,
    *,
    client: AuthenticatedClient,
    body: DraftApproveRequest,

) -> Optional[Union[ErrorResponse, GenericSuccess]]:
    """ Approve a pending draft for posting.

     Approves the draft and optionally posts it immediately to the app store. The auto_post parameter
    controls whether to post immediately or queue for later.

    Args:
        draft_id (str):
        body (DraftApproveRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, GenericSuccess]
     """


    return (await asyncio_detailed(
        draft_id=draft_id,
client=client,
body=body,

    )).parsed

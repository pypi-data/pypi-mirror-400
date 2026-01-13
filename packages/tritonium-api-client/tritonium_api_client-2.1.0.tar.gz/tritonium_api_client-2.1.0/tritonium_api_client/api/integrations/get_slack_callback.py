from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error_response import ErrorResponse
from ...models.integration import Integration
from ...types import UNSET, Unset
from typing import cast
from typing import Union



def _get_kwargs(
    *,
    code: Union[Unset, str] = UNSET,
    state: Union[Unset, str] = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["code"] = code

    params["state"] = state


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/integrations/slack/callback",
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[ErrorResponse, Integration]]:
    if response.status_code == 200:
        response_200 = Integration.from_dict(response.json())



        return response_200

    if response.status_code == 400:
        response_400 = ErrorResponse.from_dict(response.json())



        return response_400

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[ErrorResponse, Integration]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    code: Union[Unset, str] = UNSET,
    state: Union[Unset, str] = UNSET,

) -> Response[Union[ErrorResponse, Integration]]:
    """ Complete Slack OAuth exchange.

    Args:
        code (Union[Unset, str]):
        state (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, Integration]]
     """


    kwargs = _get_kwargs(
        code=code,
state=state,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    code: Union[Unset, str] = UNSET,
    state: Union[Unset, str] = UNSET,

) -> Optional[Union[ErrorResponse, Integration]]:
    """ Complete Slack OAuth exchange.

    Args:
        code (Union[Unset, str]):
        state (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, Integration]
     """


    return sync_detailed(
        client=client,
code=code,
state=state,

    ).parsed

async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    code: Union[Unset, str] = UNSET,
    state: Union[Unset, str] = UNSET,

) -> Response[Union[ErrorResponse, Integration]]:
    """ Complete Slack OAuth exchange.

    Args:
        code (Union[Unset, str]):
        state (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, Integration]]
     """


    kwargs = _get_kwargs(
        code=code,
state=state,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    code: Union[Unset, str] = UNSET,
    state: Union[Unset, str] = UNSET,

) -> Optional[Union[ErrorResponse, Integration]]:
    """ Complete Slack OAuth exchange.

    Args:
        code (Union[Unset, str]):
        state (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, Integration]
     """


    return (await asyncio_detailed(
        client=client,
code=code,
state=state,

    )).parsed

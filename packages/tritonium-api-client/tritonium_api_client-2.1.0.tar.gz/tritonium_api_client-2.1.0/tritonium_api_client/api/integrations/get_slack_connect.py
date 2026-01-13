from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error_response import ErrorResponse
from ...models.generic_success import GenericSuccess
from ...types import UNSET, Unset
from typing import cast
from typing import Union



def _get_kwargs(
    *,
    redirect_uri: Union[Unset, str] = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["redirect_uri"] = redirect_uri


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/integrations/slack/connect",
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[ErrorResponse, GenericSuccess]]:
    if response.status_code == 200:
        response_200 = GenericSuccess.from_dict(response.json())



        return response_200

    if response.status_code == 401:
        response_401 = ErrorResponse.from_dict(response.json())



        return response_401

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
    *,
    client: AuthenticatedClient,
    redirect_uri: Union[Unset, str] = UNSET,

) -> Response[Union[ErrorResponse, GenericSuccess]]:
    """ Start Slack OAuth flow.

    Args:
        redirect_uri (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, GenericSuccess]]
     """


    kwargs = _get_kwargs(
        redirect_uri=redirect_uri,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: AuthenticatedClient,
    redirect_uri: Union[Unset, str] = UNSET,

) -> Optional[Union[ErrorResponse, GenericSuccess]]:
    """ Start Slack OAuth flow.

    Args:
        redirect_uri (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, GenericSuccess]
     """


    return sync_detailed(
        client=client,
redirect_uri=redirect_uri,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    redirect_uri: Union[Unset, str] = UNSET,

) -> Response[Union[ErrorResponse, GenericSuccess]]:
    """ Start Slack OAuth flow.

    Args:
        redirect_uri (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, GenericSuccess]]
     """


    kwargs = _get_kwargs(
        redirect_uri=redirect_uri,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient,
    redirect_uri: Union[Unset, str] = UNSET,

) -> Optional[Union[ErrorResponse, GenericSuccess]]:
    """ Start Slack OAuth flow.

    Args:
        redirect_uri (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, GenericSuccess]
     """


    return (await asyncio_detailed(
        client=client,
redirect_uri=redirect_uri,

    )).parsed

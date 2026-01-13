from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error_response import ErrorResponse
from typing import cast



def _get_kwargs(
    app_uuid: str,
    segment_type: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/apps/{app_uuid}/segments/{segment_type}/reviews".format(app_uuid=app_uuid,segment_type=segment_type,),
    }


    return _kwargs



def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[ErrorResponse]:
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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[ErrorResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    app_uuid: str,
    segment_type: str,
    *,
    client: AuthenticatedClient,

) -> Response[ErrorResponse]:
    """ Retrieve reviews tied to a specific segment.

    Args:
        app_uuid (str):
        segment_type (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse]
     """


    kwargs = _get_kwargs(
        app_uuid=app_uuid,
segment_type=segment_type,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    app_uuid: str,
    segment_type: str,
    *,
    client: AuthenticatedClient,

) -> Optional[ErrorResponse]:
    """ Retrieve reviews tied to a specific segment.

    Args:
        app_uuid (str):
        segment_type (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse
     """


    return sync_detailed(
        app_uuid=app_uuid,
segment_type=segment_type,
client=client,

    ).parsed

async def asyncio_detailed(
    app_uuid: str,
    segment_type: str,
    *,
    client: AuthenticatedClient,

) -> Response[ErrorResponse]:
    """ Retrieve reviews tied to a specific segment.

    Args:
        app_uuid (str):
        segment_type (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse]
     """


    kwargs = _get_kwargs(
        app_uuid=app_uuid,
segment_type=segment_type,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    app_uuid: str,
    segment_type: str,
    *,
    client: AuthenticatedClient,

) -> Optional[ErrorResponse]:
    """ Retrieve reviews tied to a specific segment.

    Args:
        app_uuid (str):
        segment_type (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse
     """


    return (await asyncio_detailed(
        app_uuid=app_uuid,
segment_type=segment_type,
client=client,

    )).parsed

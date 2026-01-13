from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.competitor import Competitor
from ...models.competitor_upsert_request import CompetitorUpsertRequest
from ...models.error_response import ErrorResponse
from typing import cast



def _get_kwargs(
    app_uuid: str,
    *,
    body: CompetitorUpsertRequest,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/apps/{app_uuid}/competitors".format(app_uuid=app_uuid,),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Competitor, ErrorResponse]]:
    if response.status_code == 201:
        response_201 = Competitor.from_dict(response.json())



        return response_201

    if response.status_code == 400:
        response_400 = ErrorResponse.from_dict(response.json())



        return response_400

    if response.status_code == 401:
        response_401 = ErrorResponse.from_dict(response.json())



        return response_401

    if response.status_code == 403:
        response_403 = ErrorResponse.from_dict(response.json())



        return response_403

    if response.status_code == 404:
        response_404 = ErrorResponse.from_dict(response.json())



        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Competitor, ErrorResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    app_uuid: str,
    *,
    client: AuthenticatedClient,
    body: CompetitorUpsertRequest,

) -> Response[Union[Competitor, ErrorResponse]]:
    """ Register a competitor app.

    Args:
        app_uuid (str):
        body (CompetitorUpsertRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Competitor, ErrorResponse]]
     """


    kwargs = _get_kwargs(
        app_uuid=app_uuid,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    app_uuid: str,
    *,
    client: AuthenticatedClient,
    body: CompetitorUpsertRequest,

) -> Optional[Union[Competitor, ErrorResponse]]:
    """ Register a competitor app.

    Args:
        app_uuid (str):
        body (CompetitorUpsertRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Competitor, ErrorResponse]
     """


    return sync_detailed(
        app_uuid=app_uuid,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    app_uuid: str,
    *,
    client: AuthenticatedClient,
    body: CompetitorUpsertRequest,

) -> Response[Union[Competitor, ErrorResponse]]:
    """ Register a competitor app.

    Args:
        app_uuid (str):
        body (CompetitorUpsertRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Competitor, ErrorResponse]]
     """


    kwargs = _get_kwargs(
        app_uuid=app_uuid,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    app_uuid: str,
    *,
    client: AuthenticatedClient,
    body: CompetitorUpsertRequest,

) -> Optional[Union[Competitor, ErrorResponse]]:
    """ Register a competitor app.

    Args:
        app_uuid (str):
        body (CompetitorUpsertRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Competitor, ErrorResponse]
     """


    return (await asyncio_detailed(
        app_uuid=app_uuid,
client=client,
body=body,

    )).parsed

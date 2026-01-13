from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error_response import ErrorResponse
from ...models.post_duplicate_dashboard_response_201 import PostDuplicateDashboardResponse201
from typing import cast
from uuid import UUID



def _get_kwargs(
    dashboard_id: UUID,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/dashboards/{dashboard_id}/duplicate".format(dashboard_id=dashboard_id,),
    }


    return _kwargs



def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[ErrorResponse, PostDuplicateDashboardResponse201]]:
    if response.status_code == 201:
        response_201 = PostDuplicateDashboardResponse201.from_dict(response.json())



        return response_201

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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[ErrorResponse, PostDuplicateDashboardResponse201]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    dashboard_id: UUID,
    *,
    client: AuthenticatedClient,

) -> Response[Union[ErrorResponse, PostDuplicateDashboardResponse201]]:
    """ Duplicate a dashboard.

    Args:
        dashboard_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, PostDuplicateDashboardResponse201]]
     """


    kwargs = _get_kwargs(
        dashboard_id=dashboard_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    dashboard_id: UUID,
    *,
    client: AuthenticatedClient,

) -> Optional[Union[ErrorResponse, PostDuplicateDashboardResponse201]]:
    """ Duplicate a dashboard.

    Args:
        dashboard_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, PostDuplicateDashboardResponse201]
     """


    return sync_detailed(
        dashboard_id=dashboard_id,
client=client,

    ).parsed

async def asyncio_detailed(
    dashboard_id: UUID,
    *,
    client: AuthenticatedClient,

) -> Response[Union[ErrorResponse, PostDuplicateDashboardResponse201]]:
    """ Duplicate a dashboard.

    Args:
        dashboard_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, PostDuplicateDashboardResponse201]]
     """


    kwargs = _get_kwargs(
        dashboard_id=dashboard_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    dashboard_id: UUID,
    *,
    client: AuthenticatedClient,

) -> Optional[Union[ErrorResponse, PostDuplicateDashboardResponse201]]:
    """ Duplicate a dashboard.

    Args:
        dashboard_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, PostDuplicateDashboardResponse201]
     """


    return (await asyncio_detailed(
        dashboard_id=dashboard_id,
client=client,

    )).parsed

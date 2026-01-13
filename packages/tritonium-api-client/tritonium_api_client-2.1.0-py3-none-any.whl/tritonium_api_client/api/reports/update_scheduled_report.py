from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.create_scheduled_report_request import CreateScheduledReportRequest
from ...models.error_response import ErrorResponse
from ...models.scheduled_report_response import ScheduledReportResponse
from typing import cast



def _get_kwargs(
    schedule_id: str,
    *,
    body: CreateScheduledReportRequest,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/api/v1/reports/scheduled/{schedule_id}".format(schedule_id=schedule_id,),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[ErrorResponse, ScheduledReportResponse]]:
    if response.status_code == 200:
        response_200 = ScheduledReportResponse.from_dict(response.json())



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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[ErrorResponse, ScheduledReportResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    schedule_id: str,
    *,
    client: AuthenticatedClient,
    body: CreateScheduledReportRequest,

) -> Response[Union[ErrorResponse, ScheduledReportResponse]]:
    """ Update a scheduled report.

    Args:
        schedule_id (str):
        body (CreateScheduledReportRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, ScheduledReportResponse]]
     """


    kwargs = _get_kwargs(
        schedule_id=schedule_id,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    schedule_id: str,
    *,
    client: AuthenticatedClient,
    body: CreateScheduledReportRequest,

) -> Optional[Union[ErrorResponse, ScheduledReportResponse]]:
    """ Update a scheduled report.

    Args:
        schedule_id (str):
        body (CreateScheduledReportRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, ScheduledReportResponse]
     """


    return sync_detailed(
        schedule_id=schedule_id,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    schedule_id: str,
    *,
    client: AuthenticatedClient,
    body: CreateScheduledReportRequest,

) -> Response[Union[ErrorResponse, ScheduledReportResponse]]:
    """ Update a scheduled report.

    Args:
        schedule_id (str):
        body (CreateScheduledReportRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, ScheduledReportResponse]]
     """


    kwargs = _get_kwargs(
        schedule_id=schedule_id,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    schedule_id: str,
    *,
    client: AuthenticatedClient,
    body: CreateScheduledReportRequest,

) -> Optional[Union[ErrorResponse, ScheduledReportResponse]]:
    """ Update a scheduled report.

    Args:
        schedule_id (str):
        body (CreateScheduledReportRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, ScheduledReportResponse]
     """


    return (await asyncio_detailed(
        schedule_id=schedule_id,
client=client,
body=body,

    )).parsed

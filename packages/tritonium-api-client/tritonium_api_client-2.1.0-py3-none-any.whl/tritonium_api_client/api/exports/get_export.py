from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error_response import ErrorResponse
from ...models.export_job_response import ExportJobResponse
from typing import cast



def _get_kwargs(
    job_id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/exports/{job_id}".format(job_id=job_id,),
    }


    return _kwargs



def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[ErrorResponse, ExportJobResponse]]:
    if response.status_code == 200:
        response_200 = ExportJobResponse.from_dict(response.json())



        return response_200

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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[ErrorResponse, ExportJobResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    job_id: str,
    *,
    client: AuthenticatedClient,

) -> Response[Union[ErrorResponse, ExportJobResponse]]:
    """ Get export job status and download URL.

    Args:
        job_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, ExportJobResponse]]
     """


    kwargs = _get_kwargs(
        job_id=job_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    job_id: str,
    *,
    client: AuthenticatedClient,

) -> Optional[Union[ErrorResponse, ExportJobResponse]]:
    """ Get export job status and download URL.

    Args:
        job_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, ExportJobResponse]
     """


    return sync_detailed(
        job_id=job_id,
client=client,

    ).parsed

async def asyncio_detailed(
    job_id: str,
    *,
    client: AuthenticatedClient,

) -> Response[Union[ErrorResponse, ExportJobResponse]]:
    """ Get export job status and download URL.

    Args:
        job_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, ExportJobResponse]]
     """


    kwargs = _get_kwargs(
        job_id=job_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    job_id: str,
    *,
    client: AuthenticatedClient,

) -> Optional[Union[ErrorResponse, ExportJobResponse]]:
    """ Get export job status and download URL.

    Args:
        job_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, ExportJobResponse]
     """


    return (await asyncio_detailed(
        job_id=job_id,
client=client,

    )).parsed

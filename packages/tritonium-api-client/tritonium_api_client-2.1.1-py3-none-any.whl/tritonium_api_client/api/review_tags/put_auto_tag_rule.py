from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error_response import ErrorResponse
from ...models.put_auto_tag_rule_response_200 import PutAutoTagRuleResponse200
from ...models.update_auto_tag_rule_request import UpdateAutoTagRuleRequest
from typing import cast
from uuid import UUID



def _get_kwargs(
    rule_id: UUID,
    *,
    body: UpdateAutoTagRuleRequest,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/api/v1/review-tags/auto-rules/{rule_id}".format(rule_id=rule_id,),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[ErrorResponse, PutAutoTagRuleResponse200]]:
    if response.status_code == 200:
        response_200 = PutAutoTagRuleResponse200.from_dict(response.json())



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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[ErrorResponse, PutAutoTagRuleResponse200]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    rule_id: UUID,
    *,
    client: AuthenticatedClient,
    body: UpdateAutoTagRuleRequest,

) -> Response[Union[ErrorResponse, PutAutoTagRuleResponse200]]:
    """ Update an auto-tagging rule.

    Args:
        rule_id (UUID):
        body (UpdateAutoTagRuleRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, PutAutoTagRuleResponse200]]
     """


    kwargs = _get_kwargs(
        rule_id=rule_id,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    rule_id: UUID,
    *,
    client: AuthenticatedClient,
    body: UpdateAutoTagRuleRequest,

) -> Optional[Union[ErrorResponse, PutAutoTagRuleResponse200]]:
    """ Update an auto-tagging rule.

    Args:
        rule_id (UUID):
        body (UpdateAutoTagRuleRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, PutAutoTagRuleResponse200]
     """


    return sync_detailed(
        rule_id=rule_id,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    rule_id: UUID,
    *,
    client: AuthenticatedClient,
    body: UpdateAutoTagRuleRequest,

) -> Response[Union[ErrorResponse, PutAutoTagRuleResponse200]]:
    """ Update an auto-tagging rule.

    Args:
        rule_id (UUID):
        body (UpdateAutoTagRuleRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, PutAutoTagRuleResponse200]]
     """


    kwargs = _get_kwargs(
        rule_id=rule_id,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    rule_id: UUID,
    *,
    client: AuthenticatedClient,
    body: UpdateAutoTagRuleRequest,

) -> Optional[Union[ErrorResponse, PutAutoTagRuleResponse200]]:
    """ Update an auto-tagging rule.

    Args:
        rule_id (UUID):
        body (UpdateAutoTagRuleRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, PutAutoTagRuleResponse200]
     """


    return (await asyncio_detailed(
        rule_id=rule_id,
client=client,
body=body,

    )).parsed

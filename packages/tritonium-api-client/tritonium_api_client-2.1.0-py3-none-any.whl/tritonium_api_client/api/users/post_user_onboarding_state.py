from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error_response import ErrorResponse
from ...models.post_user_onboarding_state_body import PostUserOnboardingStateBody
from ...models.post_user_onboarding_state_response_200 import PostUserOnboardingStateResponse200
from typing import cast



def _get_kwargs(
    *,
    body: PostUserOnboardingStateBody,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/users/me/onboarding",
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[ErrorResponse, PostUserOnboardingStateResponse200]]:
    if response.status_code == 200:
        response_200 = PostUserOnboardingStateResponse200.from_dict(response.json())



        return response_200

    if response.status_code == 400:
        response_400 = ErrorResponse.from_dict(response.json())



        return response_400

    if response.status_code == 401:
        response_401 = ErrorResponse.from_dict(response.json())



        return response_401

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[ErrorResponse, PostUserOnboardingStateResponse200]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: PostUserOnboardingStateBody,

) -> Response[Union[ErrorResponse, PostUserOnboardingStateResponse200]]:
    """ Mark onboarding tour completion for the signed-in user.

    Args:
        body (PostUserOnboardingStateBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, PostUserOnboardingStateResponse200]]
     """


    kwargs = _get_kwargs(
        body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: AuthenticatedClient,
    body: PostUserOnboardingStateBody,

) -> Optional[Union[ErrorResponse, PostUserOnboardingStateResponse200]]:
    """ Mark onboarding tour completion for the signed-in user.

    Args:
        body (PostUserOnboardingStateBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, PostUserOnboardingStateResponse200]
     """


    return sync_detailed(
        client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: PostUserOnboardingStateBody,

) -> Response[Union[ErrorResponse, PostUserOnboardingStateResponse200]]:
    """ Mark onboarding tour completion for the signed-in user.

    Args:
        body (PostUserOnboardingStateBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, PostUserOnboardingStateResponse200]]
     """


    kwargs = _get_kwargs(
        body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient,
    body: PostUserOnboardingStateBody,

) -> Optional[Union[ErrorResponse, PostUserOnboardingStateResponse200]]:
    """ Mark onboarding tour completion for the signed-in user.

    Args:
        body (PostUserOnboardingStateBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, PostUserOnboardingStateResponse200]
     """


    return (await asyncio_detailed(
        client=client,
body=body,

    )).parsed

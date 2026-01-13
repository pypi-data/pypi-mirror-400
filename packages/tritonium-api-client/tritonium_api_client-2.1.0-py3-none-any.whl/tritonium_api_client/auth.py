"""
Authentication helpers for the Tritonium API.

This module provides utilities for API key authentication and token management.
"""

from typing import Optional
from attrs import define, field
import httpx


@define
class APIKeyAuth(httpx.Auth):
    """
    httpx Auth class for API key authentication.

    Usage:
        from tritonium_api_client import Client
        from tritonium_api_client.auth import APIKeyAuth

        auth = APIKeyAuth(api_key="trtn_live_your_key_here")
        client = Client(
            base_url="https://api.tritonium.com",
            httpx_args={"auth": auth}
        )
    """

    api_key: str = field()

    def auth_flow(self, request: httpx.Request):
        request.headers["X-API-Key"] = self.api_key
        yield request


@define
class BearerAuth(httpx.Auth):
    """
    httpx Auth class for Bearer token authentication.

    Usage:
        from tritonium_api_client import Client
        from tritonium_api_client.auth import BearerAuth

        auth = BearerAuth(token="your_jwt_token")
        client = Client(
            base_url="https://api.tritonium.com",
            httpx_args={"auth": auth}
        )
    """

    token: str = field()

    def auth_flow(self, request: httpx.Request):
        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request


def create_api_key_client(
    api_key: str,
    base_url: str = "https://api.tritonium.com",
    timeout: Optional[float] = 30.0,
    **kwargs
):
    """
    Create a Tritonium API client with API key authentication.

    Args:
        api_key: Your Tritonium API key (starts with trtn_live_ or trtn_test_)
        base_url: API base URL (default: production)
        timeout: Request timeout in seconds
        **kwargs: Additional arguments passed to httpx.Client

    Returns:
        Client: Configured Tritonium API client

    Example:
        from tritonium_api_client.auth import create_api_key_client

        client = create_api_key_client("trtn_live_your_key_here")

        # Use the client
        from tritonium_api_client.api.apps import list_apps
        response = list_apps.sync(client=client)
    """
    from .client import Client

    auth = APIKeyAuth(api_key=api_key)
    httpx_args = kwargs.pop("httpx_args", {})
    httpx_args["auth"] = auth

    return Client(
        base_url=base_url,
        timeout=httpx.Timeout(timeout) if timeout else None,
        httpx_args=httpx_args,
        **kwargs
    )


def create_bearer_client(
    token: str,
    base_url: str = "https://api.tritonium.com",
    timeout: Optional[float] = 30.0,
    **kwargs
):
    """
    Create a Tritonium API client with Bearer token authentication.

    Args:
        token: Your Cognito JWT access token
        base_url: API base URL (default: production)
        timeout: Request timeout in seconds
        **kwargs: Additional arguments passed to httpx.Client

    Returns:
        Client: Configured Tritonium API client

    Example:
        from tritonium_api_client.auth import create_bearer_client

        client = create_bearer_client("your_jwt_token")
    """
    from .client import Client

    auth = BearerAuth(token=token)
    httpx_args = kwargs.pop("httpx_args", {})
    httpx_args["auth"] = auth

    return Client(
        base_url=base_url,
        timeout=httpx.Timeout(timeout) if timeout else None,
        httpx_args=httpx_args,
        **kwargs
    )

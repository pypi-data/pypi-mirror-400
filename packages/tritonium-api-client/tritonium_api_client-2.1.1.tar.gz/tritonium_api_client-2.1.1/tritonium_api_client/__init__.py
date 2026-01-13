"""
A client library for accessing Tritonium API.

This SDK provides:
- Type-safe API client generated from OpenAPI spec
- Authentication helpers for API keys and JWT tokens
- Webhook signature verification utilities

Quick Start:
    from tritonium_api_client.auth import create_api_key_client

    client = create_api_key_client("trtn_live_your_key_here")

    from tritonium_api_client.api.apps import list_apps
    response = list_apps.sync(client=client)
"""
from .client import AuthenticatedClient, Client
from .auth import APIKeyAuth, BearerAuth, create_api_key_client, create_bearer_client
from .webhooks import (
    verify_webhook,
    verify_signature,
    construct_event,
    WebhookEvent,
    WebhookVerificationError,
    WebhookExpiredError,
    WebhookSignatureError,
    EventTypes,
)

__all__ = (
    # Client classes
    "AuthenticatedClient",
    "Client",
    # Auth helpers
    "APIKeyAuth",
    "BearerAuth",
    "create_api_key_client",
    "create_bearer_client",
    # Webhook utilities
    "verify_webhook",
    "verify_signature",
    "construct_event",
    "WebhookEvent",
    "WebhookVerificationError",
    "WebhookExpiredError",
    "WebhookSignatureError",
    "EventTypes",
)

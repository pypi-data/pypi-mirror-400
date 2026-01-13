"""
Webhook verification utilities for Tritonium.

This module provides functions for verifying webhook signatures and handling
incoming webhook events from Tritonium.
"""

import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional, Union


class WebhookVerificationError(Exception):
    """Raised when webhook signature verification fails."""
    pass


class WebhookExpiredError(WebhookVerificationError):
    """Raised when webhook timestamp is too old."""
    pass


class WebhookSignatureError(WebhookVerificationError):
    """Raised when webhook signature is invalid."""
    pass


@dataclass
class WebhookEvent:
    """
    Parsed webhook event from Tritonium.

    Attributes:
        event_id: Unique identifier for this event
        event_type: Type of event (e.g., 'review.received', 'alert.triggered')
        timestamp: When the event occurred
        tenant_id: Tenant that owns this event
        app_uuid: Optional app UUID related to the event
        data: Event-specific payload data
        raw_payload: Original JSON payload
    """
    event_id: str
    event_type: str
    timestamp: datetime
    tenant_id: str
    app_uuid: Optional[str]
    data: dict[str, Any]
    raw_payload: dict[str, Any]


def verify_signature(
    payload: Union[str, bytes],
    signature: str,
    secret: str,
) -> bool:
    """
    Verify a webhook signature.

    Args:
        payload: Raw request body (string or bytes)
        signature: Value of X-Tritonium-Signature header
        secret: Your webhook signing secret

    Returns:
        True if signature is valid, False otherwise
    """
    if isinstance(payload, str):
        payload = payload.encode('utf-8')

    # Extract the hex signature (remove 'sha256=' prefix)
    if signature.startswith('sha256='):
        received_sig = signature[7:]
    else:
        received_sig = signature

    # Compute expected signature
    expected_sig = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()

    # Constant-time comparison to prevent timing attacks
    return hmac.compare_digest(received_sig, expected_sig)


def verify_timestamp(
    timestamp: str,
    tolerance_seconds: int = 300
) -> bool:
    """
    Verify that a webhook timestamp is within acceptable range.

    Args:
        timestamp: ISO 8601 timestamp string
        tolerance_seconds: Maximum age in seconds (default: 5 minutes)

    Returns:
        True if timestamp is valid, False otherwise
    """
    try:
        # Parse ISO 8601 timestamp
        webhook_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)

        # Calculate age
        age_seconds = abs((now - webhook_time).total_seconds())

        return age_seconds <= tolerance_seconds
    except (ValueError, TypeError):
        return False


def verify_webhook(
    payload: Union[str, bytes],
    signature: str,
    timestamp: str,
    secret: str,
    tolerance_seconds: int = 300,
) -> WebhookEvent:
    """
    Verify a webhook and parse the event.

    This is the main function for processing incoming webhooks. It:
    1. Verifies the timestamp is not too old (replay protection)
    2. Verifies the HMAC signature
    3. Parses and returns the event

    Args:
        payload: Raw request body (string or bytes)
        signature: Value of X-Tritonium-Signature header
        timestamp: Value of X-Tritonium-Timestamp header
        secret: Your webhook signing secret
        tolerance_seconds: Maximum age in seconds (default: 5 minutes)

    Returns:
        WebhookEvent: Parsed and verified webhook event

    Raises:
        WebhookExpiredError: If timestamp is too old
        WebhookSignatureError: If signature is invalid
        WebhookVerificationError: If payload cannot be parsed

    Example:
        from flask import Flask, request
        from tritonium_api_client.webhooks import verify_webhook, WebhookVerificationError

        app = Flask(__name__)
        WEBHOOK_SECRET = "whsec_your_secret"

        @app.route('/webhook', methods=['POST'])
        def handle_webhook():
            try:
                event = verify_webhook(
                    payload=request.get_data(),
                    signature=request.headers.get('X-Tritonium-Signature', ''),
                    timestamp=request.headers.get('X-Tritonium-Timestamp', ''),
                    secret=WEBHOOK_SECRET,
                )

                if event.event_type == 'review.received':
                    process_review(event.data)
                elif event.event_type == 'alert.triggered':
                    process_alert(event.data)

                return {'status': 'ok'}, 200

            except WebhookVerificationError as e:
                return {'error': str(e)}, 401
    """
    # Check timestamp first (replay protection)
    if not verify_timestamp(timestamp, tolerance_seconds):
        raise WebhookExpiredError(
            f"Webhook timestamp is too old or invalid: {timestamp}"
        )

    # Verify signature
    if not verify_signature(payload, signature, secret):
        raise WebhookSignatureError("Invalid webhook signature")

    # Parse payload
    try:
        if isinstance(payload, bytes):
            payload_str = payload.decode('utf-8')
        else:
            payload_str = payload

        data = json.loads(payload_str)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise WebhookVerificationError(f"Invalid webhook payload: {e}")

    # Parse timestamp
    try:
        event_timestamp = datetime.fromisoformat(
            data.get('timestamp', timestamp).replace('Z', '+00:00')
        )
    except (ValueError, TypeError):
        event_timestamp = datetime.now(timezone.utc)

    return WebhookEvent(
        event_id=data.get('event_id', ''),
        event_type=data.get('event_type', ''),
        timestamp=event_timestamp,
        tenant_id=data.get('tenant_id', ''),
        app_uuid=data.get('app_uuid'),
        data=data.get('data', {}),
        raw_payload=data,
    )


def construct_event(
    payload: Union[str, bytes, dict[str, Any]],
    signature: str,
    timestamp: str,
    secret: str,
    tolerance_seconds: int = 300,
) -> WebhookEvent:
    """
    Alias for verify_webhook for compatibility with other webhook libraries.

    See verify_webhook for documentation.
    """
    if isinstance(payload, dict):
        payload = json.dumps(payload, separators=(',', ':'), sort_keys=True)
    return verify_webhook(payload, signature, timestamp, secret, tolerance_seconds)


# Event type constants for convenience
class EventTypes:
    """Constants for Tritonium webhook event types."""

    CRISIS_DETECTED = "crisis.detected"
    INSIGHT_GENERATED = "insight.generated"
    REVIEW_RECEIVED = "review.received"
    ANALYSIS_COMPLETED = "analysis.completed"
    ALERT_TRIGGERED = "alert.triggered"
    TEST_PING = "test.ping"

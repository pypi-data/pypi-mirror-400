import os
import logging
import hmac
import hashlib
import json
import time
import warnings
from typing import Optional, Dict, Any, List

import requests

from .types import Message, WebhookEvent


# Configure logging
logger = logging.getLogger("lenzyai")

# Webhook configuration
WEBHOOK_SIGNATURE_TOLERANCE_SECONDS = 300


class Lenzy:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        enabled: Optional[bool] = None,
    ) -> None:
        # Determine if SDK is enabled
        enabled_env = self._get_env_with_fallback("LENZY_ENABLED", "LENZYAI_ENABLED")
        if enabled is not None:
            self._enabled = enabled
        elif enabled_env is not None:
            self._enabled = enabled_env not in ("false", "0")
        else:
            self._enabled = True

        # Get API key
        self._api_key = api_key or self._get_env_with_fallback("LENZY_API_KEY", "LENZYAI_API_KEY") or ""

        # Validate API key requirement
        if not self._api_key and self._enabled:
            raise ValueError(
                "API key is required. Please provide it in the constructor or "
                "set the LENZY_API_KEY environment variable."
            )

        # Get base URL
        self._base_url = (
            base_url
            or self._get_env_with_fallback("LENZY_API_BASE_URL", "LENZYAI_API_BASE_URL")
            or "https://app.lenzy.ai"
        )

        # Create session for connection pooling
        self._session = requests.Session()
        self._session.headers.update({
            "Content-Type": "application/json",
        })

    def record_messages(
        self,
        project_id: str,
        external_conversation_id: str,
        messages: List[Message],
        external_user_id: Optional[str] = None,
    ) -> None:
        if not self._enabled:
            return

        try:
            # Validate inputs
            if not project_id:
                raise ValueError("project_id is required")
            if not external_conversation_id:
                raise ValueError("external_conversation_id is required")
            if not messages or len(messages) == 0:
                raise ValueError("At least 1 message is required")
            if external_user_id is not None and len(external_user_id) == 0:
                raise ValueError("external_user_id must not be empty if provided")

            # Transform messages to API format
            messages_payload: List[Dict[str, Any]] = []
            for message in messages:
                # Validate message structure
                if not isinstance(message, dict):
                    raise ValueError("Each message must be a dictionary")
                if "role" not in message:
                    raise ValueError("Each message must have a 'role' field")
                if "content" not in message:
                    raise ValueError("Each message must have a 'content' field")
                if message["role"] not in ("USER", "ASSISTANT"):
                    raise ValueError("Message role must be 'USER' or 'ASSISTANT'")

                # Build message payload
                message_dict: Dict[str, Any] = {
                    "role": message["role"],
                    "content": message["content"],
                    "externalConversationId": external_conversation_id,
                }

                # Add optional fields
                if "external_id" in message:
                    message_dict["externalId"] = message["external_id"]
                if "sent_at" in message:
                    message_dict["sentAt"] = message["sent_at"]

                if external_user_id:
                    message_dict["externalUserId"] = external_user_id

                messages_payload.append(message_dict)

            # Build URL
            url = f"{self._base_url}/api/projects/{project_id}/messages"

            # Make request
            response = self._session.post(
                url,
                json=messages_payload,
                headers={"x-api-key": self._api_key},
                timeout=30,
            )

            # Check for errors
            if not response.ok:
                error_data = {}
                try:
                    error_data = response.json()
                except Exception:
                    pass

                logger.error(
                    f"Lenzy Error: Error recording messages. "
                    f"Status: {response.status_code}, "
                    f"Response: {error_data}"
                )
                return

        except requests.exceptions.RequestException as e:
            logger.error(f"Lenzy Error: Error recording messages. {e}")
        except Exception as e:
            logger.error(f"Lenzy Error: Error recording messages. {e}")

    @staticmethod
    def _get_env_with_fallback(new_key: str, old_key: str) -> Optional[str]:
        new_value = os.environ.get(new_key)
        if new_value is not None:
            return new_value

        old_value = os.environ.get(old_key)
        if old_value is not None:
            warnings.warn(
                f"{old_key} is deprecated, use {new_key} instead. "
                f"{old_key} will be removed in a future version.",
                DeprecationWarning,
                stacklevel=4
            )
            return old_value

        return None

    def __enter__(self) -> "Lenzy":
        return self

    def __exit__(self, *args: Any) -> None:
        self._session.close()

    def close(self) -> None:
        self._session.close()

    @staticmethod
    def validate_webhook_payload(
        payload: str,
        signature: str,
        secret: str,
    ) -> WebhookEvent:
        # Parse signature header format: "t=<timestamp>,v1=<signature>"
        parts = signature.split(',')
        if len(parts) != 2:
            raise ValueError('Invalid signature format')

        timestamp_part = parts[0]
        signature_part = parts[1]

        if not timestamp_part.startswith('t=') or not signature_part.startswith('v1='):
            raise ValueError('Invalid signature format')

        try:
            timestamp = int(timestamp_part[2:])
        except ValueError:
            raise ValueError('Invalid signature format')

        provided_signature = signature_part[3:]

        # Check timestamp tolerance (prevent replay attacks)
        current_time = int(time.time())
        if abs(current_time - timestamp) > WEBHOOK_SIGNATURE_TOLERANCE_SECONDS:
            raise ValueError('Signature expired')

        # Reconstruct the signed payload: "timestamp.payload"
        signed_payload = f"{timestamp}.{payload}"

        # Compute expected signature using HMAC-SHA256
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            signed_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        # Timing-safe comparison to prevent timing attacks
        if len(expected_signature) != len(provided_signature):
            raise ValueError('Invalid signature')

        is_signature_valid = hmac.compare_digest(
            expected_signature,
            provided_signature
        )

        if not is_signature_valid:
            raise ValueError('Invalid signature')

        # Parse the JSON payload
        raw_payload = json.loads(payload)

        # Convert to Python snake_case convention with explicit field mapping
        return {
            'type': raw_payload['type'],
            'data': {
                'alert_id': raw_payload['data']['alertId'],
                'events': [
                    {
                        'id': event['id'],
                        'description': event['description'],
                        'reason': event['reason'],
                        'user_quote': event['userQuote'],
                        'user_message_id': event['userMessageId'],
                        'external_user_message_id': event.get('externalUserMessageId'),
                        'assistant_quote': event['assistantQuote'],
                        'assistant_message_id': event['assistantMessageId'],
                        'external_assistant_message_id': event.get('externalAssistantMessageId'),
                        'user_id': event.get('userId'),
                        'external_user_id': event.get('externalUserId'),
                        'happened_at': event['happenedAt'],
                        'fields': event['fields'],
                        'last_happened_for_user_at': event.get('lastHappenedForUserAt'),
                    }
                    for event in raw_payload['data']['events']
                ]
            }
        }


class LenzyAI(Lenzy):
    """
    Deprecated: Use Lenzy instead.

    This class is maintained for backward compatibility and will be removed in a future version.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        enabled: Optional[bool] = None,
    ) -> None:
        warnings.warn(
            "LenzyAI is deprecated, use Lenzy instead. "
            "LenzyAI will be removed in a future version.",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(api_key=api_key, base_url=base_url, enabled=enabled)

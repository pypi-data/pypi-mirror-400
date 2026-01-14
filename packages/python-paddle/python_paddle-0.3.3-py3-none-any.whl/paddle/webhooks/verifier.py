import hashlib
import hmac
import time

from paddle.webhooks.exceptions import ValidationError


def verify(secret: str, signature: str, body: str, error: bool = True) -> bool:
    """Validates a Paddle webhook request.

    Args:
        secret (str): The webhook secret.
        signature (str): The Paddle-Signature header value.
        body (str): The raw request body.
        error (bool, optional): Whether to raise an error on validation failure. Defaults to True.

    Returns:
        bool: If the webhook is valid.

    Raises:
        ValidationError: The webhook signature header is invalid.
        ValidationError: Unable to extract timestamp or signature from Paddle-Signature header.
        ValidationError: Webhook event expired (timestamp is over 5 seconds old).
        ValidationError: Invalid webhook signature.
    """

    signature_parts = signature.split(";")

    if len(signature_parts) != 2:
        if error:
            raise ValidationError("Invalid Paddle-Signature header format")

        return False

    timestamp = signature_parts[0].split("=")[1]
    signature = signature_parts[1].split("=")[1]

    if not timestamp or not signature:
        if error:
            raise ValidationError(
                "Unable to extract timestamp or signature from Paddle-Signature header"
            )

        return False

    event_time = int(timestamp)
    current_time = int(time.time())

    if current_time - event_time > 5:
        if error:
            raise ValidationError(
                "Webhook event expired (timestamp is over 5 seconds old)"
            )

        return False

    signed_payload = f"{timestamp}:{body}"

    computed_hash = hmac.new(
        secret.encode(), signed_payload.encode(), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(computed_hash, signature):
        if error:
            raise ValidationError("Invalid webhook signature")

        return False

    return True

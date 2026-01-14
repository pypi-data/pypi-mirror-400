"""Webhook Module."""

import hmac
from datetime import datetime, timezone
from hashlib import sha256

__all__ = [
    "NoSignatureError",
    "NoTimestampError",
    "SignatureMismatchError",
    "SignatureVerificationError",
    "TimestampOutsideToleranceError",
]


class SignatureVerificationError(ValueError):
    """Exceptions raised when webhook signature verification fails."""

    pass


class NoTimestampError(SignatureVerificationError):
    """Error raised when the timestamp is missing from signature header."""

    def __init__(self) -> None:
        """Initialize NoTimestampError."""
        super().__init__("No timestamp found in header")


class NoSignatureError(SignatureVerificationError):
    """Error raised when the signatures are missing from signature header."""

    def __init__(self) -> None:
        """Initialize NoSignatureError."""
        super().__init__("No signatures found in header")


class SignatureMismatchError(SignatureVerificationError):
    """Error raised when the computed signature does not match signatures in header."""

    def __init__(self) -> None:
        """Initialize SignatureMismatchError."""
        super().__init__("No signatures found matching the expected signature")


class TimestampOutsideToleranceError(SignatureVerificationError):
    """Error raised when timestamp is outside the tolerance window."""

    def __init__(self) -> None:
        """Initialize TimestampOutsideToleranceError."""
        super().__init__("Timestamp outside the tolerance window")


def verify(
    payload: bytes,
    signature_header: str,
    secret: str,
    tolerance: int = 300,
    scheme: str = "v1",
) -> None:
    """Verify webhook signature.

    Args:
        payload: Payload bytes from the webhook request body.
        signature_header: The signature header.
        secret: The webhook secret.
        tolerance: Maximum allowed age of the timestamp in seconds. Defaults to 300.
        scheme: Key for the signatures in signature header. Defaults to "v1".

    Raises:
        NoTimestampError: Error raised when the timestamp is missing from signature
            header.
        NoSignatureError: Error raised when the signatures are missing from signature
            header.
        SignatureMismatchError: Error raised when the computed signature does not match
            signatures in header.
        TimestampOutsideToleranceError: Error raised when timestamp is outside the
            tolerance window.
    """
    timestamp, signatures = _parse_signature_header(signature_header, scheme)

    _verify_timestamp(timestamp, tolerance)

    signed_payload = b"%d." % timestamp + payload

    expected_signature = _compute_signature(signed_payload, secret)

    _compare(expected_signature, signatures)


def _parse_signature_header(
    signature_header: str, scheme: str
) -> tuple[int, list[str]]:
    """Parse the signature header to extract timestamp and signatures.

    Args:
        signature_header: The signature header.
        scheme: Key for the signatures in signature header.

    Returns:
        Tuple containing timestamp and signatures.

    Raises:
        NoTimestampError: Error raised when the timestamp is missing from signature
            header.
        NoSignatureError: Error raised when the signatures are missing from signature
            header.
    """
    list_items = [item.split("=", 1) for item in signature_header.split(",")]

    timestamp_str = next(
        (item[1] for item in list_items if len(item) == 2 and item[0] == "t"),
        None,
    )
    if timestamp_str is None:
        raise NoTimestampError()

    signatures = [
        item[1] for item in list_items if len(item) == 2 and item[0] == scheme
    ]

    if not signatures:
        raise NoSignatureError()

    return int(timestamp_str), signatures


def _compute_signature(payload: bytes, secret: str) -> str:
    """Compute signature using payload and webhook secret.

    Args:
        payload: Payload bytes from the webhook request body.
        secret: The webhook secret.

    Returns:
        Computed signature.
    """
    mac = hmac.new(secret.encode("utf-8"), msg=payload, digestmod=sha256)
    return mac.hexdigest()


def _compare(expected_signature: str, header_signatures: list[str]) -> None:
    """Compare signature headers with expected computed signature.

    Args:
        expected_signature: The expected computed signature.
        header_signatures: list of signatures from the signature header.

    Raises:
        SignatureMismatchError: Error raised when the expected signature does not match
            signatures in header.
    """
    for signature in header_signatures:
        if hmac.compare_digest(expected_signature, signature):
            return None
    raise SignatureMismatchError()


def _verify_timestamp(timestamp: int, tolerance: int) -> None:
    """Verify that the webhook timestamp is within the tolerance window.

    Args:
        timestamp: Timestamp from the webhook signature header.
        tolerance: Maximum allowed age of the timestamp in seconds.

    Raises:
        TimestampOutsideToleranceError: Error raised when timestamp is outside the
            tolerance window.
    """
    now_utc = datetime.now(timezone.utc).timestamp()
    if timestamp < now_utc - tolerance or timestamp > now_utc + tolerance:
        raise TimestampOutsideToleranceError()

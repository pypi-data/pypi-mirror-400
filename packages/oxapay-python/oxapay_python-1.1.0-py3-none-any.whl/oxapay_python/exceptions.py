"""SDK exception hierarchy.

All exceptions raised by the SDK inherit from :class:`~oxapay.exceptions.OxaPayException`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class OxaPayException(Exception):
    """Base exception type for the SDK.

    Attributes
    ----------
    message:
        Human-readable error message.
    context:
        Extra details (e.g., HTTP response payload).
    previous:
        Optional chained exception.
    """
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    previous: Optional[BaseException] = None

    def set_context(self, ctx: Dict[str, Any]) -> "OxaPayException":
        """Attach extra context and return `self` for fluent usage."""
        self.context = ctx
        return self

    def __str__(self) -> str:
        return self.message


class ValidationRequestException(OxaPayException):
    pass


class InvalidApiKeyException(OxaPayException):
    pass


class NotFoundException(OxaPayException):
    pass


class RateLimitException(OxaPayException):
    pass


class ServerErrorException(OxaPayException):
    pass


class ServiceUnavailableException(OxaPayException):
    pass


class HttpException(OxaPayException):
    pass


class MissingApiKeyException(OxaPayException):
    pass


class MissingTrackIdException(OxaPayException):
    pass


class MissingAddressException(OxaPayException):
    pass


class WebhookSignatureException(OxaPayException):
    pass


class WebhookNotReceivedException(OxaPayException):
    pass

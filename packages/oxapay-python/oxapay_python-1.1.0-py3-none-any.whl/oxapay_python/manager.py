"""Public entrypoint for the SDK.

Most users only need :class:`~oxapay.manager.OxaPayManager`.
"""

from __future__ import annotations

from typing import Optional

from . import __version__
from .endpoints.account import Account
from .endpoints.common import Common
from .endpoints.exchange import Exchange
from .endpoints.payment import Payment
from .endpoints.payout import Payout
from .exceptions import WebhookNotReceivedException
from .http.client import OxaPayClient
from .services.webhook import Webhook


class OxaPayManager:
    """Factory for OxaPay API endpoints.

    Parameters
    ----------
    timeout:
        Request timeout in seconds.
    client:
        Optional custom HTTP client (useful for testing).
    raw:
        When ``True`` endpoint methods return the full API payload as-is.
        When ``False`` (default) they unwrap and return ``payload['data']``.
    """
    BASE_URL = "https://api.oxapay.com/v1"

    def __init__(self, timeout: int = 20, client: Optional[OxaPayClient] = None, *, raw: bool = False):
        self.timeout = int(timeout) if timeout else 20
        self.client = client or OxaPayClient(self.BASE_URL, self.timeout, __version__, raw=raw)
        if client is not None:
            self.client.raw = bool(raw)

    def payment(self, merchant_api_key: str, callback_url: Optional[str] = None, sandbox: Optional[bool] = None) -> Payment:
        """Create the Payment endpoint client."""
        return Payment(self.client, merchant_api_key, callback_url=callback_url, sandbox=sandbox)

    def payout(self, payout_api_key: str, callback_url: Optional[str] = None) -> Payout:
        """Create the Payout endpoint client."""
        return Payout(self.client, payout_api_key, callback_url=callback_url)

    def exchange(self, general_api_key: str) -> Exchange:
        """Create the Exchange endpoint client."""
        return Exchange(self.client, general_api_key)

    def common(self) -> Common:
        """Create the Common endpoint client (no API key required)."""
        return Common(self.client)

    def account(self, general_api_key: str) -> Account:
        """Create the Account endpoint client."""
        return Account(self.client, general_api_key)

    def webhook(
        self,
        merchant_api_key: Optional[str] = None,
        payout_api_key: Optional[str] = None,
        *,
        raw_body: Optional[str] = None,
        headers: Optional[dict] = None,
    ) -> Webhook:
        """Create a webhook verifier/decoder.

        Notes
        -----
        In a web framework, pass the *raw request body* (string) and headers.
        """
        if raw_body is None:
            raise WebhookNotReceivedException(
                "raw_body is required in pure SDK usage (pass raw request body from your framework)."
            )
        return Webhook(merchant_api_key, payout_api_key, raw_body=raw_body, headers=headers or {})

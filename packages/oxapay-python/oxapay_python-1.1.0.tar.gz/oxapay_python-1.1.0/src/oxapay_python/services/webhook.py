"""Webhook verification / parsing."""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any, Dict, Optional

from ..exceptions import MissingApiKeyException, WebhookNotReceivedException, WebhookSignatureException


class Webhook:
    """Parse and verify OxaPay webhooks.

    Parameters
    ----------
    merchant_api_key:
        Used when webhook `type` belongs to merchant events.
    payout_api_key:
        Used when webhook `type` is `payout`.
    raw_body:
        Raw request body (string) received by your framework.
    headers:
        Request headers (must include `hmac`).
    """
    def __init__(
        self,
        merchant_api_key: Optional[str] = None,
        payout_api_key: Optional[str] = None,
        *,
        raw_body: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        self._raw_body = raw_body if raw_body is not None else ""
        self._headers = headers or {}

        if not self._raw_body:
            raise WebhookNotReceivedException("Webhook is not received!")

        try:
            data = json.loads(self._raw_body)
        except Exception:
            data = None

        if not isinstance(data, dict):
            raise WebhookNotReceivedException("Webhook is not received!")

        self._data = data
        self._keys = {"merchant": merchant_api_key, "payout": payout_api_key}

    def set_merchant_api_key(self, merchant_api_key: str) -> "Webhook":
        self._keys["merchant"] = merchant_api_key
        return self

    def set_payout_api_key(self, payout_api_key: str) -> "Webhook":
        self._keys["payout"] = payout_api_key
        return self

    def get_data(self, verify: bool = True) -> Dict[str, Any]:
        """Return decoded webhook payload (optionally verified)."""
        if verify:
            self.verify()
        return self._data

    def verify(self) -> None:
        """Verify webhook HMAC signature.

        Raises
        ------
        WebhookSignatureException
            If signature is missing/invalid.
        """
        hmac_header = self._headers.get("hmac") or self._headers.get("HMAC") or self._headers.get("Hmac") or ""
        if not hmac_header:
            raise WebhookSignatureException("Missing HMAC header.")

        secret = self._resolve_api_key(str(self._data.get("type") or ""))
        calc = hmac.new(secret.encode("utf-8"), self._raw_body.encode("utf-8"), hashlib.sha512).hexdigest()

        if not hmac.compare_digest(calc, str(hmac_header)):
            raise WebhookSignatureException("Invalid HMAC signature.").set_context(
                {"content": self._raw_body, "hmac": str(hmac_header), "new_hmac": calc}
            )

    def _resolve_api_key(self, payload_type: str) -> str:
        merchant_types = {"invoice", "white_label", "static_address", "payment_link", "donation"}
        group = "payout" if payload_type == "payout" else "merchant"
        if payload_type in merchant_types:
            group = "merchant"

        key = self._keys.get(group)
        if not key:
            raise MissingApiKeyException(f"{group} API key is not set.")
        return key

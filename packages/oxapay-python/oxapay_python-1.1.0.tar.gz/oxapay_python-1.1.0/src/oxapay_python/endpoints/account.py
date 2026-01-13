"""Account endpoints."""

from __future__ import annotations

from typing import Any, Dict

from ..http.client import OxaPayClient


class Account:
    """Account API wrapper."""
    def __init__(self, client: OxaPayClient, general_api_key: str):
        self._client = client
        self._api_key = general_api_key

    def _headers(self) -> Dict[str, str]:
        return {"general_api_key": self._api_key}

    def balance(self, currency: str = "") -> Dict[str, Any]:
        """Get account balance (optionally filtered by currency)."""
        payload = self._client.get("general/account/balance", {"currency": currency}, self._headers())
        return self._client.maybe_unwrap(payload, {})

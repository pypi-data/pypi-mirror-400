"""Public endpoints that do not require an API key."""

from __future__ import annotations

from typing import Any, Dict

from ..http.client import OxaPayClient


class Common:
    """Common API wrapper."""
    def __init__(self, client: OxaPayClient):
        self._client = client

    def prices(self) -> Dict[str, Any]:
        """Get current prices."""
        return self._client.maybe_unwrap(self._client.get("common/prices", {}, {}), {})

    def currencies(self) -> Dict[str, Any]:
        """Get supported currencies."""
        return self._client.maybe_unwrap(self._client.get("common/currencies", {}, {}), {})

    def fiats(self) -> Dict[str, Any]:
        """Get supported fiats."""
        return self._client.maybe_unwrap(self._client.get("common/fiats", {}, {}), {})

    def networks(self) -> Dict[str, Any]:
        """Get supported networks."""
        return self._client.maybe_unwrap(self._client.get("common/networks", {}, {}), {})

    def monitor(self) -> Dict[str, Any]:
        """Get service monitor status."""
        return self._client.maybe_unwrap(self._client.get("common/monitor", {}, {}), {})

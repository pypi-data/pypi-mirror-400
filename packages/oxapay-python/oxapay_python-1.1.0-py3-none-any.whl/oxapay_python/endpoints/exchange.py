"""Exchange endpoints."""

from __future__ import annotations

from typing import Any, Dict, Optional

from ..http.client import OxaPayClient


class Exchange:
    """Exchange API wrapper."""
    def __init__(self, client: OxaPayClient, general_api_key: str):
        self._client = client
        self._api_key = general_api_key

    def _headers(self) -> Dict[str, str]:
        return {"general_api_key": self._api_key}

    def swap_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a swap request."""
        return self._client.maybe_unwrap(self._client.post("general/swap", data, self._headers()), {})

    def swap_history(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List swap history."""
        return self._client.maybe_unwrap(self._client.get("general/swap", filters or {}, self._headers()), {})

    def swap_pairs(self) -> Dict[str, Any]:
        """List supported swap pairs."""
        return self._client.maybe_unwrap(self._client.get("general/swap/pairs", {}, self._headers()), {})

    def swap_calculate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate swap amounts."""
        return self._client.maybe_unwrap(self._client.post("general/swap/calculate", data, self._headers()), {})

    def swap_rate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get swap rate for a pair/amount."""
        return self._client.maybe_unwrap(self._client.post("general/swap/rate", data, self._headers()), {})

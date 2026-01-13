"""Payout endpoints."""

from __future__ import annotations

from typing import Any, Dict, Optional, Union

from ..exceptions import MissingTrackIdException
from ..http.client import OxaPayClient
from ._mixins import CallbackUrlMixin


class Payout(CallbackUrlMixin):
    """Payout API wrapper."""
    def __init__(self, client: OxaPayClient, payout_api_key: str, callback_url: Optional[str] = None):
        CallbackUrlMixin.__init__(self, callback_url)
        self._client = client
        self._api_key = payout_api_key

    def _headers(self) -> Dict[str, str]:
        return {"payout_api_key": self._api_key}

    def generate(self, data: Dict[str, Any], callback_url: Optional[str] = None) -> Dict[str, Any]:
        """Create a payout request."""
        payload = self._set_callback_url(data, callback_url)
        return self._client.maybe_unwrap(self._client.post("payout", payload, self._headers()), {})

    def information(self, track_id: Union[int, str]) -> Dict[str, Any]:
        """Fetch payout information by track_id."""
        if not track_id:
            raise MissingTrackIdException("Track id must be provided")
        return self._client.maybe_unwrap(self._client.get(f"payout/{track_id}", {}, self._headers()), {})

    def history(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List payout history."""
        return self._client.maybe_unwrap(self._client.get("payout", filters or {}, self._headers()), {})

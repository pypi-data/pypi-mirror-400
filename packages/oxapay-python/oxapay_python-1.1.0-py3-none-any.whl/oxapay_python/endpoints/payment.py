"""Payment endpoints (invoice, white-label, static address, etc.)."""

from __future__ import annotations

from typing import Any, Dict, Optional, Union

from ..exceptions import MissingAddressException, MissingTrackIdException
from ..http.client import OxaPayClient
from ._mixins import CallbackUrlMixin, SandboxMixin


class Payment(CallbackUrlMixin, SandboxMixin):
    """Payment API wrapper.

    Notes
    -----
    Methods accept `data` dictionaries mirroring the API schema.
    """
    def __init__(self, client: OxaPayClient, merchant_api_key: str, callback_url: Optional[str] = None, sandbox: Optional[bool] = None):
        CallbackUrlMixin.__init__(self, callback_url)
        SandboxMixin.__init__(self, sandbox if sandbox is not None else False)
        self._client = client
        self._api_key = merchant_api_key

    def _headers(self) -> Dict[str, str]:
        return {"merchant_api_key": self._api_key}

    def generate_invoice(self, data: Dict[str, Any], callback_url: Optional[str] = None, sandbox: Optional[bool] = None) -> Dict[str, Any]:
        """Create a payment invoice."""
        payload = self._set_callback_url(self._set_sandbox(data, sandbox), callback_url)
        return self._client.maybe_unwrap(self._client.post("payment/invoice", payload, self._headers()), {})

    def generate_white_label(self, data: Dict[str, Any], callback_url: Optional[str] = None) -> Dict[str, Any]:
        """Create a white-label payment."""
        payload = self._set_callback_url(data, callback_url)
        return self._client.maybe_unwrap(self._client.post("payment/white-label", payload, self._headers()), {})

    def generate_static_address(self, data: Dict[str, Any], callback_url: Optional[str] = None) -> Dict[str, Any]:
        """Create a static address."""
        payload = self._set_callback_url(data, callback_url)
        return self._client.maybe_unwrap(self._client.post("payment/static-address", payload, self._headers()), {})

    def revoke_static_address(self, address: str = "", network: str = "") -> None:
        """Revoke a previously generated static address."""
        if not address and not network:
            raise MissingAddressException("address must be provided!")
        self._client.post("payment/static-address/revoke", {"address": address, "network": network}, self._headers())

    def static_address_list(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List static addresses."""
        return self._client.maybe_unwrap(self._client.get("payment/static-address", filters or {}, self._headers()), {})

    def information(self, track_id: Union[int, str]) -> Dict[str, Any]:
        """Fetch payment information by track_id."""
        if not track_id:
            raise MissingTrackIdException("Track id must be provided")
        return self._client.maybe_unwrap(self._client.get(f"payment/{track_id}", {}, self._headers()), {})

    def history(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List payment history."""
        return self._client.maybe_unwrap(self._client.get("payment", filters or {}, self._headers()), {})

    def accepted_currencies(self) -> Dict[str, Any]:
        """List accepted currencies for payments."""
        return self._client.maybe_unwrap(self._client.get("payment/accepted-currencies", {}, self._headers()), {})

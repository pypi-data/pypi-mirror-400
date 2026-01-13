"""Low-level HTTP client used by endpoint classes."""

from __future__ import annotations

from typing import Any, Dict, Optional

import requests

from ..exceptions import (
    HttpException,
    InvalidApiKeyException,
    NotFoundException,
    RateLimitException,
    ServerErrorException,
    ServiceUnavailableException,
    ValidationRequestException,
)


class OxaPayClient:
    """HTTP client wrapper around `requests`.

    `raw` controls whether endpoint methods return the full response payload
    or only the `data` field.
    """
    def __init__(
        self,
        base_url: str,
        timeout: int,
        version: str,
        session: Optional[requests.Session] = None,
        *,
        raw: bool = False,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = int(timeout) if timeout else 20
        self.version = version
        self.raw = bool(raw)
        self.session = session or requests.Session()

    def maybe_unwrap(self, payload: Dict[str, Any], default: Any) -> Any:
        """Return `payload` (raw) or `payload['data']` (default mode)."""
        if self.raw:
            return payload
        return payload.get("data", default)

    def post(
        self,
        path: str,
        payload: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Send a JSON POST request and return the decoded JSON payload."""
        return self._request("POST", path, json_body=payload or {}, headers=headers or {})

    def get(
        self,
        path: str,
        query: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Send a GET request and return the decoded JSON payload."""
        return self._request("GET", path, params=query or {}, headers=headers or {})

    def _endpoint(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def _base_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        return {
            "Origin": f"oxa-python-sdk-v-{self.version}",
            **headers,
        }

    def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        try:
            res = self.session.request(
                method=method,
                url=self._endpoint(path),
                headers=self._base_headers(headers or {}),
                json=json_body if method.upper() != "GET" else None,
                params=params if method.upper() == "GET" else None,
                timeout=self.timeout,
            )
        except requests.RequestException as e:
            raise HttpException(str(e) or "Network error", previous=e).set_context(
                {"previous": e.__class__.__name__, "message": str(e)}
            )

        status = int(res.status_code)
        body_text = res.text or ""

        try:
            payload = res.json() if body_text else {}
        except ValueError:
            payload = {}

        if status >= 400:
            raise self._map_exception(status, payload, body_text)

        return payload

    def _map_exception(self, status: int, payload: Dict[str, Any], raw: str) -> Exception:
        base = (payload.get("message") or "").strip() or "HTTP error"
        err_msg = ""
        try:
            err_msg = str((payload.get("error") or {}).get("message") or "").strip()
        except Exception:
            err_msg = ""

        msg = (base + (" " + err_msg if err_msg else "")).strip()

        if status == 400:
            ex: Exception = ValidationRequestException(msg)
        elif status == 401:
            ex = InvalidApiKeyException(msg)
        elif status == 404:
            ex = NotFoundException(msg)
        elif status == 429:
            ex = RateLimitException(msg)
        elif status == 503:
            ex = ServiceUnavailableException(msg)
        elif status >= 500:
            ex = ServerErrorException(msg)
        else:
            ex = HttpException(msg)

        if hasattr(ex, "set_context"):
            ex.set_context({"response": {"status": status, "payload": payload, "raw": raw}})

        return ex

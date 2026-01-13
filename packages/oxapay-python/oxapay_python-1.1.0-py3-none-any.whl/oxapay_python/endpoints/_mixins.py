from __future__ import annotations

from typing import Any, Dict, Optional


class CallbackUrlMixin:
    def __init__(self, callback_url: Optional[str] = None):
        self._callback_url = callback_url or ""

    def _set_callback_url(self, data: Dict[str, Any], callback_url: Optional[str] = None) -> Dict[str, Any]:
        url = self._callback_url if callback_url is None else (callback_url or "")
        if url:
            data = dict(data)
            data["callback_url"] = url
        return data


class SandboxMixin:
    def __init__(self, sandbox: bool = False):
        self._sandbox = bool(sandbox)

    def _set_sandbox(self, data: Dict[str, Any], sandbox: Optional[bool] = None) -> Dict[str, Any]:
        s = self._sandbox if sandbox is None else bool(sandbox)
        if s is not None:
            data = dict(data)
            data["sandbox"] = s
        return data

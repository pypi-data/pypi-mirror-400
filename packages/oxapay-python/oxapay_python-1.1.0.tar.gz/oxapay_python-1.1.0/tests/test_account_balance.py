import pytest

from oxapay_python import OxaPayManager

class FakeClient:
    def __init__(self, *, raw: bool = False):
        self.raw = bool(raw)
        self.calls = []
        self.post_return = None
        self.get_return = None
        self.post_side_effect = None
        self.get_side_effect = None

    def maybe_unwrap(self, payload, default):
        if self.raw:
            return payload
        return (payload or {}).get("data", default)

    def post(self, path, payload=None, headers=None):
        self.calls.append(("post", path, payload or {}, headers or {}))
        if self.post_side_effect:
            raise self.post_side_effect
        return self.post_return or {}

    def get(self, path, query=None, headers=None):
        self.calls.append(("get", path, query or {}, headers or {}))
        if self.get_side_effect:
            raise self.get_side_effect
        return self.get_return or {}



@pytest.fixture()
def sdk():
    client = FakeClient(raw=True)
    return OxaPayManager(timeout=20, client=client, raw=True), client


def test_account_balance_returns_dict_shape(sdk):
    manager, client = sdk

    client.get_return = {
        "data": {"USDT": 10.5, "BTC": 0.0022866845},
        "message": "ok",
        "error": {},
        "status": 200,
        "version": "1.0.0",
    }

    res = manager.account("general-key").balance()

    data = res.get("data") or {}
    assert isinstance(data, dict)
    assert data["USDT"] == 10.5

    assert client.calls[0][0] == "get"
    assert client.calls[0][1] == "general/account/balance"
    assert client.calls[0][2] == {"currency": ""}
    assert client.calls[0][3].get("general_api_key") == "general-key"

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


def test_create_invoice_and_returns_track_id_payment_url_expired_at_date(sdk):
    manager, client = sdk

    payload = {"amount": 1.23, "currency": "USDT", "lifetime": 10}

    client.post_return = {
        "data": {
            "track_id": "193139644",
            "payment_url": "https://pay.oxapay.com/13355044/193139644",
            "expired_at": 1755999478,
            "date": 1755997678,
        },
        "message": "ok",
        "error": {},
        "status": 200,
        "version": "1.0.0",
    }

    res = manager.payment("merchant-key").generate_invoice(payload, callback_url="https://example.com/cb")

    data = res.get("data") or {}
    assert set(["track_id", "payment_url", "expired_at", "date"]).issubset(set(data.keys()))

    assert client.calls[0][0] == "post"
    assert client.calls[0][1] == "payment/invoice"
    assert client.calls[0][2]["amount"] == 1.23
    assert client.calls[0][3].get("merchant_api_key") == "merchant-key"

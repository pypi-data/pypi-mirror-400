import pytest

from oxapay_python import OxaPayManager
from oxapay_python.exceptions import (
    InvalidApiKeyException,
    NotFoundException,
    RateLimitException,
    ServerErrorException,
    ServiceUnavailableException,
    ValidationRequestException,
)

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


def test_maps_400_to_validation_request_exception_with_context(sdk):
    manager, client = sdk

    e = ValidationRequestException("bad request").set_context({
        "response": {"status": 400, "error": {"key": "lifetime", "message": "The lifetime field must be an integer."}}
    })
    client.post_side_effect = e

    with pytest.raises(ValidationRequestException) as ex:
        manager.payment("merchant-key").generate_invoice({"amount": 1.0, "currency": "USDT", "lifetime": "x"})

    assert ex.value.context.get("response", {}).get("status") == 400


@pytest.mark.parametrize(
    "exc_cls",
    [InvalidApiKeyException, NotFoundException, RateLimitException, ServerErrorException, ServiceUnavailableException],
)
def test_propagates_http_exceptions(sdk, exc_cls):
    manager, client = sdk
    client.get_side_effect = exc_cls("boom")

    with pytest.raises(exc_cls):
        manager.common().monitor()

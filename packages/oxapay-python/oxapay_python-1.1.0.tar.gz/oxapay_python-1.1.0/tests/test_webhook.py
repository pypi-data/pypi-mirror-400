import hashlib
import hmac
import json

import pytest

from oxapay_python.services.webhook import Webhook
from oxapay_python.exceptions import WebhookSignatureException


def _sign(secret: str, raw_body: str) -> str:
    return hmac.new(secret.encode("utf-8"), raw_body.encode("utf-8"), hashlib.sha512).hexdigest()


def test_verifies_invoice_webhook_when_merchant_key_is_passed_explicitly():
    payload = {"type": "invoice", "status": "Paid"}
    raw = json.dumps(payload)
    secret = "custom-merchant-secret"
    headers = {"HMAC": _sign(secret, raw)}

    data = Webhook(merchant_api_key=secret, payout_api_key=None, raw_body=raw, headers=headers).get_data(True)
    assert data["status"] == "Paid"


def test_verifies_payout_webhook_when_key_is_passed_explicitly():
    payload = {"type": "payout", "status": "Confirmed"}
    raw = json.dumps(payload)
    secret = "custom-payout-secret"
    headers = {"HMAC": _sign(secret, raw)}

    data = Webhook(merchant_api_key=None, payout_api_key=secret, raw_body=raw, headers=headers).get_data(True)
    assert data["status"] == "Confirmed"


def test_accepts_lowercase_hmac_header():
    payload = {"type": "invoice", "status": "Paid"}
    raw = json.dumps(payload)
    secret = "merchant-key"
    headers = {"hmac": _sign(secret, raw)}

    data = Webhook(merchant_api_key=secret, payout_api_key=None, raw_body=raw, headers=headers).get_data(True)
    assert data["status"] == "Paid"


def test_raises_on_invalid_signature():
    payload = {"type": "invoice", "status": "Paid"}
    raw = json.dumps(payload)
    headers = {"HMAC": "deadbeef"}

    with pytest.raises(WebhookSignatureException):
        Webhook(merchant_api_key="merchant-key", payout_api_key=None, raw_body=raw, headers=headers).get_data(True)

import httpx
import pytest
import requests
from requests import Session

from py_mdr.client import MDRClient


class MockResponse:
    @staticmethod
    def should_throw():
        return False

    def raise_for_status(self):
        if self.should_throw():
            raise requests.RequestException("Test exception")

    @property
    def text(self):
        return '{"status": "ok"}'


def mocked_post(*args, **kwargs):
    assert args[1] == "https://host:8080/services/collector/event"

    data: dict = kwargs["json"]
    assert data == {
        "source": "pymdr::dataset.test",
        "event": {
            "source_format": "pymdr::dataset.test",
            "message": "Test message"
        }
    }

    # Validate headers
    session: Session = args[0]
    assert session.headers.get("Authorization") == "Splunk <TOKEN>"

    # Generated from: uuid.uuid5(uuid.NAMESPACE_DNS, "dataset.tst.schubergphilis.com")
    client_id = "0b4b167e-189b-522c-98db-0ee38b529270"
    assert session.headers.get("X-Splunk-Request-Channel") == client_id

    return MockResponse()


# TODO: Add tests that rely on betamax for interaction with external

def test_validations(monkeypatch):
    monkeypatch.setattr(MDRClient, "get_valid_client", lambda *args, **kwargs: httpx.Client())

    client = MDRClient(dataset_name="dummy",
                       namespace="dummy",
                       host="a.random.host:8080",
                       token="A_NOT_SO_VALID_TOKEN")
    assert client._validate_dataset_name("good_dataset_name")
    with pytest.raises(ValueError):
        client._validate_dataset_name("Bad-Dataset-Name")
    with pytest.raises(ValueError):
        client._validate_dataset_name("Very Bad Dataset NAME!!")

    assert client._validate_namespace("vgd")
    with pytest.raises(ValueError):
        client._validate_namespace("not_good")
    assert client._validate_namespace("shouldwork")
    with pytest.raises(ValueError):
        client._validate_namespace("Very Bad Namespace Name!!")

import logging

import httpx
import requests
from pytest import fixture

from py_mdr.client import MDRClient
from py_mdr.handler import MDRHandler
from py_mdr.ocsf_models.events.system_activity.event_log_activity import EventLogActivity


class MockResponse:
    def raise_for_status(self):
        pass

    @property
    def text(self):
        return "This is a mocked property"


@fixture
def mocked_handler(monkeypatch):
    monkeypatch.setattr(requests.Session, "post", lambda *args, **kwargs: MockResponse())
    monkeypatch.setattr(MDRClient, "get_valid_client", lambda *args, **kwargs: httpx.Client())
    return MDRHandler(

        dataset_name="test_dataset",
        namespace="test",
        host="some.host:1234",
        token="DUMMY_TOKEN"
    )


def test_map_log(mocked_handler):
    line_number = 10

    record = logging.LogRecord("Test", logging.DEBUG, "tests/", line_number, "This is a test", args=None, exc_info=None)
    log_activity: EventLogActivity = mocked_handler.map_log_record(record)

    # Check correct type and mappings
    assert type(log_activity) is EventLogActivity

    assert log_activity.message == record.msg
    assert log_activity.metadata.log_level == record.levelname
    assert log_activity.enrichments[0].name == "file_information"
    assert log_activity.enrichments[0].data["line_number"] == 10

def test_handler(mocked_handler):
    mdr_handler = mocked_handler

    # Test handling
    record = logging.LogRecord("Test", logging.DEBUG, "tests/", 10, "This is a test", args=None, exc_info=None)
    mdr_handler.emit(record)

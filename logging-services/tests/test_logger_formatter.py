import logging
import json
from logging-services.logging.logger import JsonFormatter

def test_json_formatter_basic():
    formatter = JsonFormatter()

    record = logging.LogRecord(
        name="test-service",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Test message",
        args=(),
        exc_info=None
    )

    output = formatter.format(record)
    log = json.loads(output)

    assert log["message"] == "Test message"
    assert log["level"] == "INFO"
    assert log["service"] == "test-service"
    assert "timestamp" in log

def test_json_formatter_with_correlation_id():
    formatter = JsonFormatter()

    record = logging.LogRecord(
        name="test-service",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="BLABLABLA",
        args=(),
        exc_info=None
    )

    record.correlation_id = "abc-123"

    output = formatter.format(record)
    log = json.loads(output)

    assert log["correlation_id"] == "abc-123"
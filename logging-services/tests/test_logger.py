import logging
from logging-services.logging.logger import setup_logger


def test_logger_outputs_log(caplog):
    logger = setup_logger("test-service")

    with caplog.at_level(logging.INFO):
        logger.info("Hello la team")

    assert "Hello la team" in caplog.text

def test_logger_with_correlation_id(caplog):
    logger = setup_logger("test-service")

    with caplog.at_level(logging.INFO):
        logger.info(
            "BLABLABLA",
            extra={"correlation_id": "xyz-789"}
        )

    assert "BLABLABLA" in caplog.text
    assert "xyz-789" in caplog.text
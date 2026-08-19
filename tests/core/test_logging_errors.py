import logging

from modules.core.errors import ConfigurationError, GenomepipeError, InputValidationError
from modules.core.logging import configure_logging, get_logger


def test_error_hierarchy():
    assert issubclass(ConfigurationError, GenomepipeError)
    assert issubclass(InputValidationError, GenomepipeError)


def test_logger_configuration_is_scoped(tmp_path):
    logger = configure_logging(tmp_path / "genomepipe.log")
    assert logger.name == "genomepipe"
    assert logger.propagate is False
    logger.info("test message")
    for handler in logger.handlers:
        handler.flush()
    assert "test message" in (tmp_path / "genomepipe.log").read_text()


def test_child_logger_uses_genomepipe_namespace():
    logger = get_logger("input")
    assert logger.name == "genomepipe.input"
    assert logger.level == logging.NOTSET

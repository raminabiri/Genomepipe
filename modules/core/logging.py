import logging
from pathlib import Path


LOGGER_NAME = "genomepipe"


def configure_logging(log_file: Path | None = None, level: int = logging.INFO) -> logging.Logger:
    """Configure a single application logger without changing global root logging."""
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)
    logger.propagate = False

    if not logger.handlers:
        stream = logging.StreamHandler()
        stream.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        logger.addHandler(stream)

    if log_file is not None and not any(
        isinstance(handler, logging.FileHandler) and Path(handler.baseFilename) == log_file.resolve()
        for handler in logger.handlers
    ):
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    return logging.getLogger(f"{LOGGER_NAME}.{name}" if name else LOGGER_NAME)

import logging
import os
import sys

log = logging.getLogger(__name__)


def configure() -> None:
    make_log(__name__)


def make_log(log_name: str) -> logging.Logger:
    log_format = os.getenv("LOG_FORMAT", "%(levelname)s [%(name)s] %(message)s")
    log_level = os.getenv("LOG_LEVEL", "INFO")
    logging.basicConfig(format=log_format, level=logging.DEBUG, stream=sys.stdout)
    log.debug(f"Initializing logger for {log_name}")

    if not log_level == "DEBUG":
        log.debug(f"Changing root log level to {log_level}")
    logging.getLogger().setLevel(log_level)

    for log_spec in os.getenv("OTHER_LOG_LEVELS", "").split():
        logger, level = log_spec.split(":", maxsplit=1)
        log.debug(f"Changing log level for {logger} to {level}")
        logging.getLogger(logger).setLevel(level)

    return logging.getLogger(log_name)

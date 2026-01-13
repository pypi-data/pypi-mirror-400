import sys
from typing import Union

from loguru import logger

LEVELS = (
    "TRACE",
    "DEBUG",
    "INFO",
    "SUCCESS",
    "WARNING",
    "ERROR",
    "CRITICAL",
    5,
    10,
    20,
    25,
    30,
    40,
    50,
)


def initialize_logger(logging_level: Union[str, int]) -> None:
    """
    Creates a logger for each ORKG instance.
    Defines the format, content, and colors of the logging messages and the output location.
    :param logging_level: the minimum severity threshold from which log messages are shown
    """
    if logging_level not in LEVELS:
        raise ValueError(
            "the provided logging level is not valid! Options: 'DEBUG', 'INFO', 'WARNING', 'ERROR'"
        )
    logger.remove()
    logger.level("INFO", color="<light-blue>")
    logger.level("DEBUG", color="<fg #4c73c2>")
    fmt = "<fg #65bfea>[{time:HH:mm:ss.SS}]</fg #65bfea> <level>[{level}]</level> <fg #4cc295>[{name}:{function}]</fg #4cc295> <fg #b3f5f3>{message}</fg #b3f5f3>"
    logger.add(sys.stderr, level=logging_level, colorize=True, format=fmt)

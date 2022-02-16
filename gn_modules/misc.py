"""
This file contain miscellaneous functions.
"""

import logging
import enum
import os

def initialize_logger(name: str, filename: str = None, level: int = logging.DEBUG, terminal: bool = False) -> logging.Logger:
    """
    Initialize a simple logger with a file handler and a stream handler if terminal is true.
    To create a child logger you don't need to initialize a new one, just call logger = logging.getLogger(parent.child)
    """

    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter(
        '%(asctime)s\t%(levelname)s\t%(message)s')

    if filename:
        file_handler = logging.FileHandler(filename)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if terminal:
        stream = logging.StreamHandler()
        stream.setFormatter(formatter)
        logger.addHandler(stream)

    os.chmod(filename,0o664)
    logger.info('Logger created.')

    return logger


class AutoName(enum.Enum):
    """Auto naming from labels."""
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name

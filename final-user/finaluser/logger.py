import logging
import sys
from typing import Optional

LOGGING_FORMATTER = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

DebugLevels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
DebugLevelType = str


def get_logger(name: Optional[str] = None, level: DebugLevelType = 'INFO') -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(LOGGING_FORMATTER)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    if not level or level not in DebugLevels:
        logger.warning('Invalid logging level %s. Setting logging level to DEBUG.', level)
        level = 'DEBUG'

    logger.setLevel(level)
    return logger

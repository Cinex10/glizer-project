"""Centralized logging configuration for the whole project.

Import this module *once* (ideally in the application entry-point) before other
project modules so that `basicConfig` runs early.  After that, every module can
simply do:

    from logging import get_logger
    logger = get_logger(__name__)

and inherit the configuration defined here.
"""

from dotenv import load_dotenv
import logging
import os
from typing import Union

load_dotenv()

# ---------------------------------------------------------------------------
# Configure root logger
# ---------------------------------------------------------------------------

LOG_LEVEL_ENV = os.getenv("LOG_LEVEL", "INFO").upper()

# Map the string level to the `logging` module constant; default to INFO on
# unexpected values.
LEVEL: int = getattr(logging, LOG_LEVEL_ENV, logging.INFO)

logging.basicConfig(
    level=LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


# ---------------------------------------------------------------------------
# Convenience helper
# ---------------------------------------------------------------------------

def get_logger(name: Union[str, None] = None) -> logging.Logger:
    """Return a logger with the given *name* using the global configuration."""
    return logging.getLogger(name)

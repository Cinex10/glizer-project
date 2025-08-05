"""Maintenance tasks such as periodic cleanup of temporary user data directories.

This module currently contains a single job function that deletes the
`user-data` directory. It is designed to be used with an RQ worker that has
its scheduler component enabled so that the job can be scheduled to repeat
at a fixed interval.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from logging_config import get_logger

logger = get_logger(__name__)


def _resolve_user_data_path() -> Path:
    """Return the absolute path to the `user-data` directory.
    """
    user_data_env = "user-data"
    path = Path(user_data_env).expanduser().resolve()
    return path


def delete_user_data_folder() -> None:
    """Delete the entire `user-data` directory.

    This function is intended to be scheduled as a repeating job using RQ. It
    removes the directory and *all* of its contents using :pyfunc:`shutil.rmtree`.
    If the directory does not exist, the function logs this fact and returns
    silently.
    """
    path = _resolve_user_data_path()

    if not path.exists():
        logger.info("User data directory %s does not exist – nothing to delete", path)
        return

    # Safety guard: ensure we are about to delete a directory, not a file.
    if not path.is_dir():
        logger.warning("Configured user data path %s is not a directory – skipping deletion", path)
        return

    try:
        shutil.rmtree(path)
        logger.info("Successfully deleted user data directory at %s", path)
    except Exception as exc:
        logger.error("Failed to delete user data directory %s: %s", path, exc)

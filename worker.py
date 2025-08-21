#!/usr/bin/env python3
"""
RQ Worker startup script.
Usage: python worker.py
"""

import os
import sys
from dotenv import load_dotenv
import logging

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.transaction.worker import start_worker

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    logger.info("Starting RQ worker for transaction processing...")
    start_worker() 
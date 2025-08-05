#!/usr/bin/env python3
"""
RQ Worker startup script.
Usage: python worker.py
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.transaction.worker import start_worker

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    print("Starting RQ worker for transaction processing...")
    start_worker() 
"""
ShopPulse Logging Utility
=========================
A simple, beginner-friendly logging utility for terminal and execution tracking.

Author: ShopPulse Big Data Team
Date: November 2026
"""

import sys
from datetime import datetime

def log_info(message: str) -> None:
    """Print an informational message with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [INFO] {message}")

def log_success(message: str) -> None:
    """Print a success confirmation message."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [SUCCESS] \u2714 {message}")

def log_warning(message: str) -> None:
    """Print a warning message."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [WARNING] \u26A0 {message}", file=sys.stderr)

def log_error(message: str) -> None:
    """Print an error message."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [ERROR] \u2718 {message}", file=sys.stderr)


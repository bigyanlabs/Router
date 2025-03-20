import logging
import os
from datetime import datetime
from typing import Any

LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, f"{datetime.now().strftime('%Y-%m-%d')}.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def log_request(route: str, method: str, status: int) -> None:
    """Logs each request."""
    logging.info(f"Route: {route} | Method: {method} | Status: {status}")

def log_error(error: Any) -> None:
    """Logs errors."""
    logging.error(f"Error: {error}", exc_info=True)

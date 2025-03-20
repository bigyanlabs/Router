import logging
import os
import atexit
import json
import time
from datetime import datetime
from typing import Any

LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

DEVELOPMENT_MODE = os.environ.get('FLASK_ENV') == 'development' or os.environ.get('DEBUG') == 'True'

SESSION_TRACKING_FILE = os.path.join(LOG_DIR, ".session_tracker")
MAX_DEV_SESSION_AGE = 3600  

def get_or_create_session_id():
    """Get an existing session ID or create a new one based on environment"""
    if DEVELOPMENT_MODE:
        try:
            if os.path.exists(SESSION_TRACKING_FILE):
                with open(SESSION_TRACKING_FILE, 'r') as f:
                    session_data = json.load(f)
                    last_session = session_data.get('last_session')
                    timestamp = session_data.get('timestamp', 0)
                    
                   
                    if last_session and time.time() - timestamp < MAX_DEV_SESSION_AGE:
                        return last_session
        except (json.JSONDecodeError, IOError):
            pass
    
   
    new_session = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if DEVELOPMENT_MODE:
        try:
            with open(SESSION_TRACKING_FILE, 'w') as f:
                json.dump({
                    'last_session': new_session,
                    'timestamp': time.time()
                }, f)
        except IOError:
            
            pass
    
    return new_session


SESSION_ID = get_or_create_session_id()


LOG_FILE = os.path.join(LOG_DIR, f"{datetime.now().strftime('%Y-%m-%d')}_{SESSION_ID}.log")


logger = logging.getLogger()


if not logger.handlers:
    logger.setLevel(logging.DEBUG)
    
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s", "%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

def log_request(route: str, method: str, status: Any) -> None:
    """Logs each request."""
    logger.info(f"Route: {route} | Method: {method} | Status: {status}")

def log_error(error: Any) -> None:
    """Logs errors."""
    logger.error(f"Error: {error}", exc_info=True)

def log_warning(message: str) -> None:
    """Logs a warning message."""
    logger.warning(message)

def log_info(message: str) -> None:
    """Logs an info message."""
    logger.info(message)

def log_debug(message: str) -> None:
    """Logs a debug message."""
    logger.debug(message)

def log_startup() -> None:
    """Logs application startup."""
    startup_type = "RELOADED" if DEVELOPMENT_MODE else "STARTED"
    logger.info(f"===== SERVER {startup_type} (Session ID: {SESSION_ID}) =====")
    logger.info(f"Log file: {LOG_FILE}")

def log_shutdown() -> None:
    """Logs application shutdown."""
    if not DEVELOPMENT_MODE:
        logger.info(f"===== SERVER SHUTTING DOWN (Session ID: {SESSION_ID}) =====")
    logging.shutdown()


atexit.register(log_shutdown)

log_startup()


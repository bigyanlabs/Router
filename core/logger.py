import logging
import os
import atexit
import json
import time
from datetime import datetime
from typing import Any
import sys

LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

DEVELOPMENT_MODE = os.environ.get('FLASK_ENV') == 'development' or os.environ.get('DEBUG') == 'True'

# Session management
SESSION_TRACKING_FILE = os.path.join(LOG_DIR, ".session_tracker")
MAX_DEV_SESSION_AGE = 3600  


def get_or_create_session_id():
    """Get an existing session ID or create a new one based on environment"""
    new_session_created = False
    
    if DEVELOPMENT_MODE:
        try:
            if os.path.exists(SESSION_TRACKING_FILE):
                with open(SESSION_TRACKING_FILE, 'r') as f:
                    session_data = json.load(f)
                    last_session = session_data.get('last_session')
                    timestamp = session_data.get('timestamp', 0)
                    
                    # If the session is recent enough, reuse it
                    if last_session and time.time() - timestamp < MAX_DEV_SESSION_AGE:
                        return last_session, False
        except (json.JSONDecodeError, IOError):
            pass
    
    # Generate a new session ID
    new_session = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_session_created = True
    
    # Save it for future use in development mode
    if DEVELOPMENT_MODE:
        try:
            with open(SESSION_TRACKING_FILE, 'w') as f:
                json.dump({
                    'last_session': new_session,
                    'timestamp': time.time()
                }, f)
        except IOError:
            pass
    
    return new_session, new_session_created

SESSION_ID, IS_NEW_SESSION = get_or_create_session_id()


LOG_FILE = os.path.join(LOG_DIR, f"{datetime.now().strftime('%Y-%m-%d')}_{SESSION_ID}.log")


logger = logging.getLogger('myapp')


if not logger.handlers:
    logger.setLevel(logging.DEBUG)
    logger.propagate = False  
    
  
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s", "%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
   
    if IS_NEW_SESSION or not DEVELOPMENT_MODE:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)  
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)


if DEVELOPMENT_MODE and not IS_NEW_SESSION:
    class NullStream(object):
        def write(self, *args, **kwargs):
            pass
        def flush(self, *args, **kwargs):
            pass

    
    if 'WERKZEUG_RUN_MAIN' in os.environ:
        sys.stdout = NullStream()
        sys.stderr = NullStream()

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
  
    if IS_NEW_SESSION or not DEVELOPMENT_MODE:
        startup_type = "STARTED" if IS_NEW_SESSION else "RELOADED"
        logger.info(f"===== SERVER {startup_type} (Session ID: {SESSION_ID}) =====")
        logger.info(f"Log file: {LOG_FILE}")
    else:
        # Only log to file, not console for reloads
        file_only_logger = logging.getLogger("file_only")
        if not file_only_logger.handlers:
            file_only_logger.setLevel(logging.DEBUG)
            file_handler = logging.FileHandler(LOG_FILE)
            file_handler.setFormatter(formatter)
            file_only_logger.addHandler(file_handler)
        
        file_only_logger.info(f"===== SERVER RELOADED (Session ID: {SESSION_ID}) =====")

def log_shutdown() -> None:
    """Logs application shutdown."""
  
    if not DEVELOPMENT_MODE or IS_NEW_SESSION:
        logger.info(f"===== SERVER SHUTTING DOWN (Session ID: {SESSION_ID}) =====")
    logging.shutdown()


atexit.register(log_shutdown)


log_startup()


quiet_logger = logging.getLogger("quiet")
if not quiet_logger.handlers:
    quiet_logger.setLevel(logging.DEBUG)
    quiet_logger.propagate = False  
    file_handler = logging.FileHandler(LOG_FILE)
    formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s", "%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(formatter)
    quiet_logger.addHandler(file_handler)

def log_quiet(message: str, level: str = "INFO") -> None:
    """Logs a message to file only, without console output"""
    level = level.upper()
    if level == "DEBUG":
        quiet_logger.debug(message)
    elif level == "INFO":
        quiet_logger.info(message)
    elif level == "WARNING":
        quiet_logger.warning(message)
    elif level == "ERROR":
        quiet_logger.error(message)
    else:
        quiet_logger.info(message)
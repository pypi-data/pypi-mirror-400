"""
Logging Configuration for Nyx System
Provides centralized logging with file rotation and structured output.
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Configuration
LOG_DIR = Path(".nyx/logs")
LOG_FILE = LOG_DIR / "nyx.log"
MAX_BYTES = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT = 3


def get_logger(name: str = "Nyx") -> logging.Logger:
    """
    Returns a configured logger instance with console and file handlers.
    Uses singleton pattern - only configures once per logger name.
    """
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)
    
    # Ensure log directory exists
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Console Handler (stderr to avoid polluting stdout for MCP)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    ))
    logger.addHandler(console_handler)

    # File Handler (rotating)
    try:
        file_handler = RotatingFileHandler(
            LOG_FILE, 
            maxBytes=MAX_BYTES, 
            backupCount=BACKUP_COUNT, 
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'
        ))
        logger.addHandler(file_handler)
    except Exception as e:
        sys.stderr.write(f"Warning: Could not set up file logging: {e}\n")

    return logger


# Global logger instance
logger = get_logger()

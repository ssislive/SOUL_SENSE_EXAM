import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional

from app.config import LOG_DIR
LOG_FILE: str = "soulsense.log"
MAX_BYTES: int = 10 * 1024 * 1024  # 10MB
BACKUP_COUNT: int = 5

def setup_logging() -> None:
    """Configure centralized logging for the application."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    log_path = os.path.join(LOG_DIR, LOG_FILE)
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Remove default handlers if any (to avoid duplication with basicConfig elsewhere)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # File Handler
    file_handler = RotatingFileHandler(
        log_path, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT, encoding='utf-8'
    )
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        "%(levelname)s: %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    logging.info("Logging initialized.")

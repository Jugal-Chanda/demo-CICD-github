import logging
import sys
from pathlib import Path
from ..config import get_config

def setup_logger(name: str, config=None) -> logging.Logger:
    """
    Set up logger with proper configuration

    Args:
        name: Logger name (usually __name__)
        config: Configuration object (optional)

    Returns:
        Configured logger instance
    """
    if config is None:
        config = get_config()

    logger = logging.getLogger(name)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, config.LOG_LEVEL.upper()))

    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if log file is specified)
    if hasattr(config, 'LOG_FILE') and config.LOG_FILE:
        try:
            log_path = Path(config.LOG_FILE)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(config.LOG_FILE)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Could not set up file logging: {e}")

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get logger instance with default configuration

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return setup_logger(name)
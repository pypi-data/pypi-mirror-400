import logging
import sys
from typing import Optional

def setup_production_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    enable_json: bool = False
) -> None:
    """
    Setup production-ready logging for py-flowcheck.
    
    :param level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    :param format_string: Custom format string
    :param enable_json: Enable JSON structured logging
    """
    if format_string is None:
        if enable_json:
            format_string = '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
        else:
            format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        stream=sys.stdout,
        force=True
    )
    
    # Set py-flowcheck logger level
    logger = logging.getLogger('py_flowcheck')
    logger.setLevel(getattr(logging, level.upper()))

def get_logger(name: str) -> logging.Logger:
    """Get a logger for py-flowcheck components."""
    return logging.getLogger(f'py_flowcheck.{name}')
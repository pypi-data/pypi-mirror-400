"""
Logging configuration for dlt pipelines.

This module provides a consistent logging setup across all dlt pipelines.

Usage:
    from dlt_utils import configure_logging
    
    # In your main function
    configure_logging(debug=args.debug)
"""
import logging


def configure_logging(
    debug: bool = False,
    log_format: str | None = None,
    date_format: str = "%Y-%m-%d %H:%M:%S",
) -> None:
    """
    Configure logging for a dlt pipeline.
    
    Args:
        debug: If True, set log level to DEBUG, otherwise INFO.
        log_format: Custom log format string. If None, uses default format.
        date_format: Date format for log timestamps.
    
    Example:
        configure_logging(debug=args.debug)
    """
    log_level = logging.DEBUG if debug else logging.INFO
    
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Logger name (typically __name__).
        
    Returns:
        Configured logger instance.
    """
    return logging.getLogger(name)

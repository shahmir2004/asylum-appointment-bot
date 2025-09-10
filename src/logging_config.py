"""
Logging configuration for Asylum Appointment Booking Bot MVP

This module sets up centralized logging for the entire application.
All components should import and use the logger from this module.
"""

import logging
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_logging():
    """
    Configure application-wide logging based on environment variables.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Get configuration from environment
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_file = os.getenv('LOG_FILE', 'logs/asylum_bot.log')
    log_format = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Ensure log directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
        handlers=[
            # File handler for persistent logs
            logging.FileHandler(log_file, encoding='utf-8'),
            # Console handler for real-time monitoring
            logging.StreamHandler()
        ]
    )
    
    # Create application logger
    logger = logging.getLogger('asylum_bot')
    
    # Log startup information
    logger.info("="*50)
    logger.info("Asylum Appointment Booking Bot - MVP Starting")
    logger.info(f"Log Level: {log_level}")
    logger.info(f"Log File: {log_file}")
    logger.info("="*50)
    
    return logger

def get_logger(name: str = None):
    """
    Get a logger instance for a specific component.
    
    Args:
        name (str): Logger name (usually module name)
        
    Returns:
        logging.Logger: Logger instance
    """
    if name:
        return logging.getLogger(f'asylum_bot.{name}')
    return logging.getLogger('asylum_bot')

# Initialize default logger
default_logger = setup_logging()

# Example usage for other modules:
# from src.logging_config import get_logger
# logger = get_logger(__name__)

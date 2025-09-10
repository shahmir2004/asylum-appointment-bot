"""
Test script to verify logging configuration is working properly.
Run this to ensure logs are being written to both console and file.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.logging_config import get_logger

def test_logging():
    """Test logging functionality"""
    logger = get_logger('test')
    
    logger.info("Testing INFO level logging")
    logger.warning("Testing WARNING level logging")
    logger.error("Testing ERROR level logging")
    logger.debug("Testing DEBUG level logging (may not appear depending on log level)")
    
    print("\n" + "="*50)
    print("Logging test completed!")
    print("Check logs/asylum_bot.log for file output")
    print("Console output should appear above")
    print("="*50)

if __name__ == "__main__":
    test_logging()

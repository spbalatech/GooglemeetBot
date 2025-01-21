import logging
import sys
from datetime import datetime
from pathlib import Path

def setup_logger():
    """Configure and return a logger instance."""
    # Create logs directory if it doesn't exist
    Path("logs").mkdir(exist_ok=True)
    
    logger = logging.getLogger('MeetBot')
    logger.setLevel(logging.INFO)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # Create file handler
    file_handler = logging.FileHandler(
        f'logs/meetbot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    )
    file_handler.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

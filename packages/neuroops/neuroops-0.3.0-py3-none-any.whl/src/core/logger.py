import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logger(name="neuroops", log_file="neuroops.log", level=logging.INFO):
    """
    Configures a robust rotating file logger.
    Writes to ~/.neuroops/<log_file>
    Rotates at 5MB, keeps 1 backup.
    """
    home = Path.home()
    log_dir = home / ".neuroops"
    
    # Ensure dir exists (CLI entry point does this too, but safety first)
    if not log_dir.exists():
        log_dir.mkdir(parents=True)
        
    log_path = log_dir / log_file
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers if reloading
    if not logger.handlers:
        # Rotating File Handler (The "Black Box Recorder")
        handler = RotatingFileHandler(
            log_path, 
            maxBytes=5*1024*1024, # 5MB
            backupCount=1
        )
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Optional: Console handler for development (can be removed for silent prod)
        # console = logging.StreamHandler()
        # console.setFormatter(formatter)
        # logger.addHandler(console)
        
    return logger

# Singleton instance
logger = setup_logger()

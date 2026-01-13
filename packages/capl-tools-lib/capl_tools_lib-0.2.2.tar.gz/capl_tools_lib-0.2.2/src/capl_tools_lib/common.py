import logging
import sys

# ==========================================
#              Logging Configuration
# ==========================================

# Master switch to enable/disable all logging output for this library
ENABLE_LOGGING = True

# Default logging level for all modules (e.g., logging.INFO, logging.WARNING)
DEFAULT_LEVEL = logging.WARNING

# Specific configuration for individual modules.
# Add the module name (e.g., 'capl_tools_lib.scanner') and desired level.
# This allows you to "enable" debug logging for just one file.
MODULE_CONFIG = {
    # "capl_tools_lib.scanner": logging.DEBUG,
    # "capl_tools_lib.parser": logging.INFO,
}

# ==========================================

def get_logger(name: str) -> logging.Logger:
    """
    Factory function to get a configured logger for a module.
    
    Usage in your files:
        from .common import get_logger
        logger = get_logger(__name__)
    """
    logger = logging.getLogger(name)
    
    # Apply specific level if configured, otherwise default
    if name in MODULE_CONFIG:
        logger.setLevel(MODULE_CONFIG[name])
    else:
        logger.setLevel(DEFAULT_LEVEL)
        
    # Ensure the library's root logger is set up with a handler
    _ensure_root_handler()
    
    return logger

def _ensure_root_handler():
    """
    Internal function to attach a console handler to the package root logger
    so logs actually show up.
    """
    package_name = __name__.split('.')[0] # e.g., 'capl_tools_lib'
    root_logger = logging.getLogger(package_name)
    
    # Only configure if enabled and no handlers exist yet
    if ENABLE_LOGGING and not root_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '[%(levelname)s] %(name)s: %(message)s'
        )
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
        
        # The root logger must allow everything through so children can filter
        root_logger.setLevel(logging.DEBUG) 
        
        # If you want to stop logs from propagating to the main app's root logger:
        # root_logger.propagate = False

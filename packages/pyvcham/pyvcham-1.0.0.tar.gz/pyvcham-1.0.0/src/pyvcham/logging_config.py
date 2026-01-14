import logging
import logging.config
import os

# Logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',  # Use INFO or WARNING for production
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 3,
            'formatter': 'standard'
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'DEBUG'
    },
    'loggers': {
        'matplotlib': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',  # Suppress DEBUG messages from matplotlib
            'propagate': False
        },
    }
}

def setup_logging():
    """
    Set up logging configuration for the application.

    This function configures logging using a predefined configuration dictionary.
    It sets up both console and file logging with rotating file handlers.
    """
    try:
        # Ensure the log directory exists
        log_file_path = LOGGING_CONFIG['handlers']['file']['filename']
        log_dir = os.path.dirname(log_file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # Apply logging configuration
        logging.config.dictConfig(LOGGING_CONFIG)
        logging.info("Logging configuration successfully loaded.")
    except Exception as e:
        logging.error(f"Failed to set up logging: {e}")
        raise

# Call setup_logging when this module is imported
setup_logging()

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Parameters
    ----------
    name : str
        The name of the logger (usually __name__).

    Returns
    -------
    logging.Logger
        A configured logger instance.
    """
    return logging.getLogger(name)
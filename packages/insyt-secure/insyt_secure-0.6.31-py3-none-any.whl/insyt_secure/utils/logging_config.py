import logging
import logging.config
import logging.handlers
import sys
import re
import os
from pythonjsonlogger import jsonlogger
import enum
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

# Define logging formats as an enum
class LoggingFormat(enum.Enum):
    STANDARD = "standard"
    JSON = "json"
    USER_FRIENDLY = "user_friendly"

# Default log level if not specified
DEFAULT_LOG_LEVEL = logging.INFO

class SensitiveInfoFilter(logging.Filter):
    """Filter that masks sensitive information in log records."""
    
    # Patterns to identify sensitive information
    PATTERNS = [
        # Credential patterns - usernames and passwords
        (r'(password|pwd|passwd|secret|token)["\s:=]+["\s]*([^"\s,\}]+)', r'\1: "****"'),
        (r'(username|user|uid)["\s:=]+["\s]*([^"\s,\}]+)', r'\1: "****"'),
        
        # API keys and tokens
        (r'(api[_-]?key|auth[_-]?token)["\s:=]+["\s]*([^"\s,\}]+)', r'\1: "****"'),
        (r'(key|token)["\s:=]+["\s]*([0-9a-zA-Z_\-\.]{8,})', r'\1: "****"'),
        
        # Service credentials 
        (r'(credentials)["\s:=]+["\s]*([^"\s,\}]+)', r'\1: "****"'),
        
        # Channel names
        (r'(topic|channel|path)["\s:=]+["\s]*([^"\s,\}]+)', r'\1: "****"'),
        
        # Project IDs (when they appear as full strings)
        (r'(project_id|project-id)["\s:=]+["\s]*([^"\s,\}]+)', r'\1: "****"'),
        
        # Full URLs containing auth info
        (r'https?://[^:]+:[^@]+@', r'https://****:****@'),
    ]
    
    def __init__(self, redact_sensitive: bool = True):
        """Initialize the filter with option to enable/disable redaction."""
        self.redact_sensitive = redact_sensitive
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log records by masking sensitive information."""
        if not self.redact_sensitive:
            return True
            
        # Get the message from the record before formatting
        if not hasattr(record, 'message'):
            record.message = record.getMessage()
            
        # Apply all patterns to the message
        message = record.message
        for pattern, replacement in self.PATTERNS:
            message = re.sub(pattern, replacement, message)
            
        # Replace the message with the redacted version
        record.message = message
            
        return True

class UserFriendlyFormatter(logging.Formatter):
    """Formatter that produces user-friendly, colorized output."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def __init__(self, fmt=None, datefmt=None, style='%', use_colors=True):
        """Initialize the formatter with color options."""
        super().__init__(fmt, datefmt, style)
        self.use_colors = use_colors and sys.stdout.isatty()  # Only use colors on TTY
    
    def format(self, record):
        """Format the log record with colors and simplified output."""
        # First, let the parent class do its formatting
        formatted_message = super().format(record)
        
        if self.use_colors:
            # Add color based on log level
            level_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            reset_color = self.COLORS['RESET']
            
            # Add color to the level name in the message
            formatted_message = formatted_message.replace(
                f"{record.levelname}:", 
                f"{level_color}{record.levelname}:{reset_color}"
            )
        
        return formatted_message

def configure_logging(
    level: Union[int, str] = DEFAULT_LOG_LEVEL,
    format: LoggingFormat = LoggingFormat.USER_FRIENDLY,
    redact_sensitive: bool = True,
    log_file: Optional[str] = None
) -> None:
    """
    Configure the logging system.
    
    Args:
        level: Logging level (DEBUG, INFO, etc.)
        format: The format to use for logs (standard, json, or user_friendly)
        redact_sensitive: Whether to redact sensitive information
        log_file: Optional file path to write logs to
    """
    # Convert string level to int if needed
    if isinstance(level, str):
        level = getattr(logging, level.upper(), DEFAULT_LOG_LEVEL)
    
    # Base configuration
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'sensitive_info_filter': {
                '()': SensitiveInfoFilter,
                'redact_sensitive': redact_sensitive
            }
        },
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'json': {
                'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s"}',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'user_friendly': {
                '()': UserFriendlyFormatter,
                'format': '%(asctime)s %(levelname)s: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
                'use_colors': True
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': level,
                'formatter': format.value,
                'filters': ['sensitive_info_filter'],
                'stream': 'ext://sys.stdout'
            }
        },
        'loggers': {
            '': {  # Root logger
                'handlers': ['console'],
                'level': level,
                'propagate': True
            },
            'insyt_secure': {
                'handlers': ['console'],
                'level': level,
                'propagate': False
            }
        }
    }
    
    # Add file handler if log_file is specified
    if log_file:
        log_path = Path(log_file)
        log_dir = log_path.parent
        
        # Create directory if it doesn't exist
        if not log_dir.exists():
            log_dir.mkdir(parents=True, exist_ok=True)
            
        config['handlers']['file'] = {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'level': level,
            'formatter': format.value,
            'filters': ['sensitive_info_filter'],
            'filename': str(log_path),
            'when': 'midnight',
            'interval': 1,
            'backupCount': 7,
            'encoding': 'utf-8'
        }
        
        # Add file handler to loggers
        config['loggers']['']['handlers'].append('file')
        config['loggers']['insyt_secure']['handlers'].append('file')
    
    # Apply the configuration
    logging.config.dictConfig(config)
    
    # Log startup message at DEBUG level
    logger = logging.getLogger('insyt_secure.logging')
    logger.debug(f"Logging configured: level={logging.getLevelName(level)}, format={format.value}")
    
    # If we're using JSON logging, warn about color codes
    if format == LoggingFormat.JSON and any(h.formatter == 'user_friendly' for h in logger.handlers):
        logger.warning("Using JSON logging format with color codes may affect JSON parsing.")

def get_log_level_from_env(log_level=None):
    """
    Get log level from parameter or environment variables.
    
    Args:
        log_level: Optional log level name (debug, info, etc.)
                  If not provided, will read from INSYT_LOG_LEVEL environment variable
    
    Returns:
        int: The corresponding logging level (logging.DEBUG, logging.INFO, etc.)
    """
    log_level_name = log_level or os.environ.get('INSYT_LOG_LEVEL', 'INFO')
    log_level_name = log_level_name.upper()
    
    log_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    return log_levels.get(log_level_name, logging.INFO)

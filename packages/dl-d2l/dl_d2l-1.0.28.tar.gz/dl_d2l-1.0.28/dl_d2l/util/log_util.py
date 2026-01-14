import json
import logging
import os
import sys
from pathlib import Path


class StructuredFormatter(logging.Formatter):
    """Structured logging formatter that outputs JSON or structured text."""

    def __init__(self, fmt=None, datefmt=None, style='%', validate=True, colored=False, structured=False):
        super().__init__(fmt, datefmt, style, validate)
        self.colored = colored
        self.structured = structured

        # Define color codes
        self.COLORS = {
            'DEBUG': '\033[36m',  # Cyan
            'INFO': '\033[32m',  # Green
            'WARNING': '\033[33m',  # Yellow
            'ERROR': '\033[31m',  # Red
            'CRITICAL': '\033[35m',  # Magenta
            'RESET': '\033[0m'  # Reset
        }

    def formatTime(self, record, datefmt=None):
        """Format time to include milliseconds."""
        import time
        ct = self.converter(record.created)
        if datefmt:
            s = time.strftime(datefmt, ct)
        else:
            # Default format with milliseconds
            s = time.strftime("%Y-%m-%d %H:%M:%S", ct)
        return f"{s},{record.msecs:03.0f}"

    def format(self, record):
        # Abbreviate the pathname to include only the package path and filename
        if hasattr(record, 'pathname'):
            record.shortpath = os.path.relpath(record.pathname, start=os.getcwd())

        if self.structured:
            # Format as structured JSON-like output
            log_entry = {
                'timestamp': self.formatTime(record, self.datefmt),
                'level': record.levelname,
                'logger': record.name,
                'file': record.shortpath,
                'line': record.lineno,
                'function': record.funcName,
                'message': record.getMessage(),
            }

            # Add any extra fields that were passed
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                               'filename', 'module', 'lineno', 'funcName', 'created',
                               'msecs', 'relativeCreated', 'thread', 'threadName',
                               'processName', 'process', 'getMessage', 'shortpath']:
                    log_entry[key] = value

            return json.dumps(log_entry, ensure_ascii=False)
        else:
            # Add colored output if enabled
            if self.colored:
                levelname = record.levelname
                if levelname in self.COLORS:
                    record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}\033[0m"

            return super().format(record)


class EnterpriseFormatter(StructuredFormatter):
    """Enterprise-grade logging formatter with multiple format options."""

    def __init__(self, fmt=None, datefmt=None, style='%', validate=True, colored=False, structured=False):
        super().__init__(fmt, datefmt, style, validate, colored, structured)


class LoggerManager:
    """Enterprise-grade logger manager with configurable options."""

    def __init__(self):
        self._configured = False
        self._loggers = {}
        self._console_handler = None
        self._file_handler = None
        self._log_dir = "logs"

    def configure(self,
                  level=logging.INFO,
                  console=True,
                  console_format="%(asctime)s | %(levelname)-8s | %(name)s | %(shortpath)s:%(lineno)d | %(message)s",
                  file_logging=False,
                  file_format="%(asctime)s | %(levelname)-8s | %(name)s | %(shortpath)s:%(lineno)d | %(funcName)s | %(message)s",
                  log_file_path=None,
                  max_bytes=10 * 1024 * 1024,  # 10MB
                  backup_count=5,
                  colored_output=False,
                  structured_output=False,
                  json_output=False):
        """
        Configure the logging system with enterprise-grade settings.
        
        Args:
            level: Logging level (default: INFO)
            console: Enable console logging (default: True)
            console_format: Format for console output
            file_logging: Enable file logging (default: False)
            file_format: Format for file output
            log_file_path: Path to log file (default: logs/app.log)
            max_bytes: Maximum size of log file before rotation
            backup_count: Number of backup files to keep
            colored_output: Enable colored console output (default: False)
            structured_output: Enable structured logging (default: False)
            json_output: Output logs as JSON (default: False)
        """
        if self._configured:
            return

        # Create logs directory if needed
        if file_logging:
            Path(self._log_dir).mkdir(exist_ok=True)

        # Determine if we want structured output
        use_structured = structured_output or json_output

        # Console handler
        if console:
            self._console_handler = logging.StreamHandler(sys.stdout)
            console_formatter = EnterpriseFormatter(
                fmt=console_format if not use_structured else None,
                datefmt='%Y-%m-%d %H:%M:%S',  # Will be overridden by formatTime method to include milliseconds
                structured=use_structured
            )
            if colored_output and not json_output:
                console_formatter.colored = True
            self._console_handler.setFormatter(console_formatter)

        # File handler
        if file_logging:
            if log_file_path is None:
                log_file_path = os.path.join(self._log_dir, "application.log")

            # Create directory for log file if needed
            log_file_dir = os.path.dirname(log_file_path)
            if log_file_dir:
                Path(log_file_dir).mkdir(parents=True, exist_ok=True)

            # Use RotatingFileHandler for log rotation
            try:
                from logging.handlers import RotatingFileHandler
                self._file_handler = RotatingFileHandler(
                    log_file_path,
                    maxBytes=max_bytes,
                    backupCount=backup_count,
                    encoding='utf-8'
                )
            except ImportError:
                # Fallback to basic FileHandler if RotatingFileHandler is not available
                self._file_handler = logging.FileHandler(log_file_path, encoding='utf-8')

            file_formatter = EnterpriseFormatter(
                fmt=file_format if not json_output else None,
                datefmt='%Y-%m-%d %H:%M:%S',  # Will be overridden by formatTime method to include milliseconds
                structured=use_structured
            )
            self._file_handler.setFormatter(file_formatter)

        # Set up basic configuration
        handlers = [h for h in [self._console_handler, self._file_handler] if h is not None]
        logging.basicConfig(
            level=level,
            handlers=handlers,
            force=True  # This ensures reconfiguration works
        )

        self._configured = True

    def get_logger(self, name, level=None):
        """
        Get a logger with the specified name.
        
        Args:
            name: Name of the logger
            level: Optional level to set for this specific logger
            
        Returns:
            Configured logger instance
        """
        if name in self._loggers:
            logger = self._loggers[name]
        else:
            logger = logging.getLogger(name)

            # Only add handlers if they don't already exist to avoid duplicates
            if not logger.handlers:
                for handler in [h for h in [self._console_handler, self._file_handler] if h is not None]:
                    logger.addHandler(handler)

            # Set level if provided
            if level is not None:
                logger.setLevel(level)

            self._loggers[name] = logger

        return logger


# Global logger manager instance
_logger_manager = LoggerManager()


def configure_logging(**kwargs):
    """
    Configure logging with enterprise-grade settings.
    This should be called once at application startup.
    """
    _logger_manager.configure(**kwargs)


def get_logger(name=__name__, level=None):
    """
    Get a logger with the specified name.
    
    Args:
        name: Name of the logger (default: __name__)
        level: Optional level for this specific logger
        
    Returns:
        Configured logger instance
    """
    return _logger_manager.get_logger(name, level)


class StructuredLogger:
    """Wrapper class for structured logging with additional context."""

    def __init__(self, name: str = __name__):
        self._logger = get_logger(name)

    def debug(self, message: str, **kwargs):
        """Log a debug message with structured context."""
        # Avoid conflicts with reserved log record attributes
        safe_kwargs = {k: v for k, v in kwargs.items() if
                       k not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                                 'filename', 'module', 'lineno', 'funcName', 'created',
                                 'msecs', 'relativeCreated', 'thread', 'threadName',
                                 'processName', 'process', 'getMessage', 'shortpath']}
        self._logger.debug(message, extra=safe_kwargs)

    def info(self, message: str, **kwargs):
        """Log an info message with structured context."""
        # Avoid conflicts with reserved log record attributes
        safe_kwargs = {k: v for k, v in kwargs.items() if
                       k not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                                 'filename', 'module', 'lineno', 'funcName', 'created',
                                 'msecs', 'relativeCreated', 'thread', 'threadName',
                                 'processName', 'process', 'getMessage', 'shortpath']}
        self._logger.info(message, extra=safe_kwargs)

    def warning(self, message: str, **kwargs):
        """Log a warning message with structured context."""
        # Avoid conflicts with reserved log record attributes
        safe_kwargs = {k: v for k, v in kwargs.items() if
                       k not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                                 'filename', 'module', 'lineno', 'funcName', 'created',
                                 'msecs', 'relativeCreated', 'thread', 'threadName',
                                 'processName', 'process', 'getMessage', 'shortpath']}
        self._logger.warning(message, extra=safe_kwargs)

    def error(self, message: str, **kwargs):
        """Log an error message with structured context."""
        # Avoid conflicts with reserved log record attributes
        safe_kwargs = {k: v for k, v in kwargs.items() if
                       k not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                                 'filename', 'module', 'lineno', 'funcName', 'created',
                                 'msecs', 'relativeCreated', 'thread', 'threadName',
                                 'processName', 'process', 'getMessage', 'shortpath']}
        self._logger.error(message, extra=safe_kwargs)

    def critical(self, message: str, **kwargs):
        """Log a critical message with structured context."""
        # Avoid conflicts with reserved log record attributes
        safe_kwargs = {k: v for k, v in kwargs.items() if
                       k not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                                 'filename', 'module', 'lineno', 'funcName', 'created',
                                 'msecs', 'relativeCreated', 'thread', 'threadName',
                                 'processName', 'process', 'getMessage', 'shortpath']}
        self._logger.critical(message, extra=safe_kwargs)

    def log_exception(self, message: str = "An exception occurred", **kwargs):
        """Log an exception with structured context."""
        # Avoid conflicts with reserved log record attributes
        safe_kwargs = {k: v for k, v in kwargs.items() if
                       k not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                                 'filename', 'module', 'lineno', 'funcName', 'created',
                                 'msecs', 'relativeCreated', 'thread', 'threadName',
                                 'processName', 'process', 'getMessage', 'shortpath']}
        self._logger.exception(message, extra=safe_kwargs)


def get_structured_logger(name: str = __name__) -> StructuredLogger:
    """
    Get a structured logger with additional context capabilities.
    
    Args:
        name: Name of the logger (default: __name__)
        
    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name)


# Convenience functions for different log levels
info = lambda name=__name__: get_logger(name).info
warning = lambda name=__name__: get_logger(name).warning
error = lambda name=__name__: get_logger(name).error
debug = lambda name=__name__: get_logger(name).debug
critical = lambda name=__name__: get_logger(name).critical

if __name__ == "__main__":
    # Configure with enterprise settings
    configure_logging(
        level=logging.DEBUG,
        console=True,
        file_logging=True,
        colored_output=True,
        structured_output=False  # Set to True to see structured output
    )

    # Test the logger
    logger = get_logger(__name__)
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")

    # Test with different logger names
    module_logger = get_logger("my_module")
    module_logger.info("Info from a different module logger")

    print("\n--- Testing Structured Logging ---")

    # Configure for JSON output
    configure_logging(
        level=logging.DEBUG,
        console=True,
        file_logging=True,
        json_output=True
    )

    structured_logger = get_structured_logger("structured_test")
    structured_logger.info("Structured info message", user_id=123, action="login", ip="192.168.1.1")
    structured_logger.error("Structured error message", error_code=500, module_name="auth", trace_id="abc123")

    print("\nLogging test completed. Check the logs/application.log file for file output.")

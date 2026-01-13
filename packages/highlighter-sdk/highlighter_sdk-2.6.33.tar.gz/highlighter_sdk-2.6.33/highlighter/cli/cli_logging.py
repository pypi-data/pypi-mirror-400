import logging
import os
import re
import sys
import tempfile
from logging.handlers import RotatingFileHandler
from typing import Optional

from aiko_services.main.utilities.logger import (
    _LOG_FORMAT_DATETIME,
    _LOG_FORMAT_DEFAULT,
)

__all__ = ["configure_root_logger", "TRACE", "VERBOSE", "COLOURS", "format_stream_info", "format_timing"]


# ----- Define extra levels -----
TRACE = 5
VERBOSE = 8

logging.addLevelName(TRACE, "TRACE")
logging.addLevelName(VERBOSE, "VERBOSE")


# Add convenience methods to Logger class
def _trace(self, message, *args, **kwargs):
    if self.isEnabledFor(TRACE):
        self._log(TRACE, message, args, **kwargs)


def _verbose(self, message, *args, **kwargs):
    if self.isEnabledFor(VERBOSE):
        self._log(VERBOSE, message, args, **kwargs)


logging.Logger.trace = _trace
logging.Logger.verbose = _verbose

# Terse log format - compact and easy to read
# Format: MM-DD HH:MM:SS [LVL] module:line message
TERSE_LOG_FORMAT = "%(asctime)s [%(levelname).3s] %(message)s   |> %(name)s#%(funcName)s:%(lineno)d"

# More verbose debug format for deep debugging
DEBUG_LOG_FORMAT = "%(asctime)s.%(msecs)03d %(levelname)-8s %(threadName)s %(message)s   |> %(name)s#%(funcName)s:%(lineno)-6d"

RESET = "\033[0m"

# Named colors for manual use via extra={"color": "red"}
COLOURS = {
    "grey": "\033[90m",
    "light_grey": "\033[37m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[97m",
    "bold": "\033[1m",
}

# Color map for each log level
# INFO uses standard color, lower levels use dimmer colors, higher levels use bright colors
COLOUR_MAP = {
    TRACE: "\033[90m",  # grey (dimmest)
    VERBOSE: "\033[37m",  # light grey
    logging.DEBUG: "\033[36m",  # cyan (light)
    logging.INFO: None,  # standard/no color
    logging.WARNING: "\033[33m",  # yellow
    logging.ERROR: "\033[31m",  # red
    logging.CRITICAL: "\033[41m",  # red background
}


class ColourFormatter(logging.Formatter):
    """Formatter that adds colors based on log level or custom color attribute.

    Supports multiple modes:
    1. Automatic level-based coloring (default)
    2. Manual color override via extra parameter:
       logger.info("message", extra={"color": "red"})
    3. Stream info formatting via extra parameters:
       logger.info("message", extra={"stream_id": "7", "capability_name": "VideoDataSource"})
    """

    def format(self, record):
        # Add stream info prefix if provided via extra
        stream_id = getattr(record, "stream_id", None)
        capability_name = getattr(record, "capability_name", None)
        frame_id = getattr(record, "frame_id", None)

        if stream_id is not None:
            stream_prefix = format_stream_info(stream_id, capability_name, frame_id)
            # Store original message and prepend stream info
            original_msg = record.getMessage()
            record.msg = f"{stream_prefix}: {original_msg}"
            record.args = ()  # Clear args since we've already formatted the message

        msg = super().format(record)

        # Color the tail (module.function:line) in grey
        tail = f"|> {record.name}#{record.funcName}:{record.lineno}"
        coloured_tail = f"{COLOURS['grey']}{tail}{RESET}"
        msg = msg.replace(tail, coloured_tail)

        # Check for manual color override first
        color = getattr(record, "color", None)
        if color and color in COLOURS:
            return f"{COLOURS[color]}{msg}{RESET}"

        # Fall back to level-based colors for console output
        color_code = COLOUR_MAP.get(record.levelno)
        if color_code:
            return f"{color_code}{msg}{RESET}"

        return msg


class TerseNameFilter(logging.Filter):
    """Remove redundant 'highlighter.' prefix from logger names."""

    def filter(self, record):
        if record.name.startswith("highlighter."):
            record.name = record.name[12:]  # Remove "highlighter." prefix
        return True


def is_running_under_pytest():
    """Check if we're actually running under pytest (not just if pytest is installed)"""
    # More robust check: look for PYTEST_CURRENT_TEST environment variable
    # which is only set when actually running tests
    return os.getenv("PYTEST_CURRENT_TEST") is not None


def configure_root_logger(
    _log_path: Optional[str] = None,
    _log_level: Optional[str] = None,
    _log_rotation_max_kilobytes: Optional[int] = None,
    _log_rotation_backup_count: Optional[int] = None,
):
    """Configure the root logger with file and stream handlers.

    Supports HL_LOG_LEVEL environment variable:
    - HL_LOG_LEVEL: Set specific log level (TRACE, VERBOSE, DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Args:
        _log_path: Optional path for log file
        _log_level: Optional explicit log level (overrides environment variable)
        _log_rotation_max_kilobytes: Optional max size for log rotation
        _log_rotation_backup_count: Optional number of backup files
    """
    if _log_path is None:
        temp_file = tempfile.NamedTemporaryFile(suffix=".log", delete=False)
        _log_path = temp_file.name
        temp_file.close()

    # Only check environment variables if _log_level wasn't explicitly passed
    if _log_level is None:
        _log_level = os.getenv("HL_LOG_LEVEL", "WARNING")

    # Set defaults for log rotation parameters
    if _log_rotation_max_kilobytes is None:
        _log_rotation_max_kilobytes = 100 * 1024  # 100 MB in KB
    if _log_rotation_backup_count is None:
        _log_rotation_backup_count = 4

    root = logging.getLogger()
    if root.hasHandlers():
        for handler in root.handlers:
            handler.close()
        root.handlers.clear()

    # Use terse format by default, DEBUG format only for DEBUG level
    log_format = DEBUG_LOG_FORMAT if _log_level == "DEBUG" else TERSE_LOG_FORMAT
    datefmt = "%m-%d %H:%M:%S" if _log_level != "DEBUG" else _LOG_FORMAT_DATETIME

    # Use colored formatter for console output
    color_formatter = ColourFormatter(log_format, datefmt=datefmt)

    # Use plain formatter for file output
    plain_formatter = logging.Formatter(log_format, datefmt=datefmt)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(color_formatter)
    stream_handler.addFilter(TerseNameFilter())  # Strip "highlighter." prefix

    handlers = [stream_handler]

    log_level_mapping = {
        "TRACE": TRACE,
        "VERBOSE": VERBOSE,
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    log_level = log_level_mapping.get(_log_level)
    if log_level is None:
        raise SystemExit(f"Invalid log_level '{_log_level}'")

    if not is_running_under_pytest():
        # Ensure log_path exists
        directory = os.path.dirname(_log_path)
        os.makedirs(directory, exist_ok=True)

        if not os.path.exists(_log_path):
            with open(_log_path, "w") as file:
                file.write("")  # Creates an empty file

        # Setup File Handler
        file_handler = RotatingFileHandler(
            _log_path,
            maxBytes=_log_rotation_max_kilobytes * 1024,  # Convert KB to bytes
            backupCount=_log_rotation_backup_count,
        )
        file_handler.setFormatter(plain_formatter)
        file_handler.addFilter(TerseNameFilter())  # Strip "highlighter." prefix

        handlers.append(file_handler)
    logging.basicConfig(handlers=handlers)
    # Set the log level for highlighter code
    logging.getLogger("highlighter").setLevel(log_level)
    logging.getLogger(__name__).info(f"log_path: {_log_path}")

    for module_path, module_log_level in get_log_level_env_vars().items():
        logging.getLogger(module_path).setLevel(module_log_level)
        logging.getLogger(__name__).info(f"Set log level for {module_path} to {module_log_level}")


def get_log_level_env_vars():
    """Lookup log-level directives from environment variables
    matching the pattern:
        LOG_LEVEL_module_DOT_path_DOT_segment=INFO
    into {"module.path.segment": "INFO"}
    """
    pattern = re.compile(r"^LOG_LEVEL_(.*)$")
    results = {}
    for key, value in os.environ.items():
        match = pattern.match(key)
        if match:
            # Replace all "_DOT_" with "." in the matched part
            dotted_path = match.group(1).replace("_DOT_", ".")
            results[dotted_path] = value
    return results


class ColourStr:
    HEADER = "\033[95m"

    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"

    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    RESET = "\033[0m"

    @staticmethod
    def blue(s):
        return ColourStr.BLUE + s + ColourStr.RESET

    @staticmethod
    def cyan(s):
        return ColourStr.CYAN + s + ColourStr.RESET

    @staticmethod
    def green(s):
        return ColourStr.GREEN + s + ColourStr.RESET

    @staticmethod
    def red(s):
        return ColourStr.RED + s + ColourStr.RESET

    @staticmethod
    def yellow(s):
        return ColourStr.YELLOW + s + ColourStr.RESET

    @staticmethod
    def bold(s):
        return ColourStr.BOLD + s + ColourStr.RESET

    @staticmethod
    def underline(s):
        return ColourStr.UNDERLINE + s + ColourStr.RESET


def format_stream_info(stream_id, capability_name=None, frame_id=None):
    """Format stream information with consistent colors.

    Args:
        stream_id: Stream identifier (string or number)
        capability_name: Optional capability name
        frame_id: Optional frame identifier

    Returns:
        Formatted string with colors: "<Stream <id>:<frame_id>| Capability>"

    Example:
        format_stream_info("7", "VideoDataSource", "23")
        # Returns colored: "<Stream 7:23| VideoDataSource>"
    """
    stream_id_str = str(stream_id) if stream_id is not None else "unknown"

    # Add frame_id if provided
    if frame_id is not None:
        stream_id_str = f"{stream_id_str}:{frame_id}"

    # Color stream ID in cyan
    colored_stream = f"<{COLOURS['cyan']}Stream {stream_id_str}{RESET}|"

    if capability_name:
        # Color capability name in magenta
        colored_cap = f"{COLOURS['magenta']}{capability_name}{RESET}>"
        return f"{colored_stream} {colored_cap}"

    return colored_stream


def format_timing(label, seconds, unit="s", color_threshold=None):
    """Format timing information with consistent colors.

    Args:
        label: Label for the timing (e.g., "S3", "upload", "save_local")
        seconds: Time in seconds
        unit: Unit to display (default: "s" for seconds)
        color_threshold: Optional dict with thresholds {"fast": 1.0, "slow": 5.0}
                        Values under "fast" are green, over "slow" are yellow

    Returns:
        Formatted string with colors: "label: X.XXs"

    Example:
        format_timing("upload", 2.5, color_threshold={"fast": 1.0, "slow": 5.0})
        # Returns colored: "upload: 2.5s" (in yellow if >5s, green if <1s, default otherwise)
    """
    # Choose color based on threshold if provided
    if color_threshold:
        if seconds < color_threshold.get("fast", float("inf")):
            color = COLOURS["green"]
        elif seconds > color_threshold.get("slow", float("inf")):
            color = COLOURS["yellow"]
        else:
            color = ""
    else:
        color = ""

    # Format the timing value
    if unit == "s":
        value_str = f"{seconds:.3f}{unit}"
    else:
        value_str = f"{seconds:.1f}{unit}"

    if color:
        return f"{label}: {color}{value_str}{RESET}"
    else:
        return f"{label}: {value_str}"

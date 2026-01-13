import sys
import os
import traceback

from datetime import datetime
from typing import Tuple, Optional, Union

from enum import Enum, unique
from pathlib import Path


DEVELOPER_MODE=True #originally in thread flags - it is here because of packaging - maybe rename locally to PACKAGING_MODE
MESSAGE_CATEGORIES=["*"]

if DEVELOPER_MODE:
    from configparser import ConfigParser

#from src.function_handlers.abstract_function_handler import AbstractFunctionHandler #NO! Antipattern! Circular import!


if DEVELOPER_MODE:
    # instantiate
    config = ConfigParser()
    config.optionxform = str

    # parse existing file
    config.read(Path('config/flog_config.ini'))

    try:
        output_stream = config.get("LOGGER", "Output stream")
        if output_stream == "file":
            if not os.path.exists('../logs'):
                os.makedirs('../logs')
    
            OUTPUT = open("../logs/flog.out", "a+")
        else:
            OUTPUT = sys.stdout
    except Exception as e:
        print("forloop_modules.flog: Warning: Output stream couldn't be defined - ignoring ",e)
        OUTPUT = sys.stdout
else:
    OUTPUT = sys.stdout


@unique
class LogColor(Enum):
    """
    Helper class for coloring log output
    """
    OKGREEN = '\033[92m'
    ERROR = '\033[31m'
    WARNING = '\033[93m'
    BOLD = '\033[1m'
    COLOROFF = '\033[0m'


# Logging enum
# Constants reproducing logging look-a-like syntax
@unique
class FlogLevel(Enum):
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    MINORINFO = 15
    DEBUG = 10
    NOTSET = 0


# Logging levels for specific classes, logs with values higher than config are printed
# If class name is not found, parent class may be used, otherwise DEFAULT config is sed
FLOG_CONFIG = {
    "DEFAULT": FlogLevel.WARNING,
    "Wizard": FlogLevel.INFO,
    "Scanner": FlogLevel.INFO,
    "CleaningUtility": FlogLevel.INFO,
    "DfToListHandler": FlogLevel.DEBUG
}

if DEVELOPER_MODE:
    # update FLOG_CONFIG with config.ini settings
    try:
        ini_flog_config = dict(config.items("LOGGER.FLOG_CONFIG"))
        for key, value in ini_flog_config.items():
            FLOG_CONFIG[key] = eval(f"FlogLevel.{value}")
            
    except Exception as e:
        print("forloop_modules.flog: Warning: FLOG_CONFIG wasn't redefined - ignoring ",e)
        


class EmptyClass:
    """
    Dummy class with empty name for flogger calls from outside of any class
    """

    def __init__(self):
        self.__class__.__name__ = ""


def augment_message(message: str, color: LogColor, header: str = "") -> str:
    message = f"{header}{message}"
    if OUTPUT == sys.stdout:
        message = f'{color.value}{message}{LogColor.COLOROFF.value}'
    return message


def get_class_name_config_key_pair(class_instance: object) -> Tuple[str, str]:
    """
    Helper function to get class name and corresponding key in flog config dictionary
    Corresponding key may be class' name, class' parent name or 'DEFAULT'

    :param class_instance: class from which logger was called
    :return: class name and corresponding key in flog config dictionary
    :rtype: str, str
    """
    cls_name = type(class_instance).__name__
    flog_config_key = "DEFAULT"
    if cls_name in FLOG_CONFIG:
        flog_config_key = cls_name

    if flog_config_key == "DEFAULT":
        ancestor_cls_name = type(class_instance.__class__.__bases__[0]).__name__
        if ancestor_cls_name in FLOG_CONFIG:
            flog_config_key = ancestor_cls_name

    return cls_name, flog_config_key


def get_cls_loglevel(class_name: str) -> int:
    """
    Get minimum log level for specified class

    :param class_name: flog config key corresponding to log calling class, empty if called outside of class
    :type class_name: str
    :return: Minimum log level is the minimum the flogger is allowed to output
    :rtype: int
    """
    log_level = FLOG_CONFIG[class_name].value

    return log_level


def get_callers_class_instance():
    # return instance of a class that flog has been called from
    # sys._getframe(2) returns fourth frame from stack (get_callers_class_instance - error - {caller}
    try:
        class_instance = sys._getframe(2).f_locals["self"]
    except KeyError:
        class_instance = EmptyClass()

    return class_instance


def wrap_add_class_name(func):
    # automatically add class instance to flogger method call
    def add_class_name(message: str, class_instance=None, message_category = "*"):
        if class_instance is None:
            class_instance = get_callers_class_instance()

        return func(message, class_instance, message_category = message_category)
    return add_class_name


def is_error_raised():
    _, exc_value, _ = sys.exc_info()
    return exc_value is not None

def print_exception_if_raised():
    if is_error_raised():
        traceback.print_exc()


class FlogLogger:
    """
    Static logger class that provides logging functionality with runtime-configurable log levels.
    All logging methods delegate to this class instance.
    """
    
    _instance = None
    _runtime_log_level: Optional[FlogLevel] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FlogLogger, cls).__new__(cls)
        return cls._instance
    
    def set_log_level(self, level: Union[FlogLevel, str], class_name: Optional[str] = None):
        """
        Set the log level at runtime.
        
        :param level: The FlogLevel enum or string (case-insensitive) to set. 
                      Valid strings: "debug", "minorinfo", "info", "warning", "error", "critical", "notset"
        :param class_name: Optional class name to set level for specific class. If None, sets DEFAULT level.
        :raises ValueError: If the provided level string doesn't match any valid log level.
        """
        # Convert string to FlogLevel if needed
        if isinstance(level, str):
            level_str = level  # Keep original for error message
            level_upper = level.upper()
            try:
                level = FlogLevel[level_upper]
            except KeyError:
                valid_levels = ", ".join([lev.name.lower() for lev in FlogLevel])
                raise ValueError(
                    f"Invalid log level '{level_str}'. Valid levels are: {valid_levels}"
                )
        
        if class_name is None:
            class_name = "DEFAULT"
        FLOG_CONFIG[class_name] = level
        self._runtime_log_level = level
    
    def get_log_level(self, class_name: Optional[str] = None) -> FlogLevel:
        """
        Get the current log level.
        
        :param class_name: Optional class name to get level for. If None, returns DEFAULT level.
        :return: The current FlogLevel
        """
        if class_name is None:
            class_name = "DEFAULT"
        return FLOG_CONFIG.get(class_name, FlogLevel.WARNING)
    
    def _flog(self, message: str, class_name: str, color: LogColor = LogColor.COLOROFF, message_category="*"):
        """
        Internal method to print a specified message prepended with datetime and class name
        
        When thread_flags.DEVELOPER_MODE == False ==> DISABLED! (colored printing disrupts packaged versions)
        """
        if DEVELOPER_MODE:
            header = f"{datetime.now().strftime('%H:%M:%S')} "
            if class_name:
                header += f"{class_name}: "
                
            colored_message = augment_message(message, color, header)
            if message_category in MESSAGE_CATEGORIES:
                print(colored_message, file=OUTPUT)
    
    @wrap_add_class_name
    def critical(self, message="", class_instance: object = EmptyClass(), message_category="*"):
        """print red colored critical message"""
        message = str(message)
        class_name, class_flog_config_key = get_class_name_config_key_pair(class_instance)
        cls_min_log_level = get_cls_loglevel(class_flog_config_key)
        
        if cls_min_log_level <= FlogLevel.CRITICAL.value:
            if is_error_raised():
                traceback.print_exc()
            self._flog(message, class_name, color=LogColor.ERROR, message_category=message_category)
    
    @wrap_add_class_name
    def error(self, message="", class_instance: object = EmptyClass(), message_category="*"):
        """print red colored error message"""
        message = str(message)
        class_name, class_flog_config_key = get_class_name_config_key_pair(class_instance)
        cls_min_log_level = get_cls_loglevel(class_flog_config_key)
        
        if cls_min_log_level <= FlogLevel.ERROR.value:
            if is_error_raised():
                traceback.print_exc()
            self._flog(message, class_name, color=LogColor.ERROR, message_category=message_category)
    
    @wrap_add_class_name
    def warning(self, message="", class_instance: object = EmptyClass(), message_category="*"):
        """print yellow colored warning message"""
        message = str(message)
        class_name, class_flog_config_key = get_class_name_config_key_pair(class_instance)
        cls_min_log_level = get_cls_loglevel(class_flog_config_key)
        
        if cls_min_log_level <= FlogLevel.WARNING.value:
            self._flog(message, class_name, color=LogColor.WARNING, message_category=message_category)
    
    @wrap_add_class_name
    def info(self, message="", class_instance: object = EmptyClass(), message_category="*"):
        """print info message"""
        message = str(message)
        class_name, class_flog_config_key = get_class_name_config_key_pair(class_instance)
        cls_min_log_level = get_cls_loglevel(class_flog_config_key)
        
        if cls_min_log_level <= FlogLevel.INFO.value:
            self._flog(message, class_name, message_category=message_category)
    
    @wrap_add_class_name
    def minor_info(self, message="", class_instance: object = EmptyClass(), message_category="*"):
        """print minor_info message"""
        message = str(message)
        class_name, class_flog_config_key = get_class_name_config_key_pair(class_instance)
        cls_min_log_level = get_cls_loglevel(class_flog_config_key)
        
        if cls_min_log_level <= FlogLevel.MINORINFO.value:
            self._flog(message, class_name, message_category=message_category)
    
    @wrap_add_class_name
    def debug(self, message="", class_instance: object = EmptyClass(), message_category="*"):
        """print debug message"""
        message = str(message)
        class_name, class_flog_config_key = get_class_name_config_key_pair(class_instance)
        cls_min_log_level = get_cls_loglevel(class_flog_config_key)
        
        if cls_min_log_level <= FlogLevel.DEBUG.value:
            self._flog(message, class_name, message_category=message_category)
    
    def help(self):
        """Display help information about using flog"""
        help_text = """
FLOG - Logging Help Guide

For detailed documentation, please see the README.md file in the flog_pkg directory.

Quick Reference:
    Import:        import forloop_modules.flog as flog
    Basic usage:   flog.info("message"), flog.error("message"), etc.
    Log levels:    DEBUG, MINORINFO, INFO, WARNING, ERROR, CRITICAL
    Set level:     flog.logger.set_log_level(flog.FlogLevel.DEBUG)
    Get level:     flog.logger.get_log_level()
    Help:          flog.help() or see README.md
"""
        print(help_text)


# Create singleton instance
_logger = FlogLogger()

# Module-level functions that delegate to the static class instance
# This maintains backward compatibility with existing code
def critical(message="", class_instance: object = EmptyClass(), message_category="*"):
    """print red colored critical message"""
    _logger.critical(message, class_instance, message_category)

def error(message="", class_instance: object = EmptyClass(), message_category="*"):
    """print red colored error message"""
    _logger.error(message, class_instance, message_category)

def warning(message="", class_instance: object = EmptyClass(), message_category="*"):
    """print yellow colored warning message"""
    _logger.warning(message, class_instance, message_category)

def info(message="", class_instance: object = EmptyClass(), message_category="*"):
    """print info message"""
    _logger.info(message, class_instance, message_category)

def minor_info(message="", class_instance: object = EmptyClass(), message_category="*"):
    """print minor_info message"""
    _logger.minor_info(message, class_instance, message_category)

def debug(message="", class_instance: object = EmptyClass(), message_category="*"):
    """print debug message"""
    _logger.debug(message, class_instance, message_category)

def flog(message: str, class_name: str, color: LogColor = LogColor.COLOROFF, message_category="*"):
    """
    print a specified message prepended with datetime and class name(or empty string in case of EmptyClass)
    
    When thread_flags.DEVELOPER_MODE == False ==> DISABLED! (colored printing disrupts packaged versions)
    """
    _logger._flog(message, class_name, color, message_category)

def help():
    """
    Display help information about using flog.
    This is a convenience function that calls logger.help()
    """
    _logger.help()


if __name__ == '__main__':
    debug(message="debug test: you should not see this")
    minor_info(message="minor_info test: you should not see this")
    info(message="info test")
    warning(message="warning test")
    error(message="error test")
    critical(message="critical test")
    
    # Test runtime log level setting
    _logger.set_log_level(FlogLevel.MINORINFO)
    debug(message="debug test: you should not see this")
    minor_info(message="minor_info test: you should see this")
    
    _logger.set_log_level(FlogLevel.DEBUG)
    debug(message="debug test - you should see this")
    minor_info(message="minor_info test - you should see this")
    
    class Test:
        def __init__(self):
            info("testing info logging from class Test")
    
    Test()

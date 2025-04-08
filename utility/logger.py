import logging
import sys
import time
import os
from enum import Enum

from .variables import *


class AnsiColor(Enum):
    NONE = 0,

    # Foreground Colors
    FG_BLACK = 30
    FG_RED = 31
    FG_GREEN = 32
    FG_YELLOW = 33
    FG_BLUE = 34
    FG_MAGENTA = 35
    FG_CYAN = 36
    FG_WHITE = 37
    FG_DEFAULT = 39


# Root logger so we can use it while it's technically not registered.
root_logger = logging.getLogger('ciscripts')

_level_name_length = 5
_channel_name_length = 8

# A list of all logging channels currently setup
_registered_loggers_names: list[str] = []
_registered_loggers: list[logging.Logger] = []


class ColoredFormatter(logging.Formatter):
    format_str = f'[%(levelname)-{_level_name_length}s] [%(name)-{_channel_name_length}s] %(message)s'

    colors = {
        logging.INFO: AnsiColor.FG_CYAN,
        logging.DEBUG: AnsiColor.FG_BLUE,
        logging.WARNING: AnsiColor.FG_YELLOW,
        logging.ERROR: AnsiColor.FG_RED,
        logging.CRITICAL: AnsiColor.FG_RED,
        logging.FATAL: AnsiColor.FG_RED
    }

    @staticmethod
    def _clr_fmt(msg, color: AnsiColor) -> str:
        return f'\033[0;{str(color.value)}m{msg}\033[0m'

    def format(self, record):
        if len(record.name) > _channel_name_length:
            record.name = record.name[:_channel_name_length]

        if len(record.levelname) > _level_name_length:
            record.levelname = record.levelname[:_level_name_length]

        clr_str = self._clr_fmt(self.format_str, color=self.colors.get(record.levelno))
        formatter = logging.Formatter(clr_str)
        return formatter.format(record)


def register_logger(name: str) -> logging.Logger:
    """
    Gets the specified logger and adds our custom formatter and stream handler to it
    Returns the updated logger

    NOTE: This should only be done once, if you wish to get the logger after it has already been made you can do:
    logging.getLogger(name). Doing setup_logger multiple tiimes on the same name will cause duplicate messages to
    appear in the console.
    """
    if name in _registered_loggers_names:
        raise Exception(f'Tried to register {name} logger, however logger was already registered. Please use logger.getLogger(\'{name}\')instead!.')

    root_logger.debug(f'Registering logger: {name}')

    logger = logging.getLogger(name)

    # Set the default level to be INFO
    logger.setLevel(logging.INFO)

    # Add handler
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    sh.setFormatter(ColoredFormatter())
    logger.addHandler(sh)

    # Keep a note that this logger was already registered.
    _registered_loggers_names.append(name)
    _registered_loggers.append(logger)

    return logger


def set_logging_level(level):
    if is_ci() and level == logging.DEBUG:
        if ciscripts_force_allow_debug():
            root_logger.warning('CISCRIPTS_FORCE_ALLOW_DEBUG specified! Allowing debug prints while in CI mode. '
                                'Please be aware this may expose secrets in log files.')
        else:
            root_logger.error('Cannot set DEBUG on CI machines! Secrets such as passwords may be shown. Which is BAD!!')
            return

    for logger in _registered_loggers:
        logger.setLevel(level)
        logger.handlers[0].setLevel(level)


def gl_open_block(section_name: str, section_header: str):
    """
    Defines the start of a collapsible section in GitLab CI job outputs
    """
    print(f'\033[0Ksection_start:{int(time.time())}:{section_name}\r\033[0K{section_header}', flush=True)


def gl_close_block(section_name: str):
    """
    Defines the end of a collapsable section in GitLab CI job outputs
    """
    print(f'\033[0Ksection_end:{int(time.time())}:{section_name}\r\033[0K', flush=True)

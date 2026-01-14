#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Global logging configuration."""

from __future__ import annotations

import logging
from typing import Optional

import pygelf

from egos_helpers.constants import NAME

_LOG_LEVELS = {
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
    "FATAL",
    "NOTSET",
}


def _normalize_level(level: Optional[str]) -> str:
    """Return a valid, normalized log level name."""
    if not level:
        level = "INFO"
    level = level.upper()
    if level not in _LOG_LEVELS:
        level = "INFO"
    return level


def setup_logger(
    name: str,
    level: Optional[str] = "INFO",
    gelf_host: Optional[str] = None,
    gelf_port: Optional[int] = None,
    configure_egos: bool = True,
    **kwargs: object,
) -> logging.Logger:
    """
    Set up and return a logger.

    The logger is configured with a stream handler using the formatter from
    :py:func:`get_formatter()`. Existing handlers on the named logger are
    removed and propagation to the root logger is disabled.

    If ``gelf_host`` and ``gelf_port`` are provided, a GELF UDP handler is
    added. Any extra keyword arguments are passed to
    :class:`pygelf.GelfUdpHandler`.

    When ``configure_egos`` is True, the ``ix-notifiers`` and
    :data:`egos_helpers.constants.NAME` loggers are configured in the same
    way (stream handler, cleared handlers, disabled propagation).

    :param name: The name of the logger to initialize.
    :param level: The logging level name (case-insensitive), defaults to 'INFO'.
    :param gelf_host: The FQDN of the GELF host, defaults to None.
    :param gelf_port: The port for the GELF host, defaults to None.
    :param configure_egos:
        Set to False if you do not want the egos libraries to also log;
        defaults to True.
    :return: A configured :class:`logging.Logger` instance.
    """
    level = _normalize_level(level)
    numeric_level = logging.getLevelName(level)

    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.setLevel(numeric_level)
    logger.propagate = False

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(get_formatter(level))
    logger.addHandler(stream_handler)

    if gelf_host and gelf_port:
        gelf_handler = pygelf.GelfUdpHandler(
            host=gelf_host,
            port=gelf_port,
            debug=True,
            include_extra_fields=True,
            **kwargs,
        )
        logger.addHandler(gelf_handler)

    if configure_egos:
        for logger_name in ("ix-notifiers", NAME):
            eg_logger = logging.getLogger(logger_name)
            eg_logger.handlers.clear()
            eg_logger.setLevel(numeric_level)
            eg_logger.propagate = False

            eg_handler = logging.StreamHandler()
            eg_handler.setFormatter(get_formatter(level))
            eg_logger.addHandler(eg_handler)

    return logger


def get_formatter(level: Optional[str] = "INFO") -> logging.Formatter:
    """
    Generate a formatter for log records.

    The generated formatter will include the module, line number and function
    name when the level is DEBUG.

    :param level: The log level name for which the formatter is created.
                  Defaults to 'INFO'.
    :return: A configured :class:`logging.Formatter` instance.
    """
    level = _normalize_level(level)

    fmt = "%(asctime)s.%(msecs)03d %(levelname)s [%(name)s"

    if level == "DEBUG":
        fmt += " %(module)s:%(lineno)d %(funcName)s"

    fmt += "] %(message)s"

    return logging.Formatter(fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S")

# hydra_router/constants/DHydra.py
#
#   Hydra Router
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2025-2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/hydra_router
#    Website: https://hydra-router.readthedocs.io/en/latest
#    License: GPL 3.0

import logging
from typing import Dict


# Project globals
class DHydra:
    """
    Global project constants and version information.

    Contains the current version string and other project-wide constants
    used throughout the HydraRouter package.
    """

    VERSION: str = "0.12.23"


# HydraServer defaults
class DHydraServerDef:
    """
    Default configuration values for HydraServer instances.

    Provides standard hostname and port values used when no explicit
    configuration is provided during server initialization.
    """

    HOSTNAME: str = "localhost"
    PORT: int = 5757


# HydraClient messages
class DHydraMsg:
    """
    Message templates for HydraClient logging and user feedback.

    Contains formatted string templates with placeholders for dynamic
    values. Use .format() method to substitute actual values.
    """

    CLEANUP: str = "HydraClient cleanup complete"
    CONNECTED: str = "HydraClient connected to {server_address}"
    ERROR: str = "HydraClient error: {e}"
    PORT_HELP: str = "Server port to connect to (default: {server_port})"
    RECEIVED: str = "Received response: {response}"
    SENDING: str = "Sending request: {message}"
    SERVER_HELP: str = "Server hostname to connect to (default: {server_address})"


# HydraLog levels
class DHydraLog:
    """
    Logging level constants for HydraLog configuration.

    Defines string constants for different logging levels that map
    to Python's standard logging levels via the LOG_LEVELS dictionary.
    """

    INFO: str = "info"
    DEBUG: str = "debug"
    WARNING: str = "warning"
    ERROR: str = "error"
    CRITICAL: str = "critical"
    DEFAULT: str = "warning"


# HydraLog levels dictionary
# Mapping of HydraLog level strings to Python logging level integers.
# Used by HydraLog to convert string-based log level configuration
# to the integer values expected by Python's logging module.
LOG_LEVELS: Dict[str, int] = {
    DHydraLog.INFO: logging.INFO,
    DHydraLog.DEBUG: logging.DEBUG,
    DHydraLog.WARNING: logging.WARNING,
    DHydraLog.ERROR: logging.ERROR,
    DHydraLog.CRITICAL: logging.CRITICAL,
    DHydraLog.DEFAULT: logging.WARNING,
}


# HydraServer messages
class DHydraServerMsg:
    """
    Message templates for HydraServer logging and user feedback.

    Contains formatted string templates with placeholders for dynamic
    values. Use .format() method to substitute actual values.
    """

    ADDRESS_HELP: str = "Address to bind to (default: '*' for all interfaces)"
    BIND: str = "HydraServer bound to {bind_address}"
    CLEANUP: str = "HydraServer cleanup complete"
    ERROR: str = "HydraServer error: {e}"
    LOOP_UP: str = "HydraServer message loop on {address}:{port} is up and running"
    PORT_HELP: str = "Port to bind to (default: {port})"
    RECEIVE: str = "Received request: {message}"
    SENT: str = "Sent response: {response}"
    SHUTDOWN: str = "HydraServer shutting down..."
    STARTING: str = "Starting HydraServer on {address}:{port}"
    STOP_HELP: str = "Press Ctrl+C to stop the server"
    USER_STOP: str = "Server stopped by user"


# Hydra Router Modules
class DModule:
    """
    Module identifier constants for HydraRouter components.

    Provides standardized string identifiers for different HydraRouter
    modules, used in logging and component identification.
    """

    HYDRA_CLIENT: str = "HydraClient"
    HYDRA_SERVER: str = "HydraServer"

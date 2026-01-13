# -*- coding:utf-8 -*-
"""
XuguDB Database Driver - Platform Adapter

This module dynamically loads the appropriate xgcondb driver based on:
- Operating System (Windows, Linux, macOS)
- Architecture (x86_64, arm64)
- Python version

Platform directories:
- xgcondb-win/     - Windows (x86_64)
- xgcondb-mac/     - macOS (darwin, universal)
- xgcondb-linux-64/    - Linux x86_64
- xgcondb-linux-arm64/ - Linux ARM64
"""

import sys
import platform
import os
import importlib
import importlib.util


def _setup_shared_library_path(module_dir):
    """
    Setup shared library path for Linux/Windows platforms.

    On Linux, Python extensions may depend on external .so files (like libxugusql.so)
    that need to be found by the dynamic linker. We add the module directory to
    LD_LIBRARY_PATH before importing the module.

    On Windows, similar handling for DLL files.

    Args:
        module_dir: Absolute path to the platform-specific module directory
    """
    system = platform.system()

    if system == "Linux":
        # Get the directory containing the shared libraries
        lib_path = os.path.abspath(module_dir)

        # Add to LD_LIBRARY_PATH if not already present
        ld_library_path = os.environ.get('LD_LIBRARY_PATH', '')
        if lib_path not in ld_library_path.split(':'):
            if ld_library_path:
                os.environ['LD_LIBRARY_PATH'] = f"{lib_path}:{ld_library_path}"
            else:
                os.environ['LD_LIBRARY_PATH'] = lib_path

            # On some systems, we also need to update the process's view of the library path
            # This is done by re-initializing the dynamic linker
            try:
                import ctypes
                # Try to preload the shared library
                libxugusql_path = os.path.join(lib_path, 'libxugusql.so')
                if os.path.exists(libxugusql_path):
                    # Use RTLD_GLOBAL to make symbols available to subsequently loaded modules
                    ctypes.CDLL(libxugusql_path, mode=ctypes.RTLD_GLOBAL)
            except Exception:
                # If preloading fails, continue anyway - it might still work
                pass

    elif system == "Windows":
        # For Windows, ensure the DLL directory is in PATH
        dll_path = os.path.abspath(module_dir)
        path_env = os.environ.get('PATH', '')
        if dll_path not in path_env.split(os.pathsep):
            os.environ['PATH'] = f"{dll_path}{os.pathsep}{path_env}"


def _get_platform_module():
    """
    Determine the platform-specific xgcondb module to import.

    Returns:
        module: The platform-specific xgcondb module
    """
    system = platform.system()
    machine = platform.machine()

    # Map platform info to module name
    if system == "Windows":
        module_name = "xgcondb-win"
    elif system == "Darwin":
        # macOS (Darwin)
        module_name = "xgcondb-mac"
    elif system == "Linux":
        if machine in ("aarch64", "arm64"):
            module_name = "xgcondb-linux-arm64"
        else:
            # Default to x86_64 for Linux
            module_name = "xgcondb-linux-64"
    else:
        raise ImportError(
            f"Unsupported platform: {system} {machine}. "
            f"Please contact XuguDB support for driver availability."
        )

    # Get the directory of the platform-specific module
    try:
        # First, find the module spec to get its path
        module_spec = importlib.util.find_spec(module_name)
        if module_spec and module_spec.origin:
            module_dir = os.path.dirname(os.path.abspath(module_spec.origin))
            # Setup shared library path before importing
            _setup_shared_library_path(module_dir)
    except Exception:
        # If we can't find the module spec, continue anyway
        pass

    try:
        return importlib.import_module(module_name)
    except ImportError as e:
        raise ImportError(
            f"Failed to import XuguDB driver for {system} {machine} "
            f"(module: {module_name}). Original error: {e}"
        )


# Import platform-specific module
_platform_module = _get_platform_module()

# Export all public attributes from platform-specific module
# This includes: Connect, connect, Connection, version, constants, etc.
_connect = _platform_module._connect
version = getattr(_platform_module, 'version', 'unknown')


def Connect(**kwargs):
    """
    Create a connection to the XuguDB database.

    Parameters:
        host: Database server IP address (or comma-separated IPs for HA)
        port: Database server port (default: 5138)
        database: Database name
        user: Username (default: SYSDBA)
        password: Password
        charset: Character encoding (default: utf8)
        usessl: SSL connection setting (default: "off")

    Returns:
        Connection object
    """
    if kwargs is None:
        raise TypeError('Connection parameters are incorrect!')
    elif 'host' in kwargs and 'port' in kwargs and 'database' in kwargs and 'user' in kwargs and 'password' in kwargs:
        if kwargs['host'] is None or kwargs['port'] is None or kwargs['database'] is None or kwargs['user'] is None or \
                kwargs['password'] is None:
            raise TypeError('Connection parameters are incorrect!')

    if 'charset' not in kwargs:
        kwargs['charset'] = "utf8"
    if 'usessl' not in kwargs:
        kwargs['usessl'] = "off"

    connectionstring = ""
    for key, value in kwargs.items():
        if key == 'host':
            if ',' in value:
                connectionstring = connectionstring + "IPS=" + str(value) + ";"
            else:
                connectionstring = connectionstring + "IP=" + str(value) + ";"
        else:
            connectionstring = connectionstring + key + "=" + str(value) + ";"

    conn = _connect(connectstring=connectionstring)
    return conn


# Public API aliases
connect = Connection = Connect
paramstyle = 'qmark'
threadsafety = 2.0

# Export type constants from platform module
XG_C_NULL = 0
XG_C_BOOL = 1
XG_C_CHAR = 2
XG_C_TINYINT = 3
XG_C_SHORT = 4
XG_C_INTEGER = 5
XG_C_BIGINT = 6
XG_C_FLOAT = 7
XG_C_DOUBLE = 8
XG_C_NUMERIC = 9
XG_C_DATE = 10
XG_C_TIME = 11
XG_C_TIME_TZ = 12
XG_C_DATETIME = 13
XG_C_DATETIME_TZ = 14
XG_C_BINARY = 15
XG_C_NVARBINARY = 18
XG_C_INTERVAL = 21
DATETIME_ASLONG = 23
XG_C_INTERVAL_YEAR_TO_MONTH = 28
XG_C_INTERVAL_DAY_TO_SECOND = 31
XG_C_TIMESTAMP = 13
XG_C_LOB = 40
XG_C_CLOB = 41
XG_C_BLOB = 42
XG_C_REFCUR = 58
XG_C_NCHAR = 62
XG_C_CHARN1 = 63

__all__ = [
    "Connect",
    "connect",
    "Connection",
    "version",
    "threadsafety",
    "paramstyle",
]

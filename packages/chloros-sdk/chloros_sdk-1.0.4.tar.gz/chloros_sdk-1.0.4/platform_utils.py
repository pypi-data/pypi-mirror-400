#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Platform Utilities for Chloros
==============================

Central module for cross-platform support. Provides unified interfaces
for OS-specific operations including:
- Exiftool path discovery
- Subprocess configuration (window hiding on Windows)
- Application data directories
- Machine identification for licensing
- Backend executable discovery
- Process management

This module enables a single unified codebase to work on both
Windows and Linux (and macOS in the future).

Copyright (c) 2025 MAPIR Inc. All rights reserved.
"""

import sys
import os
import shutil
import subprocess
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

# Platform detection constants
PLATFORM = sys.platform  # 'win32', 'linux', 'darwin'
IS_WINDOWS = PLATFORM == 'win32'
IS_LINUX = PLATFORM.startswith('linux')
IS_MACOS = PLATFORM == 'darwin'

# Logger
logger = logging.getLogger(__name__)


# =============================================================================
# EXIFTOOL DISCOVERY
# =============================================================================

def get_exiftool_path() -> str:
    """
    Get the exiftool executable path for the current platform.

    On Windows:
        1. Check for bundled exiftool.exe in the same directory
        2. Check common installation paths
        3. Fall back to PATH lookup

    On Linux/macOS:
        1. Use system exiftool from PATH
        2. Check common installation paths

    Returns:
        str: Path to exiftool executable

    Raises:
        FileNotFoundError: If exiftool cannot be found
    """
    if IS_WINDOWS:
        # Check bundled exiftool.exe first (same directory as this module)
        bundled = Path(__file__).parent / 'exiftool.exe'
        if bundled.exists():
            return str(bundled)

        # Check common Windows installation paths
        windows_paths = [
            r'C:\Windows\exiftool.exe',
            r'C:\Program Files\exiftool\exiftool.exe',
            r'C:\exiftool\exiftool.exe',
        ]
        for path in windows_paths:
            if os.path.exists(path):
                return path

        # Try PATH lookup
        found = shutil.which('exiftool.exe') or shutil.which('exiftool')
        if found:
            return found

        # Last resort: return the expected bundled path (will fail at runtime)
        return str(bundled)

    else:  # Linux/macOS
        # Try PATH lookup first (most common on Linux)
        found = shutil.which('exiftool')
        if found:
            return found

        # Check common Linux paths
        linux_paths = [
            '/usr/bin/exiftool',
            '/usr/local/bin/exiftool',
            '/opt/local/bin/exiftool',  # MacPorts
        ]
        for path in linux_paths:
            if os.path.exists(path):
                return path

        # Return 'exiftool' and let it fail at runtime if not found
        return 'exiftool'


def is_exiftool_available() -> bool:
    """
    Check if exiftool is available and working.

    Returns:
        bool: True if exiftool can be executed
    """
    try:
        exiftool_path = get_exiftool_path()
        result = subprocess.run(
            [exiftool_path, '-ver'],
            capture_output=True,
            text=True,
            timeout=5,
            **get_subprocess_kwargs()
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        return False


# =============================================================================
# SUBPROCESS CONFIGURATION
# =============================================================================

def get_subprocess_kwargs() -> Dict[str, Any]:
    """
    Get platform-appropriate subprocess keyword arguments.

    On Windows, this includes STARTUPINFO to hide console windows.
    On Linux/macOS, returns an empty dict (no special handling needed).

    Returns:
        dict: Keyword arguments to pass to subprocess.run/Popen

    Example:
        >>> result = subprocess.run(cmd, **get_subprocess_kwargs())
    """
    if IS_WINDOWS:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0  # SW_HIDE
        return {'startupinfo': startupinfo}
    return {}


def get_creationflags() -> int:
    """
    Get platform-appropriate process creation flags.

    On Windows, returns CREATE_NO_WINDOW to prevent console windows.
    On Linux/macOS, returns 0.

    Returns:
        int: Creation flags for subprocess
    """
    if IS_WINDOWS:
        CREATE_NO_WINDOW = 0x08000000
        return CREATE_NO_WINDOW
    return 0


# =============================================================================
# APPLICATION DATA DIRECTORIES
# =============================================================================

def get_app_data_dir() -> Path:
    """
    Get the application data directory for the current platform.

    Windows: %LOCALAPPDATA%/Chloros or %APPDATA%/Chloros
    macOS: ~/Library/Application Support/Chloros
    Linux: $XDG_DATA_HOME/chloros or ~/.local/share/chloros

    Returns:
        Path: Application data directory (created if needed)
    """
    if IS_WINDOWS:
        base = Path(os.environ.get('LOCALAPPDATA',
                   os.environ.get('APPDATA', Path.home())))
        app_dir = base / 'Chloros'
    elif IS_MACOS:
        app_dir = Path.home() / 'Library' / 'Application Support' / 'Chloros'
    else:  # Linux
        xdg_data = os.environ.get('XDG_DATA_HOME', str(Path.home() / '.local' / 'share'))
        app_dir = Path(xdg_data) / 'chloros'

    # Ensure directory exists
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def get_config_dir() -> Path:
    """
    Get the configuration directory for the current platform.

    Windows: %APPDATA%/Chloros/config
    macOS: ~/Library/Application Support/Chloros/config
    Linux: $XDG_CONFIG_HOME/chloros or ~/.config/chloros

    Returns:
        Path: Configuration directory (created if needed)
    """
    if IS_WINDOWS:
        base = Path(os.environ.get('APPDATA', Path.home()))
        config_dir = base / 'Chloros' / 'config'
    elif IS_MACOS:
        config_dir = Path.home() / 'Library' / 'Application Support' / 'Chloros' / 'config'
    else:  # Linux
        xdg_config = os.environ.get('XDG_CONFIG_HOME', str(Path.home() / '.config'))
        config_dir = Path(xdg_config) / 'chloros'

    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_cache_dir() -> Path:
    """
    Get the cache directory for the current platform.

    Windows: %APPDATA%/Chloros/cache
    macOS: ~/Library/Caches/Chloros
    Linux: $XDG_CACHE_HOME/chloros or ~/.cache/chloros

    Returns:
        Path: Cache directory (created if needed)
    """
    if IS_WINDOWS:
        base = Path(os.environ.get('APPDATA', Path.home()))
        cache_dir = base / 'Chloros' / 'cache'
    elif IS_MACOS:
        cache_dir = Path.home() / 'Library' / 'Caches' / 'Chloros'
    else:  # Linux
        xdg_cache = os.environ.get('XDG_CACHE_HOME', str(Path.home() / '.cache'))
        cache_dir = Path(xdg_cache) / 'chloros'

    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_log_dir() -> Path:
    """
    Get the log directory for the current platform.

    Returns:
        Path: Log directory (created if needed)
    """
    if IS_WINDOWS:
        log_dir = get_app_data_dir() / 'logs'
    elif IS_MACOS:
        log_dir = Path.home() / 'Library' / 'Logs' / 'Chloros'
    else:  # Linux
        log_dir = get_cache_dir() / 'logs'

    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def get_user_projects_dir() -> Path:
    """
    Get the default user projects directory.

    Returns:
        Path: Default projects directory
    """
    return Path.home() / 'Chloros Projects'


# =============================================================================
# MACHINE IDENTIFICATION (FOR LICENSING)
# =============================================================================

def get_machine_id() -> str:
    """
    Get a unique machine identifier for licensing purposes.

    This ID must be:
    - Persistent across reboots
    - Unique per physical machine
    - Consistent across application restarts

    Windows: Uses MachineGuid from Windows Registry
    Linux: Uses /etc/machine-id (systemd standard)
    macOS: Uses hardware UUID from IOKit

    Returns:
        str: Unique machine identifier

    Raises:
        RuntimeError: If machine ID cannot be determined
    """
    if IS_WINDOWS:
        return _get_machine_id_windows()
    elif IS_MACOS:
        return _get_machine_id_macos()
    else:  # Linux
        return _get_machine_id_linux()


def _get_machine_id_windows() -> str:
    """Get machine ID from Windows Registry."""
    try:
        import winreg
        reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        key = winreg.OpenKey(reg, r"SOFTWARE\Microsoft\Cryptography")
        machine_guid, _ = winreg.QueryValueEx(key, "MachineGuid")
        winreg.CloseKey(key)
        return str(machine_guid)
    except Exception as e:
        logger.warning(f"Failed to get Windows MachineGuid: {e}")
        return _get_machine_id_fallback()


def _get_machine_id_linux() -> str:
    """
    Get machine ID from Linux system files.

    Uses /etc/machine-id which is the systemd standard.
    Falls back to /var/lib/dbus/machine-id for older systems.
    """
    # Primary: /etc/machine-id (systemd standard)
    machine_id_path = Path('/etc/machine-id')
    if machine_id_path.exists():
        try:
            machine_id = machine_id_path.read_text().strip()
            if machine_id:
                return machine_id
        except Exception as e:
            logger.warning(f"Failed to read /etc/machine-id: {e}")

    # Fallback: /var/lib/dbus/machine-id
    dbus_id_path = Path('/var/lib/dbus/machine-id')
    if dbus_id_path.exists():
        try:
            machine_id = dbus_id_path.read_text().strip()
            if machine_id:
                return machine_id
        except Exception as e:
            logger.warning(f"Failed to read dbus machine-id: {e}")

    return _get_machine_id_fallback()


def _get_machine_id_macos() -> str:
    """Get machine ID from macOS hardware UUID."""
    try:
        result = subprocess.run(
            ['ioreg', '-rd1', '-c', 'IOPlatformExpertDevice'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'IOPlatformUUID' in line:
                    # Extract UUID from line like: "IOPlatformUUID" = "..."
                    import re
                    match = re.search(r'"IOPlatformUUID"\s*=\s*"([^"]+)"', line)
                    if match:
                        return match.group(1)
    except Exception as e:
        logger.warning(f"Failed to get macOS hardware UUID: {e}")

    return _get_machine_id_fallback()


def _get_machine_id_fallback() -> str:
    """
    Fallback machine ID using MAC address.

    Less reliable than platform-specific methods but works everywhere.
    """
    import uuid
    # uuid.getnode() returns MAC address as 48-bit integer
    mac = uuid.getnode()
    # Format as hex string similar to UUIDs
    return f"{mac:012x}"


# =============================================================================
# BACKEND EXECUTABLE DISCOVERY
# =============================================================================

def get_backend_search_paths() -> List[str]:
    """
    Get platform-appropriate backend executable search paths.

    Returns paths to search for the Chloros backend executable,
    ordered from most specific to most general.

    Returns:
        List[str]: List of paths to search for backend executable
    """
    paths = []

    # Get directory containing this script (for development)
    script_dir = Path(__file__).parent

    if IS_WINDOWS:
        # Installed version paths
        paths.extend([
            r'C:\Program Files\MAPIR\Chloros\resources\backend\chloros-backend-safe.exe',
            r'C:\Program Files\MAPIR\Chloros\resources\backend\chloros-backend.exe',
            r'C:\Program Files\Chloros\resources\backend\chloros-backend-safe.exe',
            r'C:\Program Files\Chloros\resources\backend\chloros-backend.exe',
            r'C:\Program Files (x86)\MAPIR\Chloros\resources\backend\chloros-backend-safe.exe',
            r'C:\Program Files (x86)\Chloros\resources\backend\chloros-backend.exe',
        ])

        # Development paths (same directory)
        paths.extend([
            str(script_dir / 'chloros-backend-safe.exe'),
            str(script_dir / 'chloros-backend.exe'),
            str(script_dir / 'dist' / 'chloros-backend-safe.exe'),
            str(script_dir / 'dist' / 'chloros-backend.exe'),
        ])

        # Python backend for development
        paths.append(str(script_dir / 'backend_server.py'))

    else:  # Linux/macOS
        # Installed version paths
        paths.extend([
            '/usr/lib/chloros/chloros-backend',  # .deb package location
            '/opt/mapir/chloros/backend/chloros-backend',
            '/usr/local/bin/chloros-backend',
            str(Path.home() / '.local' / 'bin' / 'chloros-backend'),
        ])

        # Development paths
        paths.extend([
            str(script_dir / 'chloros-backend'),
            str(script_dir / 'dist' / 'chloros-backend'),
        ])

        # Python backend for development
        paths.append(str(script_dir / 'backend_server.py'))

    return paths


def find_backend_executable() -> Optional[str]:
    """
    Find the Chloros backend executable.

    Searches platform-appropriate locations for the backend.

    Returns:
        Optional[str]: Path to backend executable, or None if not found
    """
    for path in get_backend_search_paths():
        if os.path.exists(path):
            return path
    return None


def get_backend_executable_name() -> str:
    """
    Get the backend executable name for the current platform.

    Returns:
        str: 'chloros-backend.exe' on Windows, 'chloros-backend' on Linux/macOS
    """
    if IS_WINDOWS:
        return 'chloros-backend.exe'
    return 'chloros-backend'


# =============================================================================
# PROCESS MANAGEMENT
# =============================================================================

def kill_process_by_name(process_name: str) -> bool:
    """
    Kill a process by name in a platform-appropriate way.

    Args:
        process_name: Name of the process to kill

    Returns:
        bool: True if process was killed, False otherwise
    """
    try:
        if IS_WINDOWS:
            result = subprocess.run(
                ['taskkill', '/F', '/IM', process_name],
                capture_output=True,
                **get_subprocess_kwargs()
            )
            return result.returncode == 0
        else:
            # Try pkill first (more common)
            result = subprocess.run(
                ['pkill', '-f', process_name],
                capture_output=True
            )
            if result.returncode == 0:
                return True

            # Fallback to killall
            result = subprocess.run(
                ['killall', process_name],
                capture_output=True
            )
            return result.returncode == 0
    except Exception as e:
        logger.warning(f"Failed to kill process {process_name}: {e}")
        return False


def is_process_running(process_name: str) -> bool:
    """
    Check if a process is running by name.

    Args:
        process_name: Name of the process to check

    Returns:
        bool: True if process is running
    """
    try:
        if IS_WINDOWS:
            result = subprocess.run(
                ['tasklist', '/FI', f'IMAGENAME eq {process_name}'],
                capture_output=True,
                text=True,
                **get_subprocess_kwargs()
            )
            return process_name.lower() in result.stdout.lower()
        else:
            result = subprocess.run(
                ['pgrep', '-f', process_name],
                capture_output=True
            )
            return result.returncode == 0
    except Exception:
        return False


def get_process_using_port(port: int) -> Optional[int]:
    """
    Get the PID of the process using a specific port.

    Args:
        port: Port number to check

    Returns:
        Optional[int]: PID of process using port, or None
    """
    try:
        if IS_WINDOWS:
            result = subprocess.run(
                ['netstat', '-ano'],
                capture_output=True,
                text=True,
                **get_subprocess_kwargs()
            )
            for line in result.stdout.split('\n'):
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.split()
                    if parts:
                        return int(parts[-1])
        else:
            # Use lsof on Linux/macOS
            result = subprocess.run(
                ['lsof', '-ti', f':{port}'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                return int(result.stdout.strip().split('\n')[0])
    except Exception as e:
        logger.warning(f"Failed to get process using port {port}: {e}")

    return None


def kill_process_on_port(port: int) -> bool:
    """
    Kill the process using a specific port.

    Args:
        port: Port number

    Returns:
        bool: True if process was killed
    """
    pid = get_process_using_port(port)
    if pid:
        try:
            if IS_WINDOWS:
                result = subprocess.run(
                    ['taskkill', '/F', '/PID', str(pid)],
                    capture_output=True,
                    **get_subprocess_kwargs()
                )
            else:
                result = subprocess.run(
                    ['kill', '-9', str(pid)],
                    capture_output=True
                )
            return result.returncode == 0
        except Exception as e:
            logger.warning(f"Failed to kill PID {pid}: {e}")
    return False


# =============================================================================
# FILE DIALOGS
# =============================================================================

def open_file_dialog(
    title: str = "Select File",
    filetypes: Optional[List[tuple]] = None,
    initialdir: Optional[str] = None
) -> Optional[str]:
    """
    Open a file selection dialog.

    Uses tkinter on Linux/macOS, native dialog on Windows.

    Args:
        title: Dialog title
        filetypes: List of (description, pattern) tuples
        initialdir: Initial directory

    Returns:
        Optional[str]: Selected file path or None if cancelled
    """
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()  # Hide the main window

        if filetypes is None:
            filetypes = [("All files", "*.*")]

        file_path = filedialog.askopenfilename(
            title=title,
            filetypes=filetypes,
            initialdir=initialdir
        )

        root.destroy()
        return file_path if file_path else None

    except ImportError:
        logger.warning("tkinter not available for file dialogs")
        return None
    except Exception as e:
        logger.warning(f"File dialog failed: {e}")
        return None


def open_folder_dialog(
    title: str = "Select Folder",
    initialdir: Optional[str] = None
) -> Optional[str]:
    """
    Open a folder selection dialog.

    Args:
        title: Dialog title
        initialdir: Initial directory

    Returns:
        Optional[str]: Selected folder path or None if cancelled
    """
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()

        folder_path = filedialog.askdirectory(
            title=title,
            initialdir=initialdir
        )

        root.destroy()
        return folder_path if folder_path else None

    except ImportError:
        logger.warning("tkinter not available for folder dialogs")
        return None
    except Exception as e:
        logger.warning(f"Folder dialog failed: {e}")
        return None


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_platform_info() -> Dict[str, Any]:
    """
    Get information about the current platform.

    Returns:
        dict: Platform information including OS, architecture, etc.
    """
    import platform as plat

    return {
        'system': plat.system(),
        'release': plat.release(),
        'version': plat.version(),
        'machine': plat.machine(),
        'processor': plat.processor(),
        'python_version': plat.python_version(),
        'is_windows': IS_WINDOWS,
        'is_linux': IS_LINUX,
        'is_macos': IS_MACOS,
    }


def ensure_utf8_console():
    """
    Ensure console supports UTF-8 output.

    On Windows, sets console code page to UTF-8.
    On Linux/macOS, this is typically the default.
    """
    if IS_WINDOWS:
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleOutputCP(65001)
            kernel32.SetConsoleCP(65001)
        except Exception:
            pass  # Silently fail if we can't set UTF-8

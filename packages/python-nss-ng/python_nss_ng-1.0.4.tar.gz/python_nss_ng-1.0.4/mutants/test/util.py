# SPDX-License-Identifier: MPL-2.0
# SPDX-FileCopyrightText: Copyright (c) 2010-2025 python-nss-ng contributors

import contextlib
import os
import sys
import sysconfig
from typing import Any, Optional


def get_build_dir() -> Optional[str]:
    """
    Walk from the current directory up until a directory is found
    which contains a regular file called "meson.build" and a directory
    called "build". If found return the fully qualified path to
    the build directory's platform specific directory, this is where
    the architecture specific build produced by meson is located.

    If the build directory cannot be found in the tree None is returned.
    """
    cwd = os.getcwd()
    path_components = cwd.split(os.sep)
    while len(path_components):
        path = os.path.join(os.sep, *path_components) if path_components[0] else os.path.join(*path_components)
        meson_path = os.path.join(path, 'meson.build')
        build_path = os.path.join(path, 'build')

        # Does this directory contain the file "meson.build" and the directory "build"?
        if (os.path.exists(meson_path) and os.path.exists(build_path) and
                os.path.isfile(meson_path) and os.path.isdir(build_path)):
            # Found, return the path concatenated with the architecture
            # specific build directory

            # Get platform-specific information using sysconfig
            platform = sysconfig.get_platform()
            version = f"{sys.version_info.major}.{sys.version_info.minor}"
            platform_specifier = f"lib.{platform}-{version}"

            build_lib_dir = os.path.join(build_path, platform_specifier)

            # If the exact directory doesn't exist, try to find any lib.* directory
            if not os.path.exists(build_lib_dir):
                try:
                    for entry in os.listdir(build_path):
                        if entry.startswith('lib.'):
                            candidate = os.path.join(build_path, entry)
                            if os.path.isdir(candidate):
                                return candidate
                except OSError:
                    pass

            return build_lib_dir

        # Not found, ascend to parent directory and try again
        path_components.pop()

    # Failed to find the build directory
    return None


def insert_build_dir_into_path() -> None:
    """Insert the build directory at the beginning of sys.path."""
    build_dir = get_build_dir()
    if build_dir:
        sys.path.insert(0, build_dir)


def find_nss_tool(tool_name: str) -> str:
    """
    Find an NSS tool (certutil, modutil, pk12util, etc.) in the system.

    Tries multiple locations:
    1. /usr/bin/ (Linux/Unix default)
    2. /opt/homebrew/bin/ (macOS Apple Silicon Homebrew)
    3. /usr/local/bin/ (macOS Intel Homebrew)
    4. Search PATH environment variable

    Args:
        tool_name: Name of the tool (e.g., 'certutil', 'modutil', 'pk12util')

    Returns:
        str: Full path to the tool

    Raises:
        RuntimeError: If the tool cannot be found
    """
    import shutil

    # List of directories to check in order
    search_paths = [
        '/usr/bin',
        '/opt/homebrew/bin',  # macOS Apple Silicon Homebrew
        '/usr/local/bin',     # macOS Intel Homebrew
    ]

    # First, try common locations
    for base_dir in search_paths:
        tool_path = os.path.join(base_dir, tool_name)
        if os.path.exists(tool_path) and os.access(tool_path, os.X_OK):
            return tool_path

    # If not found in common locations, search PATH
    tool_path_from_which = shutil.which(tool_name)
    if tool_path_from_which:
        return tool_path_from_which

    # Not found anywhere
    raise RuntimeError(
        f"NSS tool '{tool_name}' not found. Please install NSS utilities.\n"
        f"  macOS: brew install nss\n"
        f"  Fedora/RHEL: dnf install nss-tools\n"
        f"  Debian/Ubuntu: apt-get install libnss3-tools"
    )


@contextlib.contextmanager
def temp_file_with_data(data: bytes) -> Any:
    """
    Context manager for creating a temporary file with data.

    The file is automatically cleaned up when the context exits.

    Args:
        data: Binary data to write to the temporary file

    Yields:
        str: Path to the temporary file

    Example:
        >>> with temp_file_with_data(b"password123") as path:
        ...     # Use the file at 'path'
        ...     pass
        >>> # File is now deleted
    """
    import tempfile

    fd, path = tempfile.mkstemp()
    try:
        os.write(fd, data)
        os.close(fd)
        yield path
    finally:
        with contextlib.suppress(OSError):
            os.remove(path)

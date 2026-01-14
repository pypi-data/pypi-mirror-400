# Copyright (c) 2025, qBraid Development Team
# All rights reserved.

"""
Module for managing packages in qBraid environments.

All functions use env_id (not slug) to identify environments,
since env_id is the unique local identifier. Same slug can be
installed multiple times with different env_ids.
"""

import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

from qbraid_core.system.executables import is_valid_python, python_paths_equivalent
from qbraid_core.system.packages import set_include_sys_site_pkgs_value

from .exceptions import EnvironmentNotFoundError, EnvironmentOperationError
from .registry import EnvironmentRegistryManager
from .state import update_state_json

logger = logging.getLogger(__name__)


def _get_env_python(env_id: str) -> tuple[Path, str]:
    """Get environment path and python executable for env_id.

    Args:
        env_id: Environment ID (local registry identifier)

    Returns:
        tuple[Path, str]: (env_path, python_executable)

    Raises:
        EnvironmentNotFoundError: If env_id not found in registry
        EnvironmentOperationError: If python executable not found
    """
    registry = EnvironmentRegistryManager()
    result = registry.find_by_env_id(env_id)

    if result is None:
        raise EnvironmentNotFoundError(
            f"Environment '{env_id}' not found in registry. "
            "Use env_id (not slug) for local operations."
        )

    _, entry = result
    env_path = entry.path

    if not env_path.exists():
        raise EnvironmentNotFoundError(
            f"Environment path does not exist: {env_path}"
        )

    # Find python executable
    python_exe = _find_python_in_env(env_path)
    if python_exe is None:
        raise EnvironmentOperationError(
            f"Could not find valid Python executable in environment: {env_path}"
        )

    return env_path, python_exe


def _find_python_in_env(env_path: Path) -> Optional[str]:
    """Find Python executable in environment.

    Args:
        env_path: Path to environment directory

    Returns:
        str or None: Path to python executable
    """
    # Check kernel.json first
    kernels_dir = env_path / "kernels"
    if kernels_dir.is_dir():
        for resource_dir in kernels_dir.iterdir():
            if "python" in resource_dir.name:
                kernel_json = resource_dir / "kernel.json"
                if kernel_json.exists():
                    import json
                    with kernel_json.open(encoding="utf-8") as f:
                        data = json.load(f)
                        if data.get("language") == "python":
                            python_path = data["argv"][0]
                            if is_valid_python(python_path):
                                return python_path

    # Fallback: check pyenv bin
    if sys.platform == "win32":
        python_path = env_path / "pyenv" / "Scripts" / "python.exe"
    else:
        python_path = env_path / "pyenv" / "bin" / "python"

    if is_valid_python(python_path):
        return str(python_path)

    return None


def pip_install(
    env_id: str,
    packages: list[str],
    upgrade_pip: bool = False,
    system_site_packages: bool = True,
) -> dict:
    """Install packages into an environment.

    Args:
        env_id: Environment ID (local registry identifier, NOT slug)
        packages: List of packages to install (e.g., ["numpy", "pandas>=1.0"])
        upgrade_pip: If True, upgrade pip before installing packages
        system_site_packages: If True, include system site packages

    Returns:
        dict: Result with 'success', 'message', and 'output' keys

    Raises:
        EnvironmentNotFoundError: If env_id not found in registry
        EnvironmentOperationError: If installation fails

    Example:
        >>> pip_install("abc123", ["numpy", "pandas"])
        {'success': True, 'message': 'Installed 2 packages', 'output': '...'}
    """
    if not packages and not upgrade_pip:
        return {"success": True, "message": "No packages provided", "output": ""}

    env_path, python = _get_env_python(env_id)
    output_messages = []

    # Upgrade pip if requested
    if upgrade_pip:
        logger.info("Upgrading pip in environment %s", env_id)
        result = subprocess.run(
            [python, "-m", "pip", "install", "--upgrade", "pip"],
            capture_output=True,
            check=False,
        )
        stderr = result.stderr.decode("utf-8")
        stdout = result.stdout.decode("utf-8")
        output_messages.append(stderr + stdout.strip().split("\n")[-1])

    if not packages:
        return {
            "success": True,
            "message": "Upgraded pip",
            "output": " ".join(output_messages),
        }

    # Write packages to temp requirements file
    reqs_tmp = env_path / "reqs_tmp.txt"
    with open(reqs_tmp, "w", encoding="utf-8") as f:
        for package in packages:
            f.write(package + "\n")

    install_command = [python, "-m", "pip", "install", "-r", str(reqs_tmp)]

    try:
        # Handle system site packages setting
        is_system_python = python_paths_equivalent(python, sys.executable)

        if not is_system_python:
            cfg = env_path / "pyenv" / "pyvenv.cfg"
            if cfg.exists():
                set_include_sys_site_pkgs_value(False, str(cfg))

        # Run pip install
        logger.info("Installing packages in environment %s: %s", env_id, packages)
        result = subprocess.run(install_command, capture_output=True, check=False)

        # Restore system site packages if needed
        if not is_system_python and system_site_packages:
            cfg = env_path / "pyenv" / "pyvenv.cfg"
            if cfg.exists():
                set_include_sys_site_pkgs_value(True, str(cfg))

        stderr = result.stderr.decode("utf-8")
        stdout = result.stdout.decode("utf-8")
        output_messages.append(stderr + stdout.strip().split("\n")[-1])

        success = result.returncode == 0
        message = f"Installed {len(packages)} package(s)" if success else "Installation failed"

        # Update registry with new packages if successful
        if success:
            _update_registry_packages(env_id)

        return {
            "success": success,
            "message": message,
            "output": " ".join(output_messages),
            "returncode": result.returncode,
        }

    finally:
        # Clean up temp file
        if reqs_tmp.exists():
            try:
                os.remove(reqs_tmp)
            except OSError as err:
                logger.warning("Could not remove temp file %s: %s", reqs_tmp, err)


def pip_uninstall(env_id: str, packages: list[str]) -> dict:
    """Uninstall packages from an environment.

    Args:
        env_id: Environment ID (local registry identifier, NOT slug)
        packages: List of packages to uninstall

    Returns:
        dict: Result with 'success', 'message', and 'output' keys

    Raises:
        EnvironmentNotFoundError: If env_id not found in registry
        EnvironmentOperationError: If uninstallation fails

    Example:
        >>> pip_uninstall("abc123", ["numpy"])
        {'success': True, 'message': 'Uninstalled 1 packages', 'output': '...'}
    """
    if not packages:
        return {"success": True, "message": "No packages provided", "output": ""}

    env_path, python = _get_env_python(env_id)

    command = [python, "-m", "pip", "uninstall", "-y"] + packages

    logger.info("Uninstalling packages from environment %s: %s", env_id, packages)
    result = subprocess.run(command, capture_output=True, check=False)

    stderr = result.stderr.decode("utf-8")
    stdout = result.stdout.decode("utf-8")
    output = stderr + stdout.strip().split("\n")[-1]

    success = result.returncode == 0
    message = f"Uninstalled {len(packages)} package(s)" if success else "Uninstallation failed"

    # Update registry with new packages if successful
    if success:
        _update_registry_packages(env_id)

    return {
        "success": success,
        "message": message,
        "output": output,
        "returncode": result.returncode,
    }


def _update_registry_packages(env_id: str) -> None:
    """Update registry with current packages from pip freeze.

    Args:
        env_id: Environment ID
    """
    try:
        packages = pip_freeze(env_id)
        pkg_dict = {}
        for pkg in packages:
            if "==" in pkg:
                name, version = pkg.split("==", 1)
                pkg_dict[name] = version
            else:
                # Package without version (editable, etc.)
                pkg_dict[pkg] = ""

        registry = EnvironmentRegistryManager()
        registry.update_environment(env_id, python_packages=pkg_dict)
        logger.debug("Updated registry packages for environment %s", env_id)
    except Exception as err:  # pylint: disable=broad-exception-caught
        logger.warning("Failed to update registry packages for %s: %s", env_id, err)


def pip_freeze(env_id: str, system_site_packages: bool = True) -> list[str]:
    """Get list of installed packages in an environment (pip freeze).

    Args:
        env_id: Environment ID (local registry identifier, NOT slug)
        system_site_packages: If True, include system site packages in output

    Returns:
        list[str]: List of installed packages in "package==version" format

    Raises:
        EnvironmentNotFoundError: If env_id not found in registry
        EnvironmentOperationError: If pip freeze fails

    Example:
        >>> pip_freeze("abc123")
        ['numpy==1.24.0', 'pandas==2.0.0', ...]
    """
    env_path, python = _get_env_python(env_id)

    # Handle system site packages setting
    # Only disable system site packages if explicitly requested (system_site_packages=False)
    is_system_python = python_paths_equivalent(python, sys.executable)
    cfg = env_path / "pyenv" / "pyvenv.cfg"
    modified_cfg = False

    if not system_site_packages and not is_system_python and cfg.exists():
        set_include_sys_site_pkgs_value(False, str(cfg))
        modified_cfg = True

    try:
        logger.debug("Running pip freeze for environment %s", env_id)
        result = subprocess.run(
            [python, "-m", "pip", "freeze"],
            capture_output=True,
            check=False,
        )

        if result.returncode != 0:
            stderr = result.stderr.decode("utf-8")
            raise EnvironmentOperationError(f"pip freeze failed: {stderr}")

        stdout = result.stdout.decode("utf-8")
        packages = [line.strip() for line in stdout.splitlines() if line.strip()]

        # Process package lines to normalize format
        normalized = []
        for pkg in packages:
            processed = _process_freeze_line(pkg)
            if processed:
                normalized.append(processed)

        return normalized

    finally:
        # Restore system site packages if we modified it
        if modified_cfg:
            set_include_sys_site_pkgs_value(True, str(cfg))


def _process_freeze_line(line: str) -> Optional[str]:
    """Process a pip freeze output line to normalize format.

    Args:
        line: Raw line from pip freeze

    Returns:
        str or None: Normalized "package==version" format or None if invalid
    """
    line = line.strip()
    if not line:
        return None

    # Handle "package @ file://..." format
    if " @ " in line:
        package = line.split(" @ ")[0].strip()
        if not package:
            return None
        # Try to extract version from the URL or return package name only
        return package

    # Handle editable installs "-e git+..."
    if line.startswith("-e"):
        if "egg=" in line:
            package = line.split("egg=")[-1].strip()
            return package
        return None

    # Normal "package==version" format
    if "==" in line:
        return line

    return None

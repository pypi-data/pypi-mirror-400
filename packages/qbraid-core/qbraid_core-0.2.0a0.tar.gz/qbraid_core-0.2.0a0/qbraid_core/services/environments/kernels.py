# Copyright (c) 2025, qBraid Development Team
# All rights reserved.

"""
Module for managing kernels.

"""
import sys
from pathlib import Path
from typing import Any, Optional

from jupyter_client.kernelspec import KernelSpecManager

from qbraid_core.system.executables import is_exe

from .paths import installed_envs_data


def _get_kernels_path(environment: str) -> Path:
    """Get the path to the kernels directory for the given environment.
    
    Args:
        environment: Environment name (if unique) or env_id
        
    Returns:
        Path to kernels directory
    """
    env_id_to_path, name_to_env_id = installed_envs_data()

    # Try to find by name first, then by env_id
    env_id = None
    if environment in name_to_env_id:
        env_id = name_to_env_id.get(environment, None)
    else:
        # Assume it's an env_id
        env_id = environment

    if env_id not in env_id_to_path:
        raise ValueError(
            f"Environment '{environment}' not found. "
            "Use name (if unique) or env_id to reference the environment."
        )

    env_path = env_id_to_path[env_id]
    kernels_path = env_path / "kernels"
    return kernels_path


def get_all_kernels(
    exclude_invalid: bool = False, exclude_kernels: Optional[list[str]] = None
) -> dict[str, Any]:
    """
    Returns a dictionary mapping kernel names to kernelspecs, with options to
    exclude certain kernels.

    Args:
        exclude_invalid (bool): If True, kernels with non-executable paths are excluded.
        exclude_kernels (list[str], optional): List of kernel names to exclude.

    Returns:
        dict[str, Any]: A dictionary of kernel names to their corresponding kernelspec details.
    """
    kernel_spec_manager = KernelSpecManager()
    kernelspecs = kernel_spec_manager.get_all_specs()

    # Filter out deprecated or unwanted kernels
    kernelspecs = {k: v for k, v in kernelspecs.items() if k not in (exclude_kernels or [])}

    # Optionally remove kernels with non-executable paths
    if exclude_invalid:
        for kernel_name, spec in list(kernelspecs.items()):
            try:
                exe_path = spec["spec"]["argv"][0]
                if not is_exe(exe_path):
                    raise ValueError("Invalid executable path.")
            except (KeyError, IndexError, TypeError, ValueError):
                kernel_spec_manager.remove_kernel_spec(kernel_name)
                kernelspecs.pop(kernel_name, None)

    return kernelspecs


def add_kernels(environment: str) -> None:
    """Add a kernel to user's Jupyter kernel directory."""
    kernel_spec_manager = KernelSpecManager()
    kernels_path = _get_kernels_path(environment)

    # Use user=True to install to user-level data directory
    # This ensures kernels are found regardless of virtualenv setup
    for kernel in kernels_path.iterdir():
        kernel_spec_manager.install_kernel_spec(source_dir=str(kernel), user=True)


def remove_kernels(environment: str) -> None:
    """Remove a kernel."""
    kernel_spec_manager = KernelSpecManager()
    kernels_path = _get_kernels_path(environment)

    for kernel in kernels_path.iterdir():
        kernel_spec_manager.remove_kernel_spec(kernel.name)

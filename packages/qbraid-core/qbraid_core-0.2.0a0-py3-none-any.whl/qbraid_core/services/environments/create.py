# Copyright (c) 2025, qBraid Development Team
# All rights reserved.

"""
Module for creating custom environments.

"""
import base64
import binascii
import json
import logging
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, Union

from jupyter_client.kernelspec import KernelSpecManager

from qbraid_core.system.generic import replace_str
from qbraid_core.system.packages import set_include_sys_site_pkgs_value

from .paths import is_temporary_location
from .registry import EnvironmentRegistryManager
from .schema import EnvironmentConfig

logger = logging.getLogger(__name__)


def create_local_venv(
    slug_path: Union[str, Path],
    prompt: str,
    python_exe: Optional[Union[str, Path]] = None,
    env_id: Optional[str] = None,
) -> None:
    """Create virtual environment and swap PS1 display name.

    Args:
        slug_path: Path to environment directory
        prompt: Shell prompt name
        python_exe: Python executable to use (defaults to sys.executable)
        env_id: Optional environment ID to update registry with installed packages
    """
    try:
        # Ensure slug_path is a Path object
        slug_path = Path(slug_path)
        venv_path = slug_path / "pyenv"
        python_exe = Path(python_exe or sys.executable)
        subprocess.run([str(python_exe), "-m", "venv", str(venv_path)], check=True)

        # Determine the correct directory for activation scripts based on the operating system
        if sys.platform == "win32":
            scripts_path = venv_path / "Scripts"
            activate_files = ["activate.bat", "Activate.ps1"]
        else:
            scripts_path = venv_path / "bin"
            activate_files = ["activate", "activate.csh", "activate.fish"]

        for file in activate_files:
            file_path = scripts_path / file
            if file_path.exists():
                replace_str("(pyenv)", f"({prompt})", str(file_path))

        set_include_sys_site_pkgs_value(True, venv_path / "pyvenv.cfg")

        # Update registry with base packages if env_id provided
        if env_id:
            try:
                from .packages import _update_registry_packages
                _update_registry_packages(env_id)
            except Exception as pkg_err:  # pylint: disable=broad-exception-caught
                logger.warning("Failed to update registry packages: %s", pkg_err)

    except Exception as err:  # pylint: disable=broad-exception-caught
        logger.error("Error creating virtual environment: %s", err)
        # Error can be tracked in registry metadata if needed


# pylint: disable-next=too-many-locals
def create_qbraid_env_assets(
    env_id: str,
    env_id_path: str,
    env_config: EnvironmentConfig,
    image_data_url: Optional[str] = None,
) -> None:
    """Create a qBraid environment including python venv, PS1 configs,
    and kernel resource files. Environment is registered in the registry.

    Args:
        env_id: Environment ID (4-digit alphanumeric) - used for directory naming
        env_id_path: Path to environment directory (named with env_id)
        env_config: Environment configuration
        image_data_url: Optional base64-encoded image data URL
    """
    local_resource_dir = os.path.join(env_id_path, "kernels", f"python3_{env_id}")
    os.makedirs(local_resource_dir, exist_ok=True)

    # Note: state.json is no longer created - registry metadata is used instead

    # create kernel.json
    kernel_json_path = os.path.join(local_resource_dir, "kernel.json")
    kernel_spec_manager = KernelSpecManager()
    kernelspec_dict = kernel_spec_manager.get_all_specs()
    kernel_data = kernelspec_dict["python3"]["spec"]
    if sys.platform == "win32":
        python_exec_path = os.path.join(env_id_path, "pyenv", "Scripts", "python.exe")
    else:
        python_exec_path = os.path.join(env_id_path, "pyenv", "bin", "python")
    kernel_data["argv"][0] = python_exec_path
    kernel_data["display_name"] = (
        env_config.kernel_name if env_config.kernel_name else f"Python 3 [{env_config.name}]"
    )
    with open(kernel_json_path, "w", encoding="utf-8") as file:
        json.dump(kernel_data, file, indent=4)

    # copy logo files
    if image_data_url:
        img_path = os.path.join(local_resource_dir, "logo-64x64.png")
        save_image_from_data_url(image_data_url, img_path)

        # change to the local file name for the icon
        env_config.icon = Path(img_path)
    else:
        sys_resource_dir = kernelspec_dict["python3"]["resource_dir"]
        logo_files = ["logo-32x32.png", "logo-64x64.png", "logo-svg.svg"]
        updated_config = False
        for file_name in logo_files:
            sys_path = os.path.join(sys_resource_dir, file_name)
            loc_path = os.path.join(local_resource_dir, file_name)
            if os.path.isfile(sys_path):
                shutil.copy(sys_path, loc_path)
                if not updated_config:
                    env_config.icon = Path(loc_path)
                    updated_config = True

    # Register environment in registry (single source of truth)
    # No longer create qbraid.yaml - registry is the source of truth
    # Note: slug is None for locally created environments (will be set when published)
    try:
        registry_mgr = EnvironmentRegistryManager()
        env_id_path_obj = Path(env_id_path)
        is_temp = is_temporary_location(env_id_path_obj)

        registered_env_id = registry_mgr.register_environment(
            path=env_id_path_obj,
            env_type="temporary" if is_temp else "qbraid-managed",
            env_id=env_id,  # Use provided env_id
            slug=None,  # No slug until published
            config=env_config,
            is_temporary=is_temp,
        )
        logger.info(
            "Registered environment in registry: %s (env_id: %s)", env_config.name, registered_env_id
        )
    except Exception as reg_err:  # pylint: disable=broad-exception-caught
        # Log error but don't fail environment creation if registry fails
        logger.warning("Failed to register environment in registry: %s", reg_err)


def save_image_from_data_url(data_url: str, output_path: str) -> None:
    """Save an image from a base64-encoded Data URL to a file."""
    # Extract base64 content from the Data URL
    match = re.search(r"base64,(.*)", data_url)
    if not match:
        raise ValueError("Invalid Data URL")

    try:
        image_data = base64.b64decode(match.group(1))
    except binascii.Error as err:
        raise ValueError("Invalid Data URL") from err

    # Ensure the output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Write the image data to a file
    with open(output_path, "wb") as file:
        file.write(image_data)

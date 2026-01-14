# Copyright (c) 2025, qBraid Development Team
# All rights reserved.

# pylint: disable=too-many-lines

"""
Module providing client for interacting with qBraid environments service.

"""
import asyncio
import json
import logging
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
import time
from pathlib import Path
from typing import Any, Callable, Optional

import yaml
import zstandard as zstd

from qbraid_core.client import QbraidClientV1
from qbraid_core.exceptions import AuthError, RequestsApiError
from qbraid_core.registry import register_client
from qbraid_core.system.executables import (
    get_python_executables,
    get_python_version,
    is_valid_python,
)

from .exceptions import (
    EnvironmentDownloadError,
    EnvironmentExtractionError,
    EnvironmentInstallError,
    EnvironmentOperationError,
    EnvironmentRegistryError,
    EnvironmentServiceRequestError,
    EnvironmentValidationError,
)
from .paths import extract_alias_from_path, get_default_envs_paths
from .registry import EnvironmentRegistryManager
from .schema import EnvironmentConfig
from .validate import is_valid_env_name, is_valid_slug

logger = logging.getLogger(__name__)


@register_client()
class EnvironmentManagerClient(QbraidClientV1):
    """Client for interacting with qBraid environment services."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.envs_paths = get_default_envs_paths()

    @property
    def envs_paths(self) -> list[Path]:
        """Returns a dictionary of environment paths.

        Returns:
            A dictionary containing the environment paths.
        """
        return self._envs_paths

    @envs_paths.setter
    def envs_paths(self, value: list[Path]):
        """Sets the qBraid environments paths."""
        self._envs_paths = value

    def _validate_python_version(self, python_version: str) -> None:
        """Checks if the given python version is valid according to the system and conda
        python installations.

        Args:
            python_version: The python version to check.

        Returns:
            True if the python version is valid, False otherwise.
        """
        python_versions = get_python_executables()

        system_py_versions = python_versions["system"]
        value_in_system = python_version in system_py_versions

        conda_py_versions = python_versions["conda"]
        value_in_conda = python_version in conda_py_versions

        qbraid_client = None

        try:
            qbraid_client = QbraidClientV1()
        except (AuthError, EnvironmentServiceRequestError) as err:
            logger.error("Error creating QbraidClient: %s", err)

        if qbraid_client and qbraid_client.running_in_lab() is True:
            if value_in_system is False and value_in_conda is False:
                raise ValueError(
                    f"Python version '{python_version}' not found in system or conda"
                    " python installations"
                )
        else:
            if value_in_system is False:
                logger.warning(
                    "Python version '%s' not found in system python installations", python_version
                )
            # set the default here
            python_version = list(python_versions["system"].keys())[0]

        logger.info("Using python version '%s' for custom environment", python_version)

    def remote_publish_environment(
        self,
        config: Optional[EnvironmentConfig] = None,
        file_path: Optional[str] = None,
        persist_env: Optional[bool] = False,
    ) -> dict:
        """Triggers the remote publish of a custom environment.

        Args:
            config: Environment configuration.
            file_path: Path to the environment YAML file.
            persist_env: Whether to persist the environment in user space.

        Returns:
            A dictionary containing the response data.
        """
        if config and file_path:
            raise ValueError(
                "Only one of YAML file or config data can be provided for env creation"
            )

        if not config and not file_path:
            raise ValueError("Either YAML file or config data must be provided for env creation")

        # 1. Prepare files for request
        req_files = {}
        icon_path = str(config.icon) if config else ""

        if file_path:
            # ensure file exists
            if not Path(file_path).exists():
                raise ValueError(f"Env config file not found at path: {file_path}")
            yaml_file = open(file_path, "rb")  # pylint: disable=consider-using-with
            req_files["yamlFile"] = (Path(file_path).stem, yaml_file, "text/yaml")

            with open(file_path, "r", encoding="utf-8") as f:
                icon_path = str(yaml.safe_load(f)["icon"])

        if not Path(icon_path).exists():
            raise ValueError(f"Icon file not found at path: {icon_path}")
        # need to pass an open file object to requests
        img_file = open(icon_path, "rb")  # pylint: disable=consider-using-with
        req_files["iconFile"] = (Path(icon_path).stem, img_file, "image/png")

        # 2. Prepare request body
        req_body = {
            "persistEnv": persist_env,
            "config": config.model_dump_json(by_alias=True) if config else None,
        }
        try:
            env_publish_data = self.session.post(
                "/environments/remote/publish", data=req_body, files=req_files
            ).json()
        except RequestsApiError as err:
            raise EnvironmentServiceRequestError(
                f"Remote publish environment request failed: {err}"
            ) from err

        if (
            env_publish_data is None
            or len(env_publish_data) == 0
            or env_publish_data.get("envSlug") is None
        ):
            raise EnvironmentServiceRequestError(
                f"Remote publish environment request responded with invalid data: "
                f"{env_publish_data}",
            )

        return env_publish_data

    def retrieve_remote_publish_status(self, env_slug: str) -> dict:
        """Retrieves the status of the remote publish request for the given environment slug.

        Args:
            env_slug: The slug of the environment to retrieve the status for.

        Returns:
            A dictionary containing the response data.
        """
        try:
            env_publish_status = self.session.get(
                "/environments/remote/publish/status", params={"envSlug": env_slug}
            ).json()
        except RequestsApiError as err:
            raise EnvironmentServiceRequestError(
                f"Request failed to retrieve remote publish status: {err}"
            ) from err

        if (
            env_publish_status is None
            or len(env_publish_status) == 0
            or env_publish_status.get("status") is None
        ):
            raise EnvironmentServiceRequestError(
                f"Request failed to retrieve remote publish status: {env_publish_status}",
            )

        return env_publish_status["status"]

    def wait_for_env_remote_publish(
        self, env_slug: str, timeout: Optional[int] = None, poll_interval: int = 20
    ) -> bool:
        """Monitors the remote publish status of the given environment slug by polling the remote
        create status field.

        Args:
            env_slug: The slug of the environment to monitor the status for.
            timeout: The maximum time to wait for the remote publish to complete.
            poll_interval: The time interval in seconds to poll the remote publish
                           status.
        Raises:
            TimeoutError: If the remote publish status is not complete within the timeout period.

        Returns:
            success: True if the remote publish was successful, False otherwise.
        """
        # default wait time is 10 minutes
        retries = timeout // poll_interval if timeout else 30
        status = None

        for retry in range(retries):
            status = self.retrieve_remote_publish_status(env_slug)
            logger.info("Remote publish status: %s", status)
            if status in ["COMPLETE", "FAILED"]:
                break

            if retry == retries - 1:
                raise TimeoutError(
                    f"Remote env publish not complete within timeout period, final status: {status}"
                )

            logger.info("Retrying in %d seconds", poll_interval)
            time.sleep(poll_interval)

        return status == "COMPLETE"

    def create_environment(self, config: EnvironmentConfig) -> dict[str, Any]:
        """Creates a new environment with the given configuration.

        Args:
            config: Environment configuration.

        Returns:
            A dictionary containing the environment data.

        Raises:
            ValueError: If the environment name is invalid or the description is too long.
            EnvironmentServiceRequestError: If the create environment request fails.
        """
        if not is_valid_env_name(config.name):
            raise ValueError(f"Invalid environment name: {config.name}")

        if config.description and len(config.description) > 300:
            raise ValueError("Description is too long. Maximum length is 300 characters.")

        if config.python_version:
            self._validate_python_version(config.python_version)

        # Build form data for multipart/form-data request
        req_data: dict[str, Any] = {
            "name": config.name,
        }

        if config.description:
            req_data["description"] = config.description

        if config.tags:
            # Tags should be comma-separated string for form data
            tags = config.tags if isinstance(config.tags, str) else ",".join(config.tags)
            req_data["tags"] = tags

        if config.visibility:
            req_data["visibility"] = config.visibility

        if config.kernel_name:
            req_data["kernelName"] = config.kernel_name

        if config.shell_prompt:
            req_data["prompt"] = config.shell_prompt

        req_files = {}
        if config.icon:
            # need to pass an open file object to requests
            img_file = open(config.icon, "rb")  # pylint: disable=consider-using-with
            req_files["image"] = (Path(config.icon).stem, img_file, "image/png")

        try:
            response = self.session.post(
                "/environments", data=req_data, files=req_files if req_files else None
            ).json()

            # Handle new API response format: {success: true, data: {environment: {...}}}
            if isinstance(response, dict) and response.get("success") and "data" in response:
                data = response["data"]
                # Environment may be nested under 'environment' key
                env_data = data.get("environment", data)
            else:
                env_data = response

        except RequestsApiError as err:
            raise EnvironmentServiceRequestError(
                f"Create environment request failed: {err}"
            ) from err

        if env_data is None or len(env_data) == 0 or env_data.get("slug") is None:
            raise EnvironmentServiceRequestError(
                "Create environment request responded with invalid environment data"
            )

        return env_data

    def delete_environment(self, slug: str) -> None:
        """Deletes the environment with the given slug.

        Args:
            slug: The slug of the environment to delete.

        Returns:
            None

        Raises:
            ValueError: If the environment slug is invalid.
            EnvironmentServiceRequestError: If the delete environment request fails.
        """
        if not is_valid_slug(slug):
            raise ValueError(f"Invalid environment slug: {slug}")

        try:
            self.session.delete(f"/environments/{slug}")
        except RequestsApiError as err:
            raise EnvironmentServiceRequestError(
                f"Delete environment request failed: {err}"
            ) from err

    def update_environment(self, slug: str, **kwargs) -> dict[str, Any]:
        """Update environment metadata.

        Args:
            slug: The slug of the environment to update.
            **kwargs: Fields to update. Supported fields include:
                - displayName: Display name for the environment
                - description: Environment description
                - tags: List of tags
                - visibility: 'public' or 'private'
                - logo: Logo configuration with 'light' and 'dark' URLs

        Returns:
            Dictionary containing the updated environment data.

        Raises:
            ValueError: If the environment slug is invalid.
            EnvironmentServiceRequestError: If the update request fails.
        """
        if not is_valid_slug(slug):
            raise ValueError(f"Invalid environment slug: {slug}")

        try:
            response = self.session.put(f"/environments/{slug}", json=kwargs).json()

            # Handle new API response format: {success: true, data: {...}}
            if isinstance(response, dict) and response.get("success") and "data" in response:
                return response["data"]

            # Handle legacy format (direct object)
            if isinstance(response, dict):
                return response

            raise EnvironmentServiceRequestError(
                f"Unexpected response format from API: {response}"
            )
        except RequestsApiError as err:
            raise EnvironmentServiceRequestError(
                f"Update environment request failed: {err}"
            ) from err

    def share_environment(
        self, slug: str, target_type: str, target_id: str, permissions: list[str]
    ) -> dict[str, Any]:
        """Share environment with a user or organization.

        Args:
            slug: The slug of the environment to share.
            target_type: Type of target - 'user' or 'organization'.
            target_id: ID of the user or organization to share with.
            permissions: List of permissions to grant. Valid values:
                - 'read': Can view the environment
                - 'write': Can modify the environment
                - 'execute': Can download/install the environment

        Returns:
            Dictionary containing the share result with granted permissions.

        Raises:
            ValueError: If the environment slug is invalid or permissions are invalid.
            EnvironmentServiceRequestError: If the share request fails.
        """
        if not is_valid_slug(slug):
            raise ValueError(f"Invalid environment slug: {slug}")

        valid_permissions = {"read", "write", "execute"}
        invalid = set(permissions) - valid_permissions
        if invalid:
            raise ValueError(f"Invalid permissions: {invalid}. Valid: {valid_permissions}")

        if target_type not in ("user", "organization"):
            raise ValueError(f"Invalid target_type: {target_type}. Must be 'user' or 'organization'")

        try:
            response = self.session.post(
                f"/environments/{slug}/share",
                json={
                    "targetType": target_type,
                    "targetId": target_id,
                    "permissions": permissions,
                },
            ).json()

            # Handle new API response format: {success: true, data: {...}}
            if isinstance(response, dict) and response.get("success") and "data" in response:
                return response["data"]

            if isinstance(response, dict):
                return response

            raise EnvironmentServiceRequestError(
                f"Unexpected response format from API: {response}"
            )
        except RequestsApiError as err:
            raise EnvironmentServiceRequestError(
                f"Share environment request failed: {err}"
            ) from err

    def revoke_environment_access(
        self, slug: str, target_type: str, target_id: str, permissions: list[str]
    ) -> dict[str, Any]:
        """Revoke environment access from a user or organization.

        Args:
            slug: The slug of the environment.
            target_type: Type of target - 'user' or 'organization'.
            target_id: ID of the user or organization to revoke access from.
            permissions: List of permissions to revoke.

        Returns:
            Dictionary containing the revoke result.

        Raises:
            ValueError: If the environment slug is invalid.
            EnvironmentServiceRequestError: If the revoke request fails.
        """
        if not is_valid_slug(slug):
            raise ValueError(f"Invalid environment slug: {slug}")

        if target_type not in ("user", "organization"):
            raise ValueError(f"Invalid target_type: {target_type}. Must be 'user' or 'organization'")

        try:
            response = self.session.delete(
                f"/environments/{slug}/share",
                json={
                    "targetType": target_type,
                    "targetId": target_id,
                    "permissions": permissions,
                },
            ).json()

            # Handle new API response format: {success: true, data: {...}}
            if isinstance(response, dict) and response.get("success") and "data" in response:
                return response["data"]

            if isinstance(response, dict):
                return response

            raise EnvironmentServiceRequestError(
                f"Unexpected response format from API: {response}"
            )
        except RequestsApiError as err:
            raise EnvironmentServiceRequestError(
                f"Revoke environment access request failed: {err}"
            ) from err

    def get_environment_shared_with(self, slug: str) -> dict[str, Any]:
        """Get list of users and organizations the environment is shared with.

        Args:
            slug: The slug of the environment.

        Returns:
            Dictionary containing lists of users and organizations with their permissions.

        Raises:
            ValueError: If the environment slug is invalid.
            EnvironmentServiceRequestError: If the request fails.
        """
        if not is_valid_slug(slug):
            raise ValueError(f"Invalid environment slug: {slug}")

        try:
            response = self.session.get(f"/environments/{slug}/shared-with").json()

            # Handle new API response format: {success: true, data: {...}}
            if isinstance(response, dict) and response.get("success") and "data" in response:
                return response["data"]

            if isinstance(response, dict):
                return response

            raise EnvironmentServiceRequestError(
                f"Unexpected response format from API: {response}"
            )
        except RequestsApiError as err:
            raise EnvironmentServiceRequestError(
                f"Get environment shared-with request failed: {err}"
            ) from err

    def _extract_zstd_tar(
        self,
        zstd_file_path: Path,
        extract_to: Path,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
    ) -> Path:
        """Extract a zstd-compressed tar file to a directory.

        Args:
            zstd_file_path: Path to the .tar.zst file
            extract_to: Directory to extract to
            progress_callback: Optional callback for progress reporting (stage, completed, total)

        Returns:
            Path to the extracted directory (first directory found)

        Raises:
            EnvironmentExtractionError: If extraction fails
        """
        extract_to.mkdir(parents=True, exist_ok=True)

        # Get compressed file size for progress estimation
        compressed_size = zstd_file_path.stat().st_size

        # Decompress zstd and extract tar
        try:
            with open(zstd_file_path, "rb") as zstd_file:
                dctx = zstd.ZstdDecompressor()
                with dctx.stream_reader(zstd_file) as reader:
                    with tarfile.open(fileobj=reader, mode="r|") as tar:
                        extracted_bytes = 0
                        for member in tar:
                            tar.extract(member, extract_to)
                            # Track bytes extracted (size of each member)
                            extracted_bytes += member.size
                            if progress_callback:
                                # Report bytes extracted; estimate total as 3x compressed size
                                # (typical compression ratio for environments)
                                estimated_total = compressed_size * 3
                                progress_callback("extract", extracted_bytes, estimated_total)

            # Find the extracted directory (should be the first/only top-level dir)
            extracted_dirs = [d for d in extract_to.iterdir() if d.is_dir()]
            if not extracted_dirs:
                raise EnvironmentExtractionError("No directory found after extraction")
            return extracted_dirs[0]

        except Exception as err:
            raise EnvironmentExtractionError(
                f"Failed to extract environment archive: {err}"
            ) from err

    def get_available_environments(
        self, page: Optional[int] = None, limit: Optional[int] = None
    ) -> dict[str, Any]:
        """Get list of available pre-built environments for installation.

        Args:
            page: Page number for pagination (default: 1)
            limit: Number of environments per page (default: 20)

        Returns:
            A dictionary containing environments list and pagination metadata.

        Raises:
            EnvironmentServiceRequestError: If the request fails.
        """
        try:
            params = {}
            if page is not None:
                params["page"] = page
            if limit is not None:
                params["limit"] = limit

            response = self.session.get("/environments", params=params).json()

            # Check if we're on qBraid Lab (cloud) or local
            is_cloud = self.running_in_lab()

            # Handle API response format: {data: [...], pagination: {...}}
            # May or may not have "success" field
            if isinstance(response, dict) and "data" in response:
                environments = response["data"]
                # Add availability status to each environment
                for env in environments:
                    env["available_for_installation"] = is_cloud

                # Pagination can be at top level or under "meta"
                pagination = response.get("pagination") or response.get("meta", {}).get(
                    "pagination", {}
                )

                return {
                    "environments": environments,
                    "pagination": pagination,
                }

            # Handle legacy response formats for backward compatibility
            if isinstance(response, list):
                # Add availability status to each environment
                for env in response:
                    env["available_for_installation"] = is_cloud
                return {"environments": response}

            if isinstance(response, dict) and "environments" in response:
                # Handle case where API returns wrapped response
                environments = response["environments"]
                for env in environments:
                    env["available_for_installation"] = is_cloud
                return response

            # Fallback for unexpected response format
            return {"environments": []}
        except RequestsApiError as err:
            raise EnvironmentServiceRequestError(
                f"Get available environments request failed: {err}"
            ) from err

    def get_environment_by_slug(self, slug: str) -> dict[str, Any]:
        """Get a specific environment by its slug.

        Args:
            slug: Environment slug identifier

        Returns:
            A dictionary containing the environment data.

        Raises:
            EnvironmentServiceRequestError: If the request fails.
            EnvironmentValidationError: If slug is invalid.
        """
        if not slug:
            raise EnvironmentValidationError("Environment slug is required")

        try:
            response = self.session.get(f"/environments/{slug}").json()

            # Handle new API response format: {success: true, data: {...}}
            if isinstance(response, dict) and response.get("success") and "data" in response:
                env_data = response["data"]
                # Add availability status
                env_data["available_for_installation"] = self.running_in_lab()
                return env_data

            # Handle legacy format (direct object)
            if isinstance(response, dict) and "slug" in response:
                response["available_for_installation"] = self.running_in_lab()
                return response

            raise EnvironmentServiceRequestError(
                f"Unexpected response format from API: {response}"
            )
        except RequestsApiError as err:
            raise EnvironmentServiceRequestError(
                f"Get environment by slug request failed: {err}"
            ) from err

    def get_environment_groups(
        self, page: Optional[int] = None, limit: Optional[int] = None
    ) -> dict[str, Any]:
        """Get list of environment groups.

        Environment groups are collections of environments that can be
        managed together. Groups reference environments by _id in their
        environments array.

        Args:
            page: Page number for pagination (default: 1)
            limit: Number of groups per page (default: 20)

        Returns:
            A dictionary containing environment groups list and pagination metadata.

        Raises:
            EnvironmentServiceRequestError: If the request fails.
        """
        try:
            params = {}
            if page is not None:
                params["page"] = page
            if limit is not None:
                params["limit"] = limit

            response = self.session.get("/environment-groups", params=params).json()

            # Handle new API response format: {success: true, data: [...], meta: {...}}
            if isinstance(response, dict) and response.get("success") and "data" in response:
                return {
                    "environment_groups": response["data"],
                    "pagination": response.get("meta", {}).get("pagination", {}),
                }

            # Handle legacy response formats for backward compatibility
            if isinstance(response, list):
                return {"environment_groups": response}

            if isinstance(response, dict) and "environment_groups" in response:
                return response

            # Fallback for unexpected response format
            return {"environment_groups": []}
        except RequestsApiError as err:
            raise EnvironmentServiceRequestError(
                f"Get environment groups request failed: {err}"
            ) from err

    def get_environment_group_by_slug(self, group_slug: str) -> dict[str, Any]:
        """Get a specific environment group by its slug.

        Args:
            group_slug: Environment group slug identifier

        Returns:
            A dictionary containing the environment group data.

        Raises:
            EnvironmentServiceRequestError: If the request fails.
            EnvironmentValidationError: If group_slug is invalid.
        """
        if not group_slug:
            raise EnvironmentValidationError("Environment group slug is required")

        try:
            response = self.session.get(f"/environment-groups/{group_slug}").json()

            # Handle new API response format: {success: true, data: {...}}
            if isinstance(response, dict) and response.get("success") and "data" in response:
                return response["data"]

            # Handle legacy format (direct object)
            if isinstance(response, dict) and ("slug" in response or "name" in response):
                return response

            raise EnvironmentServiceRequestError(
                f"Unexpected response format from API: {response}"
            )
        except RequestsApiError as err:
            raise EnvironmentServiceRequestError(
                f"Get environment group by slug request failed: {err}"
            ) from err

    # pylint: disable-next=too-many-branches,too-many-statements,too-many-locals
    async def install_environment_from_storage(
        self,
        slug: str,
        target_dir: str,
        temp: bool = False,
        overwrite: bool = False,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
    ) -> dict[str, Any]:
        """Install environment from cloud storage (S3/GCS).

        Gets a signed download URL from the API and downloads/installs the environment.

        Args:
            slug: Environment slug to install
            target_dir: Target directory for installation
            temp: If True, install as temporary (non-persistent)
            overwrite: If True, overwrite existing environment without prompting
            progress_callback: Optional callback function(stage, completed, total)
                for progress reporting (download/extract).

        Returns:
            Dictionary with installation status and metadata

        Raises:
            EnvironmentValidationError: If installation arguments are invalid
            EnvironmentDownloadError: If getting download URL or downloading fails
            EnvironmentExtractionError: If extraction fails
            EnvironmentInstallError: If relocation or registration fails
        """
        # Get signed download URL from API using execute endpoint
        storage_url = None
        try:
            response = self.session.post(f"/environments/{slug}/execute").json()

            # Handle new API response format: {success: true, data: {downloadUrl: ...}}
            if isinstance(response, dict) and response.get("success") and "data" in response:
                storage_url = response["data"].get("downloadUrl")
            else:
                storage_url = response.get("downloadUrl")

            if not storage_url:
                raise EnvironmentDownloadError(
                    f"Download URL not found in API response for '{slug}'"
                )
        except RequestsApiError as err:
            raise EnvironmentDownloadError(
                f"Failed to get download URL for environment '{slug}': {err}"
            ) from err

        # Fetch environment data from API to get all schema fields
        try:
            # Use the new get_environment_by_slug method
            env_data = self.get_environment_by_slug(slug)
        except EnvironmentServiceRequestError as err:
            raise EnvironmentServiceRequestError(
                f"Failed to fetch environment data for '{slug}': {err}"
            ) from err
        except Exception as err:
            raise EnvironmentValidationError(
                f"Environment '{slug}' not found: {err}"
            ) from err


        

        # Use exact environment slug as directory name for downloaded environments
        final_target = Path(target_dir) / slug

        # Installing from storage is only supported in qBraid Lab
        if not self.running_in_lab():
            raise EnvironmentOperationError(
                "Installing environments from storage is only supported in qBraid Lab. "
                "Environments are Linux-specific and will not work on other systems."
            )

        # Handle existing environment
        if final_target.exists():
            if not overwrite:
                raise EnvironmentValidationError(
                    f"Environment '{slug}' already exists at {final_target}. "
                    "Set overwrite=True to replace it."
                )

            # Remove existing environment
            shutil.rmtree(final_target)

        try:
            # Download using requests with progress callback support
            def _download_file() -> str:
                """Download file synchronously using requests."""
                try:
                    response = self.session.get(storage_url, stream=True)
                    response.raise_for_status()
                except RequestsApiError as err:
                    raise EnvironmentDownloadError(
                        f"Failed to download environment archive from {storage_url}: {err}"
                    ) from err

                # Get total size if available
                total_size = int(response.headers.get("content-length", 0))

                with tempfile.NamedTemporaryFile(suffix=".tar.zst", delete=False) as temp_file:
                    bytes_downloaded = 0
                    chunk_size = 8192

                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            temp_file.write(chunk)
                            bytes_downloaded += len(chunk)
                            if progress_callback:
                                progress_callback("download", bytes_downloaded, total_size)

                    return temp_file.name

            # Run download in thread pool to avoid blocking event loop
            temp_file_path = await asyncio.to_thread(_download_file)

            # Ensure parent directory exists
            final_target.parent.mkdir(parents=True, exist_ok=True)

            # Extract directly to target directory
            def _extract_directly() -> None:
                """Extract directly to target directory."""
                extracted_dir = self._extract_zstd_tar(
                    Path(temp_file_path),
                    final_target.parent,
                    progress_callback,
                )
                # Move extracted directory to final target if needed
                if extracted_dir != final_target:
                    if final_target.exists():
                        shutil.rmtree(final_target)
                    extracted_dir.rename(final_target)

            await asyncio.to_thread(_extract_directly)

            # Verify extraction was successful
            if not final_target.exists():
                raise EnvironmentInstallError(
                    f"Environment directory {final_target} not found after extraction"
                )

            # Fix hardcoded paths for relocation
            await self._relocate_environment_paths(final_target)

            # Register environment in registry
            # Convert API response to EnvironmentConfig if needed
            try:
                registry_mgr = EnvironmentRegistryManager()
                
                # Check if this slug is already registered (by slug, not path)
                existing_by_slug = registry_mgr.find_by_slug(slug)
                if existing_by_slug:
                    existing_env_id, existing_entry = existing_by_slug
                    if existing_entry.path != final_target:
                        logger.warning(
                            "Environment with slug '%s' already registered (env_id: %s) at %s. "
                            "Installing duplicate to %s with new env_id.",
                            slug,
                            existing_env_id,
                            existing_entry.path,
                            final_target,
                        )
                    else:
                        logger.debug("Environment %s already registered at this path", slug)
                        # Return existing env_id
                        return {
                            "status": "success",
                            "env_id": existing_env_id,
                            "slug": slug,
                            "target_dir": str(final_target),
                            "temp": temp,
                        }

                # Create EnvironmentConfig from API data
                # Map API response fields to EnvironmentConfig
                # Convert packagesInImage list ['pkg==ver', ...] to dict {'pkg': 'ver', ...}
                packages_list = env_data.get("packagesInImage", [])
                python_packages = None
                if packages_list:
                    python_packages = {}
                    for pkg in packages_list:
                        if "==" in pkg:
                            name, version = pkg.split("==", 1)
                            python_packages[name] = version
                        else:
                            python_packages[pkg] = ""

                # Auto-discover metadata from extracted environment if API doesn't provide it
                discovered_icon = None
                discovered_kernel_name = None
                discovered_python_version = None

                # Look for kernel.json and logo files in kernels directory
                kernels_dir = final_target / "kernels"
                if kernels_dir.is_dir():
                    for kernel_dir in kernels_dir.iterdir():
                        if kernel_dir.is_dir():
                            # Try to get kernel name from kernel.json
                            kernel_json = kernel_dir / "kernel.json"
                            if kernel_json.exists() and not discovered_kernel_name:
                                try:
                                    with kernel_json.open(encoding="utf-8") as f:
                                        kernel_data = json.load(f)
                                        discovered_kernel_name = kernel_data.get("display_name")
                                except (json.JSONDecodeError, IOError):
                                    pass

                            # Try to find logo file
                            if not discovered_icon:
                                for logo_name in ["logo-64x64.png", "logo-32x32.png"]:
                                    logo_path = kernel_dir / logo_name
                                    if logo_path.exists():
                                        discovered_icon = logo_path
                                        break

                # Try to get python version from pyenv
                pyenv_python = final_target / "pyenv" / "bin" / "python"
                if pyenv_python.exists() and not discovered_python_version:
                    try:
                        result = subprocess.run(
                            [str(pyenv_python), "--version"],
                            capture_output=True,
                            text=True,
                            check=False,
                        )
                        if result.returncode == 0:
                            # Output is "Python 3.x.y", extract just "3.x.y"
                            version_output = result.stdout.strip()
                            if version_output.startswith("Python "):
                                discovered_python_version = version_output[7:]  # Remove "Python "
                            else:
                                discovered_python_version = version_output
                    except Exception:  # pylint: disable=broad-exception-caught
                        pass

                # Don't pass python_packages to EnvironmentConfig (has PyPI validator)
                # Pass it directly to register_environment instead
                env_config = EnvironmentConfig(
                    name=env_data.get("name", extract_alias_from_path(final_target)),
                    description=env_data.get("description"),
                    tags=env_data.get("tags"),
                    icon=Path(env_data["icon"]) if env_data.get("icon") else discovered_icon,
                    python_version=env_data.get("pythonVersion") or discovered_python_version,
                    kernel_name=env_data.get("kernelName") or discovered_kernel_name,
                    shell_prompt=env_data.get("shellPrompt"),
                    visibility=env_data.get("visibility", "private"),
                )

                # Register with slug (for downloaded environments, directory uses slug)
                # Skip name check for downloaded environments - they can have duplicate names
                # Users will reference by env_id if names conflict
                env_id = registry_mgr.register_environment(
                    path=final_target,
                    env_type="temporary" if temp else "qbraid-managed",
                    slug=slug,
                    config=env_config,
                    is_temporary=temp,
                    skip_name_check=True,  # Allow duplicate names for downloaded environments
                    python_packages=python_packages,  # Pass directly to bypass PyPI validation
                )
                logger.info(
                    "Registered environment in registry: %s (env_id: %s, slug: %s)",
                    env_config.name,
                    env_id,
                    slug,
                )
            except Exception as reg_err:
                raise EnvironmentRegistryError(
                    f"Failed to register environment '{slug}' in registry: {reg_err}"
                ) from reg_err

            # Clean up temp file
            Path(temp_file_path).unlink(missing_ok=True)

            return {
                "status": "success",
                "env_id": env_id,
                "slug": slug,
                "target_dir": str(final_target),
                "temp": temp,
            }

        except EnvironmentOperationError:
            raise
        except Exception as err:
            # Clean up on failure
            if "temp_file_path" in locals():
                Path(temp_file_path).unlink(missing_ok=True)
            if final_target.exists():
                shutil.rmtree(final_target, ignore_errors=True)

            raise EnvironmentInstallError(f"Environment installation failed: {err}") from err

    async def publish_environment(
        self,
        identifier: str,
        overwrite: bool = False,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
    ) -> dict[str, Any]:
        """Publish environment to cloud storage (GCS) for global distribution.

        Creates the environment in the API first to get the slug, then prepares
        a copy with updated paths and uploads it.

        Args:
            identifier: Environment name (if unique) or env_id to publish
            overwrite: If True, overwrite existing published environment
            progress_callback: Optional callback function(stage, completed, total)
                for progress reporting (prepare/archive/upload).

        Returns:
            Dictionary with publish status and metadata

        Raises:
            EnvironmentValidationError: If publish arguments are invalid
            EnvironmentServiceRequestError: If API request fails
            EnvironmentOperationError: If preparation, archiving or upload fails
        """
        registry_mgr = EnvironmentRegistryManager()
        
        # Find environment in registry
        entry = None
        env_id = None
        
        found_by_name = registry_mgr.find_by_name(identifier)
        if found_by_name:
            env_id, entry = found_by_name
        else:
            found_by_id = registry_mgr.find_by_env_id(identifier)
            if found_by_id:
                env_id, entry = found_by_id
            else:
                raise EnvironmentValidationError(
                    f"Environment '{identifier}' not found. "
                    "Use name (if unique) or env_id to reference the environment."
                )

        env_path = entry.path

        # Validate environment path exists
        if not env_path.exists():
            raise EnvironmentValidationError(
                f"Environment path does not exist: {env_path}"
            )

        if not env_path.is_dir():
            raise EnvironmentValidationError(
                f"Environment path is not a directory: {env_path}"
            )

        # Convert EnvironmentEntry to EnvironmentConfig for API call
        env_config = EnvironmentConfig(
            name=entry.name,
            description=entry.description,
            tags=entry.tags,
            icon=entry.icon,
            python_version=entry.python_version,
            kernel_name=entry.kernel_name,
            shell_prompt=entry.shell_prompt,
            python_packages=entry.python_packages,
            visibility=entry.visibility,
        )

        # Step 1: Create environment in API to get slug
        if progress_callback:
            progress_callback("prepare", 0, 3)
        
        try:
            env_data = self.create_environment(env_config)
            slug = env_data.get("slug")
            if not slug:
                raise EnvironmentServiceRequestError(
                    "Create environment API did not return a slug"
                )
        except Exception as err:
            raise EnvironmentServiceRequestError(
                f"Failed to create environment in API: {err}"
            ) from err

        if progress_callback:
            progress_callback("prepare", 1, 3)

        # Step 2: Prepare environment copy with slug naming and updated paths
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            slug_env_path = temp_dir_path / slug

            def _prepare_environment_copy() -> None:
                """Copy environment and update paths for .qbraid/environments."""
                # Copy environment directory to temp location with slug name
                shutil.copytree(env_path, slug_env_path, symlinks=True, dirs_exist_ok=False)
                
                # Update paths in shebangs and activation scripts
                pyenv_path = slug_env_path / "pyenv"
                if pyenv_path.exists():
                    bin_dir = pyenv_path / "bin"
                    if bin_dir.exists():
                        # Expected path in published environment
                        expected_path = f"/home/jovyan/.qbraid/environments/{slug}/pyenv"
                        
                        # Fix executable shebangs
                        new_shebang = f"#!{expected_path}/bin/python3"
                        
                        for exe_file in bin_dir.iterdir():
                            if exe_file.is_file() and os.access(exe_file, os.X_OK):
                                try:
                                    with open(exe_file, "rb") as f:
                                        first_line = f.readline()
                                        if first_line.startswith(b"#!"):
                                            content = first_line + f.read()
                                            text_content = content.decode("utf-8", errors="ignore")
                                            lines = text_content.split("\n")
                                            # Update shebang to use .qbraid/environments path
                                            lines[0] = new_shebang
                                            new_content = "\n".join(lines).encode("utf-8")
                                            with open(exe_file, "wb") as out_f:
                                                out_f.write(new_content)
                                except (OSError, UnicodeDecodeError) as err:
                                    logger.warning("Failed to fix shebang in %s: %s", exe_file, err)
                        
                        # Fix activation script VIRTUAL_ENV
                        activate_script = bin_dir / "activate"
                        if activate_script.exists():
                            try:
                                with open(activate_script, "r", encoding="utf-8") as f:
                                    content = f.read()
                                
                                # Replace VIRTUAL_ENV path
                                pattern = r'VIRTUAL_ENV="[^"]*"'
                                replacement = f'VIRTUAL_ENV="{expected_path}"'
                                new_content = re.sub(pattern, replacement, content)
                                
                                if new_content != content:
                                    with open(activate_script, "w", encoding="utf-8") as f:
                                        f.write(new_content)
                            except (OSError, UnicodeDecodeError) as err:
                                logger.warning("Failed to fix activation script: %s", err)

            await asyncio.to_thread(_prepare_environment_copy)
            
            if progress_callback:
                progress_callback("prepare", 2, 3)

            # Step 3: Get upload signed URL from API
            try:
                response = self.session.post(
                    f"/environments/{slug}/upload-url",
                    json={"action": "publish", "overwrite": overwrite}
                )
                response.raise_for_status()
                data = response.json()

                # Handle new API response format: {success: true, data: {uploadUrl: ...}}
                if isinstance(data, dict) and data.get("success") and "data" in data:
                    upload_url = data["data"].get("uploadUrl")
                else:
                    # Legacy format fallback
                    upload_url = data.get("signedUrl") or data.get("uploadUrl")

                if not upload_url:
                    raise EnvironmentServiceRequestError(
                        f"Upload URL not found in API response for '{slug}'"
                    )
            except RequestsApiError as err:
                raise EnvironmentServiceRequestError(
                    f"Failed to get upload URL for environment '{slug}': {err}"
                ) from err

            if progress_callback:
                progress_callback("prepare", 3, 3)

            try:
                # Step 4: Create archive preserving symlinks
                def _create_archive() -> str:
                    """Create compressed archive synchronously, preserving symlinks."""
                    with tempfile.NamedTemporaryFile(suffix=".tar.zst", delete=False) as temp_archive:
                        archive_path = temp_archive.name

                        # Create tar archive preserving symlinks (default behavior)
                        with tarfile.open(archive_path, "w") as tar:
                            tar.add(slug_env_path, arcname=slug)
                            # Note: tarfile.add() preserves symlinks by default

                        # Compress with zstd
                        compressed_path = archive_path + ".compressed"
                        with open(archive_path, "rb") as f_in:
                            with open(compressed_path, "wb") as f_out:
                                cctx = zstd.ZstdCompressor()
                                cctx.copy_stream(f_in, f_out)

                        # Replace original with compressed
                        Path(archive_path).unlink()
                        Path(compressed_path).rename(archive_path)

                        if progress_callback:
                            archive_size = Path(archive_path).stat().st_size
                            progress_callback("archive", archive_size, archive_size)

                        return archive_path

                # Run archive creation in thread pool
                archive_path = await asyncio.to_thread(_create_archive)

                # Step 5: Upload to GCS using signed URL
                def _upload_archive() -> None:
                    """Upload archive synchronously."""
                    archive_size = Path(archive_path).stat().st_size

                    with open(archive_path, "rb") as f:
                        # Use requests to upload with progress
                        response = self.session.put(
                            upload_url,
                            data=f,
                            headers={"Content-Type": "application/zstd"}
                        )
                        response.raise_for_status()

                        if progress_callback:
                            progress_callback("upload", archive_size, archive_size)

                # Run upload in thread pool
                await asyncio.to_thread(_upload_archive)

                # Clean up archive
                Path(archive_path).unlink(missing_ok=True)

                # Update registry with slug
                try:
                    entry = registry_mgr.get_environment(env_id)
                    entry.slug = slug
                    registry_mgr.save_registry()
                    logger.info("Updated registry with slug %s for env_id %s", slug, env_id)
                except Exception as reg_err:
                    logger.warning("Failed to update registry with slug: %s", reg_err)

                return {
                    "status": "success",
                    "slug": slug,
                    "env_id": env_id,
                    "bucket": data.get("bucket"),
                    "path": data.get("path"),
                }

            except Exception as err:
                # Clean up on failure
                if "archive_path" in locals():
                    Path(archive_path).unlink(missing_ok=True)

                raise EnvironmentOperationError(
                    f"Failed to publish environment '{identifier}': {err}"
                ) from err

    async def _relocate_environment_paths(self, env_path: Path):
        """Fix hardcoded paths in relocated environment.

        Note:
            This operation is Lab/POSIX-specific and only runs in qBraid Lab.

        Raises:
            EnvironmentOperationError: If not running in qBraid Lab
        """
        # This operation is specific to qBraid Lab POSIX environments
        if not self.running_in_lab():
            raise EnvironmentOperationError(
                "Path relocation is only supported in qBraid Lab environment"
            )

        pyenv_path = env_path / "pyenv"
        if not pyenv_path.exists():
            return

        def _fix_paths() -> None:
            """Fix executable shebangs and activation script paths."""
            bin_dir = pyenv_path / "bin"
            if not bin_dir.exists():
                return

            # Fix executable shebangs
            shebang_pattern = re.compile(r"^#!.*\.qbraid/environments/.*/pyenv/bin/python3")
            new_shebang = f"#!{pyenv_path}/bin/python3"

            for exe_file in bin_dir.iterdir():
                if exe_file.is_file() and os.access(exe_file, os.X_OK):
                    try:
                        with open(exe_file, "rb") as f:
                            first_line = f.readline()
                            if first_line.startswith(b"#!"):
                                # Read the rest of the file
                                content = first_line + f.read()
                                text_content = content.decode("utf-8", errors="ignore")
                                if shebang_pattern.match(text_content.split("\n")[0]):
                                    # Replace shebang
                                    lines = text_content.split("\n")
                                    lines[0] = new_shebang
                                    new_content = "\n".join(lines).encode("utf-8")
                                    with open(exe_file, "wb") as out_f:
                                        out_f.write(new_content)
                    except (OSError, UnicodeDecodeError) as err:
                        logger.warning("Failed to fix shebang in %s: %s", exe_file, err)

            # Fix activation script VIRTUAL_ENV
            activate_script = pyenv_path / "bin" / "activate"
            if activate_script.exists():
                try:
                    with open(activate_script, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Replace VIRTUAL_ENV path
                    pattern = r'VIRTUAL_ENV="/.*\.qbraid/environments/.*/pyenv"'
                    replacement = f'VIRTUAL_ENV="{pyenv_path}"'
                    new_content = re.sub(pattern, replacement, content)

                    if new_content != content:
                        with open(activate_script, "w", encoding="utf-8") as f:
                            f.write(new_content)
                except (OSError, UnicodeDecodeError) as err:
                    logger.warning("Failed to fix activation script: %s", err)

        await asyncio.to_thread(_fix_paths)

    async def uninstall_environment_local(
        self, identifier: str, delete_metadata: bool = True, force: bool = False
    ) -> dict[str, Any]:
        """Uninstall a locally installed environment.

        Removes the environment directory from the local filesystem. Optionally
        also deletes the environment metadata from the qBraid API.

        Args:
            identifier: Environment name or env_id to uninstall.
            delete_metadata: If True, also delete environment from API (requires slug). Default True.
            force: If True, skip confirmation prompts. Default False.

        Returns:
            dict[str, Any]: Dictionary with status information.

        Raises:
            EnvironmentValidationError: If name conflicts and env_id not provided.
            EnvironmentRegistryError: If environment not found in registry.
            EnvironmentInstallError: If local removal fails.

        Example:
            >>> emc = EnvironmentManagerClient()
            >>> result = await emc.uninstall_environment_local('qiskit')  # by name
            >>> result = await emc.uninstall_environment_local('a1b2')  # by env_id
        """
        registry_mgr = EnvironmentRegistryManager()
        
        # Try to find by name first, then by env_id
        entry = None
        env_id = None
        
        found_by_name = registry_mgr.find_by_name(identifier)
        if found_by_name:
            env_id, entry = found_by_name
        else:
            found_by_id = registry_mgr.find_by_env_id(identifier)
            if found_by_id:
                env_id, entry = found_by_id
            else:
                raise EnvironmentRegistryError(
                    f"Environment '{identifier}' not found. "
                    "Use name (if unique) or env_id to reference the environment."
                )

        env_path = entry.path

        if not force:
            logger.warning("Removing environment at %s", env_path)

        try:
            # Remove local directory
            shutil.rmtree(env_path)
            logger.info("Removed environment directory: %s", env_path)

            # Remove from registry
            try:
                registry_mgr.unregister_environment(env_id)
                logger.debug("Removed environment from registry: %s", env_id)
            except Exception as err:
                raise EnvironmentRegistryError(
                    f"Failed to unregister environment '{env_id}' from registry: {err}"
                ) from err

            metadata_deleted = False

            # Optionally delete from API (requires slug)
            if delete_metadata and entry.slug:
                try:
                    self.delete_environment(entry.slug)
                    metadata_deleted = True
                    logger.info("Deleted environment metadata from API: %s", entry.slug)
                except Exception as err:
                    logger.warning("Failed to delete metadata for %s: %s", entry.slug, err)

            return {
                "status": "success",
                "env_id": env_id,
                "slug": entry.slug,
                "path": str(env_path),
                "deleted_metadata": metadata_deleted,
            }

        except EnvironmentRegistryError:
            raise
        except Exception as err:
            raise EnvironmentInstallError(
                f"Failed to uninstall environment '{identifier}': {err}"
            ) from err

    def register_external_environment(
        self,
        path: Path,
        name: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> dict[str, Any]:
        """Register an external Python environment with qBraid.

        Args:
            path: Path to the Python environment directory
            name: Environment name. If None, uses directory name.
            metadata: Additional metadata to store

        Returns:
            dict[str, Any]: Registration result with env_id, name, and path

        Raises:
            EnvironmentValidationError: If the provided path is invalid or name conflicts.
            EnvironmentRegistryError: If registration fails.

        Example:
            >>> emc = EnvironmentManagerClient()
            >>> result = emc.register_external_environment(
            ...     Path('/home/user/conda/envs/my_env'),
            ...     name='myenv'
            ... )
            >>> print(result)
            {'env_id': 'a1b2', 'name': 'myenv', 'path': '/home/user/conda/...'}
        """
        # Validate path
        if not path.exists() or not path.is_dir():
            raise EnvironmentValidationError(f"Path does not exist or is not a directory: {path}")

        # Find Python executable
        python_candidates = [
            path / "bin" / "python",
            path / "bin" / "python3",
            path / "Scripts" / "python.exe",
        ]

        python_path = None
        for candidate in python_candidates:
            if is_valid_python(candidate):
                python_path = candidate
                break

        if not python_path:
            raise EnvironmentValidationError(f"No valid Python executable found in {path}")

        # Generate name if not provided
        if not name:
            name = path.name

        # Get Python version
        try:
            python_version = get_python_version(Path(python_path))
        except Exception as err:
            logger.warning("Failed to get Python version: %s", err)
            python_version = "unknown"

        # Prepare metadata
        env_metadata = metadata or {}
        env_metadata.update(
            {
                "python_version": python_version,
                "python_path": str(python_path),
                "original_path": str(path.resolve()),
            }
        )

        # Register in registry
        registry_mgr = EnvironmentRegistryManager()
        try:
            env_id = registry_mgr.register_environment(
                path=path,
                env_type="external",
                name=name,
                slug=None,  # External environments don't have cloud slugs
                is_temporary=False,
                metadata=env_metadata,
            )
        except ValueError as name_err:
            # Name conflict
            raise EnvironmentValidationError(
                f"{name_err}. Please use the env_id to reference this environment."
            ) from name_err
        except Exception as err:
            raise EnvironmentRegistryError(
                f"Failed to register external environment: {err}"
            ) from err

        logger.info("Registered external environment: %s (env_id: %s) at %s", name, env_id, path)

        return {
            "env_id": env_id,
            "name": name,
            "path": str(path),
            "python_version": python_version,
        }

    def unregister_external_environment(self, identifier: str) -> dict[str, Any]:
        """Unregister an external environment from qBraid.

        This only removes the environment from the registry. The actual files
        are NOT deleted.

        Args:
            identifier: Environment name or env_id to unregister

        Returns:
            dict[str, Any]: Unregistration result

        Raises:
            EnvironmentValidationError: If name conflicts and env_id not provided.
            EnvironmentRegistryError: If environment not found or is not external

        Example:
            >>> emc = EnvironmentManagerClient()
            >>> result = emc.unregister_external_environment('myenv')  # by name
            >>> result = emc.unregister_external_environment('a1b2')  # by env_id
        """
        registry_mgr = EnvironmentRegistryManager()
        
        # Try to find by name first, then by env_id
        entry = None
        env_id = None
        
        found_by_name = registry_mgr.find_by_name(identifier)
        if found_by_name:
            env_id, entry = found_by_name
        else:
            found_by_id = registry_mgr.find_by_env_id(identifier)
            if found_by_id:
                env_id, entry = found_by_id
            else:
                raise EnvironmentRegistryError(
                    f"Environment '{identifier}' not found. "
                    "Use name (if unique) or env_id to reference the environment."
                )

        if entry.type != "external":
            raise EnvironmentRegistryError(
                f"Environment '{identifier}' is type '{entry.type}', not 'external'. "
                f"Use uninstall_environment_local() for qBraid-managed environments."
            )

        path = entry.path
        registry_mgr.unregister_environment(env_id)
        logger.info("Unregistered external environment: %s (env_id: %s)", entry.name, env_id)

        return {
            "status": "success",
            "env_id": env_id,
            "name": entry.name,
            "path": str(path),
        }

    def sync_registry(self) -> dict[str, int]:
        """Synchronize environment registry with filesystem.

        This will:
        - Remove registry entries where paths no longer exist
        - Auto-discover new qBraid environments in default paths
        - Verify all registered environments still exist

        Returns:
            dict[str, int]: Statistics about sync operation
                - removed: Number of invalid entries removed
                - discovered: Number of new environments discovered
                - verified: Number of existing entries verified

        Example:
            >>> emc = EnvironmentManagerClient()
            >>> stats = emc.sync_registry()
            >>> print(stats)
            {'removed': 1, 'discovered': 2, 'verified': 5}
        """
        registry_mgr = EnvironmentRegistryManager()
        stats = registry_mgr.sync_with_filesystem()

        logger.info("Registry sync complete: %s", stats)
        return stats

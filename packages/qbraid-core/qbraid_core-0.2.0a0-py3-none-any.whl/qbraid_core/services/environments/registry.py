# Copyright (c) 2025, qBraid Development Team
# All rights reserved.

"""
Module for managing the qBraid environment registry.

The registry provides a central source of truth for all Python environments
tracked by qBraid, including qBraid-managed, temporary, and external environments.
"""

import json
import logging
import secrets
import shutil
import string
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_serializer, field_validator

from .exceptions import EnvironmentNotFoundError
from .paths import extract_alias_from_path, get_default_envs_paths, is_temporary_location
from .schema import EnvironmentConfig
from .validate import is_valid_slug

logger = logging.getLogger(__name__)


def generate_env_id() -> str:
    """Generate a random 4-digit alphanumeric environment ID.

    Returns:
        str: 4-character alphanumeric ID (e.g., "a1b2", "x9k3")
    """
    chars = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(4))

EnvironmentType = Literal["qbraid-managed", "external", "temporary"]


class EnvironmentEntry(BaseModel):
    """Single environment entry in the registry.

    Attributes:
        env_id: Unique identifier on user's computer (4-digit alphanumeric, e.g., "a1b2")
        slug: Unique identifier on qBraid cloud database (optional, for cloud environments)
        path: Filesystem path to the environment
        type: Type of environment (qbraid-managed, external, temporary)
        name: Environment name (required, from EnvironmentConfig)
        description: Environment description
        tags: List of tags
        icon: Path to icon image file
        python_version: Python version (e.g., "3.11.0")
        kernel_name: Display name for Jupyter kernel
        shell_prompt: Shell prompt string
        python_packages: Dict of package names and version specifiers
        visibility: Visibility setting (default: "private")
        installed_at: ISO timestamp when environment was installed (qbraid-managed)
        registered_at: ISO timestamp when environment was registered (external)
        is_temporary: Whether this is a temporary environment
        metadata: Additional metadata about the environment (e.g., install status)
    """

    env_id: str  # Unique identifier on user's computer (4-digit alphanumeric)
    slug: Optional[str] = None  # Cloud identifier (for downloaded/published environments)
    path: Path
    type: EnvironmentType
    name: str  # Required field from EnvironmentConfig
    description: Optional[str] = None
    tags: Optional[list[str]] = None
    icon: Optional[Path] = None
    python_version: Optional[str] = None
    kernel_name: Optional[str] = None
    shell_prompt: Optional[str] = None
    python_packages: Optional[dict[str, str]] = None
    visibility: str = "private"
    installed_at: Optional[str] = None
    registered_at: Optional[str] = None
    is_temporary: bool = False
    metadata: dict = Field(default_factory=dict)

    @field_serializer("path")
    def serialize_path(self, path: Path) -> str:
        """Serialize Path to string."""
        return str(path)

    @field_validator("path", mode="before")
    @classmethod
    def validate_path(cls, v):
        """Convert string to Path if needed."""
        if isinstance(v, str):
            return Path(v)
        return v

    @field_validator("icon", mode="before")
    @classmethod
    def validate_icon(cls, v):
        """Convert string to Path if needed."""
        if isinstance(v, str):
            return Path(v)
        return v

    @field_serializer("icon")
    def serialize_icon(self, icon: Optional[Path]) -> Optional[str]:
        """Serialize Path to string."""
        return str(icon) if icon else None

    def get_base_alias(self) -> str:
        """Get base alias from name (name is required field).

        Returns:
            str: Environment name (used as base alias)
        """
        return self.name


# pylint: disable-next=too-few-public-methods
class EnvironmentRegistry(BaseModel):
    """Central registry for all qBraid-tracked environments.

    Attributes:
        version: Registry schema version
        environments: Dictionary mapping env_id to environment entry
    """

    version: str = "3.0"  # Updated to use env_id as key, slug stored in entry
    environments: dict[str, EnvironmentEntry] = Field(default_factory=dict)


class EnvironmentRegistryManager:
    """Manages the environment registry file.

    The registry is stored at ~/.qbraid/environments.json and tracks all
    Python environments that qBraid knows about, regardless of location or type.
    """

    def __init__(self, registry_path: Optional[Path] = None):
        """Initialize the registry manager.

        Args:
            registry_path: Path to registry file. Defaults to ~/.qbraid/environments.json
        """
        self.registry_path = registry_path or self._get_default_registry_path()
        self.registry = self.load_registry()

    @staticmethod
    def _get_default_registry_path() -> Path:
        """Get the default registry file path."""
        return Path.home() / ".qbraid" / "environments.json"

    def load_registry(self) -> EnvironmentRegistry:
        """Load registry from file, create if doesn't exist.

        Returns:
            EnvironmentRegistry: Loaded registry or new empty registry
        """
        if self.registry_path.exists():
            try:
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return EnvironmentRegistry(**data)
            except (json.JSONDecodeError, ValueError) as err:
                logger.warning("Failed to load registry, creating new one: %s", err)
                # Backup corrupted registry
                backup_path = self.registry_path.with_suffix(".json.backup")
                if self.registry_path.exists():
                    self.registry_path.rename(backup_path)
                    logger.info("Backed up corrupted registry to %s", backup_path)

        return EnvironmentRegistry()

    def save_registry(self) -> None:
        """Save registry to file."""
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)

        # Serialize with custom handling for Path objects
        registry_dict = self.registry.model_dump(mode="json")

        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(registry_dict, f, indent=2)

        logger.debug("Registry saved to %s", self.registry_path)

    def register_environment(
        self,
        path: Path,
        env_type: EnvironmentType,
        env_id: Optional[str] = None,
        slug: Optional[str] = None,
        config: Optional[EnvironmentConfig] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[list[str]] = None,
        icon: Optional[Path] = None,
        python_version: Optional[str] = None,
        kernel_name: Optional[str] = None,
        shell_prompt: Optional[str] = None,
        python_packages: Optional[dict[str, str]] = None,
        visibility: str = "private",
        is_temporary: bool = False,
        metadata: Optional[dict] = None,
        skip_name_check: bool = False,
    ) -> str:
        """Register a new environment.

        Args:
            path: Filesystem path to the environment
            env_type: Type of environment
            env_id: Environment ID (4-digit alphanumeric). If None, generates unique ID.
            slug: Cloud identifier (optional, for downloaded/published environments)
            config: EnvironmentConfig object (if provided, other fields are ignored)
            name: Environment name (required if config not provided)
            description: Environment description
            tags: List of tags
            icon: Path to icon image file
            python_version: Python version
            kernel_name: Display name for Jupyter kernel
            shell_prompt: Shell prompt string
            python_packages: Dict of package names and version specifiers
            visibility: Visibility setting (default: "private")
            is_temporary: Whether this is a temporary environment
            metadata: Additional metadata to store (e.g., install status)
            skip_name_check: If True, skip name conflict checking (for downloaded environments)

        Returns:
            str: The env_id used for registration

        Raises:
            ValueError: If name conflicts with existing environment and env_id not provided
        """
        now = datetime.now(timezone.utc).isoformat()

        # Use config if provided, otherwise use individual fields
        # Direct parameters override config values if both provided
        if config:
            env_name = config.name
            env_description = config.description
            env_tags = config.tags
            env_icon = config.icon
            env_python_version = config.python_version
            env_kernel_name = config.kernel_name
            env_shell_prompt = config.shell_prompt
            env_python_packages = python_packages if python_packages else config.python_packages
            env_visibility = config.visibility
        else:
            if name is None:
                raise ValueError("Either config or name must be provided")
            env_name = name
            env_description = description
            env_tags = tags
            env_icon = icon
            env_python_version = python_version
            env_kernel_name = kernel_name
            env_shell_prompt = shell_prompt
            env_python_packages = python_packages
            env_visibility = visibility

        # Generate unique env_id if not provided
        if env_id is None:
            env_id = self._generate_unique_env_id()

        # Check for name conflicts if name is provided and check is not skipped
        # Skip name check for downloaded environments (they can have duplicate names)
        if env_name and not skip_name_check:
            existing_by_name = self.find_by_name(env_name)
            if existing_by_name and existing_by_name[0] != env_id:
                raise ValueError(
                    f"Environment with name '{env_name}' already exists (env_id: {existing_by_name[0]}). "
                    f"Please use env_id '{existing_by_name[0]}' to reference it, or choose a different name."
                )

        # Create entry
        entry = EnvironmentEntry(
            env_id=env_id,
            slug=slug,
            path=path,
            type=env_type,
            name=env_name,
            description=env_description,
            tags=env_tags,
            icon=env_icon,
            python_version=env_python_version,
            kernel_name=env_kernel_name,
            shell_prompt=env_shell_prompt,
            python_packages=env_python_packages,
            visibility=env_visibility,
            installed_at=now if env_type in ("qbraid-managed", "temporary") else None,
            registered_at=now if env_type == "external" else None,
            is_temporary=is_temporary,
            metadata=metadata or {},
        )

        self.registry.environments[env_id] = entry
        self.save_registry()

        logger.info("Registered environment: %s (env_id: %s, slug: %s)", env_name, env_id, slug)
        return env_id

    def _generate_unique_env_id(self) -> str:
        """Generate a unique env_id that doesn't exist in registry.

        Returns:
            str: Unique 4-digit alphanumeric env_id
        """
        max_attempts = 100
        for _ in range(max_attempts):
            env_id = generate_env_id()
            if env_id not in self.registry.environments:
                return env_id
        raise RuntimeError("Failed to generate unique env_id after 100 attempts")

    def unregister_environment(self, env_id: str) -> None:
        """Remove environment from registry.

        Args:
            env_id: Environment ID to remove

        Raises:
            EnvironmentNotFoundError: If the environment is not found in the registry
        """
        if env_id not in self.registry.environments:
            raise EnvironmentNotFoundError(f"Environment '{env_id}' not found in registry")

        del self.registry.environments[env_id]
        self.save_registry()
        logger.info("Unregistered environment: %s", env_id)

    def get_environment(self, env_id: str) -> EnvironmentEntry:
        """Get environment entry by env_id.

        Args:
            env_id: Environment ID

        Returns:
            EnvironmentEntry: Environment entry

        Raises:
            EnvironmentNotFoundError: If the environment is not found in the registry
        """
        entry = self.registry.environments.get(env_id)
        if entry is None:
            raise EnvironmentNotFoundError(f"Environment '{env_id}' not found in registry")
        return entry

    def list_environments(
        self,
        env_type: Optional[EnvironmentType] = None,
        include_temporary: bool = True,
    ) -> dict[str, EnvironmentEntry]:
        """List all registered environments with optional filtering.

        Args:
            env_type: Filter by environment type
            include_temporary: Whether to include temporary environments

        Returns:
            dict[str, EnvironmentEntry]: Filtered environment entries
        """
        envs = self.registry.environments.copy()

        if env_type:
            envs = {k: v for k, v in envs.items() if v.type == env_type}

        if not include_temporary:
            envs = {k: v for k, v in envs.items() if not v.is_temporary}

        return envs

    def find_by_name(self, name: str) -> Optional[tuple[str, EnvironmentEntry]]:
        """Find environment by name.

        Args:
            name: Environment name to search for

        Returns:
            Optional[tuple[str, EnvironmentEntry]]: (env_id, entry) tuple or None
        """
        for env_id, entry in self.registry.environments.items():
            if entry.name == name:
                return (env_id, entry)
        return None

    def find_by_env_id(self, env_id: str) -> Optional[tuple[str, EnvironmentEntry]]:
        """Find environment by env_id.

        Args:
            env_id: Environment ID to search for

        Returns:
            Optional[tuple[str, EnvironmentEntry]]: (env_id, entry) tuple or None
        """
        if env_id in self.registry.environments:
            return (env_id, self.registry.environments[env_id])
        return None

    def find_by_slug(self, slug: str) -> Optional[tuple[str, EnvironmentEntry]]:
        """Find first environment by slug (cloud identifier).

        Note: Same slug can be installed multiple times with different env_ids.
        Use find_all_by_slug() to get all installations.

        Args:
            slug: Environment slug to search for

        Returns:
            Optional[tuple[str, EnvironmentEntry]]: (env_id, entry) tuple or None
        """
        for env_id, entry in self.registry.environments.items():
            if entry.slug == slug:
                return (env_id, entry)
        return None

    def find_all_by_slug(self, slug: str) -> list[tuple[str, EnvironmentEntry]]:
        """Find ALL environments with given slug.

        Same slug can be installed multiple times (different locations, different env_ids).
        This method returns all installations.

        Args:
            slug: Environment slug to search for

        Returns:
            list[tuple[str, EnvironmentEntry]]: List of (env_id, entry) tuples
        """
        results = []
        for env_id, entry in self.registry.environments.items():
            if entry.slug == slug:
                results.append((env_id, entry))
        return results

    def update_metadata(self, env_id: str, metadata: dict) -> None:
        """Update metadata for an environment.

        Args:
            env_id: Environment ID
            metadata: New metadata to merge with existing

        Raises:
            EnvironmentNotFoundError: If the environment is not found in the registry
        """
        if env_id not in self.registry.environments:
            raise EnvironmentNotFoundError(f"Environment '{env_id}' not found in registry")

        self.registry.environments[env_id].metadata.update(metadata)
        self.save_registry()
        logger.debug("Updated metadata for environment: %s", env_id)

    def update_environment(self, env_id: str, **kwargs) -> None:
        """Update environment entry fields.

        Args:
            env_id: Environment ID
            **kwargs: Fields to update (name, description, tags, python_packages,
                      kernel_name, shell_prompt, icon, visibility, etc.)

        Raises:
            EnvironmentNotFoundError: If the environment is not found in the registry
            ValueError: If attempting to update protected fields (env_id, slug, path)

        Example:
            >>> registry.update_environment("abc1", name="New Name", tags=["quantum"])
            >>> registry.update_environment("abc1", python_packages={"numpy": "1.24.0"})
        """
        # Protected fields that cannot be updated
        protected_fields = {"env_id", "slug", "type"}

        for field in kwargs:
            if field in protected_fields:
                raise ValueError(f"Cannot update protected field: '{field}'")

        if env_id not in self.registry.environments:
            raise EnvironmentNotFoundError(f"Environment '{env_id}' not found in registry")

        entry = self.registry.environments[env_id]
        for key, value in kwargs.items():
            if hasattr(entry, key):
                setattr(entry, key, value)
            else:
                logger.warning("Unknown field '%s' ignored for environment %s", key, env_id)

        self.save_registry()
        logger.debug("Updated environment: %s with fields: %s", env_id, list(kwargs.keys()))

    def sync_with_filesystem(self) -> dict[str, int]:
        """Sync registry with actual filesystem state.

        This will:
        1. Remove registry entries where paths no longer exist
        2. Auto-discover new qBraid environments in default paths
        3. Verify all registered environments still exist

        Returns:
            dict[str, int]: Statistics about sync operation
                - removed: Number of invalid entries removed
                - discovered: Number of new environments discovered
                - verified: Number of existing entries verified
        """
        stats = {"removed": 0, "discovered": 0, "verified": 0}

        # Remove entries where path no longer exists
        to_remove = []
        for env_id, entry in self.registry.environments.items():
            if not entry.path.exists():
                to_remove.append(env_id)
                logger.info("Removing registry entry with missing path: %s (env_id: %s)", entry.name, env_id)

        for env_id in to_remove:
            self.unregister_environment(env_id)
            stats["removed"] += 1

        env_paths = get_default_envs_paths()

        for env_path in env_paths:
            if not env_path.exists():
                continue

            try:
                env_dir: Path
                for env_dir in env_path.iterdir():
                    if not env_dir.is_dir():
                        continue

                    # Check if this directory is already registered (by path)
                    already_registered = False
                    for entry in self.registry.environments.values():
                        if entry.path == env_dir:
                            stats["verified"] += 1
                            already_registered = True
                            break

                    if already_registered:
                        continue

                    # Auto-register discovered environment
                    # Extract name from path (registry is now single source of truth)
                    # For backward compatibility, try to read from qbraid.yaml if it exists
                    name = None
                    config = None
                    slug = None

                    # Try to read from qbraid.yaml for migration (optional)
                    env_config_path = env_dir / "qbraid.yaml"
                    if env_config_path.exists():
                        try:
                            config = EnvironmentConfig.from_yaml(env_config_path)
                            name = config.name
                        except Exception:  # pylint: disable=broad-exception-caught
                            pass

                    # If directory name looks like a slug (name_abc123), extract slug
                    if is_valid_slug(env_dir.name):
                        slug = env_dir.name

                    # Fall back to path extraction for name
                    if name is None:
                        name = extract_alias_from_path(env_dir)

                    is_temp = is_temporary_location(env_dir)

                    # Register with config if available, otherwise just name
                    # Skip name check for auto-discovered environments (they may have duplicate names)
                    try:
                        if config:
                            self.register_environment(
                                path=env_dir,
                                env_type="temporary" if is_temp else "qbraid-managed",
                                slug=slug,
                                config=config,
                                is_temporary=is_temp,
                                skip_name_check=True,  # Allow duplicate names for auto-discovered
                            )
                        else:
                            self.register_environment(
                                path=env_dir,
                                env_type="temporary" if is_temp else "qbraid-managed",
                                slug=slug,
                                name=name,
                                is_temporary=is_temp,
                                skip_name_check=True,  # Allow duplicate names for auto-discovered
                            )
                        stats["discovered"] += 1
                        logger.info("Auto-discovered environment: %s", env_dir.name)
                    except Exception as err:
                        # Log and skip on any error during auto-discovery
                        logger.warning("Skipping environment during auto-discovery: %s", err)
                        continue

            except PermissionError as err:
                logger.warning("Permission denied accessing %s: %s", env_path, err)
                continue

        if stats["removed"] or stats["discovered"]:
            self.save_registry()

        logger.info("Registry sync complete: %s", stats)
        return stats

    def cleanup_temporary(self) -> list[str]:
        """Remove all temporary environments from registry and filesystem.

        Returns:
            list[str]: List of env_ids that were removed
        """
        removed = []

        for env_id, entry in list(self.registry.environments.items()):
            if not entry.is_temporary:
                continue

            # Remove from filesystem
            if entry.path.exists():
                try:
                    shutil.rmtree(entry.path)
                    logger.info("Removed temporary environment: %s", entry.path)
                except Exception as err:  # pylint: disable=broad-exception-caught
                    logger.error("Failed to remove temporary environment %s: %s", env_id, err)
                    continue

            # Remove from registry
            self.unregister_environment(env_id)
            removed.append(env_id)

        return removed

    def export_to_file(self, output_path: Path) -> None:
        """Export registry to a JSON file.

        Args:
            output_path: Path to output file
        """
        registry_dict = self.registry.model_dump(mode="json")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(registry_dict, f, indent=2)

        logger.info("Registry exported to %s", output_path)

    def get_stats(self) -> dict[str, int]:
        """Get statistics about registered environments.

        Returns:
            dict[str, int]: Statistics including total count and counts by type
        """
        total = len(self.registry.environments)
        by_type: dict[str, int] = {}
        temporary_count = 0

        for entry in self.registry.environments.values():
            by_type[entry.type] = by_type.get(entry.type, 0) + 1
            if entry.is_temporary:
                temporary_count += 1

        return {
            "total": total,
            "qbraid_managed": by_type.get("qbraid-managed", 0),
            "external": by_type.get("external", 0),
            "temporary_total": by_type.get("temporary", 0),
            "temporary_marked": temporary_count,
        }

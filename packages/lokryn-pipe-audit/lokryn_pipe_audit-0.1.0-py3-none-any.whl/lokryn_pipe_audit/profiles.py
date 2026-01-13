"""Profile management for external storage providers.

Profiles define how pipe-audit-core connects to external systems (S3, local)
for reading/writing validated data. They are loaded from a `profiles.toml`
file at runtime and may contain environment-variable references for sensitive values.

Example profiles.toml:
    [s3_profile]
    provider = "s3"
    region = "us-east-1"
    access_key = "${AWS_ACCESS_KEY_ID}"
    secret_key = "${AWS_SECRET_ACCESS_KEY}"

    [local_profile]
    provider = "local"
"""

from __future__ import annotations

import os
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import ProfileLoadError, ProfileNotFoundError


@dataclass
class Profile:
    """A single profile definition for connecting to an external provider.

    Fields are provider-specific. Only the relevant subset is used depending
    on the `provider` value ("s3", "local", etc.).

    Attributes:
        provider: Provider type ("s3", "local")
        endpoint: Optional custom endpoint URL (for S3-compatible storage)
        region: AWS region (S3)
        access_key: AWS access key ID (S3)
        secret_key: AWS secret access key (S3)
        path_style: Use path-style addressing for S3 (for MinIO, etc.)
    """

    provider: str
    endpoint: str | None = None
    region: str | None = None
    access_key: str | None = None
    secret_key: str | None = None
    path_style: bool | None = None
    # GCS
    service_account_json: str | None = None
    # Azure
    connection_string: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Profile:
        """Create a Profile from a dictionary."""
        return cls(
            provider=data.get("provider", "local"),
            endpoint=data.get("endpoint"),
            region=data.get("region"),
            access_key=data.get("access_key"),
            secret_key=data.get("secret_key"),
            path_style=data.get("path_style"),
            service_account_json=data.get("service_account_json"),
            connection_string=data.get("connection_string"),
        )


# Type alias for a collection of profiles keyed by name
Profiles = dict[str, Profile]


def expand_env_vars(value: str) -> str:
    """Expand ${VAR} placeholders into environment variable values.

    Supports multiple placeholders in a single string.

    Args:
        value: String potentially containing ${VAR} placeholders

    Returns:
        String with placeholders replaced by environment variable values.
        If a variable is not set, the original placeholder is preserved.

    Examples:
        >>> os.environ["MY_VAR"] = "hello"
        >>> expand_env_vars("${MY_VAR}")
        'hello'
        >>> expand_env_vars("prefix-${MY_VAR}-suffix")
        'prefix-hello-suffix'
    """
    pattern = r"\$\{([^}]+)\}"

    def replacer(match: re.Match[str]) -> str:
        var_name = match.group(1)
        return os.environ.get(var_name, match.group(0))

    return re.sub(pattern, replacer, value)


def _expand_profile_fields(profile: Profile) -> None:
    """Expand environment variables in sensitive profile fields (in-place)."""
    if profile.access_key is not None:
        profile.access_key = expand_env_vars(profile.access_key)
    if profile.secret_key is not None:
        profile.secret_key = expand_env_vars(profile.secret_key)
    if profile.endpoint is not None:
        profile.endpoint = expand_env_vars(profile.endpoint)
    if profile.service_account_json is not None:
        profile.service_account_json = expand_env_vars(profile.service_account_json)
    if profile.connection_string is not None:
        profile.connection_string = expand_env_vars(profile.connection_string)


def load_profiles(path: str | Path = "profiles.toml") -> Profiles:
    """Load all profiles from a TOML file, expanding environment variables.

    Args:
        path: Path to the profiles TOML file (default: "profiles.toml")

    Returns:
        Dictionary mapping profile names to Profile objects

    Raises:
        ProfileLoadError: If the file cannot be read or parsed

    Example:
        >>> profiles = load_profiles()
        >>> s3_profile = profiles["s3_profile"]
        >>> print(s3_profile.region)
        'us-east-1'
    """
    path = Path(path)

    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ProfileLoadError(f"Profiles file not found: {path}", str(path))
    except OSError as e:
        raise ProfileLoadError(f"Error reading profiles file: {e}", str(path))

    try:
        data = tomllib.loads(content)
    except tomllib.TOMLDecodeError as e:
        raise ProfileLoadError(f"Invalid TOML: {e}", str(path))

    profiles: Profiles = {}
    for name, profile_data in data.items():
        if isinstance(profile_data, dict):
            profile = Profile.from_dict(profile_data)
            _expand_profile_fields(profile)
            profiles[name] = profile

    return profiles


def get_profile(profiles: Profiles, name: str) -> Profile:
    """Get a profile by name.

    Args:
        profiles: Dictionary of loaded profiles
        name: Profile name to look up

    Returns:
        The requested Profile

    Raises:
        ProfileNotFoundError: If the profile does not exist
    """
    if name not in profiles:
        raise ProfileNotFoundError(name)
    return profiles[name]

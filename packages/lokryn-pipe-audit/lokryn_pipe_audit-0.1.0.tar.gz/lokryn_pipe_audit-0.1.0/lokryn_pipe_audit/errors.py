"""Custom exception hierarchy for pipe-audit-core."""

from __future__ import annotations


class ValidationError(Exception):
    """Base exception for all validation errors."""

    pass


class ContractParseError(ValidationError):
    """Contract TOML parsing or schema validation error."""

    def __init__(self, message: str, path: str | None = None) -> None:
        self.path = path
        super().__init__(f"{message}" + (f" (file: {path})" if path else ""))


class ConnectorError(ValidationError):
    """Error connecting to or fetching from a data source."""

    def __init__(self, message: str, connector_type: str | None = None) -> None:
        self.connector_type = connector_type
        super().__init__(f"{message}" + (f" (connector: {connector_type})" if connector_type else ""))


class ProfileNotFoundError(ValidationError):
    """Requested profile does not exist in profiles.toml."""

    def __init__(self, profile_name: str) -> None:
        self.profile_name = profile_name
        super().__init__(f"Profile not found: {profile_name}")


class ProfileLoadError(ValidationError):
    """Error loading or parsing profiles.toml."""

    def __init__(self, message: str, path: str | None = None) -> None:
        self.path = path
        super().__init__(f"{message}" + (f" (file: {path})" if path else ""))


class DriverError(ValidationError):
    """Error loading or parsing data with a driver."""

    def __init__(self, message: str, driver_type: str | None = None) -> None:
        self.driver_type = driver_type
        super().__init__(f"{message}" + (f" (driver: {driver_type})" if driver_type else ""))


class UnsupportedFormatError(DriverError):
    """File format is not supported."""

    def __init__(self, extension: str) -> None:
        self.extension = extension
        super().__init__(f"Unsupported file format: {extension}")


class PatternError(ValidationError):
    """Invalid regex pattern in validation rule."""

    def __init__(self, pattern: str, error: str) -> None:
        self.pattern = pattern
        self.error = error
        super().__init__(f"Invalid regex pattern '{pattern}': {error}")


class MovementError(ValidationError):
    """Error moving/writing data to destination or quarantine."""

    def __init__(self, message: str, location: str | None = None) -> None:
        self.location = location
        super().__init__(f"{message}" + (f" (location: {location})" if location else ""))

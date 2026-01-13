"""File movement orchestration for pipe-audit-core.

This module handles writing validated data to its final destination
(success path) or to quarantine (failure path). It supports local
filesystem and S3 backends and integrates with configured profiles.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import polars as pl

from .connectors import LocalConnector, S3Connector, get_connector
from .contracts import Destination, Quarantine, Source
from .drivers import CsvDriver, ParquetDriver
from .errors import MovementError
from .profiles import Profiles, get_profile


class FileMovement:
    """File movement orchestrator.

    Handles writing data to destination or quarantine locations.
    """

    @staticmethod
    async def validate_profiles(
        source: Source | None,
        destination: Destination | None,
        quarantine: Quarantine | None,
        profiles: Profiles,
    ) -> tuple[bool, bool, bool]:
        """Validate connectivity for source, destination, and quarantine profiles.

        Args:
            source: Source configuration
            destination: Destination configuration
            quarantine: Quarantine configuration
            profiles: Loaded profiles

        Returns:
            Tuple of (source_valid, dest_valid, quarantine_valid)
        """
        source_valid = await FileMovement._test_profile_connectivity(
            profile_name=source.profile if source else None,
            destination_type=source.type if source else None,
            profiles=profiles,
        )

        dest_valid = await FileMovement._test_profile_connectivity(
            profile_name=destination.profile if destination else None,
            destination_type=destination.type if destination else None,
            profiles=profiles,
        )

        quarantine_valid = await FileMovement._test_profile_connectivity(
            profile_name=quarantine.profile if quarantine else None,
            destination_type=quarantine.type if quarantine else None,
            profiles=profiles,
        )

        return source_valid, dest_valid, quarantine_valid

    @staticmethod
    async def _test_profile_connectivity(
        profile_name: str | None,
        destination_type: str | None,
        profiles: Profiles,
    ) -> bool:
        """Test connectivity for a given profile/type.

        Args:
            profile_name: Name of the profile to test
            destination_type: Type of destination
            profiles: Loaded profiles

        Returns:
            True if connectivity is valid
        """
        if destination_type in ("local", "not_moved", None):
            return True

        if profile_name is None:
            return False

        if profile_name not in profiles:
            return False

        # For S3, we could test connectivity by listing buckets
        # For now, assume valid if profile exists
        return True

    @staticmethod
    def generate_filename(
        original_location: str,
        is_quarantine: bool = False,
        format_override: str | None = None,
    ) -> str:
        """Generate a unique filename with timestamp.

        Args:
            original_location: Original file path/URL
            is_quarantine: Whether this is for quarantine (adds suffix)
            format_override: Optional format override (e.g., "csv", "parquet")

        Returns:
            Generated filename with timestamp
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        # Extract stem from path
        path = Path(original_location.split("/")[-1])
        stem = path.stem

        # Determine extension
        if format_override:
            extension = format_override.lstrip(".")
        elif path.suffix:
            extension = path.suffix.lstrip(".")
        else:
            extension = "csv"

        if is_quarantine:
            return f"{stem}_{timestamp}_quarantine.{extension}"
        return f"{stem}_{timestamp}.{extension}"

    @staticmethod
    def _build_destination_path(base_location: str, filename: str) -> str:
        """Build a full destination path.

        Args:
            base_location: Base directory or URL
            filename: Filename to append

        Returns:
            Full path
        """
        if base_location.endswith("/"):
            return f"{base_location}{filename}"
        return f"{base_location}/{filename}"

    @staticmethod
    def serialize_dataframe(df: pl.DataFrame, format_type: str) -> bytes:
        """Serialize a DataFrame to bytes.

        Args:
            df: DataFrame to serialize
            format_type: Output format ("csv" or "parquet")

        Returns:
            Serialized bytes

        Raises:
            MovementError: If format is not supported
        """
        format_lower = format_type.lower().strip(".")

        if format_lower == "csv":
            driver = CsvDriver()
            return driver.save(df)
        elif format_lower == "parquet":
            driver = ParquetDriver()
            return driver.save(df)
        else:
            raise MovementError(f"Unsupported output format: {format_type}")

    @staticmethod
    async def write_success_data(
        df: pl.DataFrame,
        original_location: str,
        destination: Destination,
        profiles: Profiles,
    ) -> None:
        """Write validated data to the configured destination.

        Args:
            df: DataFrame to write
            original_location: Original source location (for filename)
            destination: Destination configuration
            profiles: Loaded profiles

        Raises:
            MovementError: If write fails
        """
        if destination.type == "not_moved":
            return

        filename = FileMovement.generate_filename(
            original_location,
            is_quarantine=False,
            format_override=destination.format,
        )

        format_type = destination.format or "csv"
        data = FileMovement.serialize_dataframe(df, format_type)

        if destination.location is None:
            raise MovementError("Destination missing location")

        full_path = FileMovement._build_destination_path(
            destination.location,
            filename,
        )

        await FileMovement._write_data(
            data=data,
            location=full_path,
            connector_type=destination.type,
            profile_name=destination.profile,
            profiles=profiles,
        )

    @staticmethod
    async def write_quarantine_data(
        df: pl.DataFrame,
        original_location: str,
        quarantine: Quarantine,
        profiles: Profiles,
    ) -> None:
        """Write failed data to the configured quarantine.

        Args:
            df: DataFrame to write
            original_location: Original source location (for filename)
            quarantine: Quarantine configuration
            profiles: Loaded profiles

        Raises:
            MovementError: If write fails
        """
        if quarantine.type == "not_moved":
            return

        filename = FileMovement.generate_filename(
            original_location,
            is_quarantine=True,
            format_override=quarantine.format,
        )

        format_type = quarantine.format or "csv"
        data = FileMovement.serialize_dataframe(df, format_type)

        if quarantine.location is None:
            raise MovementError("Quarantine missing location")

        full_path = FileMovement._build_destination_path(
            quarantine.location,
            filename,
        )

        await FileMovement._write_data(
            data=data,
            location=full_path,
            connector_type=quarantine.type,
            profile_name=quarantine.profile,
            profiles=profiles,
        )

    @staticmethod
    async def _write_data(
        data: bytes,
        location: str,
        connector_type: str,
        profile_name: str | None,
        profiles: Profiles,
    ) -> None:
        """Write data via the appropriate connector.

        Args:
            data: Bytes to write
            location: Destination location
            connector_type: Type of connector
            profile_name: Profile name for credentials
            profiles: Loaded profiles

        Raises:
            MovementError: If write fails
        """
        try:
            profile = None
            if profile_name:
                profile = get_profile(profiles, profile_name)

            connector = get_connector(connector_type, profile, location)
            await connector.put(location, data)
        except Exception as e:
            raise MovementError(f"Failed to write data: {e}", location)

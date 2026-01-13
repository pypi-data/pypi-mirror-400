"""Data format drivers for loading and saving data files.

Drivers provide a uniform interface for parsing different file formats
(CSV, Parquet, etc.) into Polars DataFrames.
"""

from __future__ import annotations

import io
from typing import Protocol

import polars as pl

from .errors import DriverError, UnsupportedFormatError


class Driver(Protocol):
    """Protocol that all drivers implement to load/save data."""

    def load(self, data: bytes) -> pl.DataFrame:
        """Load data from an in-memory byte slice into a DataFrame.

        Args:
            data: Raw file bytes

        Returns:
            Polars DataFrame

        Raises:
            DriverError: If parsing fails
        """
        ...

    def save(self, df: pl.DataFrame) -> bytes:
        """Save a DataFrame to an in-memory byte slice.

        Args:
            df: Polars DataFrame to serialize

        Returns:
            Raw file bytes

        Raises:
            DriverError: If serialization fails
        """
        ...


class CsvDriver:
    """CSV file driver.

    Loads and saves CSV data using Polars. Assumes first row contains headers.
    """

    def load(self, data: bytes) -> pl.DataFrame:
        """Load CSV data from memory into a DataFrame.

        Args:
            data: Raw CSV bytes (UTF-8 encoded)

        Returns:
            Polars DataFrame

        Raises:
            DriverError: If CSV parsing fails
        """
        try:
            return pl.read_csv(io.BytesIO(data))
        except Exception as e:
            raise DriverError(f"Failed to parse CSV: {e}", "csv")

    def save(self, df: pl.DataFrame) -> bytes:
        """Save a DataFrame to CSV bytes.

        Args:
            df: Polars DataFrame to serialize

        Returns:
            CSV bytes

        Raises:
            DriverError: If serialization fails
        """
        try:
            buffer = io.BytesIO()
            df.write_csv(buffer)
            return buffer.getvalue()
        except Exception as e:
            raise DriverError(f"Failed to write CSV: {e}", "csv")


class ParquetDriver:
    """Parquet file driver.

    Loads and saves Parquet data using Polars.
    """

    def load(self, data: bytes) -> pl.DataFrame:
        """Load Parquet data from memory into a DataFrame.

        Args:
            data: Raw Parquet bytes

        Returns:
            Polars DataFrame

        Raises:
            DriverError: If Parquet parsing fails
        """
        try:
            return pl.read_parquet(io.BytesIO(data))
        except Exception as e:
            raise DriverError(f"Failed to parse Parquet: {e}", "parquet")

    def save(self, df: pl.DataFrame) -> bytes:
        """Save a DataFrame to Parquet bytes.

        Args:
            df: Polars DataFrame to serialize

        Returns:
            Parquet bytes

        Raises:
            DriverError: If serialization fails
        """
        try:
            buffer = io.BytesIO()
            df.write_parquet(buffer)
            return buffer.getvalue()
        except Exception as e:
            raise DriverError(f"Failed to write Parquet: {e}", "parquet")


# Mapping of file extensions to driver instances
_DRIVERS: dict[str, Driver] = {
    "csv": CsvDriver(),
    "parquet": ParquetDriver(),
}


def get_driver(extension: str) -> Driver:
    """Get the appropriate driver for a file extension.

    Args:
        extension: File extension (e.g., "csv", "parquet")

    Returns:
        Driver instance for the format

    Raises:
        UnsupportedFormatError: If the extension is not supported
    """
    ext = extension.lower().lstrip(".")
    if ext not in _DRIVERS:
        raise UnsupportedFormatError(ext)
    return _DRIVERS[ext]


def get_extension_from_path(path: str) -> str:
    """Extract the file extension from a path.

    Args:
        path: File path or URL

    Returns:
        File extension without the leading dot

    Examples:
        >>> get_extension_from_path("data/file.csv")
        'csv'
        >>> get_extension_from_path("s3://bucket/file.parquet")
        'parquet'
    """
    # Handle S3 URLs and local paths
    # Extract the last component after / and get extension
    filename = path.rsplit("/", 1)[-1]
    if "." in filename:
        return filename.rsplit(".", 1)[-1].lower()
    return ""

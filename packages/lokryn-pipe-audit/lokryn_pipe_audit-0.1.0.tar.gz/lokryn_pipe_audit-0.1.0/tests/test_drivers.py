"""Tests for drivers module."""

from __future__ import annotations

import polars as pl
import pytest

from lokryn_pipe_audit.drivers import (
    CsvDriver,
    ParquetDriver,
    get_driver,
    get_extension_from_path,
)
from lokryn_pipe_audit.errors import UnsupportedFormatError


class TestCsvDriver:
    """Tests for CsvDriver."""

    def test_load_csv(self):
        csv_data = b"col_a,col_b\n1,one\n2,two\n3,three"
        driver = CsvDriver()
        df = driver.load(csv_data)
        assert df.shape == (3, 2)
        assert df.columns == ["col_a", "col_b"]

    def test_save_csv(self):
        df = pl.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
        driver = CsvDriver()
        data = driver.save(df)
        assert b"a,b" in data
        assert b"1,x" in data

    def test_round_trip(self):
        df = pl.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
        driver = CsvDriver()
        data = driver.save(df)
        loaded = driver.load(data)
        assert loaded.shape == df.shape
        assert loaded.columns == df.columns


class TestParquetDriver:
    """Tests for ParquetDriver."""

    def test_round_trip(self):
        df = pl.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
        driver = ParquetDriver()
        data = driver.save(df)
        loaded = driver.load(data)
        assert loaded.shape == df.shape
        assert loaded.columns == df.columns


class TestGetDriver:
    """Tests for get_driver factory."""

    def test_get_csv_driver(self):
        driver = get_driver("csv")
        assert isinstance(driver, CsvDriver)

    def test_get_parquet_driver(self):
        driver = get_driver("parquet")
        assert isinstance(driver, ParquetDriver)

    def test_get_driver_with_dot(self):
        driver = get_driver(".csv")
        assert isinstance(driver, CsvDriver)

    def test_get_driver_uppercase(self):
        driver = get_driver("CSV")
        assert isinstance(driver, CsvDriver)

    def test_unsupported_format(self):
        with pytest.raises(UnsupportedFormatError):
            get_driver("xlsx")


class TestGetExtensionFromPath:
    """Tests for get_extension_from_path."""

    def test_local_path(self):
        assert get_extension_from_path("data/file.csv") == "csv"

    def test_s3_path(self):
        assert get_extension_from_path("s3://bucket/key/file.parquet") == "parquet"

    def test_no_extension(self):
        assert get_extension_from_path("data/file") == ""

    def test_uppercase_extension(self):
        assert get_extension_from_path("data/file.CSV") == "csv"

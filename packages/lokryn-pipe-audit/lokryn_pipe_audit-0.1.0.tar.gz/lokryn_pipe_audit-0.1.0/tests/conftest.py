"""Pytest fixtures for pipe-audit-core tests."""

from __future__ import annotations

import pytest
import polars as pl

from lokryn_pipe_audit import Executor, InMemoryLogger


@pytest.fixture
def sample_df() -> pl.DataFrame:
    """Create a sample DataFrame for testing."""
    return pl.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "name": ["Alice", "Bob", "Charlie", None, "Eve"],
        "age": [25, 30, 35, 40, 45],
        "email": ["alice@example.com", "bob@example.com", "charlie@example.com", None, "eve@example.com"],
        "status": ["active", "active", "inactive", "active", "pending"],
    })


@pytest.fixture
def all_valid_df() -> pl.DataFrame:
    """Create a DataFrame with all valid (non-null, unique) values."""
    return pl.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "score": [85.5, 92.0, 78.5],
    })


@pytest.fixture
def df_with_nulls() -> pl.DataFrame:
    """Create a DataFrame with null values."""
    return pl.DataFrame({
        "col": ["a", None, "b", None, "c"],
    })


@pytest.fixture
def df_with_duplicates() -> pl.DataFrame:
    """Create a DataFrame with duplicate values."""
    return pl.DataFrame({
        "col": [1, 2, 2, 3, 3],
    })


@pytest.fixture
def numeric_df() -> pl.DataFrame:
    """Create a DataFrame with numeric values for statistical tests."""
    return pl.DataFrame({
        "values": [10.0, 20.0, 30.0, 40.0, 50.0],
    })


@pytest.fixture
def executor() -> Executor:
    """Create a test executor."""
    return Executor(user="test_user", host="test_host")


@pytest.fixture
def logger() -> InMemoryLogger:
    """Create an in-memory logger for testing."""
    return InMemoryLogger()


@pytest.fixture
def sample_contract_toml() -> str:
    """Create a sample contract TOML string."""
    return """
[contract]
name = "test_contract"
version = "1.0.0"
tags = ["test"]

[file]
validation = [
    { rule = "row_count", min = 1, max = 100 }
]

[[columns]]
name = "id"
validation = [
    { rule = "not_null" },
    { rule = "unique" }
]

[[columns]]
name = "name"
validation = [
    { rule = "completeness", min_ratio = 0.8 }
]

[[columns]]
name = "status"
validation = [
    { rule = "in_set", values = ["active", "inactive", "pending"] }
]

[source]
type = "local"
location = "data/test.csv"

[destination]
type = "local"
location = "output/"
"""


@pytest.fixture
def sample_profiles_toml() -> str:
    """Create a sample profiles TOML string."""
    return """
[local_profile]
provider = "local"

[s3_profile]
provider = "s3"
region = "us-east-1"
access_key = "test_key"
secret_key = "test_secret"
"""

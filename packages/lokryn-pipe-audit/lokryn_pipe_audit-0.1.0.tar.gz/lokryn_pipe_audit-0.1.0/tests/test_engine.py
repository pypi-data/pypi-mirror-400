"""Tests for engine module."""

from __future__ import annotations

import polars as pl
import pytest

from lokryn_pipe_audit.contracts import (
    ColumnContracts,
    CompoundUnique,
    Contract,
    FileContracts,
    RuleType,
    SchemaContracts,
    ValidationRule,
)
from lokryn_pipe_audit.engine import validate_dataframe
from lokryn_pipe_audit.logging import InMemoryLogger


class TestValidateDataframe:
    """Tests for validate_dataframe."""

    def test_file_level_validation(self):
        df = pl.DataFrame({"col": [1, 2, 3, 4, 5]})
        contracts = SchemaContracts(
            contract=Contract(name="test", version="1.0.0"),
            file=FileContracts(
                validation=[
                    ValidationRule(
                        rule_type=RuleType.ROW_COUNT,
                        params={"min": 1, "max": 10},
                    )
                ]
            ),
            columns=[],
        )

        results = validate_dataframe(df, contracts)
        assert len(results) == 1
        assert results[0].column == "file"
        assert results[0].rule == "row_count"
        assert results[0].result == "pass"

    def test_column_level_validation(self):
        df = pl.DataFrame({"id": [1, 2, 3]})
        contracts = SchemaContracts(
            contract=Contract(name="test", version="1.0.0"),
            columns=[
                ColumnContracts(
                    name="id",
                    validation=[
                        ValidationRule(rule_type=RuleType.NOT_NULL),
                        ValidationRule(rule_type=RuleType.UNIQUE),
                    ],
                )
            ],
        )

        results = validate_dataframe(df, contracts)
        assert len(results) == 2
        assert all(r.column == "id" for r in results)
        assert all(r.result == "pass" for r in results)

    def test_column_validation_fails(self):
        df = pl.DataFrame({"id": [1, 1, 3]})  # Duplicate values
        contracts = SchemaContracts(
            contract=Contract(name="test", version="1.0.0"),
            columns=[
                ColumnContracts(
                    name="id",
                    validation=[ValidationRule(rule_type=RuleType.UNIQUE)],
                )
            ],
        )

        results = validate_dataframe(df, contracts)
        assert len(results) == 1
        assert results[0].result == "fail"

    def test_compound_validation(self):
        df = pl.DataFrame({
            "a": [1, 1, 2],
            "b": ["x", "y", "x"],
        })
        contracts = SchemaContracts(
            contract=Contract(name="test", version="1.0.0"),
            columns=[],
            compound_unique=[CompoundUnique(columns=["a", "b"])],
        )

        results = validate_dataframe(df, contracts)
        assert len(results) == 1
        assert results[0].column == "compound"
        assert results[0].rule == "compound_unique"
        assert results[0].result == "pass"

    def test_compound_validation_fails(self):
        df = pl.DataFrame({
            "a": [1, 1, 1],
            "b": ["x", "x", "y"],
        })
        contracts = SchemaContracts(
            contract=Contract(name="test", version="1.0.0"),
            columns=[],
            compound_unique=[CompoundUnique(columns=["a", "b"])],
        )

        results = validate_dataframe(df, contracts)
        assert len(results) == 1
        assert results[0].result == "fail"

    def test_mixed_validation(self, sample_df):
        contracts = SchemaContracts(
            contract=Contract(name="test", version="1.0.0"),
            file=FileContracts(
                validation=[
                    ValidationRule(
                        rule_type=RuleType.ROW_COUNT,
                        params={"min": 1, "max": 100},
                    )
                ]
            ),
            columns=[
                ColumnContracts(
                    name="id",
                    validation=[
                        ValidationRule(rule_type=RuleType.NOT_NULL),
                        ValidationRule(rule_type=RuleType.UNIQUE),
                    ],
                ),
                ColumnContracts(
                    name="status",
                    validation=[
                        ValidationRule(
                            rule_type=RuleType.IN_SET,
                            params={"values": ["active", "inactive", "pending"]},
                        )
                    ],
                ),
            ],
        )

        results = validate_dataframe(sample_df, contracts)

        # Should have 4 results: 1 file + 2 id + 1 status
        assert len(results) == 4

        # File-level should pass
        file_results = [r for r in results if r.column == "file"]
        assert len(file_results) == 1
        assert file_results[0].result == "pass"

        # id not_null should pass (no nulls in id)
        # id unique should pass
        id_results = [r for r in results if r.column == "id"]
        assert len(id_results) == 2
        assert all(r.result == "pass" for r in id_results)

        # status in_set should pass
        status_results = [r for r in results if r.column == "status"]
        assert len(status_results) == 1
        assert status_results[0].result == "pass"

    def test_statistical_validators(self):
        df = pl.DataFrame({"score": [80.0, 85.0, 90.0, 95.0, 100.0]})
        contracts = SchemaContracts(
            contract=Contract(name="test", version="1.0.0"),
            columns=[
                ColumnContracts(
                    name="score",
                    validation=[
                        ValidationRule(
                            rule_type=RuleType.MEAN_BETWEEN,
                            params={"min": 85.0, "max": 95.0},
                        ),
                        ValidationRule(
                            rule_type=RuleType.COMPLETENESS,
                            params={"min_ratio": 1.0},
                        ),
                    ],
                )
            ],
        )

        results = validate_dataframe(df, contracts)
        assert len(results) == 2

        # Mean is 90, should pass
        mean_result = [r for r in results if r.rule == "mean_between"][0]
        assert mean_result.result == "pass"

        # No nulls, should pass
        comp_result = [r for r in results if r.rule == "completeness"][0]
        assert comp_result.result == "pass"

    def test_pattern_validator(self):
        df = pl.DataFrame({"email": ["a@b.com", "c@d.org", "invalid"]})
        contracts = SchemaContracts(
            contract=Contract(name="test", version="1.0.0"),
            columns=[
                ColumnContracts(
                    name="email",
                    validation=[
                        ValidationRule(
                            rule_type=RuleType.PATTERN,
                            params={"pattern": r"^[^@]+@[^@]+\.[^@]+$"},
                        )
                    ],
                )
            ],
        )

        results = validate_dataframe(df, contracts)
        assert len(results) == 1
        assert results[0].result == "fail"
        assert "bad_count=1" in results[0].details

"""Tests for validators."""

from __future__ import annotations

import polars as pl
import pytest

from lokryn_pipe_audit.validators import (
    BooleanValidator,
    CompletenessValidator,
    CompoundUniqueValidator,
    DateFormatValidator,
    DistinctnessValidator,
    InSetValidator,
    MaxLengthValidator,
    MeanBetweenValidator,
    NotInSetValidator,
    NotNullValidator,
    OutlierSigmaValidator,
    PatternValidator,
    RangeValidator,
    RowCountValidator,
    StdevBetweenValidator,
    TypeValidator,
    UniqueValidator,
)


class TestNotNullValidator:
    """Tests for NotNullValidator."""

    def test_passes_when_no_nulls(self):
        df = pl.DataFrame({"col": ["a", "b", "c"]})
        validator = NotNullValidator()
        report = validator.validate(df, "col")
        assert report.status == "pass"
        assert report.details is None

    def test_fails_when_some_nulls(self):
        df = pl.DataFrame({"col": ["a", None, "b"]})
        validator = NotNullValidator()
        report = validator.validate(df, "col")
        assert report.status == "fail"
        assert "null_count=1" in report.details

    def test_fails_when_all_nulls(self):
        df = pl.DataFrame({"col": [None, None, None]})
        validator = NotNullValidator()
        report = validator.validate(df, "col")
        assert report.status == "fail"
        assert "null_count=3" in report.details

    def test_passes_on_empty_column(self):
        df = pl.DataFrame({"col": []}).cast({"col": pl.String})
        validator = NotNullValidator()
        report = validator.validate(df, "col")
        assert report.status == "pass"


class TestUniqueValidator:
    """Tests for UniqueValidator."""

    def test_passes_when_all_unique(self):
        df = pl.DataFrame({"col": [1, 2, 3]})
        validator = UniqueValidator()
        report = validator.validate(df, "col")
        assert report.status == "pass"

    def test_fails_when_duplicates(self):
        df = pl.DataFrame({"col": [1, 2, 1]})
        validator = UniqueValidator()
        report = validator.validate(df, "col")
        assert report.status == "fail"
        assert "2 unique values in 3 total rows" in report.details

    def test_passes_on_empty(self):
        df = pl.DataFrame({"col": []}).cast({"col": pl.Int64})
        validator = UniqueValidator()
        report = validator.validate(df, "col")
        assert report.status == "pass"


class TestPatternValidator:
    """Tests for PatternValidator."""

    def test_passes_when_all_match(self):
        df = pl.DataFrame({"col": ["abc", "abd", "abe"]})
        validator = PatternValidator(r"^ab.$")
        report = validator.validate(df, "col")
        assert report.status == "pass"

    def test_fails_when_some_dont_match(self):
        df = pl.DataFrame({"col": ["abc", "xyz", "abd"]})
        validator = PatternValidator(r"^ab.$")
        report = validator.validate(df, "col")
        assert report.status == "fail"
        assert "bad_count=1" in report.details

    def test_ignores_nulls(self):
        df = pl.DataFrame({"col": ["abc", None, "abd"]})
        validator = PatternValidator(r"^ab.$")
        report = validator.validate(df, "col")
        assert report.status == "pass"

    def test_skips_non_string(self):
        df = pl.DataFrame({"col": [1, 2, 3]})
        validator = PatternValidator(r"^ab.$")
        report = validator.validate(df, "col")
        assert report.status == "skipped"
        assert "not a string" in report.details


class TestRangeValidator:
    """Tests for RangeValidator."""

    def test_passes_when_in_range(self):
        df = pl.DataFrame({"col": [5, 10, 15]})
        validator = RangeValidator(min_val=0, max_val=20)
        report = validator.validate(df, "col")
        assert report.status == "pass"

    def test_fails_when_below_min(self):
        df = pl.DataFrame({"col": [-5, 10, 15]})
        validator = RangeValidator(min_val=0, max_val=20)
        report = validator.validate(df, "col")
        assert report.status == "fail"
        assert "bad_count=1" in report.details

    def test_fails_when_above_max(self):
        df = pl.DataFrame({"col": [5, 25, 15]})
        validator = RangeValidator(min_val=0, max_val=20)
        report = validator.validate(df, "col")
        assert report.status == "fail"

    def test_skips_non_numeric(self):
        df = pl.DataFrame({"col": ["a", "b"]})
        validator = RangeValidator(min_val=0, max_val=20)
        report = validator.validate(df, "col")
        assert report.status == "skipped"


class TestInSetValidator:
    """Tests for InSetValidator."""

    def test_passes_when_all_in_set(self):
        df = pl.DataFrame({"col": ["a", "b", "c"]})
        validator = InSetValidator(values=["a", "b", "c"])
        report = validator.validate(df, "col")
        assert report.status == "pass"

    def test_fails_when_some_not_in_set(self):
        df = pl.DataFrame({"col": ["a", "x", "b", "y"]})
        validator = InSetValidator(values=["a", "b"])
        report = validator.validate(df, "col")
        assert report.status == "fail"
        assert "bad_count=2" in report.details

    def test_ignores_nulls(self):
        df = pl.DataFrame({"col": ["a", None, "b"]})
        validator = InSetValidator(values=["a", "b"])
        report = validator.validate(df, "col")
        assert report.status == "pass"


class TestCompletenessValidator:
    """Tests for CompletenessValidator."""

    def test_passes_when_complete(self):
        df = pl.DataFrame({"col": ["a", "b", "c"]})
        validator = CompletenessValidator(min_ratio=1.0)
        report = validator.validate(df, "col")
        assert report.status == "pass"

    def test_passes_when_above_threshold(self):
        df = pl.DataFrame({"col": ["a", None, "b"]})
        validator = CompletenessValidator(min_ratio=0.5)
        report = validator.validate(df, "col")
        assert report.status == "pass"

    def test_fails_when_below_threshold(self):
        df = pl.DataFrame({"col": ["a", None, None]})
        validator = CompletenessValidator(min_ratio=0.75)
        report = validator.validate(df, "col")
        assert report.status == "fail"
        assert "ratio=0.33" in report.details

    def test_passes_on_empty(self):
        df = pl.DataFrame({"col": []}).cast({"col": pl.String})
        validator = CompletenessValidator(min_ratio=0.9)
        report = validator.validate(df, "col")
        assert report.status == "pass"


class TestMeanBetweenValidator:
    """Tests for MeanBetweenValidator."""

    def test_passes_when_mean_in_range(self):
        df = pl.DataFrame({"col": [10.0, 20.0, 30.0]})  # mean = 20
        validator = MeanBetweenValidator(min_val=15.0, max_val=25.0)
        report = validator.validate(df, "col")
        assert report.status == "pass"

    def test_fails_when_mean_below_min(self):
        df = pl.DataFrame({"col": [1.0, 2.0, 3.0]})  # mean = 2
        validator = MeanBetweenValidator(min_val=5.0, max_val=10.0)
        report = validator.validate(df, "col")
        assert report.status == "fail"
        assert "observed_mean" in report.details


class TestRowCountValidator:
    """Tests for RowCountValidator."""

    def test_passes_when_in_range(self):
        df = pl.DataFrame({"col": [1, 2, 3, 4, 5]})
        validator = RowCountValidator(min_rows=1, max_rows=10)
        report = validator.validate(df)
        assert report.status == "pass"

    def test_fails_when_too_few(self):
        df = pl.DataFrame({"col": [1, 2]})
        validator = RowCountValidator(min_rows=5, max_rows=10)
        report = validator.validate(df)
        assert report.status == "fail"
        assert "rows=2" in report.details

    def test_fails_when_too_many(self):
        df = pl.DataFrame({"col": list(range(100))})
        validator = RowCountValidator(min_rows=1, max_rows=10)
        report = validator.validate(df)
        assert report.status == "fail"


class TestCompoundUniqueValidator:
    """Tests for CompoundUniqueValidator."""

    def test_passes_when_combinations_unique(self):
        df = pl.DataFrame({
            "a": [1, 1, 2],
            "b": ["x", "y", "x"],
        })
        validator = CompoundUniqueValidator(columns=["a", "b"])
        report = validator.validate(df)
        assert report.status == "pass"

    def test_fails_when_combinations_not_unique(self):
        df = pl.DataFrame({
            "a": [1, 1, 1],
            "b": ["x", "x", "y"],
        })
        validator = CompoundUniqueValidator(columns=["a", "b"])
        report = validator.validate(df)
        assert report.status == "fail"
        assert "distinct=2" in report.details


class TestDateFormatValidator:
    """Tests for DateFormatValidator."""

    def test_passes_when_all_match(self):
        df = pl.DataFrame({"col": ["2024-01-01 12:00:00", "2024-12-31 23:59:59"]})
        validator = DateFormatValidator(format_str="%Y-%m-%d %H:%M:%S")
        report = validator.validate(df, "col")
        assert report.status == "pass"

    def test_fails_when_some_dont_match(self):
        df = pl.DataFrame({"col": ["2024-01-01 12:00:00", "not-a-date"]})
        validator = DateFormatValidator(format_str="%Y-%m-%d %H:%M:%S")
        report = validator.validate(df, "col")
        assert report.status == "fail"
        assert "bad_count=1" in report.details


class TestOutlierSigmaValidator:
    """Tests for OutlierSigmaValidator."""

    def test_passes_when_no_outliers(self):
        df = pl.DataFrame({"col": [4.0, 5.0, 6.0]})
        validator = OutlierSigmaValidator(sigma=2.0)
        report = validator.validate(df, "col")
        assert report.status == "pass"

    def test_fails_when_outliers_present(self):
        # 8 values around 10, one outlier at 100
        df = pl.DataFrame({"col": [10.0] * 8 + [100.0]})
        validator = OutlierSigmaValidator(sigma=2.0)
        report = validator.validate(df, "col")
        assert report.status == "fail"
        assert "outliers=" in report.details

    def test_passes_when_std_zero(self):
        df = pl.DataFrame({"col": [5.0, 5.0, 5.0]})
        validator = OutlierSigmaValidator(sigma=2.0)
        report = validator.validate(df, "col")
        assert report.status == "pass"
        assert "standard deviation is zero" in report.details

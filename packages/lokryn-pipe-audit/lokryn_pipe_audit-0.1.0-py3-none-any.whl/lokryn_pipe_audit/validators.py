"""Validator protocols and implementations for pipe-audit-core.

This module defines the core protocols (ColumnValidator, FileValidator,
CompoundValidator) and all validator implementations. The engine dispatches
to these validators based on the contract rules.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

import polars as pl

from .contracts import RuleType, ValidationRule
from .errors import PatternError


@dataclass
class ValidationReport:
    """Standardized result of a validation check.

    Attributes:
        status: One of "pass", "fail", or "skipped"
        details: Optional human-readable explanation (e.g., failure reason)
    """

    status: str  # "pass", "fail", or "skipped"
    details: str | None = None


# -----------------------------------------------------------------------------
# Validator Protocols
# -----------------------------------------------------------------------------


class ColumnValidator(Protocol):
    """Protocol for column-level validators."""

    def name(self) -> str:
        """Return the human-readable name of the validator."""
        ...

    def validate(self, df: pl.DataFrame, column_name: str) -> ValidationReport:
        """Apply the validation to the given column.

        Args:
            df: The full DataFrame
            column_name: The name of the column to validate

        Returns:
            ValidationReport with status and optional details
        """
        ...


class FileValidator(Protocol):
    """Protocol for file-level validators."""

    def name(self) -> str:
        """Return the human-readable name of the validator."""
        ...

    def validate(self, df: pl.DataFrame) -> ValidationReport:
        """Apply the validation to the entire DataFrame.

        Args:
            df: The DataFrame to validate

        Returns:
            ValidationReport with status and optional details
        """
        ...


class CompoundValidator(Protocol):
    """Protocol for compound (multi-column) validators."""

    def name(self) -> str:
        """Return the human-readable name of the validator."""
        ...

    def validate(self, df: pl.DataFrame) -> ValidationReport:
        """Apply the validation across multiple columns.

        Args:
            df: The DataFrame to validate

        Returns:
            ValidationReport with status and optional details
        """
        ...


# -----------------------------------------------------------------------------
# Column-Level Validators
# -----------------------------------------------------------------------------


class NotNullValidator:
    """Validates that a column contains no null values."""

    def name(self) -> str:
        return "not_null"

    def validate(self, df: pl.DataFrame, column_name: str) -> ValidationReport:
        series = df.get_column(column_name)
        null_count = series.null_count()

        if null_count > 0:
            return ValidationReport(
                status="fail",
                details=f"null_count={null_count}",
            )
        return ValidationReport(status="pass")


class UniqueValidator:
    """Validates that all values in a column are unique."""

    def name(self) -> str:
        return "unique"

    def validate(self, df: pl.DataFrame, column_name: str) -> ValidationReport:
        series = df.get_column(column_name)
        unique_count = series.n_unique()
        total_count = len(series)

        if unique_count == total_count:
            return ValidationReport(status="pass")
        return ValidationReport(
            status="fail",
            details=f"found {unique_count} unique values in {total_count} total rows",
        )


class PatternValidator:
    """Validates that string values match a regex pattern."""

    def __init__(self, pattern: str) -> None:
        self.pattern = pattern
        try:
            self._regex = re.compile(pattern)
        except re.error as e:
            raise PatternError(pattern, str(e))

    def name(self) -> str:
        return "pattern"

    def validate(self, df: pl.DataFrame, column_name: str) -> ValidationReport:
        series = df.get_column(column_name)

        # Check if column is string type
        if series.dtype != pl.String:
            return ValidationReport(
                status="skipped",
                details="column is not a string type",
            )

        # Count non-matching values (nulls are ignored)
        bad_count = 0
        for val in series:
            if val is not None and not self._regex.match(str(val)):
                bad_count += 1

        if bad_count > 0:
            return ValidationReport(
                status="fail",
                details=f"bad_count={bad_count}, pattern={self.pattern}",
            )
        return ValidationReport(status="pass")


class MaxLengthValidator:
    """Validates that string values do not exceed a maximum length."""

    def __init__(self, value: int) -> None:
        self.value = value

    def name(self) -> str:
        return "max_length"

    def validate(self, df: pl.DataFrame, column_name: str) -> ValidationReport:
        series = df.get_column(column_name)

        if series.dtype != pl.String:
            return ValidationReport(
                status="skipped",
                details="column is not a string type",
            )

        # Count values exceeding max length
        lengths = series.str.len_chars()
        bad_count = (lengths > self.value).sum()

        if bad_count > 0:
            return ValidationReport(
                status="fail",
                details=f"bad_count={bad_count}, max_length={self.value}",
            )
        return ValidationReport(status="pass")


class RangeValidator:
    """Validates that numeric values fall within a specified range."""

    def __init__(self, min_val: int | float, max_val: int | float) -> None:
        self.min = min_val
        self.max = max_val

    def name(self) -> str:
        return "range"

    def validate(self, df: pl.DataFrame, column_name: str) -> ValidationReport:
        series = df.get_column(column_name)

        # Check if column is numeric
        if not series.dtype.is_numeric():
            return ValidationReport(
                status="skipped",
                details="column is not a numeric type",
            )

        # Count values outside range
        mask = (series < self.min) | (series > self.max)
        bad_count = mask.sum()

        if bad_count > 0:
            return ValidationReport(
                status="fail",
                details=f"bad_count={bad_count}, min={self.min}, max={self.max}",
            )
        return ValidationReport(status="pass")


class InSetValidator:
    """Validates that string values are in a specified set."""

    def __init__(self, values: list[str]) -> None:
        self.values = set(values)

    def name(self) -> str:
        return "in_set"

    def validate(self, df: pl.DataFrame, column_name: str) -> ValidationReport:
        series = df.get_column(column_name)

        if series.dtype != pl.String:
            return ValidationReport(
                status="skipped",
                details="column is not a string type",
            )

        # Count values not in the allowed set (nulls are ignored)
        bad_count = 0
        for val in series:
            if val is not None and val not in self.values:
                bad_count += 1

        if bad_count > 0:
            return ValidationReport(
                status="fail",
                details=f"bad_count={bad_count}",
            )
        return ValidationReport(status="pass")


class NotInSetValidator:
    """Validates that string values are NOT in a specified set."""

    def __init__(self, values: list[str]) -> None:
        self.values = set(values)

    def name(self) -> str:
        return "not_in_set"

    def validate(self, df: pl.DataFrame, column_name: str) -> ValidationReport:
        series = df.get_column(column_name)

        if series.dtype != pl.String:
            return ValidationReport(
                status="skipped",
                details="column is not a string type",
            )

        # Count values in the forbidden set (nulls are ignored)
        bad_count = 0
        for val in series:
            if val is not None and val in self.values:
                bad_count += 1

        if bad_count > 0:
            return ValidationReport(
                status="fail",
                details=f"bad_count={bad_count}",
            )
        return ValidationReport(status="pass")


class BooleanValidator:
    """Validates that a column contains boolean values."""

    def name(self) -> str:
        return "boolean"

    def validate(self, df: pl.DataFrame, column_name: str) -> ValidationReport:
        series = df.get_column(column_name)

        if series.dtype == pl.Boolean:
            return ValidationReport(status="pass")

        # Check if string values are boolean-like
        if series.dtype == pl.String:
            valid_values = {"true", "false", "True", "False", "TRUE", "FALSE", "1", "0"}
            bad_count = 0
            for val in series:
                if val is not None and val not in valid_values:
                    bad_count += 1

            if bad_count > 0:
                return ValidationReport(
                    status="fail",
                    details=f"bad_count={bad_count}",
                )
            return ValidationReport(status="pass")

        return ValidationReport(
            status="skipped",
            details="column is not a boolean or string type",
        )


class TypeValidator:
    """Validates that a column has a specific Polars data type."""

    # Mapping of string type names to Polars types
    _TYPE_MAP: dict[str, pl.DataType] = {
        "int64": pl.Int64,
        "int32": pl.Int32,
        "int16": pl.Int16,
        "int8": pl.Int8,
        "uint64": pl.UInt64,
        "uint32": pl.UInt32,
        "uint16": pl.UInt16,
        "uint8": pl.UInt8,
        "float64": pl.Float64,
        "float32": pl.Float32,
        "string": pl.String,
        "str": pl.String,
        "bool": pl.Boolean,
        "boolean": pl.Boolean,
        "date": pl.Date,
        "datetime": pl.Datetime,
    }

    def __init__(self, dtype: str) -> None:
        self.dtype = dtype.lower()

    def name(self) -> str:
        return "type"

    def validate(self, df: pl.DataFrame, column_name: str) -> ValidationReport:
        series = df.get_column(column_name)
        expected_type = self._TYPE_MAP.get(self.dtype)

        if expected_type is None:
            return ValidationReport(
                status="skipped",
                details=f"unknown type: {self.dtype}",
            )

        if series.dtype == expected_type:
            return ValidationReport(status="pass")

        return ValidationReport(
            status="fail",
            details=f"expected={self.dtype}, actual={series.dtype}",
        )


class DateFormatValidator:
    """Validates that string values match a date/time format."""

    def __init__(self, format_str: str) -> None:
        self.format = format_str

    def name(self) -> str:
        return "date_format"

    def validate(self, df: pl.DataFrame, column_name: str) -> ValidationReport:
        series = df.get_column(column_name)

        if series.dtype != pl.String:
            return ValidationReport(
                status="skipped",
                details="column is not a string type",
            )

        # Count values that don't match the date format
        bad_count = 0
        for val in series:
            if val is not None:
                try:
                    datetime.strptime(val, self.format)
                except ValueError:
                    bad_count += 1

        if bad_count > 0:
            return ValidationReport(
                status="fail",
                details=f"bad_count={bad_count}, format={self.format}",
            )
        return ValidationReport(status="pass")


class CompletenessValidator:
    """Validates that a column has a minimum ratio of non-null values."""

    def __init__(self, min_ratio: float) -> None:
        self.min_ratio = min_ratio

    def name(self) -> str:
        return "completeness"

    def validate(self, df: pl.DataFrame, column_name: str) -> ValidationReport:
        series = df.get_column(column_name)
        total_count = len(series)

        if total_count == 0:
            return ValidationReport(
                status="pass",
                details="column is empty",
            )

        non_null_count = total_count - series.null_count()
        ratio = non_null_count / total_count

        if ratio >= self.min_ratio:
            return ValidationReport(status="pass")
        return ValidationReport(
            status="fail",
            details=f"ratio={ratio:.2f}, min_ratio={self.min_ratio}",
        )


class DistinctnessValidator:
    """Validates that a column has a minimum ratio of unique values."""

    def __init__(self, min_ratio: float) -> None:
        self.min_ratio = min_ratio

    def name(self) -> str:
        return "distinctness"

    def validate(self, df: pl.DataFrame, column_name: str) -> ValidationReport:
        series = df.get_column(column_name)
        total_count = len(series)

        if total_count == 0:
            return ValidationReport(
                status="pass",
                details="column is empty",
            )

        unique_count = series.n_unique()
        ratio = unique_count / total_count

        if ratio >= self.min_ratio:
            return ValidationReport(status="pass")
        return ValidationReport(
            status="fail",
            details=f"ratio={ratio:.2f}, min_ratio={self.min_ratio}",
        )


class MeanBetweenValidator:
    """Validates that the mean of a numeric column falls within a range."""

    def __init__(self, min_val: float, max_val: float) -> None:
        self.min = min_val
        self.max = max_val

    def name(self) -> str:
        return "mean_between"

    def validate(self, df: pl.DataFrame, column_name: str) -> ValidationReport:
        series = df.get_column(column_name)

        if not series.dtype.is_numeric():
            return ValidationReport(
                status="skipped",
                details="column is not a numeric type",
            )

        mean = series.mean()
        if mean is None:
            return ValidationReport(
                status="skipped",
                details="could not calculate mean",
            )

        if self.min <= mean <= self.max:
            return ValidationReport(status="pass")
        return ValidationReport(
            status="fail",
            details=f"observed_mean={mean:.2f}, min={self.min}, max={self.max}",
        )


class StdevBetweenValidator:
    """Validates that the standard deviation of a numeric column falls within a range."""

    def __init__(self, min_val: float, max_val: float) -> None:
        self.min = min_val
        self.max = max_val

    def name(self) -> str:
        return "stdev_between"

    def validate(self, df: pl.DataFrame, column_name: str) -> ValidationReport:
        series = df.get_column(column_name)

        if not series.dtype.is_numeric():
            return ValidationReport(
                status="skipped",
                details="column is not a numeric type",
            )

        std = series.std()
        if std is None:
            return ValidationReport(
                status="skipped",
                details="could not calculate standard deviation",
            )

        if self.min <= std <= self.max:
            return ValidationReport(status="pass")
        return ValidationReport(
            status="fail",
            details=f"observed_stdev={std:.2f}, min={self.min}, max={self.max}",
        )


class OutlierSigmaValidator:
    """Validates that no values are more than N standard deviations from the mean."""

    def __init__(self, sigma: float) -> None:
        self.sigma = sigma

    def name(self) -> str:
        return "outlier_sigma"

    def validate(self, df: pl.DataFrame, column_name: str) -> ValidationReport:
        series = df.get_column(column_name)

        if not series.dtype.is_numeric():
            return ValidationReport(
                status="skipped",
                details="column is not a numeric type",
            )

        mean = series.mean()
        std = series.std()

        if mean is None or std is None:
            return ValidationReport(
                status="skipped",
                details="could not calculate mean or standard deviation",
            )

        if std == 0:
            return ValidationReport(
                status="pass",
                details="standard deviation is zero; no outliers possible",
            )

        # Calculate deviation from mean
        threshold = self.sigma * std
        deviation = (series - mean).abs()
        outlier_count = (deviation > threshold).sum()

        if outlier_count > 0:
            return ValidationReport(
                status="fail",
                details=f"outliers={outlier_count}, sigma={self.sigma}",
            )
        return ValidationReport(status="pass")


# -----------------------------------------------------------------------------
# File-Level Validators
# -----------------------------------------------------------------------------


class RowCountValidator:
    """Validates that the DataFrame has a row count within a specified range."""

    def __init__(self, min_rows: int, max_rows: int | None = None) -> None:
        self.min = min_rows
        self.max = max_rows

    def name(self) -> str:
        return "row_count"

    def validate(self, df: pl.DataFrame) -> ValidationReport:
        rows = df.height

        too_few = rows < self.min
        too_many = self.max is not None and rows > self.max

        if too_few or too_many:
            return ValidationReport(
                status="fail",
                details=f"rows={rows}, min={self.min}, max={self.max}",
            )
        return ValidationReport(status="pass")


class FileCompletenessValidator:
    """Validates that the entire DataFrame has a minimum ratio of non-null values."""

    def __init__(self, min_ratio: float) -> None:
        self.min_ratio = min_ratio

    def name(self) -> str:
        return "file_completeness"

    def validate(self, df: pl.DataFrame) -> ValidationReport:
        total_cells = df.height * df.width
        if total_cells == 0:
            return ValidationReport(
                status="pass",
                details="dataframe is empty",
            )

        null_count = sum(df.get_column(col).null_count() for col in df.columns)
        non_null_count = total_cells - null_count
        ratio = non_null_count / total_cells

        if ratio >= self.min_ratio:
            return ValidationReport(status="pass")
        return ValidationReport(
            status="fail",
            details=f"ratio={ratio:.2f}, min_ratio={self.min_ratio}",
        )


class ExistsValidator:
    """Validates that a file exists (always passes for loaded data)."""

    def name(self) -> str:
        return "exists"

    def validate(self, df: pl.DataFrame) -> ValidationReport:
        # If we have a DataFrame, the file existed and was loaded
        return ValidationReport(status="pass")


# -----------------------------------------------------------------------------
# Compound Validators
# -----------------------------------------------------------------------------


class CompoundUniqueValidator:
    """Validates that combinations of values across multiple columns are unique."""

    def __init__(self, columns: list[str]) -> None:
        self.columns = columns

    def name(self) -> str:
        return "compound_unique"

    def validate(self, df: pl.DataFrame) -> ValidationReport:
        total_rows = df.height

        # Get unique rows based on the specified columns
        unique_df = df.unique(subset=self.columns, keep="first")
        distinct_rows = unique_df.height

        if distinct_rows == total_rows:
            return ValidationReport(
                status="pass",
                details=f"columns={self.columns}, rows={total_rows}",
            )
        return ValidationReport(
            status="fail",
            details=f"columns={self.columns}, rows={total_rows}, distinct={distinct_rows}",
        )


# -----------------------------------------------------------------------------
# Factory Functions
# -----------------------------------------------------------------------------


def get_column_validator(rule: ValidationRule) -> ColumnValidator:
    """Create a column validator from a validation rule.

    Args:
        rule: The validation rule to create a validator for

    Returns:
        A validator instance

    Raises:
        ValueError: If the rule type is not a column-level rule
    """
    params = rule.params

    match rule.rule_type:
        case RuleType.NOT_NULL:
            return NotNullValidator()
        case RuleType.UNIQUE:
            return UniqueValidator()
        case RuleType.PATTERN:
            return PatternValidator(params["pattern"])
        case RuleType.MAX_LENGTH:
            return MaxLengthValidator(params["value"])
        case RuleType.RANGE:
            return RangeValidator(params["min"], params["max"])
        case RuleType.IN_SET:
            return InSetValidator(params["values"])
        case RuleType.NOT_IN_SET:
            return NotInSetValidator(params["values"])
        case RuleType.BOOLEAN:
            return BooleanValidator()
        case RuleType.TYPE:
            return TypeValidator(params["dtype"])
        case RuleType.DATE_FORMAT:
            return DateFormatValidator(params["format"])
        case RuleType.COMPLETENESS:
            return CompletenessValidator(params["min_ratio"])
        case RuleType.DISTINCTNESS:
            return DistinctnessValidator(params["min_ratio"])
        case RuleType.MEAN_BETWEEN:
            return MeanBetweenValidator(params["min"], params["max"])
        case RuleType.STDEV_BETWEEN:
            return StdevBetweenValidator(params["min"], params["max"])
        case RuleType.OUTLIER_SIGMA:
            return OutlierSigmaValidator(params["sigma"])
        case _:
            raise ValueError(f"Not a column-level rule: {rule.rule_type}")


def get_file_validator(rule: ValidationRule) -> FileValidator:
    """Create a file validator from a validation rule.

    Args:
        rule: The validation rule to create a validator for

    Returns:
        A validator instance

    Raises:
        ValueError: If the rule type is not a file-level rule
    """
    params = rule.params

    match rule.rule_type:
        case RuleType.ROW_COUNT:
            return RowCountValidator(params["min"], params.get("max"))
        case RuleType.EXISTS:
            return ExistsValidator()
        case RuleType.COMPLETENESS:
            # File-level completeness
            return FileCompletenessValidator(params["min_ratio"])
        case _:
            raise ValueError(f"Not a file-level rule: {rule.rule_type}")


def is_file_level_rule(rule_type: RuleType) -> bool:
    """Check if a rule type is a file-level rule."""
    return rule_type in {RuleType.ROW_COUNT, RuleType.EXISTS}


def is_column_level_rule(rule_type: RuleType) -> bool:
    """Check if a rule type is a column-level rule."""
    return rule_type not in {RuleType.ROW_COUNT, RuleType.EXISTS}

"""Contract schema definitions and TOML parsing for pipe-audit-core."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from .errors import ContractParseError


class RuleType(str, Enum):
    """Enumeration of all supported validation rule types."""

    # Column-level rules
    NOT_NULL = "not_null"
    UNIQUE = "unique"
    PATTERN = "pattern"
    MAX_LENGTH = "max_length"
    RANGE = "range"
    IN_SET = "in_set"
    NOT_IN_SET = "not_in_set"
    BOOLEAN = "boolean"
    TYPE = "type"
    DATE_FORMAT = "date_format"

    # Statistical rules
    OUTLIER_SIGMA = "outlier_sigma"
    DISTINCTNESS = "distinctness"
    COMPLETENESS = "completeness"
    MEAN_BETWEEN = "mean_between"
    STDEV_BETWEEN = "stdev_between"

    # File-level rules
    ROW_COUNT = "row_count"
    EXISTS = "exists"


@dataclass
class ValidationRule:
    """A parsed validation rule with type and parameters.

    Attributes:
        rule_type: The type of validation rule (from RuleType enum)
        params: Dictionary of rule-specific parameters (e.g., {"min": 0, "max": 100})
    """

    rule_type: RuleType
    params: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ValidationRule:
        """Parse a validation rule from a dictionary.

        Args:
            data: Dictionary with 'rule' key and optional parameters

        Returns:
            ValidationRule instance

        Raises:
            ContractParseError: If the rule type is unknown or missing
        """
        if "rule" not in data:
            raise ContractParseError("Validation rule missing 'rule' field")

        rule_name = data["rule"]
        try:
            rule_type = RuleType(rule_name)
        except ValueError:
            raise ContractParseError(f"Unknown rule type: {rule_name}")

        # Extract all non-rule keys as parameters
        params = {k: v for k, v in data.items() if k != "rule"}
        return cls(rule_type=rule_type, params=params)


@dataclass
class Contract:
    """High-level metadata about a contract.

    Attributes:
        name: Unique identifier for the contract
        version: Semantic version string
        tags: Optional list of tags for grouping/filtering
    """

    name: str
    version: str
    tags: list[str] = field(default_factory=list)


@dataclass
class Source:
    """Input source definition for a contract.

    Attributes:
        type: Connector type (e.g., "s3", "local")
        location: Path or URI to the data
        profile: Optional profile name for credentials
    """

    type: str
    location: str | None = None
    profile: str | None = None


@dataclass
class Destination:
    """Output destination definition.

    Attributes:
        type: Connector type (e.g., "s3", "local")
        location: Path or URI for output
        profile: Optional profile name for credentials
        format: Optional format override (e.g., "csv", "parquet")
    """

    type: str
    location: str | None = None
    profile: str | None = None
    format: str | None = None


@dataclass
class Quarantine:
    """Quarantine sink definition for invalid data.

    Attributes:
        type: Connector type (e.g., "s3", "local")
        location: Path or URI for quarantine output
        profile: Optional profile name for credentials
        format: Optional format override
    """

    type: str
    location: str | None = None
    profile: str | None = None
    format: str | None = None


@dataclass
class ColumnContracts:
    """Column-level contract definition.

    Associates a column name with validation rules.

    Attributes:
        name: The column name in the dataset
        validation: List of validation rules to apply
    """

    name: str
    validation: list[ValidationRule] = field(default_factory=list)


@dataclass
class FileContracts:
    """File-level contract definition.

    Validation rules that apply to the dataset as a whole.

    Attributes:
        validation: List of file-level validation rules
    """

    validation: list[ValidationRule] = field(default_factory=list)


@dataclass
class CompoundUnique:
    """Compound uniqueness contract.

    Ensures that the combination of values across multiple columns is unique.

    Attributes:
        columns: List of column names that must be unique in combination
    """

    columns: list[str] = field(default_factory=list)


@dataclass
class SchemaContracts:
    """The full schema contract definition.

    This is the top-level structure parsed from a TOML file.

    Attributes:
        contract: Metadata about the contract
        file: Optional file-level validation rules
        columns: List of column-level validation rules
        compound_unique: Optional list of compound uniqueness rules
        source: Optional input source configuration
        destination: Optional output destination configuration
        quarantine: Optional quarantine sink configuration
    """

    contract: Contract
    file: FileContracts | None = None
    columns: list[ColumnContracts] = field(default_factory=list)
    compound_unique: list[CompoundUnique] | None = None
    source: Source | None = None
    destination: Destination | None = None
    quarantine: Quarantine | None = None


def _parse_validation_rules(rules: list[dict[str, Any]]) -> list[ValidationRule]:
    """Parse a list of validation rule dictionaries."""
    return [ValidationRule.from_dict(rule) for rule in rules]


def _parse_contract(data: dict[str, Any]) -> Contract:
    """Parse contract metadata from TOML data."""
    return Contract(
        name=data.get("name", ""),
        version=data.get("version", "0.0.0"),
        tags=data.get("tags", []),
    )


def _parse_source(data: dict[str, Any] | None) -> Source | None:
    """Parse source configuration from TOML data."""
    if data is None:
        return None
    return Source(
        type=data.get("type", "local"),
        location=data.get("location"),
        profile=data.get("profile"),
    )


def _parse_destination(data: dict[str, Any] | None) -> Destination | None:
    """Parse destination configuration from TOML data."""
    if data is None:
        return None
    return Destination(
        type=data.get("type", "local"),
        location=data.get("location"),
        profile=data.get("profile"),
        format=data.get("format"),
    )


def _parse_quarantine(data: dict[str, Any] | None) -> Quarantine | None:
    """Parse quarantine configuration from TOML data."""
    if data is None:
        return None
    return Quarantine(
        type=data.get("type", "local"),
        location=data.get("location"),
        profile=data.get("profile"),
        format=data.get("format"),
    )


def _parse_file_contracts(data: dict[str, Any] | None) -> FileContracts | None:
    """Parse file-level contracts from TOML data."""
    if data is None:
        return None
    validation = data.get("validation", [])
    return FileContracts(validation=_parse_validation_rules(validation))


def _parse_column_contracts(columns: list[dict[str, Any]]) -> list[ColumnContracts]:
    """Parse column-level contracts from TOML data."""
    result = []
    for col in columns:
        validation = col.get("validation", [])
        result.append(
            ColumnContracts(
                name=col.get("name", ""),
                validation=_parse_validation_rules(validation),
            )
        )
    return result


def _parse_compound_unique(data: list[dict[str, Any]] | None) -> list[CompoundUnique] | None:
    """Parse compound uniqueness rules from TOML data."""
    if data is None:
        return None
    return [CompoundUnique(columns=item.get("columns", [])) for item in data]


def load_contract(path: str | Path) -> SchemaContracts:
    """Load and parse a contract TOML file.

    Args:
        path: Path to the contract TOML file

    Returns:
        Parsed SchemaContracts object

    Raises:
        ContractParseError: If the file cannot be read or parsed
    """
    path = Path(path)
    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ContractParseError(f"Contract file not found: {path}", str(path))
    except OSError as e:
        raise ContractParseError(f"Error reading contract file: {e}", str(path))

    try:
        data = tomllib.loads(content)
    except tomllib.TOMLDecodeError as e:
        raise ContractParseError(f"Invalid TOML: {e}", str(path))

    return parse_contract_data(data, str(path))


def parse_contract_data(data: dict[str, Any], path: str | None = None) -> SchemaContracts:
    """Parse contract data from a dictionary.

    Args:
        data: Dictionary containing contract configuration
        path: Optional path for error messages

    Returns:
        Parsed SchemaContracts object

    Raises:
        ContractParseError: If required fields are missing or invalid
    """
    if "contract" not in data:
        raise ContractParseError("Missing required 'contract' section", path)

    try:
        return SchemaContracts(
            contract=_parse_contract(data["contract"]),
            file=_parse_file_contracts(data.get("file")),
            columns=_parse_column_contracts(data.get("columns", [])),
            compound_unique=_parse_compound_unique(data.get("compound_unique")),
            source=_parse_source(data.get("source")),
            destination=_parse_destination(data.get("destination")),
            quarantine=_parse_quarantine(data.get("quarantine")),
        )
    except (KeyError, TypeError) as e:
        raise ContractParseError(f"Error parsing contract: {e}", path)


def load_contract_for_file(data_path: str | Path) -> SchemaContracts:
    """Load the TOML contract file that matches a data filename.

    Derives the contract filename from the data file stem and loads
    from the 'contracts/' directory.

    Args:
        data_path: Path to the data file (e.g., "people.csv")

    Returns:
        Parsed SchemaContracts object

    Raises:
        ContractParseError: If the contract file cannot be found or parsed

    Example:
        >>> schema = load_contract_for_file("people.csv")
        # loads "contracts/people.toml"
    """
    data_path = Path(data_path)
    stem = data_path.stem
    contract_path = Path("contracts") / f"{stem}.toml"
    return load_contract(contract_path)

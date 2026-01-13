"""Validation orchestration for pipe-audit-core.

This module is the execution heart of the system: it takes a parsed
contract, loads data into a Polars DataFrame, applies all file/column/compound
rules, and produces structured RuleResults for logging and audit trails.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import polars as pl

from .connectors import LocalConnector, S3Connector, get_connector
from .contracts import (
    CompoundUnique,
    RuleType,
    SchemaContracts,
    load_contract,
)
from .drivers import get_driver, get_extension_from_path
from .errors import ValidationError
from .logging import (
    AuditLogEntry,
    AuditLogger,
    Contract,
    Executor,
    RuleResult,
    Target,
    log_action,
)
from .profiles import Profiles, get_profile, load_profiles
from .validators import (
    BooleanValidator,
    CompletenessValidator,
    CompoundUniqueValidator,
    DateFormatValidator,
    DistinctnessValidator,
    ExistsValidator,
    FileCompletenessValidator,
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


@dataclass
class ValidationOutcome:
    """Outcome of running a contract validation.

    Attributes:
        passed: True if no rules failed
        pass_count: Number of passing rules
        fail_count: Number of failing rules
        skip_count: Number of skipped rules
        results: Detailed results per rule
    """

    passed: bool
    pass_count: int
    fail_count: int
    skip_count: int
    results: list[RuleResult]


async def execute_validation(
    data: bytes,
    extension: str,
    contracts: SchemaContracts,
    executor: Executor,
    logger: AuditLogger,
) -> list[RuleResult]:
    """Execute validation end-to-end against raw data bytes.

    Args:
        data: Raw file contents (CSV, Parquet, etc.)
        extension: File extension (used to select driver)
        contracts: Parsed schema contracts to enforce
        executor: Metadata about who/where is running validation
        logger: The audit logger to use

    Returns:
        List of RuleResult objects

    Raises:
        ValidationError: If orchestration fails
    """
    # --- Start log ---
    entry = AuditLogEntry.create(
        event="validation_start",
        executor=executor,
        contract=Contract(
            name=contracts.contract.name,
            version=contracts.contract.version,
        ),
        details=f"bytes={len(data)}, extension={extension}",
    )
    logger.log_event(entry)

    # --- Driver selection ---
    driver = get_driver(extension)

    entry = AuditLogEntry.create(
        event="driver_found",
        executor=executor,
        details=f"extension={extension}",
    )
    logger.log_event(entry)

    # --- Parse into DataFrame ---
    df = driver.load(data)

    entry = AuditLogEntry.create(
        event="dataframe_parsed",
        executor=executor,
        details=f"rows={df.height}, cols={df.width}",
    )
    logger.log_event(entry)

    # --- Apply all validators ---
    results = validate_dataframe(df, contracts)

    # --- Summary log ---
    entry = AuditLogEntry.create(
        event="validation_summary",
        executor=executor,
        contract=Contract(
            name=contracts.contract.name,
            version=contracts.contract.version,
        ),
        results=results,
    )
    logger.log_event(entry)

    return results


def validate_dataframe(
    df: pl.DataFrame,
    contracts: SchemaContracts,
) -> list[RuleResult]:
    """Apply all file-level, column-level, and compound-level validators.

    Args:
        df: Polars DataFrame containing the dataset
        contracts: Schema contracts specifying rules

    Returns:
        List of RuleResult objects, one per rule applied
    """
    results: list[RuleResult] = []

    # --- File-Level Validation ---
    if contracts.file is not None:
        for rule in contracts.file.validation:
            match rule.rule_type:
                case RuleType.ROW_COUNT:
                    validator = RowCountValidator(
                        min_rows=rule.params["min"],
                        max_rows=rule.params.get("max"),
                    )
                case RuleType.COMPLETENESS:
                    validator = FileCompletenessValidator(
                        min_ratio=rule.params["min_ratio"],
                    )
                case RuleType.EXISTS:
                    validator = ExistsValidator()
                case _:
                    continue  # Skip unsupported rules at file level

            report = validator.validate(df)
            results.append(
                RuleResult(
                    column="file",
                    rule=validator.name(),
                    result=report.status,
                    details=report.details,
                )
            )

    # --- Column-Level Validation ---
    for col in contracts.columns:
        for rule in col.validation:
            validator = _get_column_validator(rule.rule_type, rule.params)
            if validator is None:
                continue  # Skip unsupported rules

            report = validator.validate(df, col.name)
            results.append(
                RuleResult(
                    column=col.name,
                    rule=validator.name(),
                    result=report.status,
                    details=report.details,
                )
            )

    # --- Compound-Level Validation ---
    if contracts.compound_unique is not None:
        for cu in contracts.compound_unique:
            validator = CompoundUniqueValidator(columns=cu.columns)
            report = validator.validate(df)
            results.append(
                RuleResult(
                    column="compound",
                    rule=validator.name(),
                    result=report.status,
                    details=report.details,
                )
            )

    return results


def _get_column_validator(rule_type: RuleType, params: dict):
    """Get a column validator for a rule type."""
    match rule_type:
        case RuleType.NOT_NULL:
            return NotNullValidator()
        case RuleType.UNIQUE:
            return UniqueValidator()
        case RuleType.BOOLEAN:
            return BooleanValidator()
        case RuleType.RANGE:
            return RangeValidator(min_val=params["min"], max_val=params["max"])
        case RuleType.PATTERN:
            return PatternValidator(pattern=params["pattern"])
        case RuleType.MAX_LENGTH:
            return MaxLengthValidator(value=params["value"])
        case RuleType.MEAN_BETWEEN:
            return MeanBetweenValidator(min_val=params["min"], max_val=params["max"])
        case RuleType.STDEV_BETWEEN:
            return StdevBetweenValidator(min_val=params["min"], max_val=params["max"])
        case RuleType.COMPLETENESS:
            return CompletenessValidator(min_ratio=params["min_ratio"])
        case RuleType.IN_SET:
            return InSetValidator(values=params["values"])
        case RuleType.NOT_IN_SET:
            return NotInSetValidator(values=params["values"])
        case RuleType.TYPE:
            return TypeValidator(dtype=params["dtype"])
        case RuleType.OUTLIER_SIGMA:
            return OutlierSigmaValidator(sigma=params["sigma"])
        case RuleType.DATE_FORMAT:
            return DateFormatValidator(format_str=params["format"])
        case RuleType.DISTINCTNESS:
            return DistinctnessValidator(min_ratio=params["min_ratio"])
        case _:
            return None


async def run_contract_validation(
    logger: AuditLogger,
    contract_name: str,
    executor: Executor,
    profiles: Profiles | None = None,
    log_to_console: bool = False,
) -> ValidationOutcome:
    """Run a contract validation end-to-end.

    This is the main entry point for running a validation:
    - Loads contract and profiles
    - Fetches data from source
    - Executes validations
    - Moves data to destination or quarantine
    - Logs all actions

    Args:
        logger: The audit logger implementation to use
        contract_name: Name of the contract to validate
        executor: Executor context (user/host info)
        profiles: Optional pre-loaded profiles (loads from file if None)
        log_to_console: Whether to print messages to console

    Returns:
        ValidationOutcome with results

    Raises:
        ValidationError: If validation cannot be performed
    """
    # --- Contract existence check ---
    contract_path = Path("contracts") / f"{contract_name}.toml"
    if not contract_path.exists():
        raise ValidationError(f"Contract '{contract_name}' not found")

    # --- Load contract + profiles ---
    contracts = load_contract(contract_path)
    if profiles is None:
        profiles = load_profiles()

    # --- Validate source config ---
    source = contracts.source
    if source is None:
        raise ValidationError("Contract missing source")
    location = source.location
    if location is None:
        raise ValidationError("Source missing location")

    # --- Start log ---
    log_action(
        logger=logger,
        executor=executor,
        event="contract_validation_started",
        contract_name=contract_name,
    )
    if log_to_console:
        print(f"Starting validation of contract: {contract_name}")

    # --- Fetch data ---
    connector = get_connector(
        connector_type=source.type,
        profile=get_profile(profiles, source.profile) if source.profile else None,
        location=location,
    )
    data = await connector.fetch(location)

    log_action(
        logger=logger,
        executor=executor,
        event="file_read",
        details=f"bytes={len(data)}",
        location=location,
    )

    # --- Determine file extension ---
    extension = get_extension_from_path(location)
    if not extension:
        extension = "csv"  # Default

    # --- Execute validations ---
    results = await execute_validation(data, extension, contracts, executor, logger)

    # --- Calculate outcome ---
    pass_count = sum(1 for r in results if r.result == "pass")
    fail_count = sum(1 for r in results if r.result == "fail")
    skip_count = sum(1 for r in results if r.result == "skipped")
    validation_passed = fail_count == 0

    # --- Completion log ---
    details = f"pass={pass_count}, fail={fail_count}, skip={skip_count}"
    log_action(
        logger=logger,
        executor=executor,
        event="contract_validation_completed",
        details=details,
        contract_name=contracts.contract.name,
        contract_version=contracts.contract.version,
    )
    if log_to_console:
        status = "PASSED" if validation_passed else "FAILED"
        print(f"Validation {status}: {details}")

    return ValidationOutcome(
        passed=validation_passed,
        pass_count=pass_count,
        fail_count=fail_count,
        skip_count=skip_count,
        results=results,
    )


async def validate_data(
    data: bytes,
    contract_path: str | Path,
    executor: Executor | None = None,
    logger: AuditLogger | None = None,
) -> ValidationOutcome:
    """Validate data against a contract without file movement.

    This is a simplified entry point for validating in-memory data.

    Args:
        data: Raw data bytes
        contract_path: Path to the contract TOML file
        executor: Optional executor (uses environment if None)
        logger: Optional logger (uses NoOpLogger if None)

    Returns:
        ValidationOutcome with results
    """
    from .logging import NoOpLogger

    if executor is None:
        executor = Executor.from_environment()
    if logger is None:
        logger = NoOpLogger()

    # Load contract
    contracts = load_contract(contract_path)

    # Determine extension from source location or default to csv
    extension = "csv"
    if contracts.source and contracts.source.location:
        extension = get_extension_from_path(contracts.source.location) or "csv"

    # Execute validation
    results = await execute_validation(data, extension, contracts, executor, logger)

    # Calculate outcome
    pass_count = sum(1 for r in results if r.result == "pass")
    fail_count = sum(1 for r in results if r.result == "fail")
    skip_count = sum(1 for r in results if r.result == "skipped")

    return ValidationOutcome(
        passed=fail_count == 0,
        pass_count=pass_count,
        fail_count=fail_count,
        skip_count=skip_count,
        results=results,
    )

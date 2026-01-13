"""lokryn-pipe-audit: Data validation library for audit pipelines using Polars.

This library provides a framework for validating data files against
TOML-based contracts. It supports multiple file formats (CSV, Parquet)
and storage backends (local, S3, GCS, Azure).

Example usage:

    from lokryn_pipe_audit import (
        load_contract,
        validate_data,
        Executor,
        JsonlLogger,
    )

    # Load a contract
    contract = load_contract("contracts/example.toml")

    # Validate data
    with open("data.csv", "rb") as f:
        data = f.read()

    outcome = await validate_data(data, contract)
    print(f"Passed: {outcome.passed}")
    print(f"Pass count: {outcome.pass_count}")
    print(f"Fail count: {outcome.fail_count}")
"""

from __future__ import annotations

__version__ = "0.1.0"

# Contracts
from .contracts import (
    ColumnContracts,
    CompoundUnique,
    Contract,
    Destination,
    FileContracts,
    Quarantine,
    RuleType,
    SchemaContracts,
    Source,
    ValidationRule,
    load_contract,
    load_contract_for_file,
    parse_contract_data,
)

# Connectors
from .connectors import (
    AzureConnector,
    Connector,
    GCSConnector,
    LocalConnector,
    S3Connector,
    get_connector,
)

# Drivers
from .drivers import (
    CsvDriver,
    Driver,
    ParquetDriver,
    get_driver,
    get_extension_from_path,
)

# Engine
from .engine import (
    ValidationOutcome,
    execute_validation,
    run_contract_validation,
    validate_data,
    validate_dataframe,
)

# Errors
from .errors import (
    ConnectorError,
    ContractParseError,
    DriverError,
    MovementError,
    PatternError,
    ProfileLoadError,
    ProfileNotFoundError,
    UnsupportedFormatError,
    ValidationError,
)

# Logging
from .logging import (
    AuditLogEntry,
    AuditLogger,
    Contract as LogContract,
    Executor,
    InMemoryLogger,
    JsonlLogger,
    NoOpLogger,
    ProcessSummary,
    RuleResult,
    Target,
    log_action,
)

# Movement
from .movement import FileMovement

# Profiles
from .profiles import (
    Profile,
    Profiles,
    expand_env_vars,
    get_profile,
    load_profiles,
)

# Validators
from .validators import (
    BooleanValidator,
    ColumnValidator,
    CompletenessValidator,
    CompoundUniqueValidator,
    CompoundValidator,
    DateFormatValidator,
    DistinctnessValidator,
    ExistsValidator,
    FileCompletenessValidator,
    FileValidator,
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
    ValidationReport,
    get_column_validator,
    get_file_validator,
    is_column_level_rule,
    is_file_level_rule,
)

__all__ = [
    # Version
    "__version__",
    # Contracts
    "ColumnContracts",
    "CompoundUnique",
    "Contract",
    "Destination",
    "FileContracts",
    "Quarantine",
    "RuleType",
    "SchemaContracts",
    "Source",
    "ValidationRule",
    "load_contract",
    "load_contract_for_file",
    "parse_contract_data",
    # Connectors
    "AzureConnector",
    "Connector",
    "GCSConnector",
    "LocalConnector",
    "S3Connector",
    "get_connector",
    # Drivers
    "CsvDriver",
    "Driver",
    "ParquetDriver",
    "get_driver",
    "get_extension_from_path",
    # Engine
    "ValidationOutcome",
    "execute_validation",
    "run_contract_validation",
    "validate_data",
    "validate_dataframe",
    # Errors
    "ConnectorError",
    "ContractParseError",
    "DriverError",
    "MovementError",
    "PatternError",
    "ProfileLoadError",
    "ProfileNotFoundError",
    "UnsupportedFormatError",
    "ValidationError",
    # Logging
    "AuditLogEntry",
    "AuditLogger",
    "LogContract",
    "Executor",
    "InMemoryLogger",
    "JsonlLogger",
    "NoOpLogger",
    "ProcessSummary",
    "RuleResult",
    "Target",
    "log_action",
    # Movement
    "FileMovement",
    # Profiles
    "Profile",
    "Profiles",
    "expand_env_vars",
    "get_profile",
    "load_profiles",
    # Validators
    "BooleanValidator",
    "ColumnValidator",
    "CompletenessValidator",
    "CompoundUniqueValidator",
    "CompoundValidator",
    "DateFormatValidator",
    "DistinctnessValidator",
    "ExistsValidator",
    "FileCompletenessValidator",
    "FileValidator",
    "InSetValidator",
    "MaxLengthValidator",
    "MeanBetweenValidator",
    "NotInSetValidator",
    "NotNullValidator",
    "OutlierSigmaValidator",
    "PatternValidator",
    "RangeValidator",
    "RowCountValidator",
    "StdevBetweenValidator",
    "TypeValidator",
    "UniqueValidator",
    "ValidationReport",
    "get_column_validator",
    "get_file_validator",
    "is_column_level_rule",
    "is_file_level_rule",
]

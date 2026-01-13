"""Audit logging for pipe-audit-core.

This module provides structured audit logging for validation events.
Logs are written to JSONL files (one line per event) organized by date.
"""

from __future__ import annotations

import json
import os
import socket
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol


@dataclass
class Contract:
    """Contract metadata for audit logging.

    Attributes:
        name: Contract identifier
        version: Contract version string
    """

    name: str
    version: str


@dataclass
class Target:
    """Target of validation for audit logging.

    Attributes:
        file: File being validated
        column: Optional column being validated
        rule: Optional rule being applied
    """

    file: str
    column: str | None = None
    rule: str | None = None


@dataclass
class RuleResult:
    """Result of a single rule evaluation.

    Attributes:
        column: Which column was validated (or "file" for file-level rules)
        rule: Rule name (e.g., "not_null")
        result: "pass", "fail", or "skipped"
        details: Optional failure details
    """

    column: str
    rule: str
    result: str
    details: str | None = None


@dataclass
class Executor:
    """Executor metadata (who/where ran the validation).

    Attributes:
        user: User ID or system account
        host: Hostname or container ID
    """

    user: str
    host: str

    @classmethod
    def from_environment(cls) -> Executor:
        """Create an Executor from current environment.

        Uses the USER environment variable and hostname.
        """
        user = os.environ.get("USER", os.environ.get("USERNAME", "unknown"))
        host = socket.gethostname()
        return cls(user=user, host=host)


@dataclass
class ProcessSummary:
    """Summary of a full process run.

    Attributes:
        contracts_run: Number of contracts executed
        contracts_failed: Number of contracts that failed
        status: "SUCCESS" or "FAIL"
    """

    contracts_run: int
    contracts_failed: int
    status: str  # "SUCCESS" or "FAIL"


@dataclass
class AuditLogEntry:
    """Top-level audit log entry.

    Each line in audit-YYYY-MM-DD.jsonl will be one of these.

    Attributes:
        timestamp: RFC3339 timestamp
        level: Log level (e.g., "AUDIT", "INFO", "ERROR")
        event: Semantic event name (e.g., "validation_start", "movement_success")
        executor: Who/where ran this
        contract: Optional contract metadata
        target: Optional file/column/rule context
        results: Optional list of validation results
        details: Optional freeform detail string
        summary: Optional summary of a full run
    """

    timestamp: str
    level: str
    event: str
    executor: Executor
    contract: Contract | None = None
    target: Target | None = None
    results: list[RuleResult] | None = None
    details: str | None = None
    summary: ProcessSummary | None = None

    @classmethod
    def create(
        cls,
        event: str,
        executor: Executor,
        level: str = "AUDIT",
        contract: Contract | None = None,
        target: Target | None = None,
        results: list[RuleResult] | None = None,
        details: str | None = None,
        summary: ProcessSummary | None = None,
    ) -> AuditLogEntry:
        """Create an AuditLogEntry with current timestamp.

        Args:
            event: Semantic event name
            executor: Who/where ran this
            level: Log level (default: "AUDIT")
            contract: Optional contract metadata
            target: Optional file/column/rule context
            results: Optional list of validation results
            details: Optional freeform detail string
            summary: Optional summary of a full run

        Returns:
            New AuditLogEntry with current timestamp
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        return cls(
            timestamp=timestamp,
            level=level,
            event=event,
            executor=executor,
            contract=contract,
            target=target,
            results=results,
            details=details,
            summary=summary,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        result = {
            "timestamp": self.timestamp,
            "level": self.level,
            "event": self.event,
            "executor": asdict(self.executor),
        }

        if self.contract is not None:
            result["contract"] = asdict(self.contract)
        if self.target is not None:
            target_dict = {"file": self.target.file}
            if self.target.column is not None:
                target_dict["column"] = self.target.column
            if self.target.rule is not None:
                target_dict["rule"] = self.target.rule
            result["target"] = target_dict
        if self.results is not None:
            result["results"] = [asdict(r) for r in self.results]
        if self.details is not None:
            result["details"] = self.details
        if self.summary is not None:
            result["summary"] = asdict(self.summary)

        return result

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict())


class AuditLogger(Protocol):
    """Protocol for audit loggers."""

    def log_event(self, entry: AuditLogEntry) -> None:
        """Log an audit event.

        Args:
            entry: The audit log entry to record
        """
        ...

    def log_and_print(self, entry: AuditLogEntry, console_msg: str) -> None:
        """Log an audit event and print a message to console.

        Args:
            entry: The audit log entry to record
            console_msg: Message to print to console
        """
        ...


class JsonlLogger:
    """JSONL file-based audit logger.

    Writes audit logs to logs/audit-YYYY-MM-DD.jsonl files.

    Attributes:
        logs_dir: Directory where audit logs are stored
    """

    def __init__(self, logs_dir: str | Path = "logs") -> None:
        """Create a new JSONL logger.

        Args:
            logs_dir: Directory where audit logs will be stored (default: "logs")
        """
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def _today_log_path(self) -> Path:
        """Get today's log file path."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return self.logs_dir / f"audit-{today}.jsonl"

    def log_event(self, entry: AuditLogEntry) -> None:
        """Log an audit event to the daily JSONL file.

        Args:
            entry: The audit log entry to record
        """
        log_path = self._today_log_path()
        json_line = entry.to_json()

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json_line + "\n")

    def log_and_print(self, entry: AuditLogEntry, console_msg: str) -> None:
        """Log an audit event and print a message to console.

        Args:
            entry: The audit log entry to record
            console_msg: Message to print to console
        """
        self.log_event(entry)
        print(console_msg)


class NoOpLogger:
    """No-op logger for testing or silent operation."""

    def log_event(self, entry: AuditLogEntry) -> None:
        """No-op: does nothing."""
        pass

    def log_and_print(self, entry: AuditLogEntry, console_msg: str) -> None:
        """No-op: does nothing."""
        pass


class InMemoryLogger:
    """In-memory logger for testing.

    Stores all log entries in a list for later inspection.

    Attributes:
        entries: List of logged entries
        messages: List of console messages
    """

    def __init__(self) -> None:
        self.entries: list[AuditLogEntry] = []
        self.messages: list[str] = []

    def log_event(self, entry: AuditLogEntry) -> None:
        """Store an audit event in memory.

        Args:
            entry: The audit log entry to record
        """
        self.entries.append(entry)

    def log_and_print(self, entry: AuditLogEntry, console_msg: str) -> None:
        """Store an audit event and console message in memory.

        Args:
            entry: The audit log entry to record
            console_msg: Message that would be printed to console
        """
        self.entries.append(entry)
        self.messages.append(console_msg)

    def clear(self) -> None:
        """Clear all stored entries and messages."""
        self.entries.clear()
        self.messages.clear()


def log_action(
    logger: AuditLogger,
    executor: Executor,
    event: str,
    details: str | None = None,
    contract_name: str | None = None,
    contract_version: str | None = None,
    location: str | None = None,
) -> None:
    """High-level logging wrapper for common events.

    Args:
        logger: The logger to use
        executor: Who/where ran this
        event: Event name
        details: Optional details
        contract_name: Optional contract name
        contract_version: Optional contract version
        location: Optional file location
    """
    contract = None
    if contract_name and contract_version:
        contract = Contract(name=contract_name, version=contract_version)

    target = None
    if location:
        target = Target(file=location)

    entry = AuditLogEntry.create(
        event=event,
        executor=executor,
        contract=contract,
        target=target,
        details=details,
    )
    logger.log_event(entry)

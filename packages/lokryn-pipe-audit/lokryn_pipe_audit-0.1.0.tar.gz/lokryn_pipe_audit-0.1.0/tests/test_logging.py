"""Tests for logging module."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from lokryn_pipe_audit.logging import (
    AuditLogEntry,
    Contract,
    Executor,
    InMemoryLogger,
    JsonlLogger,
    NoOpLogger,
    RuleResult,
    Target,
)


class TestExecutor:
    """Tests for Executor."""

    def test_create(self):
        executor = Executor(user="test_user", host="test_host")
        assert executor.user == "test_user"
        assert executor.host == "test_host"

    def test_from_environment(self):
        executor = Executor.from_environment()
        assert executor.user is not None
        assert executor.host is not None


class TestAuditLogEntry:
    """Tests for AuditLogEntry."""

    def test_create(self):
        executor = Executor(user="test", host="host")
        entry = AuditLogEntry.create(
            event="test_event",
            executor=executor,
            details="test details",
        )
        assert entry.event == "test_event"
        assert entry.level == "AUDIT"
        assert entry.details == "test details"
        assert entry.timestamp is not None

    def test_to_dict(self):
        executor = Executor(user="test", host="host")
        entry = AuditLogEntry.create(
            event="test_event",
            executor=executor,
            contract=Contract(name="test_contract", version="1.0.0"),
        )
        d = entry.to_dict()
        assert d["event"] == "test_event"
        assert d["executor"]["user"] == "test"
        assert d["contract"]["name"] == "test_contract"

    def test_to_dict_excludes_none(self):
        executor = Executor(user="test", host="host")
        entry = AuditLogEntry.create(
            event="test_event",
            executor=executor,
        )
        d = entry.to_dict()
        assert "contract" not in d
        assert "results" not in d

    def test_to_json(self):
        executor = Executor(user="test", host="host")
        entry = AuditLogEntry.create(
            event="test_event",
            executor=executor,
        )
        json_str = entry.to_json()
        parsed = json.loads(json_str)
        assert parsed["event"] == "test_event"


class TestInMemoryLogger:
    """Tests for InMemoryLogger."""

    def test_log_event(self):
        logger = InMemoryLogger()
        executor = Executor(user="test", host="host")
        entry = AuditLogEntry.create(event="test", executor=executor)

        logger.log_event(entry)
        assert len(logger.entries) == 1
        assert logger.entries[0].event == "test"

    def test_log_and_print(self, capsys):
        logger = InMemoryLogger()
        executor = Executor(user="test", host="host")
        entry = AuditLogEntry.create(event="test", executor=executor)

        logger.log_and_print(entry, "Console message")
        assert len(logger.entries) == 1
        assert len(logger.messages) == 1
        assert logger.messages[0] == "Console message"

    def test_clear(self):
        logger = InMemoryLogger()
        executor = Executor(user="test", host="host")
        entry = AuditLogEntry.create(event="test", executor=executor)

        logger.log_event(entry)
        logger.log_and_print(entry, "msg")
        logger.clear()

        assert len(logger.entries) == 0
        assert len(logger.messages) == 0


class TestNoOpLogger:
    """Tests for NoOpLogger."""

    def test_log_event_does_nothing(self):
        logger = NoOpLogger()
        executor = Executor(user="test", host="host")
        entry = AuditLogEntry.create(event="test", executor=executor)
        logger.log_event(entry)  # Should not raise

    def test_log_and_print_does_nothing(self):
        logger = NoOpLogger()
        executor = Executor(user="test", host="host")
        entry = AuditLogEntry.create(event="test", executor=executor)
        logger.log_and_print(entry, "msg")  # Should not raise


class TestJsonlLogger:
    """Tests for JsonlLogger."""

    def test_creates_logs_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logs_dir = Path(tmpdir) / "logs"
            logger = JsonlLogger(logs_dir)
            assert logs_dir.exists()

    def test_log_event_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logs_dir = Path(tmpdir) / "logs"
            logger = JsonlLogger(logs_dir)

            executor = Executor(user="test", host="host")
            entry = AuditLogEntry.create(event="test_event", executor=executor)
            logger.log_event(entry)

            # Check that a log file was created
            log_files = list(logs_dir.glob("audit-*.jsonl"))
            assert len(log_files) == 1

            # Check content
            content = log_files[0].read_text()
            parsed = json.loads(content.strip())
            assert parsed["event"] == "test_event"

    def test_multiple_events_same_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logs_dir = Path(tmpdir) / "logs"
            logger = JsonlLogger(logs_dir)

            executor = Executor(user="test", host="host")

            for i in range(3):
                entry = AuditLogEntry.create(event=f"event_{i}", executor=executor)
                logger.log_event(entry)

            log_files = list(logs_dir.glob("audit-*.jsonl"))
            assert len(log_files) == 1

            lines = log_files[0].read_text().strip().split("\n")
            assert len(lines) == 3

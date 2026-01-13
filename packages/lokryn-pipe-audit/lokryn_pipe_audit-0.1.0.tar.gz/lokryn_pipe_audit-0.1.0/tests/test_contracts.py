"""Tests for contracts module."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from lokryn_pipe_audit.contracts import (
    RuleType,
    ValidationRule,
    load_contract,
    parse_contract_data,
)
from lokryn_pipe_audit.errors import ContractParseError


class TestValidationRule:
    """Tests for ValidationRule."""

    def test_from_dict_not_null(self):
        rule = ValidationRule.from_dict({"rule": "not_null"})
        assert rule.rule_type == RuleType.NOT_NULL
        assert rule.params == {}

    def test_from_dict_with_params(self):
        rule = ValidationRule.from_dict({"rule": "range", "min": 0, "max": 100})
        assert rule.rule_type == RuleType.RANGE
        assert rule.params == {"min": 0, "max": 100}

    def test_from_dict_pattern(self):
        rule = ValidationRule.from_dict({"rule": "pattern", "pattern": "^[A-Z]+$"})
        assert rule.rule_type == RuleType.PATTERN
        assert rule.params["pattern"] == "^[A-Z]+$"

    def test_from_dict_unknown_rule(self):
        with pytest.raises(ContractParseError) as exc_info:
            ValidationRule.from_dict({"rule": "unknown_rule"})
        assert "Unknown rule type" in str(exc_info.value)

    def test_from_dict_missing_rule(self):
        with pytest.raises(ContractParseError) as exc_info:
            ValidationRule.from_dict({"min": 0, "max": 100})
        assert "missing 'rule' field" in str(exc_info.value)


class TestParseContractData:
    """Tests for parse_contract_data."""

    def test_minimal_contract(self):
        data = {
            "contract": {
                "name": "test",
                "version": "1.0.0",
            },
            "columns": [],
        }
        contracts = parse_contract_data(data)
        assert contracts.contract.name == "test"
        assert contracts.contract.version == "1.0.0"
        assert contracts.columns == []

    def test_full_contract(self):
        data = {
            "contract": {
                "name": "test",
                "version": "1.0.0",
                "tags": ["demo"],
            },
            "file": {
                "validation": [{"rule": "row_count", "min": 10, "max": 100}],
            },
            "columns": [
                {
                    "name": "id",
                    "validation": [{"rule": "not_null"}, {"rule": "unique"}],
                }
            ],
            "compound_unique": [{"columns": ["a", "b"]}],
            "source": {
                "type": "local",
                "location": "data.csv",
            },
            "destination": {
                "type": "local",
                "location": "output/",
            },
        }
        contracts = parse_contract_data(data)

        assert contracts.contract.name == "test"
        assert contracts.file is not None
        assert len(contracts.file.validation) == 1
        assert contracts.file.validation[0].rule_type == RuleType.ROW_COUNT
        assert len(contracts.columns) == 1
        assert contracts.columns[0].name == "id"
        assert len(contracts.columns[0].validation) == 2
        assert contracts.compound_unique is not None
        assert len(contracts.compound_unique) == 1
        assert contracts.source is not None
        assert contracts.source.type == "local"
        assert contracts.destination is not None

    def test_missing_contract_section(self):
        data = {"columns": []}
        with pytest.raises(ContractParseError) as exc_info:
            parse_contract_data(data)
        assert "Missing required 'contract' section" in str(exc_info.value)


class TestLoadContract:
    """Tests for load_contract."""

    def test_load_valid_contract(self, sample_contract_toml):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(sample_contract_toml)
            f.flush()
            path = Path(f.name)

        try:
            contracts = load_contract(path)
            assert contracts.contract.name == "test_contract"
            assert contracts.contract.version == "1.0.0"
            assert contracts.file is not None
            assert len(contracts.columns) == 3
        finally:
            path.unlink()

    def test_load_nonexistent_file(self):
        with pytest.raises(ContractParseError) as exc_info:
            load_contract("nonexistent.toml")
        assert "not found" in str(exc_info.value)

    def test_load_invalid_toml(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write("this is not valid toml [[[")
            f.flush()
            path = Path(f.name)

        try:
            with pytest.raises(ContractParseError) as exc_info:
                load_contract(path)
            assert "Invalid TOML" in str(exc_info.value)
        finally:
            path.unlink()

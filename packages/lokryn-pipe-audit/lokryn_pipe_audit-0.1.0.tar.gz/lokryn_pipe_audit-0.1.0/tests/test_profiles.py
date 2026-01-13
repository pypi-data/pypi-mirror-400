"""Tests for profiles module."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from lokryn_pipe_audit.profiles import (
    Profile,
    expand_env_vars,
    get_profile,
    load_profiles,
)
from lokryn_pipe_audit.errors import ProfileLoadError, ProfileNotFoundError


class TestExpandEnvVars:
    """Tests for expand_env_vars."""

    def test_expand_single_var(self):
        os.environ["TEST_VAR"] = "hello"
        result = expand_env_vars("${TEST_VAR}")
        assert result == "hello"
        del os.environ["TEST_VAR"]

    def test_expand_multiple_vars(self):
        os.environ["VAR1"] = "hello"
        os.environ["VAR2"] = "world"
        result = expand_env_vars("${VAR1} ${VAR2}")
        assert result == "hello world"
        del os.environ["VAR1"]
        del os.environ["VAR2"]

    def test_no_expansion_needed(self):
        result = expand_env_vars("plain text")
        assert result == "plain text"

    def test_missing_var_preserved(self):
        result = expand_env_vars("${NONEXISTENT_VAR}")
        assert result == "${NONEXISTENT_VAR}"

    def test_mixed_expansion(self):
        os.environ["FOUND_VAR"] = "found"
        result = expand_env_vars("prefix-${FOUND_VAR}-${NOT_FOUND}-suffix")
        assert result == "prefix-found-${NOT_FOUND}-suffix"
        del os.environ["FOUND_VAR"]


class TestProfile:
    """Tests for Profile dataclass."""

    def test_from_dict_minimal(self):
        data = {"provider": "local"}
        profile = Profile.from_dict(data)
        assert profile.provider == "local"
        assert profile.region is None
        assert profile.access_key is None

    def test_from_dict_s3(self):
        data = {
            "provider": "s3",
            "region": "us-east-1",
            "access_key": "AKIAIOSFODNN7EXAMPLE",
            "secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
            "path_style": True,
        }
        profile = Profile.from_dict(data)
        assert profile.provider == "s3"
        assert profile.region == "us-east-1"
        assert profile.access_key == "AKIAIOSFODNN7EXAMPLE"
        assert profile.path_style is True


class TestLoadProfiles:
    """Tests for load_profiles."""

    def test_load_valid_profiles(self, sample_profiles_toml):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(sample_profiles_toml)
            f.flush()
            path = Path(f.name)

        try:
            profiles = load_profiles(path)
            assert "local_profile" in profiles
            assert "s3_profile" in profiles
            assert profiles["s3_profile"].region == "us-east-1"
        finally:
            path.unlink()

    def test_load_nonexistent_file(self):
        with pytest.raises(ProfileLoadError) as exc_info:
            load_profiles("nonexistent.toml")
        assert "not found" in str(exc_info.value)

    def test_load_with_env_expansion(self):
        os.environ["TEST_ACCESS_KEY"] = "expanded_key"
        toml_content = """
[test_profile]
provider = "s3"
access_key = "${TEST_ACCESS_KEY}"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(toml_content)
            f.flush()
            path = Path(f.name)

        try:
            profiles = load_profiles(path)
            assert profiles["test_profile"].access_key == "expanded_key"
        finally:
            path.unlink()
            del os.environ["TEST_ACCESS_KEY"]


class TestGetProfile:
    """Tests for get_profile."""

    def test_get_existing_profile(self):
        profiles = {"test": Profile(provider="local")}
        profile = get_profile(profiles, "test")
        assert profile.provider == "local"

    def test_get_nonexistent_profile(self):
        profiles = {"test": Profile(provider="local")}
        with pytest.raises(ProfileNotFoundError) as exc_info:
            get_profile(profiles, "nonexistent")
        assert "nonexistent" in str(exc_info.value)

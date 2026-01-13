"""Tests for serializer module."""

import tempfile
from pathlib import Path

import pytest

from aiauto.serializer import build_requirements, object_to_json, serialize


class TestSerialize:
    """Test serialize function."""

    def test_serialize_function_success(self):
        """Test serializing a function defined in a file."""

        def sample_function(x):
            return x * 2

        # Functions defined in test files can be serialized
        result = serialize(sample_function)
        assert "def sample_function(x):" in result
        assert "return x * 2" in result

    def test_serialize_lambda_success(self):
        """Test serializing lambda defined in file."""
        func = lambda x: x * 2  # noqa: E731
        # Lambda in file can be serialized
        result = serialize(func)
        assert "lambda" in result

    def test_serialize_builtin_fails(self):
        """Test serializing builtin function fails."""
        with pytest.raises(ValueError, match="Serialize 실패"):
            serialize(len)


class TestBuildRequirements:
    """Test build_requirements function."""

    def test_from_file(self):
        """Test building requirements from file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("numpy>=1.0\npandas>=2.0\n")
            f.flush()

            result = build_requirements(file_path=f.name)
            assert result == "numpy>=1.0\npandas>=2.0\n"

            Path(f.name).unlink()

    def test_from_list(self):
        """Test building requirements from list."""
        result = build_requirements(reqs=["numpy>=1.0", "pandas>=2.0"])
        assert result == "numpy>=1.0\npandas>=2.0"

    def test_empty_when_none(self):
        """Test empty string when no arguments."""
        result = build_requirements()
        assert result == ""

    def test_both_raises_error(self):
        """Test providing both file_path and reqs raises error."""
        with pytest.raises(ValueError, match="동시에 지정할 수 없습니다"):
            build_requirements(file_path="requirements.txt", reqs=["numpy"])

    def test_empty_list(self):
        """Test empty list returns empty string."""
        result = build_requirements(reqs=[])
        assert result == ""


class TestObjectToJson:
    """Test object_to_json function."""

    def test_none_returns_empty(self):
        """Test None returns empty string."""
        result = object_to_json(None)
        assert result == ""

    def test_dict_returns_json(self):
        """Test dict returns JSON string."""
        result = object_to_json({"key": "value", "num": 42})
        assert '"key"' in result
        assert '"value"' in result
        assert "42" in result

    def test_non_optuna_class_raises_error(self):
        """Test non-optuna class raises error."""

        class CustomClass:
            pass

        obj = CustomClass()
        with pytest.raises(ValueError, match="optuna 코어 클래스만 지원합니다"):
            object_to_json(obj)

    def test_empty_dict(self):
        """Test empty dict returns JSON."""
        result = object_to_json({})
        assert result == "{}"

"""Tests for core utility functions."""

import pytest

from aiauto.core import (
    MAX_K8S_NAME_LENGTH,
    WaitOption,
    _should_retry_rpc_error,
    _validate_study_name,
)
from aiauto.http_client import ConnectRPCError


class TestValidateStudyName:
    """Test _validate_study_name function."""

    def test_valid_simple_name(self):
        """Test valid simple study name."""
        _validate_study_name("my-study")  # Should not raise

    def test_valid_name_with_numbers(self):
        """Test valid name with numbers."""
        _validate_study_name("study-123")  # Should not raise

    def test_valid_name_only_numbers(self):
        """Test valid name with only numbers."""
        _validate_study_name("123")  # Should not raise

    def test_valid_name_starts_with_number(self):
        """Test valid name starting with number."""
        _validate_study_name("1-study")  # Should not raise

    def test_valid_single_char(self):
        """Test valid single character name."""
        _validate_study_name("a")  # Should not raise

    def test_valid_max_length(self):
        """Test valid name at max length."""
        name = "a" * MAX_K8S_NAME_LENGTH
        _validate_study_name(name)  # Should not raise

    def test_empty_name_raises_error(self):
        """Test empty name raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            _validate_study_name("")

    def test_too_long_name_raises_error(self):
        """Test name exceeding 63 characters raises ValueError."""
        name = "a" * (MAX_K8S_NAME_LENGTH + 1)
        with pytest.raises(ValueError, match="too long"):
            _validate_study_name(name)

    def test_uppercase_raises_error(self):
        """Test uppercase letters raise ValueError."""
        with pytest.raises(ValueError, match="lowercase letters"):
            _validate_study_name("My-Study")

    def test_underscore_raises_error(self):
        """Test underscore raises ValueError."""
        with pytest.raises(ValueError, match="lowercase letters"):
            _validate_study_name("my_study")

    def test_starts_with_hyphen_raises_error(self):
        """Test name starting with hyphen raises ValueError."""
        with pytest.raises(ValueError, match="Must start and end"):
            _validate_study_name("-study")

    def test_ends_with_hyphen_raises_error(self):
        """Test name ending with hyphen raises ValueError."""
        with pytest.raises(ValueError, match="Must start and end"):
            _validate_study_name("study-")

    def test_special_chars_raises_error(self):
        """Test special characters raise ValueError."""
        with pytest.raises(ValueError, match="lowercase letters"):
            _validate_study_name("my.study")
        with pytest.raises(ValueError, match="lowercase letters"):
            _validate_study_name("my@study")
        with pytest.raises(ValueError, match="lowercase letters"):
            _validate_study_name("my study")


class TestShouldRetryRpcError:
    """Test _should_retry_rpc_error function."""

    def test_retryable_unavailable(self):
        """Test unavailable error is retryable."""
        error = ConnectRPCError("unavailable", "Service unavailable")
        assert _should_retry_rpc_error(error) is True

    def test_not_retryable_failed_precondition(self):
        """Test failed_precondition error is NOT retryable (영구 실패)."""
        error = ConnectRPCError("failed_precondition", "Not ready")
        assert _should_retry_rpc_error(error) is False

    def test_not_retryable_not_found(self):
        """Test not_found error is not retryable."""
        error = ConnectRPCError("not_found", "Not found")
        assert _should_retry_rpc_error(error) is False

    def test_not_retryable_runtime_error(self):
        """Test RuntimeError is not retryable."""
        error = RuntimeError("Some error")
        assert _should_retry_rpc_error(error) is False

    def test_not_retryable_value_error(self):
        """Test ValueError is not retryable."""
        error = ValueError("Invalid value")
        assert _should_retry_rpc_error(error) is False


class TestWaitOption:
    """Test WaitOption enum."""

    def test_wait_no_value(self):
        """Test WAIT_NO has correct value."""
        assert WaitOption.WAIT_NO.value == "wait_no"

    def test_wait_atleast_one_value(self):
        """Test WAIT_ATLEAST_ONE_TRIAL has correct value."""
        assert WaitOption.WAIT_ATLEAST_ONE_TRIAL.value == "wait_atleast_one"

    def test_wait_all_value(self):
        """Test WAIT_ALL_TRIALS has correct value."""
        assert WaitOption.WAIT_ALL_TRIALS.value == "wait_all"

    def test_enum_members(self):
        """Test all enum members exist."""
        assert len(WaitOption) == 3
        assert WaitOption.WAIT_NO in WaitOption
        assert WaitOption.WAIT_ATLEAST_ONE_TRIAL in WaitOption
        assert WaitOption.WAIT_ALL_TRIALS in WaitOption


class TestConstants:
    """Test module-level constants."""

    def test_max_k8s_name_length(self):
        """Test MAX_K8S_NAME_LENGTH is 63."""
        assert MAX_K8S_NAME_LENGTH == 63

"""
Tests for MCP handler utilities.

Tests common handler functionality including path validation,
rate limiting, and audit logging.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from spreadsheet_dl._mcp.config import MCPConfig
from spreadsheet_dl._mcp.exceptions import MCPSecurityError
from spreadsheet_dl._mcp.handlers import HandlerUtils
from spreadsheet_dl._mcp.models import MCPToolResult
from spreadsheet_dl.exceptions import FileError

pytestmark = [pytest.mark.unit, pytest.mark.mcp]


class TestHandlerUtils:
    """Tests for HandlerUtils class."""

    @pytest.fixture
    def config(self, tmp_path: Path) -> MCPConfig:
        """Create test config."""
        return MCPConfig(
            allowed_paths=[tmp_path],
            rate_limit_per_minute=10,
            enable_audit_log=True,
            audit_log_path=tmp_path / "audit.log",
        )

    @pytest.fixture
    def logger(self) -> logging.Logger:
        """Create test logger."""
        return logging.getLogger("test")

    @pytest.fixture
    def utils(self, config: MCPConfig, logger: logging.Logger) -> HandlerUtils:
        """Create handler utils instance."""
        return HandlerUtils(config, logger)

    def test_init(self, config: MCPConfig, logger: logging.Logger) -> None:
        """Test HandlerUtils initialization."""
        utils = HandlerUtils(config, logger)

        assert utils.config == config
        assert utils.logger == logger
        assert utils._request_count == 0
        assert isinstance(utils._last_reset, datetime)

    def test_validate_path_success(self, utils: HandlerUtils, tmp_path: Path) -> None:
        """Test path validation with allowed path."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        result = utils._validate_path(test_file)

        assert result == test_file.resolve()

    def test_validate_path_string_input(
        self, utils: HandlerUtils, tmp_path: Path
    ) -> None:
        """Test path validation with string path."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        result = utils._validate_path(str(test_file))

        assert result == test_file.resolve()

    def test_validate_path_not_allowed(self, utils: HandlerUtils) -> None:
        """Test path validation rejects disallowed paths."""
        # Create file outside allowed paths
        disallowed = Path("/etc/passwd")

        with pytest.raises(MCPSecurityError) as exc_info:
            utils._validate_path(disallowed)

        assert "Path not allowed" in str(exc_info.value)
        assert "Allowed paths" in str(exc_info.value)

    def test_validate_path_not_exists(
        self, utils: HandlerUtils, tmp_path: Path
    ) -> None:
        """Test path validation rejects non-existent files."""
        nonexistent = tmp_path / "does_not_exist.txt"

        with pytest.raises(FileError) as exc_info:
            utils._validate_path(nonexistent)

        assert "File not found" in str(exc_info.value)

    def test_validate_path_subdirectory(
        self, utils: HandlerUtils, tmp_path: Path
    ) -> None:
        """Test path validation allows subdirectories."""
        subdir = tmp_path / "sub" / "dir"
        subdir.mkdir(parents=True)
        test_file = subdir / "test.txt"
        test_file.write_text("test")

        result = utils._validate_path(test_file)

        assert result == test_file.resolve()

    def test_check_rate_limit_within_limit(self, utils: HandlerUtils) -> None:
        """Test rate limit check within limits."""
        # Make 5 requests (limit is 10)
        for _ in range(5):
            assert utils._check_rate_limit() is True

    def test_check_rate_limit_exceeds_limit(self, utils: HandlerUtils) -> None:
        """Test rate limit check when exceeded."""
        # Make 11 requests (limit is 10)
        for _ in range(10):
            utils._check_rate_limit()

        # 11th request should exceed limit
        assert utils._check_rate_limit() is False

    def test_check_rate_limit_resets_after_minute(self, utils: HandlerUtils) -> None:
        """Test rate limit resets after 60 seconds."""
        # Exceed limit
        for _ in range(11):
            utils._check_rate_limit()

        # Manually reset timestamp to simulate 60+ seconds passing
        utils._last_reset = datetime.now() - timedelta(seconds=61)

        # Should allow requests again
        assert utils._check_rate_limit() is True

    def test_log_audit_with_audit_enabled(
        self, utils: HandlerUtils, tmp_path: Path, logger: logging.Logger
    ) -> None:
        """Test audit logging when enabled."""
        result = MCPToolResult(content=[{"type": "text", "text": "success"}])

        with patch.object(logger, "info") as mock_info:
            utils._log_audit(
                tool="test_tool",
                params={"arg1": "value1"},
                result=result,
            )

        # Verify logger was called
        mock_info.assert_called_once()
        log_data = json.loads(mock_info.call_args[0][0])
        assert log_data["tool"] == "test_tool"
        assert log_data["params"]["arg1"] == "value1"
        assert log_data["success"] is True
        assert "timestamp" in log_data

    def test_log_audit_with_error_result(
        self, utils: HandlerUtils, logger: logging.Logger
    ) -> None:
        """Test audit logging with error result."""
        result = MCPToolResult(
            content=[{"type": "text", "text": "error"}],
            is_error=True,
        )

        with patch.object(logger, "info") as mock_info:
            utils._log_audit(
                tool="test_tool",
                params={},
                result=result,
            )

        log_data = json.loads(mock_info.call_args[0][0])
        assert log_data["success"] is False

    def test_log_audit_writes_to_file(
        self, utils: HandlerUtils, tmp_path: Path
    ) -> None:
        """Test audit logging writes to file."""
        result = MCPToolResult(content=[{"type": "text", "text": "success"}])

        utils._log_audit(
            tool="test_tool",
            params={"key": "value"},
            result=result,
        )

        # Verify file was written
        audit_file = tmp_path / "audit.log"
        assert audit_file.exists()

        content = audit_file.read_text()
        log_entry = json.loads(content.strip())
        assert log_entry["tool"] == "test_tool"
        assert log_entry["params"]["key"] == "value"

    def test_log_audit_disabled(self, tmp_path: Path, logger: logging.Logger) -> None:
        """Test audit logging when disabled."""
        config = MCPConfig(
            allowed_paths=[tmp_path],
            enable_audit_log=False,
        )
        utils = HandlerUtils(config, logger)
        result = MCPToolResult(content=[{"type": "text", "text": "success"}])

        with patch.object(logger, "info") as mock_info:
            utils._log_audit(
                tool="test_tool",
                params={},
                result=result,
            )

        # Logger should not be called when audit is disabled
        mock_info.assert_not_called()

    def test_log_audit_no_path_configured(
        self, tmp_path: Path, logger: logging.Logger
    ) -> None:
        """Test audit logging without file path."""
        config = MCPConfig(
            allowed_paths=[tmp_path],
            enable_audit_log=True,
            audit_log_path=None,
        )
        utils = HandlerUtils(config, logger)
        result = MCPToolResult(content=[{"type": "text", "text": "success"}])

        with patch.object(logger, "info") as mock_info:
            utils._log_audit(
                tool="test_tool",
                params={},
                result=result,
            )

        # Logger should be called but no file written
        mock_info.assert_called_once()

    def test_log_audit_multiple_params(
        self, utils: HandlerUtils, logger: logging.Logger
    ) -> None:
        """Test audit logging with multiple parameters."""
        result = MCPToolResult(content=[{"type": "text", "text": "success"}])

        with patch.object(logger, "info") as mock_info:
            utils._log_audit(
                tool="complex_tool",
                params={
                    "str_param": "value",
                    "int_param": 42,
                    "bool_param": True,
                    "path_param": Path("/tmp/test"),
                },
                result=result,
            )

        log_data = json.loads(mock_info.call_args[0][0])
        assert log_data["params"]["str_param"] == "value"
        assert log_data["params"]["int_param"] == "42"
        assert log_data["params"]["bool_param"] == "True"
        assert "/tmp/test" in log_data["params"]["path_param"]

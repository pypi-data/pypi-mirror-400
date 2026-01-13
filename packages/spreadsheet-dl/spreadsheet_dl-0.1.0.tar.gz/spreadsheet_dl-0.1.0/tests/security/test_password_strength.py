"""Tests for password strength enforcement.

Tests the password strength checking and enforcement in CredentialStore
to prevent brute force attacks.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from spreadsheet_dl.security import (
    CredentialStore,
    check_password_strength,
    generate_password,
)


class TestPasswordStrengthChecker:
    """Test password strength checking function."""

    def test_weak_password_detected(self) -> None:
        """Test that weak passwords are detected."""
        result = check_password_strength("password")
        assert result["level"] == "weak"
        assert result["score"] < 50
        assert len(result["feedback"]) > 0

    def test_fair_password_detected(self) -> None:
        """Test that fair passwords are detected."""
        result = check_password_strength("Password1")
        assert result["level"] in ["fair", "good"]
        assert result["score"] >= 40

    def test_strong_password_detected(self) -> None:
        """Test that strong passwords are detected."""
        result = check_password_strength("MyStr0ng!Pass24")
        assert result["level"] in ["strong", "very_strong"]
        assert result["score"] >= 80

    def test_length_scoring(self) -> None:
        """Test that password length affects score."""
        short = check_password_strength("Abc1!")
        medium = check_password_strength("Abc1!Abc1!Abc1!")
        long_pass = check_password_strength("Abc1!Abc1!Abc1!Abc1!Abc1!")

        assert short["score"] < medium["score"] < long_pass["score"]

    def test_character_variety_requirements(self) -> None:
        """Test that all character types are checked."""
        result = check_password_strength("onlylowercase")
        assert not result["requirements_met"]["uppercase"]
        assert not result["requirements_met"]["digit"]
        assert not result["requirements_met"]["symbol"]

    def test_feedback_messages(self) -> None:
        """Test that helpful feedback is provided."""
        result = check_password_strength("short")
        assert (
            any("lowercase" in fb.lower() for fb in result["feedback"])
            or result["requirements_met"]["lowercase"]
        )
        assert any("uppercase" in fb.lower() for fb in result["feedback"])


class TestPasswordGenerator:
    """Test secure password generation."""

    def test_generated_password_minimum_length(self) -> None:
        """Test that generated passwords meet minimum length."""
        password = generate_password(length=8)  # Will be increased to 12
        assert len(password) >= 12

    def test_generated_password_has_variety(self) -> None:
        """Test that generated passwords have character variety."""
        password = generate_password(length=20, include_symbols=True)

        assert any(c.islower() for c in password)
        assert any(c.isupper() for c in password)
        assert any(c.isdigit() for c in password)
        assert any(not c.isalnum() for c in password)

    def test_generated_password_without_symbols(self) -> None:
        """Test password generation without symbols."""
        password = generate_password(length=16, include_symbols=False)

        assert len(password) == 16
        assert any(c.islower() for c in password)
        assert any(c.isupper() for c in password)
        assert any(c.isdigit() for c in password)
        assert all(c.isalnum() for c in password)

    def test_generated_passwords_are_unique(self) -> None:
        """Test that generated passwords are unique (high entropy)."""
        passwords = {generate_password(length=20) for _ in range(100)}
        assert len(passwords) == 100  # All unique

    def test_generated_password_is_strong(self) -> None:
        """Test that generated passwords are rated as strong."""
        password = generate_password(length=24, include_symbols=True)
        result = check_password_strength(password)
        assert result["level"] in ["strong", "very_strong"]


class TestCredentialStorePasswordEnforcement:
    """Test password strength enforcement in CredentialStore."""

    def test_weak_password_rejected_by_default(self) -> None:
        """Test that weak passwords are rejected by default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "creds.enc"
            store = CredentialStore(store_path)

            with pytest.raises(ValueError, match="Master password too weak"):
                store.store_credential("test_key", "test_value", "weak")

    def test_strong_password_accepted(self) -> None:
        """Test that strong passwords are accepted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "creds.enc"
            store = CredentialStore(store_path)

            # Should not raise
            store.store_credential("test_key", "test_value", "MyStr0ng!Password24")

    def test_enforcement_can_be_disabled_for_testing(self) -> None:
        """Test that enforcement can be disabled with flag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "creds.enc"
            store = CredentialStore(store_path)

            # Should not raise when enforcement disabled
            store.store_credential(
                "test_key",
                "test_value",
                "weak",
                enforce_password_strength=False,
            )

    def test_error_message_provides_guidance(self) -> None:
        """Test that error messages provide helpful guidance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "creds.enc"
            store = CredentialStore(store_path)

            try:
                store.store_credential("test_key", "test_value", "short")
            except ValueError as e:
                error_msg = str(e)
                assert "weak" in error_msg.lower()
                assert "generate_password" in error_msg
                assert "12+" in error_msg or "characters" in error_msg

    def test_credential_retrieval_unchanged(self) -> None:
        """Test that credential retrieval is not affected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "creds.enc"
            store = CredentialStore(store_path)

            password = "MyStr0ng!Password24"
            store.store_credential("api_key", "secret_value", password)

            # Retrieval should work normally
            retrieved = store.get_credential("api_key", password)
            assert retrieved == "secret_value"


class TestPasswordSecurityIntegration:
    """Integration tests for password security features."""

    def test_full_workflow_with_generated_password(self) -> None:
        """Test complete workflow with generated password."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "creds.enc"
            store = CredentialStore(store_path)

            # Generate strong password
            master_password = generate_password(length=24, include_symbols=True)

            # Verify it's strong
            strength = check_password_strength(master_password)
            assert strength["level"] in ["strong", "very_strong"]

            # Store credential (should succeed)
            store.store_credential("api_key", "secret", master_password)

            # Retrieve credential
            retrieved = store.get_credential("api_key", master_password)
            assert retrieved == "secret"

    def test_multiple_credentials_with_same_password(self) -> None:
        """Test storing multiple credentials with same master password."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "creds.enc"
            store = CredentialStore(store_path)

            password = "MyStr0ng!Password24"

            store.store_credential("key1", "value1", password)
            store.store_credential("key2", "value2", password)
            store.store_credential("key3", "value3", password)

            assert store.get_credential("key1", password) == "value1"
            assert store.get_credential("key2", password) == "value2"
            assert store.get_credential("key3", password) == "value3"

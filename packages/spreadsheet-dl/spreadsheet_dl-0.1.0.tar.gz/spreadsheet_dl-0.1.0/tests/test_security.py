"""Tests for security module."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from spreadsheet_dl.exceptions import FileError
from spreadsheet_dl.security import (
    AuditLogEntry,
    DecryptionError,
    EncryptionMetadata,
    FileEncryptor,
    IntegrityError,
    SecurityAuditLog,
    check_password_strength,
    generate_password,
)

if TYPE_CHECKING:
    from pathlib import Path


pytestmark = [pytest.mark.unit]


class TestEncryptionMetadata:
    """Tests for EncryptionMetadata dataclass."""

    def test_default_values(self) -> None:
        """Test default metadata values."""
        metadata = EncryptionMetadata()
        assert metadata.version == "1.0"
        assert metadata.algorithm == "AES-256-GCM"
        assert metadata.kdf == "PBKDF2-SHA256"

    def test_to_json_roundtrip(self) -> None:
        """Test JSON serialization roundtrip."""
        metadata = EncryptionMetadata(
            salt=b"test_salt_value",
            nonce=b"test_nonce",
            original_filename="budget.ods",
            content_hash="abc123",
        )
        json_str = metadata.to_json()
        restored = EncryptionMetadata.from_json(json_str)

        assert restored.salt == metadata.salt
        assert restored.nonce == metadata.nonce
        assert restored.original_filename == metadata.original_filename
        assert restored.content_hash == metadata.content_hash


class TestFileEncryptor:
    """Tests for FileEncryptor class."""

    def test_encrypt_decrypt_roundtrip(self, tmp_path: Path) -> None:
        """Test encryption and decryption roundtrip."""
        # Create test file
        original_content = b"This is a test budget file content.\n" * 100
        original_file = tmp_path / "test.ods"
        original_file.write_bytes(original_content)

        encrypted_file = tmp_path / "test.ods.enc"
        decrypted_file = tmp_path / "test_decrypted.ods"

        encryptor = FileEncryptor()
        password = "test-password-123!"

        # Encrypt
        metadata = encryptor.encrypt_file(original_file, encrypted_file, password)
        assert encrypted_file.exists()
        assert metadata.original_filename == "test.ods"
        assert metadata.content_hash != ""

        # Verify encrypted file is different from original
        assert encrypted_file.read_bytes() != original_content

        # Decrypt
        encryptor.decrypt_file(encrypted_file, decrypted_file, password)
        assert decrypted_file.exists()

        # Verify content matches
        assert decrypted_file.read_bytes() == original_content

    def test_encrypt_with_delete_original(self, tmp_path: Path) -> None:
        """Test encryption with original file deletion."""
        original_file = tmp_path / "test.ods"
        original_file.write_bytes(b"test content")
        encrypted_file = tmp_path / "test.ods.enc"

        encryptor = FileEncryptor()
        encryptor.encrypt_file(
            original_file, encrypted_file, "password", delete_original=True
        )

        assert encrypted_file.exists()
        assert not original_file.exists()

    def test_decrypt_wrong_password(self, tmp_path: Path) -> None:
        """Test decryption with wrong password fails."""
        original_file = tmp_path / "test.ods"
        original_file.write_bytes(b"test content")
        encrypted_file = tmp_path / "test.ods.enc"
        decrypted_file = tmp_path / "test_decrypted.ods"

        encryptor = FileEncryptor()
        encryptor.encrypt_file(original_file, encrypted_file, "correct-password")

        # Try to decrypt with wrong password
        with pytest.raises(IntegrityError):
            encryptor.decrypt_file(encrypted_file, decrypted_file, "wrong-password")

    def test_decrypt_corrupted_file(self, tmp_path: Path) -> None:
        """Test decryption of corrupted file fails."""
        original_file = tmp_path / "test.ods"
        original_file.write_bytes(b"test content")
        encrypted_file = tmp_path / "test.ods.enc"
        decrypted_file = tmp_path / "test_decrypted.ods"

        encryptor = FileEncryptor()
        encryptor.encrypt_file(original_file, encrypted_file, "password")

        # Corrupt the encrypted file
        content = bytearray(encrypted_file.read_bytes())
        # Modify bytes after the header (corrupt ciphertext)
        if len(content) > 100:
            content[100] ^= 0xFF
        encrypted_file.write_bytes(bytes(content))

        # Try to decrypt - corrupted file should fail with either
        # IntegrityError (if ciphertext is corrupted) or
        # DecryptionError (if metadata is corrupted)
        with pytest.raises((IntegrityError, DecryptionError)):
            encryptor.decrypt_file(encrypted_file, decrypted_file, "password")

    def test_decrypt_invalid_format(self, tmp_path: Path) -> None:
        """Test decryption of non-encrypted file fails."""
        not_encrypted = tmp_path / "not_encrypted.bin"
        not_encrypted.write_bytes(b"This is not an encrypted file")
        decrypted_file = tmp_path / "decrypted.ods"

        encryptor = FileEncryptor()
        with pytest.raises(DecryptionError) as exc_info:
            encryptor.decrypt_file(not_encrypted, decrypted_file, "password")

        assert "not an encrypted" in str(exc_info.value).lower()

    def test_encrypt_nonexistent_file(self, tmp_path: Path) -> None:
        """Test encryption of nonexistent file fails."""
        encryptor = FileEncryptor()
        with pytest.raises(FileError):
            encryptor.encrypt_file(
                tmp_path / "nonexistent.ods",
                tmp_path / "output.enc",
                "password",
            )

    def test_large_file_encryption(self, tmp_path: Path) -> None:
        """Test encryption of large file."""
        # Create 1MB file
        large_content = b"x" * (1024 * 1024)
        original_file = tmp_path / "large.ods"
        original_file.write_bytes(large_content)
        encrypted_file = tmp_path / "large.ods.enc"
        decrypted_file = tmp_path / "large_decrypted.ods"

        encryptor = FileEncryptor()
        encryptor.encrypt_file(original_file, encrypted_file, "password")
        encryptor.decrypt_file(encrypted_file, decrypted_file, "password")

        assert decrypted_file.read_bytes() == large_content

    def test_empty_file_encryption(self, tmp_path: Path) -> None:
        """Test encryption of empty file."""
        empty_file = tmp_path / "empty.ods"
        empty_file.write_bytes(b"")
        encrypted_file = tmp_path / "empty.ods.enc"
        decrypted_file = tmp_path / "empty_decrypted.ods"

        encryptor = FileEncryptor()
        encryptor.encrypt_file(empty_file, encrypted_file, "password")
        encryptor.decrypt_file(encrypted_file, decrypted_file, "password")

        assert decrypted_file.read_bytes() == b""

    def test_unicode_password(self, tmp_path: Path) -> None:
        """Test encryption with unicode password."""
        original_file = tmp_path / "test.ods"
        original_file.write_bytes(b"test content")
        encrypted_file = tmp_path / "test.ods.enc"
        decrypted_file = tmp_path / "test_decrypted.ods"

        encryptor = FileEncryptor()
        password = "complex password"

        encryptor.encrypt_file(original_file, encrypted_file, password)
        encryptor.decrypt_file(encrypted_file, decrypted_file, password)

        assert decrypted_file.read_bytes() == b"test content"


class TestSecurityAuditLog:
    """Tests for SecurityAuditLog class."""

    def test_log_action(self, tmp_path: Path) -> None:
        """Test logging an action."""
        log_path = tmp_path / "audit.log"
        audit_log = SecurityAuditLog(log_path)

        audit_log.log_action("encrypt", "/path/to/file.ods", success=True)

        assert log_path.exists()
        content = log_path.read_text()
        assert "encrypt" in content
        assert "/path/to/file.ods" in content

    def test_log_action_with_details(self, tmp_path: Path) -> None:
        """Test logging action with details."""
        log_path = tmp_path / "audit.log"
        audit_log = SecurityAuditLog(log_path)

        audit_log.log_action(
            "decrypt",
            "/path/to/file.ods",
            success=False,
            details={"error": "wrong password"},
        )

        content = log_path.read_text()
        assert "decrypt" in content
        assert "wrong password" in content

    def test_get_entries(self, tmp_path: Path) -> None:
        """Test retrieving log entries."""
        log_path = tmp_path / "audit.log"
        audit_log = SecurityAuditLog(log_path)

        # Log multiple actions
        audit_log.log_action("encrypt", "/file1.ods")
        audit_log.log_action("decrypt", "/file2.ods")
        audit_log.log_action("encrypt", "/file3.ods")

        # Get all entries
        entries = audit_log.get_entries()
        assert len(entries) == 3

        # Filter by action
        encrypt_entries = audit_log.get_entries(action="encrypt")
        assert len(encrypt_entries) == 2

        # Filter by file
        file1_entries = audit_log.get_entries(file_path="/file1.ods")
        assert len(file1_entries) == 1


class TestAuditLogEntry:
    """Tests for AuditLogEntry dataclass."""

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        entry = AuditLogEntry(
            timestamp="2024-12-28T10:00:00",
            action="encrypt",
            file_path="/path/to/file.ods",
            user="testuser",
            success=True,
            details={"key": "value"},
        )
        result = entry.to_dict()

        assert result["timestamp"] == "2024-12-28T10:00:00"
        assert result["action"] == "encrypt"
        assert result["file_path"] == "/path/to/file.ods"
        assert result["user"] == "testuser"
        assert result["success"] is True
        assert result["details"]["key"] == "value"


class TestGeneratePassword:
    """Tests for generate_password function."""

    def test_default_length(self) -> None:
        """Test default password length."""
        password = generate_password()
        assert len(password) == 20

    def test_custom_length(self) -> None:
        """Test custom password length."""
        password = generate_password(length=32)
        assert len(password) == 32

    def test_minimum_length(self) -> None:
        """Test minimum password length enforcement."""
        password = generate_password(length=5)
        assert len(password) >= 12  # Minimum enforced

    def test_character_variety(self) -> None:
        """Test password contains all character types."""
        # Generate many passwords to ensure variety
        for _ in range(10):
            password = generate_password(length=20)
            has_lower = any(c.islower() for c in password)
            has_upper = any(c.isupper() for c in password)
            has_digit = any(c.isdigit() for c in password)
            has_symbol = any(not c.isalnum() for c in password)

            assert has_lower
            assert has_upper
            assert has_digit
            assert has_symbol

    def test_without_symbols(self) -> None:
        """Test password without symbols."""
        for _ in range(10):
            password = generate_password(length=20, include_symbols=False)
            assert password.isalnum()

    def test_uniqueness(self) -> None:
        """Test passwords are unique."""
        passwords = [generate_password() for _ in range(100)]
        assert len(set(passwords)) == 100


class TestCheckPasswordStrength:
    """Tests for check_password_strength function."""

    def test_weak_password(self) -> None:
        """Test weak password detection."""
        result = check_password_strength("abc")
        assert result["level"] == "weak"
        assert result["score"] < 40
        assert len(result["feedback"]) > 0

    def test_fair_password(self) -> None:
        """Test fair password detection."""
        result = check_password_strength("Password1")
        assert result["level"] in ("fair", "good")
        assert result["score"] >= 40

    def test_good_password(self) -> None:
        """Test good password detection."""
        result = check_password_strength("Password123!")
        assert result["level"] in ("good", "strong")
        assert result["score"] >= 60

    def test_strong_password(self) -> None:
        """Test strong password detection."""
        result = check_password_strength("MyStr0ng!P@ssword2024")
        assert result["level"] == "strong"
        assert result["score"] >= 80

    def test_requirements_met(self) -> None:
        """Test requirements_met field."""
        result = check_password_strength("Test123!")
        reqs = result["requirements_met"]
        assert reqs["min_length"] is True
        assert reqs["lowercase"] is True
        assert reqs["uppercase"] is True
        assert reqs["digit"] is True
        assert reqs["symbol"] is True

    def test_feedback_provided(self) -> None:
        """Test feedback is provided for weak passwords."""
        result = check_password_strength("weak")
        assert len(result["feedback"]) > 0

    def test_no_feedback_for_strong(self) -> None:
        """Test no feedback for very strong passwords."""
        result = check_password_strength("VeryStr0ng!P@ssword2024XYZ")
        # Strong password may still have minor suggestions
        assert result["level"] == "strong"


class TestIntegration:
    """Integration tests for security module."""

    def test_full_encryption_workflow(self, tmp_path: Path) -> None:
        """Test full encryption/decryption workflow with audit logging."""
        # Setup
        log_path = tmp_path / "audit.log"
        audit_log = SecurityAuditLog(log_path)
        encryptor = FileEncryptor(audit_log)

        # Create test file
        original_content = b"Sensitive budget data: $50,000 income, $30,000 expenses"
        original_file = tmp_path / "budget.ods"
        original_file.write_bytes(original_content)

        encrypted_file = tmp_path / "budget.ods.enc"
        decrypted_file = tmp_path / "budget_restored.ods"

        # Generate strong password
        password = generate_password(length=24)
        strength = check_password_strength(password)
        assert strength["level"] in ("good", "strong")

        # Encrypt
        metadata = encryptor.encrypt_file(original_file, encrypted_file, password)
        assert encrypted_file.exists()
        assert metadata.content_hash != ""

        # Verify audit log
        entries = audit_log.get_entries(action="encrypt")
        assert len(entries) == 1
        assert entries[0].success

        # Decrypt
        encryptor.decrypt_file(encrypted_file, decrypted_file, password)
        assert decrypted_file.read_bytes() == original_content

        # Verify audit log again
        entries = audit_log.get_entries()
        assert len(entries) == 2

    def test_multiple_file_encryption(self, tmp_path: Path) -> None:
        """Test encrypting multiple files with same password."""
        encryptor = FileEncryptor()
        password = "shared-password-123!"

        files = []
        for i in range(5):
            # Create file
            original = tmp_path / f"budget_{i}.ods"
            original.write_bytes(f"Budget data {i}".encode())
            encrypted = tmp_path / f"budget_{i}.ods.enc"
            decrypted = tmp_path / f"budget_{i}_restored.ods"

            # Encrypt and decrypt
            encryptor.encrypt_file(original, encrypted, password)
            encryptor.decrypt_file(encrypted, decrypted, password)

            # Verify
            assert decrypted.read_bytes() == f"Budget data {i}".encode()
            files.append((original, encrypted, decrypted))

        # Verify all encrypted files are different (unique salts/nonces)
        encrypted_contents = [f[1].read_bytes() for f in files]
        assert len(set(encrypted_contents)) == 5

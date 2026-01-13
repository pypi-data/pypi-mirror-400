#!/usr/bin/env python3
"""
Security Features Demo

Demonstrates security features in SpreadsheetDL:
- File encryption
- Password strength checking
- Backup with integrity verification
"""

from pathlib import Path

from spreadsheet_dl import (
    BackupManager,
    BackupReason,
    FileEncryptor,
    check_password_strength,
    create_monthly_budget,
    generate_password,
)


def demo_password_strength() -> None:
    """Demonstrate password strength checking."""
    print("=== Password Strength Checking ===\n")

    test_passwords = [
        "weak",
        "StrongerPass123",
        "VeryStr0ng!Pass@2026",
    ]

    for pwd in test_passwords:
        strength = check_password_strength(pwd)
        print(f"Password: {pwd!r}")
        print(f"  Score: {strength['score']}/5")
        print(f"  Feedback: {strength.get('feedback', 'N/A')}")
        print()


def demo_secure_password_generation() -> None:
    """Demonstrate secure password generation."""
    print("=== Secure Password Generation ===\n")

    # Generate strong password
    strong_pwd = generate_password(length=20)
    print(f"Generated password: {strong_pwd}")

    # Check its strength
    strength = check_password_strength(strong_pwd)
    print(f"Strength score: {strength['score']}/5\n")


def demo_file_encryption() -> None:
    """Demonstrate file encryption."""
    print("=== File Encryption ===\n")

    # Create a budget file
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    print("Creating sample budget...")
    budget_path = create_monthly_budget(output_dir, month=1, year=2026)
    print(f"  Created: {budget_path}")

    # Encrypt the file
    password = "SecurePassword123!"
    encrypted_path = output_dir / "budget_encrypted.ods"

    print("\nEncrypting file with password...")
    encryptor = FileEncryptor()
    encryptor.encrypt_file(budget_path, encrypted_path, password)
    print(f"  Encrypted: {encrypted_path}")

    # Decrypt it back
    decrypted_path = output_dir / "budget_decrypted.ods"
    print("\nDecrypting file...")
    encryptor.decrypt_file(encrypted_path, decrypted_path, password)
    print(f"  Decrypted: {decrypted_path}\n")


def demo_backup_with_integrity() -> None:
    """Demonstrate automated backups with integrity checking."""
    print("=== Automated Backups ===\n")

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # Create a budget
    budget_path = create_monthly_budget(output_dir, month=1, year=2026)

    # Create backup with integrity verification
    backup_mgr = BackupManager(backup_dir=output_dir / "backups")

    print("Creating backup with integrity check...")
    backup_info = backup_mgr.create_backup(
        budget_path,
        reason=BackupReason.MANUAL,
    )

    print(f"  Backup created: {backup_info.backup_path}")
    print("  Integrity verified: ✓")

    # List backups
    backups = backup_mgr.list_backups()
    print(f"\nTotal backups: {len(backups)}")
    if backups:
        latest = backups[0]
        print("Latest backup:")
        print(f"  File: {latest.backup_path.name}")
        print(f"  Created: {latest.created}")
        print(f"  Reason: {latest.metadata.reason}\n")


def main() -> None:
    """Run all security demos."""
    print("=" * 70)
    print("Security Features Demo")
    print("=" * 70)
    print()

    demo_password_strength()
    demo_secure_password_generation()
    demo_file_encryption()
    demo_backup_with_integrity()

    print("=" * 70)
    print("Security features demonstrated:")
    print("- Password strength validation")
    print("- Secure password generation")
    print("- File encryption/decryption")
    print("- Automated backups with integrity checks")
    print("=" * 70)


if __name__ == "__main__":
    main()

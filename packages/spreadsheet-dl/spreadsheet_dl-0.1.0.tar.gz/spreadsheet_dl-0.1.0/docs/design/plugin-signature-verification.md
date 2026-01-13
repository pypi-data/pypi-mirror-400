# Plugin Signature Verification Design

**Version**: 1.0
**Status**: Design (Deferred to v0.2.0 (Planned))
**Author**: SpreadsheetDL Team
**Date**: 2026-01-06

## Executive Summary

This document describes the design for plugin signature verification in SpreadsheetDL. Due to the architectural complexity and the need for careful security implementation, full implementation is deferred to v0.2.0 (Planned). This document provides the design specification for future implementation.

## Problem Statement

Currently, SpreadsheetDL plugins load without any cryptographic verification of their source or integrity. This creates potential security risks:

1. **Tampering**: Malicious modification of plugin files
2. **Unauthorized Plugins**: Loading untrusted third-party plugins
3. **Supply Chain Attacks**: Compromised plugin distribution

## Design Goals

1. **Verify Plugin Integrity**: Ensure plugins have not been modified
2. **Authenticate Source**: Verify plugins come from trusted publishers
3. **Backward Compatibility**: Unsigned plugins should work with warnings
4. **Developer Experience**: Simple signing workflow for plugin authors

## Proposed Architecture

### 1. Signature Format

```python
@dataclass(frozen=True)
class PluginSignature:
    """Plugin signature metadata."""

    # Signature algorithm (Ed25519 recommended)
    algorithm: str = "Ed25519"

    # Base64-encoded signature
    signature: str = ""

    # Public key fingerprint (SHA-256 of public key)
    key_fingerprint: str = ""

    # Timestamp of signing (ISO 8601)
    signed_at: str = ""

    # Plugin manifest hash (SHA-256 of manifest.json)
    manifest_hash: str = ""

    # Certificate chain (optional, for PKI)
    certificate_chain: list[str] = field(default_factory=list)
```

### 2. Manifest File

Each plugin requires a `manifest.json`:

```json
{
  "name": "my-domain-plugin",
  "version": "1.0.0",
  "author": "Plugin Author",
  "description": "Plugin description",
  "entry_point": "plugin.py",
  "min_spreadsheet_dl_version": "0.1.0",
  "files": [
    { "path": "plugin.py", "hash": "sha256:abc123..." },
    { "path": "formulas/__init__.py", "hash": "sha256:def456..." }
  ]
}
```

### 3. Signature File

Signatures stored in `plugin.sig`:

```json
{
  "version": 1,
  "algorithm": "Ed25519",
  "signature": "base64-encoded-signature",
  "key_fingerprint": "sha256:key-fingerprint",
  "signed_at": "2026-01-06T12:00:00Z",
  "manifest_hash": "sha256:manifest-hash"
}
```

### 4. Trust Store

```python
class TrustStore:
    """Manages trusted signing keys."""

    def __init__(self, store_path: Path | None = None) -> None:
        """Initialize trust store.

        Default location: ~/.config/spreadsheet-dl/trust-store/
        """
        pass

    def add_trusted_key(
        self,
        public_key: bytes,
        name: str,
        trust_level: TrustLevel,
    ) -> str:
        """Add a public key to the trust store.

        Returns:
            Key fingerprint
        """
        pass

    def verify_signature(
        self,
        plugin_path: Path,
    ) -> VerificationResult:
        """Verify a plugin's signature.

        Returns:
            VerificationResult with status and details
        """
        pass

    def is_trusted(self, key_fingerprint: str) -> bool:
        """Check if a key is trusted."""
        pass


class TrustLevel(Enum):
    """Trust levels for signing keys."""

    UNTRUSTED = "untrusted"  # Key not in trust store
    UNKNOWN = "unknown"      # Key in store but not verified
    TRUSTED = "trusted"      # Manually trusted by user
    VERIFIED = "verified"    # Verified through PKI
    BUILTIN = "builtin"      # SpreadsheetDL official key


@dataclass
class VerificationResult:
    """Result of signature verification."""

    verified: bool
    trust_level: TrustLevel
    key_fingerprint: str | None
    signed_at: datetime | None
    warnings: list[str]
    errors: list[str]
```

### 5. Plugin Loading Flow

```
1. Discover plugin directory
2. Check for manifest.json
   - If missing: Load with warning (unsigned plugin)
3. Check for plugin.sig
   - If missing: Load with warning (unsigned plugin)
4. Verify manifest hash matches files
   - If mismatch: Reject (tampered)
5. Verify signature against manifest
   - If invalid: Reject (tampered or wrong key)
6. Check key fingerprint in trust store
   - If untrusted: Prompt user or reject based on config
7. Load plugin
```

### 6. Configuration Options

```yaml
# ~/.config/spreadsheet-dl/config.yaml
plugins:
  signature_verification:
    enabled: true

    # How to handle unsigned plugins
    # Options: allow, warn, deny
    unsigned_policy: warn

    # How to handle untrusted signatures
    # Options: prompt, allow, deny
    untrusted_policy: prompt

    # Require all plugins to be signed
    require_signatures: false

    # Auto-trust SpreadsheetDL official key
    trust_official_key: true
```

### 7. CLI Commands

```bash
# List trusted keys
spreadsheet-dl plugin keys list

# Add a trusted key
spreadsheet-dl plugin keys add path/to/public-key.pem --name "Publisher Name"

# Remove a trusted key
spreadsheet-dl plugin keys remove <fingerprint>

# Verify a plugin
spreadsheet-dl plugin verify path/to/plugin

# Sign a plugin (for developers)
spreadsheet-dl plugin sign path/to/plugin --key path/to/private-key.pem
```

## Implementation Phases

### Phase 1: Core Infrastructure (v0.2.0 (Planned))

- Signature format and parsing
- Trust store implementation
- Basic verification logic
- CLI commands for key management

### Phase 2: Developer Tools (v0.2.0 (Planned))

- Plugin signing CLI
- Manifest generation tool
- Key generation utilities

### Phase 3: PKI Integration (v0.3.0 (Planned))

- Certificate chain validation
- Revocation checking (CRL/OCSP)
- Timestamp authority integration

## Security Considerations

### Algorithm Selection

**Ed25519** is recommended for plugin signatures:

- Fast verification
- Small signature size (64 bytes)
- Resistant to timing attacks
- No parameter confusion attacks

### Key Management

1. **Private Key Protection**: Private keys should be:
   - Password-protected
   - Stored securely (hardware tokens recommended for high-value plugins)
   - Never committed to version control

2. **Key Rotation**:
   - Support for multiple valid keys during rotation period
   - Clear deprecation path for old keys

### Attack Mitigation

| Attack         | Mitigation                        |
| -------------- | --------------------------------- |
| Replay         | Timestamp in signature            |
| Downgrade      | Version in signature format       |
| Partial Update | Manifest includes all file hashes |
| Key Compromise | Revocation support (Phase 3)      |

## Migration Path

### Existing Plugins (v0.1.0 -> v0.2.0 (Planned))

1. Unsigned plugins continue to work with warnings
2. Plugin authors can sign plugins at any time
3. No breaking changes to plugin API

### Configuration Migration

Default configuration enables signature verification with `warn` policy, allowing gradual adoption.

## Dependencies

Required for implementation:

- `cryptography>=42.0.0` (already optional dependency)
- No new required dependencies

## Testing Strategy

1. **Unit Tests**: Signature generation/verification
2. **Integration Tests**: Plugin loading with various trust levels
3. **Security Tests**: Attack scenario testing
4. **Compatibility Tests**: Unsigned plugin behavior

## Open Questions

1. Should we support multiple signature algorithms?
2. How to handle plugin updates with different signing keys?
3. Should we integrate with OS-level certificate stores?

## References

- [Ed25519 Specification](https://ed25519.cr.yp.to/)
- [Python cryptography library](https://cryptography.io/)
- [Sigstore](https://sigstore.dev/) - for future PKI integration
- [TUF (The Update Framework)](https://theupdateframework.io/) - inspiration for security model

---

**Note**: This is a design document. Implementation is scheduled for v0.2.0 (Planned).

# Security Policy

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 0.1.x   | ✅        |
| < 0.1   | ❌        |

---

## Reporting a Vulnerability

**We take security seriously.** If you discover a security vulnerability, please report it responsibly.

### How to Report

**Preferred**: [Private security advisory](https://github.com/lair-click-bats/spreadsheet-dl/security/advisories/new) on GitHub

**Alternative**: Create an issue with "security" label

**Do not** report vulnerabilities through public issues unless already disclosed.

### What to Include

- Type of vulnerability
- Affected source files and locations
- Step-by-step reproduction
- Impact assessment
- Proof-of-concept (if available)
- Suggested fix (if you have one)

### Response Timeline

- **Initial response**: Within 48 hours
- **Severity assessment**: Within 7 days
- **Patch release**: Within 30 days for critical issues
- **Public disclosure**: After patch release

---

## Security Features (v0.1.0)

SpreadsheetDL v0.1.0 includes comprehensive security hardening:

### Protection Mechanisms

- ✅ **XXE Protection** - Uses `defusedxml` to prevent XML entity expansion attacks
- ✅ **ZIP Bomb Detection** - File size limits and decompression ratio checks
- ✅ **Path Traversal Prevention** - Validates all file paths
- ✅ **Formula Injection Protection** - Strict cell reference validation
- ✅ **Password Strength Enforcement** - Prevents weak master passwords
- ✅ **Automated Scanning** - Dependabot + weekly vulnerability checks

### Installation

**Recommended installation** includes security enhancements:

```bash
uv pip install spreadsheet-dl[security]
```

This installs:

- `defusedxml` - XXE and XML bomb protection
- `cryptography` - Hardware-accelerated encryption (AES-256-GCM)

---

## Threat Model

### Untrusted Inputs

SpreadsheetDL treats the following as untrusted:

- User-provided spreadsheet files (may contain malicious content)
- User-provided file paths (path traversal risk)
- Third-party plugins (arbitrary code execution risk)
- External data sources (CSV, APIs, WebDAV)
- MCP client requests (all inputs validated)
- Formula cell references (injection risk)

### Attack Vectors

1. **Malicious files**: Formula injection, XXE, ZIP bombs
2. **Path traversal**: Unsanitized file paths
3. **Plugin code execution**: Unaudited third-party plugins
4. **DoS**: Large files, circular formulas, ZIP/XML bombs
5. **Credential exposure**: API keys, passwords in code
6. **SSRF**: WebDAV and API integrations

---

## Security Best Practices

### For Users

**1. Validate inputs:**

```python
from pathlib import Path

# Good: Validate paths
if not Path(user_path).resolve().is_relative_to(safe_dir):
    raise ValueError("Path outside safe directory")

# Bad: Trust user input
builder.save(user_input_path)  # Don't do this
```

**2. Use security extras:**

```bash
uv pip install spreadsheet-dl[security]  # Recommended
```

**3. Audit third-party plugins** before loading (they have full system access)

**4. Store credentials securely:**

```python
import os

# Good: Environment variables
api_key = os.environ["PLAID_API_KEY"]

# Bad: Hardcoded
api_key = "secret-key-12345"  # Don't do this
```

### For Deployment

**Production checklist:**

- [ ] Install `spreadsheet-dl[security]` with XXE/ZIP bomb protection
- [ ] Use environment variables for credentials (not hardcoded)
- [ ] Validate all user-provided file paths
- [ ] Set file size limits for uploads
- [ ] Run vulnerability scans: `uv pip install safety && safety check`
- [ ] Keep dependencies updated: `uv pip install --upgrade spreadsheet-dl`
- [ ] Only load audited plugins
- [ ] Use principle of least privilege for file system access

**Docker example:**

```dockerfile
FROM python:3.12-slim
RUN uv pip install spreadsheet-dl[security]
USER nonroot  # Don't run as root
COPY --chown=nonroot:nonroot . /app
WORKDIR /app
```

---

## Dependency Security

### Automated Scanning

SpreadsheetDL uses:

- **Dependabot**: Automatic dependency updates
- **Weekly scans**: Vulnerability monitoring

### Manual Scanning

Check your installation:

```bash
uv pip install safety pip-audit
safety check
pip-audit
```

---

## Out of Scope

The following are **not** security vulnerabilities in SpreadsheetDL:

### 1. Formulas Executed by Spreadsheet Applications

SpreadsheetDL generates spreadsheet files. If a user opens a malicious ODS/XLSX in LibreOffice/Excel and that application executes harmful formulas, this is a vulnerability in the **spreadsheet application**, not SpreadsheetDL.

**SpreadsheetDL's responsibility**: Don't inject unexpected formulas
**User's responsibility**: Validate content before opening in spreadsheet apps

### 2. Denial of Service via Extremely Large Files

Creating a 10GB spreadsheet with 10 million rows is **resource-intensive by design**, not a vulnerability.

**User's responsibility**: Set reasonable limits in your application
**SpreadsheetDL provides**: Streaming I/O for large files (`builder.save_streaming()`)

---

## Disclosure Policy

- We follow **coordinated disclosure**
- Security fixes are released ASAP
- CVEs assigned when applicable
- Public disclosure after patch + reasonable upgrade time
- Credits given to researchers who report responsibly

---

## Security Contact

- **GitHub Security Advisories**: [Create advisory](https://github.com/lair-click-bats/spreadsheet-dl/security/advisories/new)
- **Issues**: Use "security" label for non-sensitive issues

---

**Last Updated**: 2026-01-06
**Version**: 0.1.0

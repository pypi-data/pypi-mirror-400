# Error Code Reference

This document provides a complete reference for all error codes used by SpreadsheetDL.

## Error Code Format

All error codes follow the format: `FT-<CATEGORY>-<NUMBER>`

- **FT**: SpreadsheetDL prefix
- **CATEGORY**: Three-letter category code
- **NUMBER**: Three-digit error number within category

## Error Categories

| Category | Code Range | Description                  |
| -------- | ---------- | ---------------------------- |
| GEN      | 001-099    | General/uncategorized errors |
| FILE     | 100-199    | File system errors           |
| ODS      | 200-299    | ODS spreadsheet file errors  |
| CSV      | 300-399    | CSV import errors            |
| VAL      | 400-499    | Data validation errors       |
| CFG      | 500-599    | Configuration errors         |
| NET      | 600-699    | Network/WebDAV errors        |
| TMPL     | 700-799    | Template and theme errors    |
| FMT      | 800-899    | Formatting errors            |
| EXT      | 900-999    | Extension/plugin errors      |
| SEC      | 1000-1099  | Security errors              |

---

## General Errors (FT-GEN-xxx)

### FT-GEN-001: Unknown Error

**Severity:** Error

An unexpected error occurred that doesn't fit into other categories.

**Common Causes:**

- Unhandled exception in code
- System-level errors

**Resolution:**

- Check the error details for more information
- Report the issue with full error output

---

### FT-GEN-002: Operation Cancelled

**Severity:** Info

The user cancelled the operation.

**Common Causes:**

- User pressed Ctrl+C
- User responded "no" to confirmation prompt

**Resolution:**

- Re-run the command to try again

---

### FT-GEN-003: Feature Not Implemented

**Severity:** Error

The requested feature is not yet available.

**Common Causes:**

- Using a feature that's planned but not implemented
- Using a feature from a newer version

**Resolution:**

- Check the roadmap for planned features
- Consider contributing the feature

---

## File Errors (FT-FILE-xxx)

### FT-FILE-101: File Not Found

**Severity:** Error

The specified file could not be located.

**Common Causes:**

- Incorrect file path
- File was moved or deleted
- Typo in filename

**Resolution:**

- Verify the file path is correct
- Check that the file exists: `ls -la /path/to/file`
- Use absolute paths to avoid confusion

**Example:**

```
Error [FT-FILE-101]: Budget file not found: /home/user/budget_2024.ods

  File:    /home/user/budget_2024.ods

  The specified budget file could not be located on the filesystem.

Suggestion: Check that the file path is correct and the file exists.
```

---

### FT-FILE-102: Permission Denied

**Severity:** Error

You don't have permission to access the file.

**Common Causes:**

- File owned by another user
- Restrictive file permissions
- File is read-only

**Resolution:**

- Check file permissions: `ls -la /path/to/file`
- Change permissions if needed: `chmod 644 /path/to/file`
- Run with appropriate user privileges

---

### FT-FILE-103: File Already Exists

**Severity:** Warning

The target file already exists and would be overwritten.

**Common Causes:**

- Generating a budget with a duplicate name
- Exporting to an existing file

**Resolution:**

- Use `--force` to overwrite existing file
- Choose a different output filename
- Backup the existing file first

---

### FT-FILE-104: Invalid File Format

**Severity:** Error

The file format doesn't match what was expected.

**Common Causes:**

- File is corrupted
- File has wrong extension
- File was saved in different format

**Resolution:**

- Verify the file is the correct format
- Try opening in LibreOffice to check validity
- Re-export from the source application

---

### FT-FILE-105: File Write Error

**Severity:** Error

Could not write to the file.

**Common Causes:**

- Disk is full
- No write permission
- File is locked by another application

**Resolution:**

- Check disk space: `df -h`
- Check write permissions
- Close other applications using the file

---

### FT-FILE-106: File Read Error

**Severity:** Error

Could not read the file.

**Common Causes:**

- File is corrupted
- File is being modified by another process
- Encoding issues

**Resolution:**

- Check file integrity
- Ensure no other process is modifying the file
- Try re-downloading or re-creating the file

---

## ODS Errors (FT-ODS-xxx)

### FT-ODS-201: ODS Read Error

**Severity:** Error

Cannot parse the ODS file.

**Common Causes:**

- File is corrupted
- File is not a valid ODS format
- File was created with incompatible software

**Resolution:**

- Try opening the file in LibreOffice
- Export as a new ODS file from LibreOffice
- Check if file is truly ODS format

**Example:**

```
Error [FT-ODS-201]: Cannot read ODS file: budget.ods

  File:    budget.ods

  Unable to parse ODS file - ZIP archive is corrupted

Suggestion: Ensure the file is a valid ODS spreadsheet created by LibreOffice or Collabora.
```

---

### FT-ODS-202: ODS Write Error

**Severity:** Error

Cannot write to the ODS file.

**Common Causes:**

- Disk space exhausted
- File is locked
- Permission denied

**Resolution:**

- Check disk space
- Close any applications using the file
- Check directory permissions

---

### FT-ODS-203: Sheet Not Found

**Severity:** Error

The requested sheet doesn't exist in the ODS file.

**Common Causes:**

- Sheet was renamed
- Sheet was deleted
- Using wrong sheet name

**Resolution:**

- Check available sheets in the file
- Use correct sheet name from the list
- Regenerate the budget file if structure is invalid

**Example:**

```
Error [FT-ODS-203]: Sheet 'Expense Log' not found

  Value:   Expense Log

  Available sheets: Sheet1, Budget Summary

Suggestion: Check the sheet name or use one of the available sheets.
```

---

### FT-ODS-204: Invalid ODS Structure

**Severity:** Error

The ODS file doesn't have the expected structure.

**Common Causes:**

- File was manually edited incorrectly
- File was not created by SpreadsheetDL
- Required sheets or columns are missing

**Resolution:**

- Use the `generate` command to create a new valid file
- Restore from backup if available
- Check that required sheets and columns exist

---

### FT-ODS-205: Formula Error

**Severity:** Error

A formula in the spreadsheet is invalid.

**Common Causes:**

- Syntax error in formula
- Reference to non-existent cell/sheet
- Incompatible formula format

**Resolution:**

- Check formula syntax
- Verify all cell references exist
- Use ODS/LibreOffice formula format

---

## CSV Errors (FT-CSV-xxx)

### FT-CSV-301: CSV Parse Error

**Severity:** Error

Cannot parse the CSV file.

**Common Causes:**

- Malformed CSV format
- Incorrect delimiter
- Encoding issues

**Resolution:**

- Verify CSV is properly formatted
- Check for unescaped quotes or delimiters
- Try specifying encoding explicitly

**Example:**

```
Error [FT-CSV-301]: CSV parse error at line 42: Unterminated quoted field

  File:    transactions.csv
  Line:    42

Suggestion: Check that the CSV file is properly formatted.
```

---

### FT-CSV-302: Unsupported Bank Format

**Severity:** Warning

The bank format is not recognized.

**Common Causes:**

- Using export from unsupported bank
- Bank changed their export format
- Typo in bank name

**Supported Banks:**

- chase, chase_credit
- bank_of_america
- wells_fargo
- capital_one
- discover
- amex
- usaa
- generic

**Resolution:**

- Use `--bank=generic` for manual column mapping
- Create a custom bank format definition
- Check for typos in bank name

---

### FT-CSV-303: CSV Column Missing

**Severity:** Error

A required column is not present in the CSV.

**Common Causes:**

- Wrong bank format specified
- CSV missing expected columns
- Column names changed

**Resolution:**

- Verify the bank format matches your CSV
- Check that required columns exist (date, description, amount)
- Use custom column mapping if needed

---

### FT-CSV-304: CSV Encoding Error

**Severity:** Error

Cannot read CSV due to character encoding issues.

**Common Causes:**

- Wrong encoding assumed
- File has mixed encodings
- Special characters in data

**Resolution:**

- Try `--encoding=utf-8`
- Try `--encoding=latin-1` or `--encoding=cp1252`
- Re-export from bank with UTF-8 encoding

---

## Validation Errors (FT-VAL-xxx)

### FT-VAL-401: Invalid Amount

**Severity:** Error

The amount value is not valid.

**Common Causes:**

- Non-numeric characters
- Currency symbol included
- Thousand separators

**Valid Formats:**

- `123.45`
- `99`
- `1234.56`

**Invalid Formats:**

- `$123.45` (currency symbol)
- `1,234.56` (thousand separator)
- `abc` (non-numeric)

**Resolution:**

- Enter amount as plain number
- Remove currency symbols
- Remove thousand separators

---

### FT-VAL-402: Invalid Date

**Severity:** Error

The date value is not valid.

**Expected Format:** YYYY-MM-DD (e.g., 2024-12-28)

**Common Causes:**

- Wrong date format
- Invalid date (e.g., Feb 30)
- Future date when not allowed

**Resolution:**

- Use ISO format: YYYY-MM-DD
- Verify the date is valid
- Check for typos

---

### FT-VAL-403: Invalid Category

**Severity:** Error

The expense category is not recognized.

**Valid Categories:**

- Housing, Utilities, Groceries
- Transportation, Healthcare, Insurance
- Entertainment, Dining Out, Clothing
- Personal Care, Education, Savings
- Debt Payment, Gifts, Subscriptions
- Miscellaneous

**Resolution:**

- Use one of the predefined categories
- Check spelling and capitalization
- Configure custom categories if needed

---

### FT-VAL-404: Invalid Range

**Severity:** Error

A value is outside the acceptable range.

**Common Causes:**

- Month > 12 or < 1
- Negative amounts where not allowed
- Percentage > 100

**Resolution:**

- Check the valid range for the field
- Correct the value to be within range

---

### FT-VAL-405: Required Field Missing

**Severity:** Error

A required field was not provided.

**Resolution:**

- Provide a value for the required field
- Check command help for required arguments

---

## Configuration Errors (FT-CFG-xxx)

### FT-CFG-501: Missing Configuration

**Severity:** Error

A required configuration value is not set.

**Common Causes:**

- New installation without configuration
- Config file deleted
- Environment variable not set

**Resolution:**

- Set the value in config file
- Set as environment variable
- Run configuration wizard

---

### FT-CFG-502: Invalid Configuration

**Severity:** Error

A configuration value is invalid.

**Resolution:**

- Check documentation for valid values
- Correct the value in config file
- Reset to default if unsure

---

### FT-CFG-503: Configuration Schema Error

**Severity:** Error

The configuration file fails validation.

**Resolution:**

- Fix listed validation errors
- Check YAML syntax
- Ensure all required fields are present

---

### FT-CFG-504: Configuration Migration Error

**Severity:** Error

Cannot migrate configuration to new format.

**Resolution:**

- Backup current configuration
- Create fresh configuration
- Manually migrate settings

---

## Network Errors (FT-NET-xxx)

### FT-NET-601: Connection Failed

**Severity:** Error

Cannot connect to the server.

**Common Causes:**

- No network connection
- Server is down
- Firewall blocking connection
- Incorrect URL

**Resolution:**

- Check network connection
- Verify server URL is correct
- Try accessing URL in browser
- Check firewall settings

---

### FT-NET-602: Authentication Failed

**Severity:** Error

Invalid credentials for server.

**Common Causes:**

- Wrong username or password
- Password expired
- Account locked
- Using regular password instead of app password

**Resolution:**

- Verify username and password
- For Nextcloud, use an app password
- Check if account is locked
- Reset password if needed

---

### FT-NET-603: Upload Failed

**Severity:** Error

Could not upload file to server.

**Common Causes:**

- Network interruption
- Remote path doesn't exist
- No write permission on server
- File too large

**Resolution:**

- Check network connection
- Verify remote path exists
- Check server permissions
- Try smaller file or check quota

---

### FT-NET-604: Download Failed

**Severity:** Error

Could not download file from server.

**Resolution:**

- Verify remote file exists
- Check read permissions
- Check network connection

---

### FT-NET-605: Server Error

**Severity:** Error

The server returned an error.

**Common HTTP Status Codes:**

- 500: Internal Server Error
- 502: Bad Gateway
- 503: Service Unavailable
- 504: Gateway Timeout

**Resolution:**

- Wait and try again
- Contact server administrator
- Check server status page

---

### FT-NET-606: Timeout

**Severity:** Error

The operation timed out.

**Common Causes:**

- Slow network connection
- Large file transfer
- Server overloaded

**Resolution:**

- Check network connection
- Increase timeout in configuration
- Try during off-peak hours

---

## Template Errors (FT-TMPL-xxx)

### FT-TMPL-701: Template Not Found

**Severity:** Error

The budget template is not found.

**Available Templates:**

- 50_30_20
- family
- minimalist
- zero_based
- fire
- high_income

**Resolution:**

- Use `templates` command to list available
- Check spelling of template name
- Create custom template if needed

---

### FT-TMPL-702: Template Validation Error

**Severity:** Error

The template definition is invalid.

**Resolution:**

- Fix validation errors in template
- Check template YAML syntax
- Verify required fields are present

---

### FT-TMPL-703: Theme Not Found

**Severity:** Error

The visual theme is not found.

**Available Themes:**

- default
- corporate
- minimal
- dark
- high_contrast

**Resolution:**

- Use `themes` command to list available
- Check spelling of theme name
- Create custom theme if needed

---

### FT-TMPL-704: Theme Validation Error

**Severity:** Error

The theme definition is invalid.

**Resolution:**

- Check YAML syntax
- Verify color values are valid hex
- Check all references exist

---

### FT-TMPL-705: Circular Inheritance

**Severity:** Error

Theme inheritance creates a cycle.

**Example:**
Theme A extends B, which extends C, which extends A.

**Resolution:**

- Review theme `extends` fields
- Remove circular reference
- Restructure inheritance chain

---

## Formatting Errors (FT-FMT-xxx)

### FT-FMT-801: Invalid Color

**Severity:** Error

The color value is not valid.

**Valid Format:** `#RRGGBB` (e.g., `#FF5733`)

**Resolution:**

- Use six-digit hex color code
- Include the `#` prefix
- Use valid hex characters (0-9, A-F)

---

### FT-FMT-802: Invalid Font

**Severity:** Error

The font specification is invalid.

**Resolution:**

- Use standard font names
- Examples: Arial, Liberation Sans, Times New Roman

---

### FT-FMT-803: Invalid Number Format

**Severity:** Error

The number format pattern is invalid.

**Valid Examples:**

- `#,##0.00` (currency)
- `0.00%` (percentage)
- `#,##0` (integer with commas)

**Resolution:**

- Use ODS-compatible format patterns
- Check format pattern syntax

---

### FT-FMT-804: Invalid Locale

**Severity:** Error

The locale code is not recognized.

**Valid Examples:**

- en_US
- de_DE
- fr_FR
- ja_JP

**Resolution:**

- Use standard locale codes
- Format: language_COUNTRY

---

## Extension Errors (FT-EXT-xxx)

### FT-EXT-901: Plugin Not Found

**Severity:** Error

The requested plugin is not installed.

**Resolution:**

- Install the plugin: `uv pip install spreadsheet-dl-plugin-<name>`
- Check plugin name spelling

---

### FT-EXT-902: Plugin Load Error

**Severity:** Error

Could not load the plugin.

**Common Causes:**

- Missing dependencies
- Incompatible Python version
- Plugin code errors

**Resolution:**

- Check plugin requirements
- Update plugin to latest version
- Check plugin error logs

---

### FT-EXT-903: Plugin Version Mismatch

**Severity:** Error

The plugin version is incompatible.

**Resolution:**

- Update plugin: `uv pip install --upgrade spreadsheet-dl-plugin-<name>`
- Check compatibility matrix in plugin docs

---

### FT-EXT-904: Hook Error

**Severity:** Error

A plugin hook failed during execution.

**Resolution:**

- Check plugin logs for details
- Disable the problematic plugin
- Report issue to plugin author

---

## Security Errors (FT-SEC-xxx)

### FT-SEC-1000: Security Error

**Severity:** Error

A general security-related error occurred.

**Common Causes:**

- Security policy violation
- Unauthorized operation attempted

**Resolution:**

- Check security configuration
- Verify permissions and access rights

---

### FT-SEC-1001: Encryption Error

**Severity:** Error

Failed to encrypt data.

**Common Causes:**

- Invalid encryption key
- Corrupted key material
- Unsupported encryption algorithm

**Resolution:**

- Verify encryption key is valid
- Regenerate encryption keys if needed
- Check algorithm compatibility

---

### FT-SEC-1002: Decryption Error

**Severity:** Error

Failed to decrypt data.

**Common Causes:**

- Wrong decryption key
- Corrupted encrypted data
- Data was encrypted with different algorithm

**Resolution:**

- Verify using correct decryption key
- Check data integrity
- Ensure key matches encryption method

---

### FT-SEC-1003: Key Derivation Error

**Severity:** Error

Failed to derive encryption key from password.

**Common Causes:**

- Invalid password
- Corrupted salt value
- Insufficient system resources

**Resolution:**

- Verify password is correct
- Check salt integrity
- Ensure sufficient memory available

---

### FT-SEC-1004: Integrity Error

**Severity:** Error

Data integrity verification failed.

**Common Causes:**

- Data was tampered with
- Transmission corruption
- Wrong authentication tag

**Resolution:**

- Re-download or re-transfer data
- Verify data source authenticity
- Check for transmission errors

---

### FT-SEC-1005: Credential Error

**Severity:** Error

Credential operation failed.

**Common Causes:**

- Invalid credentials format
- Credential storage corrupted
- Access to credential store denied

**Resolution:**

- Re-enter credentials
- Clear and recreate credential store
- Check credential store permissions

---

### FT-SEC-1006: Weak Password Error

**Severity:** Warning

Password does not meet security requirements.

**Requirements:**

- Minimum 12 characters
- Mix of uppercase and lowercase
- Include numbers and special characters

**Resolution:**

- Choose a stronger password
- Use a password manager
- Consider using a passphrase

---

## Getting Help

If you encounter an error not listed here or need additional assistance:

1. **Check documentation:** https://lair-click-bats.github.io/spreadsheet-dl/
2. **Search issues:** https://github.com/lair-click-bats/spreadsheet-dl/issues
3. **Report new issue:** Include full error output with `--debug` flag

### Debug Mode

For more detailed error information, run commands with `--debug`:

```bash
spreadsheet-dl --debug analyze budget.ods
```

This will include:

- Full stack trace
- System information
- Configuration details

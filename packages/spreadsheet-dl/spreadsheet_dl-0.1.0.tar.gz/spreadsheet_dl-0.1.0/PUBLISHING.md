# Publishing SpreadsheetDL to PyPI

This guide explains how to publish SpreadsheetDL to PyPI.

## Package Built and Ready

The package has been successfully built:

- ✅ Source distribution: `dist/spreadsheet_dl-0.1.0.tar.gz`
- ✅ Wheel distribution: `dist/spreadsheet_dl-0.1.0-py3-none-any.whl`

## PyPI Publication Options

### Option 1: Using PyPI API Token (Recommended for Manual Publishing)

1. **Create PyPI Account** (if not already done)
   - Go to https://pypi.org/account/register/
   - Verify your email address

2. **Generate API Token**
   - Go to https://pypi.org/manage/account/token/
   - Create a new API token for the project
   - Copy the token (starts with `pypi-`)

3. **Configure Credentials**

   ```bash
   # Set environment variable
   export UV_PUBLISH_TOKEN="pypi-..."

   # Or create ~/.pypirc file
   cat > ~/.pypirc <<EOF
   [pypi]
   username = __token__
   password = pypi-...
   EOF
   chmod 600 ~/.pypirc
   ```

4. **Publish to PyPI**
   ```bash
   uv publish
   ```

### Option 2: Using Trusted Publishing (Recommended for GitHub Actions)

1. **Configure PyPI Trusted Publisher**
   - Go to https://pypi.org/manage/account/publishing/
   - Add GitHub as a trusted publisher
   - Repository: `lair-click-bats/spreadsheet-dl`
   - Workflow name: `release.yml`
   - Environment: `release`

2. **Use GitHub Actions Workflow**

   The repository includes a `.github/workflows/publish.yml` workflow that will:
   - Build the package
   - Publish to PyPI using trusted publishing
   - Create GitHub release

   To trigger:

   ```bash
   # Push a tag
   git push origin v0.1.0
   ```

### Option 3: Manual Upload with Twine

If `uv publish` doesn't work, you can use twine:

```bash
# Install twine
pip install twine

# Upload to PyPI
twine upload dist/*
```

## Verification After Publishing

Once published, verify the package:

```bash
# Install from PyPI
pip install spreadsheet-dl

# Verify installation
spreadsheet-dl --version
python -c "import spreadsheet_dl; print(spreadsheet_dl.__version__)"
```

## Test PyPI (Optional)

To test before publishing to the main PyPI:

```bash
# Publish to Test PyPI
uv publish --publish-url https://test.pypi.org/legacy/

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ spreadsheet-dl
```

## Current Status

- ✅ Package built successfully
- ✅ All quality checks passed
- ✅ Version: 0.1.0
- ⏳ PyPI credentials needed for publication
- 📦 Ready to publish when credentials are configured

## Next Steps

1. Choose a publication method above
2. Configure credentials
3. Run `uv publish` or trigger GitHub Actions
4. Verify package installation
5. Update README with PyPI installation instructions

## Troubleshooting

### "Missing credentials" Error

- Configure PyPI API token as shown in Option 1
- Or use GitHub trusted publishing as shown in Option 2

### "Package already exists" Error

- Version 0.1.0 has already been published
- Increment version in `pyproject.toml`
- Rebuild with `uv build`
- Publish again

### "Invalid distribution" Error

- Ensure `uv build` completed successfully
- Check that `dist/` directory contains both `.tar.gz` and `.whl` files
- Verify `pyproject.toml` has all required metadata

## References

- [PyPI Publishing Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
- [UV Documentation](https://github.com/astral-sh/uv)

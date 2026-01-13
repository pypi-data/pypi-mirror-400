# Publishing to PyPI

This guide walks you through publishing `langflow-cli` to PyPI.

## Prerequisites

1. **PyPI Account**: Create an account at [pypi.org](https://pypi.org/account/register/)
2. **TestPyPI Account**: Create an account at [test.pypi.org](https://test.pypi.org/account/register/) (for testing)
3. **API Tokens**: Generate API tokens from your account settings (recommended over passwords)

## Pre-Publication Checklist

- [x] `pyproject.toml` is properly configured
- [x] `README.md` is complete and accurate
- [x] `LICENSE` file exists
- [x] Package name is available (check at https://pypi.org/project/langflow-cli/)
- [ ] All tests pass (if you have tests)
- [ ] Version number is correct in `pyproject.toml` and `langflow_cli/__init__.py`
- [ ] Code is clean and ready

## Step 1: Install Build Tools

```bash
# Using uv
uv pip install build twine

# Or using pip
pip install build twine
```

## Step 2: Build the Package

```bash
# Using uv
uv build

# Or using pip/build
python -m build
```

This creates:
- `dist/langflow_cli-0.1.0-py3-none-any.whl` (wheel)
- `dist/langflow-cli-0.1.0.tar.gz` (source distribution)

## Step 3: Test on TestPyPI (Recommended)

1. **Upload to TestPyPI**:
```bash
twine upload --repository testpypi dist/*
```

You'll be prompted for:
- Username: `__token__`
- Password: Your TestPyPI API token

2. **Test Installation**:
```bash
pip install --index-url https://test.pypi.org/simple/ langflow-cli
```

3. **Verify it works**:
```bash
langflow-cli --help
```

## Step 4: Publish to PyPI

Once testing is successful:

```bash
twine upload dist/*
```

You'll be prompted for:
- Username: `__token__`
- Password: Your PyPI API token

## Step 5: Verify Publication

1. Check the package page: https://pypi.org/project/langflow-cli/
2. Test installation:
```bash
pip install langflow-cli
langflow-cli --help
```

## Updating the Package

For future releases:

1. Update version in:
   - `pyproject.toml` (version field)
   - `langflow_cli/__init__.py` (__version__)

2. Rebuild and upload:
```bash
uv build
twine upload dist/*
```

## Important Notes

- **Package Name**: The package name on PyPI is `langflow-cli` (with hyphen)
- **Import Name**: The Python import is `langflow_cli` (with underscore)
- **Version**: Follow semantic versioning (MAJOR.MINOR.PATCH)
- **API Tokens**: Store tokens securely, never commit them to git
- **Test First**: Always test on TestPyPI before publishing to production PyPI

## Troubleshooting

### "Package already exists"
- The version number must be unique. Increment the version in `pyproject.toml`.

### "Invalid credentials"
- Make sure you're using `__token__` as username and the full token (including `pypi-` prefix) as password.

### "File already exists"
- Delete old files in `dist/` or increment the version number.


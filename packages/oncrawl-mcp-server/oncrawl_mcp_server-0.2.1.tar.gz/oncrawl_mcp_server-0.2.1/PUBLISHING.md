# Publishing Guide

## Prerequisites

1. Install build tools:
```bash
pip install build twine
```

2. Have PyPI account ready (create at https://pypi.org/account/register/)

## Build the Package

```bash
python -m build
```

This creates files in `dist/`:
- `oncrawl-mcp-server-0.1.0.tar.gz` (source)
- `oncrawl_mcp_server-0.1.0-py3-none-any.whl` (wheel)

## Test with TestPyPI (Optional but Recommended)

1. Create TestPyPI account at https://test.pypi.org/account/register/

2. Upload to TestPyPI:
```bash
python -m twine upload --repository testpypi dist/*
```

3. Test installation:
```bash
pip install --index-url https://test.pypi.org/simple/ oncrawl-mcp-server
```

## Publish to PyPI

```bash
python -m twine upload dist/*
```

You'll be prompted for:
- Username (your PyPI username)
- Password (use API token recommended)

## After Publishing

Users can install with:
```bash
pip install oncrawl-mcp-server
```

## Git Repository Setup

1. Initialize git:
```bash
git init
git add .
git commit -m "Initial commit: OnCrawl MCP Server v0.1.0"
```

2. Create GitHub repository at https://github.com/new

3. Push to GitHub:
```bash
git remote add origin https://github.com/yourusername/oncrawl-mcp-server.git
git branch -M main
git push -u origin main
```

4. Update `pyproject.toml` with actual GitHub URLs

## Version Updates

When releasing new versions:

1. Update version in:
   - `pyproject.toml`
   - `__init__.py`

2. Create git tag:
```bash
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0
```

3. Rebuild and publish:
```bash
rm -rf dist/
python -m build
python -m twine upload dist/*
```

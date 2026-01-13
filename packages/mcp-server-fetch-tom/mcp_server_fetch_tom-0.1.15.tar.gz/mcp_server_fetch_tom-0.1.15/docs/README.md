# Documentation Index

Welcome to the `mcp-server-fetch-tom` documentation!

## 📚 Documentation Files

### Publishing to PyPI

- **[PUBLISHING.md](./PUBLISHING.md)** - Comprehensive guide to building and publishing the package
  - Detailed step-by-step instructions
  - Troubleshooting common issues
  - Authentication setup
  - GitHub Actions automation
  
- **[QUICKSTART_PUBLISHING.md](./QUICKSTART_PUBLISHING.md)** - Quick reference for publishing
  - TL;DR version for experienced users
  - Essential commands only
  - Common issues and fixes
  
- **[RELEASE_CHECKLIST.md](./RELEASE_CHECKLIST.md)** - Pre-release checklist
  - Comprehensive checklist for releases
  - Quality checks
  - Testing steps
  - Post-release tasks

## 🚀 Quick Start

Choose your approach based on your experience level:

### For First-Time Publishers
→ Start with [PUBLISHING.md](./PUBLISHING.md) for a detailed walkthrough

### For Experienced Users
→ Use [QUICKSTART_PUBLISHING.md](./QUICKSTART_PUBLISHING.md) or the Makefile

### For Release Preparation
→ Follow [RELEASE_CHECKLIST.md](./RELEASE_CHECKLIST.md) before publishing

## 🛠️ Tools & Scripts

### Makefile Commands
Located in the project root, provides convenient shortcuts:

```bash
make help         # Show all available commands
make build        # Build the package
make check        # Verify package validity
make upload       # Upload to PyPI (with confirmation)
make upload-test  # Upload to TestPyPI
make clean        # Remove build artifacts
make release      # Interactive release workflow
```

See the [Makefile](../Makefile) for all available commands.

### Publish Script
Interactive script for guided publishing: `./publish.sh [version]`

Features:
- Optional version bump
- Git commit and tagging
- Package building
- Validation checks
- Choice of upload destination (TestPyPI/PyPI)

```bash
# Publish current version
./publish.sh

# Publish with version bump
./publish.sh 0.1.15
```

## 📋 Publishing Workflows

### Workflow 1: Using Makefile (Recommended)
```bash
# 1. Update version in pyproject.toml
# 2. Commit changes
git add . && git commit -m "Release v0.1.15"
git tag v0.1.15

# 3. Build and upload
make upload  # Builds, checks, and uploads with confirmation

# 4. Push tags
git push origin main && git push origin v0.1.15
```

### Workflow 2: Using publish.sh Script
```bash
# All-in-one interactive script
./publish.sh 0.1.15
```

### Workflow 3: Manual Commands
```bash
# Clean and build
rm -rf dist/
uvx --from build pyproject-build --installer uv

# Check
uvx twine check dist/*

# Upload
uvx twine upload dist/*
```

## 🔑 Prerequisites

### Required Tools
- **uv** - Fast Python package manager
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

### PyPI Account Setup
1. Create account: https://pypi.org/account/register/
2. Verify email
3. Enable 2FA (recommended)
4. Create API token: https://pypi.org/manage/account/token/
5. Configure authentication (see [PUBLISHING.md](./PUBLISHING.md))

### Optional Tools
- **make** - For using Makefile (usually pre-installed on Linux/Mac)
- **git** - For version control (usually pre-installed)

## 🆘 Troubleshooting

### Common Issues

#### "File already exists" on PyPI
**Solution:** Increment version number in `pyproject.toml` - PyPI doesn't allow re-uploading

#### Authentication Failed
**Solutions:**
- Username must be `__token__` (not your PyPI username)
- Password is your API token including `pypi-` prefix
- Check token scope and expiration

#### Module Not Found After Install
**Solution:** Ensure files are in `src/mcp_server_fetch/` directory

#### Build Errors
**Solutions:**
- Verify `pyproject.toml` configuration
- Check package structure matches build-backend expectations
- Run `uvx twine check dist/*` for specific errors

For more troubleshooting, see [PUBLISHING.md](./PUBLISHING.md#troubleshooting).

## 🔗 External Resources

### Official Documentation
- [uv Documentation](https://docs.astral.sh/uv/) - Fast Python package manager
- [Python Packaging Guide](https://packaging.python.org/) - Official packaging guide
- [Twine Documentation](https://twine.readthedocs.io/) - Package upload tool
- [PyPI Help](https://pypi.org/help/) - PyPI documentation

### PyPI Pages
- [Production PyPI](https://pypi.org/project/mcp-server-fetch-tom/)
- [Test PyPI](https://test.pypi.org/project/mcp-server-fetch-tom/)

### Project Resources
- [Main README](../README.md) - Project overview and usage
- [Makefile](../Makefile) - Build automation
- [publish.sh](../publish.sh) - Interactive publish script

## 📝 Contributing to Documentation

Found an issue or want to improve the docs? Contributions welcome!

1. Edit the relevant `.md` file in this directory
2. Test any commands you document
3. Submit a pull request

## 📄 License

This documentation is part of the mcp-server-fetch-tom project and is licensed under the MIT License.

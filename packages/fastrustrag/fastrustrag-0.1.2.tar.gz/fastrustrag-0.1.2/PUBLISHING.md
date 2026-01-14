# 📦 Publishing FastRAG to PyPI

## Prerequisites

1. **Install publishing tools:**
```bash
pip install maturin twine
```

2. **Create PyPI account:**
   - Go to https://pypi.org/account/register/
   - Verify your email
   - Set up 2FA (required)

3. **Create API token:**
   - Go to https://pypi.org/manage/account/
   - Scroll to "API tokens"
   - Create token with scope "Entire account"
   - **Save it securely!** You'll need it once

## Steps to Publish

### 1. Update Version (if needed)

Edit `pyproject.toml`:
```toml
[project]
version = "0.1.0"  # Change this for updates
```

### 2. Update Your Info

Edit `pyproject.toml`:
```toml
[project]
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]

[project.urls]
Homepage = "https://github.com/yourusername/fastrag"
Repository = "https://github.com/yourusername/fastrag"
```

### 3. Build the Package

```bash
# Clean previous builds
rm -rf dist/ target/wheels/

# Build for current platform
maturin build --release

# Or build wheels for multiple Python versions
maturin build --release --interpreter python3.8 python3.9 python3.10 python3.11 python3.12
```

**Note:** Wheels are platform-specific! For cross-platform:
- macOS (ARM): Build on M1/M2 Mac
- macOS (Intel): Build on Intel Mac or use maturin with target
- Linux: Build on Linux or use manylinux containers
- Windows: Build on Windows

### 4. Test Locally

```bash
# Install locally to test
pip install target/wheels/fastrag-0.1.0-*.whl

# Test it works
python -c "import fastrag; print('✅ Works!')"
```

### 5. Upload to PyPI

**Option A: Using maturin (recommended)**
```bash
maturin publish --username __token__ --password YOUR_PYPI_TOKEN
```

**Option B: Using twine**
```bash
twine upload target/wheels/*
# Username: __token__
# Password: YOUR_PYPI_TOKEN
```

### 6. Test Installation

```bash
# Create fresh environment
python -m venv test_env
source test_env/bin/activate  # or `test_env\Scripts\activate` on Windows

# Install from PyPI
pip install fastrag

# Test
python -c "import fastrag; print('✅ Published successfully!')"
```

## 🔄 Publishing Updates

1. Make your changes
2. Update version in `pyproject.toml`
3. Rebuild: `maturin build --release`
4. Publish: `maturin publish`

## 📋 Pre-publish Checklist

- [ ] Updated version number
- [ ] Updated your name/email in `pyproject.toml`
- [ ] Added GitHub repository URL
- [ ] Tested locally with `pip install target/wheels/fastrag-*.whl`
- [ ] All tests pass: `cargo test`
- [ ] README looks good
- [ ] LICENSE file included

## 🌍 Building for Multiple Platforms

### Using GitHub Actions (Recommended)

Create `.github/workflows/release.yml`:
```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build-wheels:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']
    
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install maturin
        run: pip install maturin
      
      - name: Build wheels
        run: maturin build --release --interpreter python${{ matrix.python-version }}
      
      - name: Upload wheels
        uses: actions/upload-artifact@v3
        with:
          name: wheels
          path: target/wheels/
      
  publish:
    needs: build-wheels
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v3
        with:
          name: wheels
          path: wheels
      
      - name: Publish to PyPI
        run: |
          pip install twine
          twine upload wheels/*
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
```

Then:
```bash
git tag v0.1.0
git push origin v0.1.0
```

## 🚨 Common Issues

### "Package already exists"
- You can't overwrite versions
- Increment version number in `pyproject.toml`

### "Invalid credentials"
- Make sure you're using `__token__` as username (with underscores)
- Check your API token is correct

### "No matching distribution"
- You need to build for each platform
- Consider using GitHub Actions for multi-platform builds

## 📚 Resources

- [PyPI Documentation](https://packaging.python.org/)
- [Maturin Guide](https://www.maturin.rs/)
- [PyO3 Documentation](https://pyo3.rs/)

---

**Ready to publish?** Run:
```bash
maturin publish
```

🎉 **Congratulations on publishing your first Rust-Python library!**

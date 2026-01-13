# PyPI Publishing Checklist - Everything You Need

## ✅ What You Already Have

1. ✅ `setup.py` - Setup configuration file exists
2. ✅ `README.md` - Project README exists
3. ✅ `requirements.txt` - Dependencies file exists
4. ✅ `soma/` package directory - Package structure exists
5. ✅ `soma/__init__.py` - Package initialization exists
6. ✅ GitHub repository - https://github.com/chavalasantosh/SOMA/

---

## ❌ What You Need to Create/Update

### 1. LICENSE File (Required)

**Status**: ❌ Missing

**Action**: Create `LICENSE` file in root directory

**Options**:
- MIT License (recommended, matches setup.py)
- Apache 2.0
- GPL

**File**: `LICENSE`

**Content** (MIT License example):
```
MIT License

Copyright (c) 2024 Santosh Chavala

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

### 2. Update setup.py (Required)

**Status**: ⚠️ Needs Updates

**Current Issues**:
- Author email is placeholder (`chavalasantosh@example.com`)
- May need to update dependencies
- Need to include vocabulary adapter dependencies

**Action**: Update `setup.py` with:
- Real author email
- Proper dependencies (if vocabulary adapter is included)
- Package data if needed

**Key Fields to Update**:
```python
author_email="your-real-email@example.com",  # Change this
```

---

### 3. MANIFEST.in (Optional but Recommended)

**Status**: ❌ Missing

**Action**: Create `MANIFEST.in` to include non-Python files

**File**: `MANIFEST.in`

**Content**:
```
include LICENSE
include README.md
include requirements.txt
recursive-include docs *.md
recursive-exclude * __pycache__
recursive-exclude * *.py[co]
recursive-exclude * .git*
recursive-exclude node_modules *
recursive-exclude frontend *
recursive-exclude tests *
```

---

### 4. .pypirc File (For Publishing)

**Status**: ❌ Missing

**Action**: Create `~/.pypirc` in your home directory (not in project)

**Location**: `~/.pypirc` or `C:\Users\SCHAVALA\.pypirc` (Windows)

**Content**:
```
[distutils]
index-servers = 
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
username = __token__
password = pypi-your-test-api-token-here
```

**Note**: Get API token from https://pypi.org/manage/account/token/

---

### 5. Package Structure Check

**Status**: ✅ Good, but verify

**Current Structure**:
```
soma/
├── __init__.py
├── soma.py
└── cli.py
```

**Potential Issues**:
- `src/` folder not included in package
- Vocabulary adapter (`src/integration/`) not accessible
- Core tokenizer (`src/core/`) not accessible

**Action**: Decide what to include:
- **Option A**: Include everything (core + integration)
- **Option B**: Only include `soma/` package (current)

**If including src/**, update `setup.py`:
```python
packages=find_packages(include=['soma', 'src.*']),
```

---

### 6. Dependencies in setup.py

**Status**: ⚠️ Needs Update

**Current**: `install_requires=[]` (empty)

**Action**: Update based on what's needed:

**Option A: Core only (no dependencies)**
```python
install_requires=[],
```

**Option B: With vocabulary adapter (requires transformers)**
```python
install_requires=[
    "transformers>=4.30.0",  # For vocabulary adapter
],
```

**Option C: Full dependencies**
```python
install_requires=[
    "transformers>=4.30.0",  # For vocabulary adapter (optional)
    # Add other dependencies if core package needs them
],
```

---

### 7. PyPI Account

**Status**: ❌ Need to create

**Action**: 
1. Go to https://pypi.org/account/register/
2. Create account
3. Enable 2FA (recommended)
4. Create API token at https://pypi.org/manage/account/token/

---

### 8. Build Tools

**Status**: ⚠️ Need to install

**Action**: Install build tools
```bash
pip install --upgrade build twine
```

**Required packages**:
- `build` - Modern build tool
- `twine` - Upload tool

---

### 9. Version Management

**Status**: ⚠️ Needs strategy

**Current**: `version="1.0.0"` in setup.py

**Action**: 
- Update version in `setup.py`
- Update version in `soma/__init__.py` (currently `__version__ = "1.0.0"`)
- Keep them in sync

**Versioning Strategy**:
- `1.0.0` - Initial release
- `1.0.1` - Bug fixes
- `1.1.0` - New features
- `2.0.0` - Breaking changes

---

### 10. Test PyPI (Recommended First Step)

**Status**: ❌ Need to test

**Action**: 
1. Create account at https://test.pypi.org/account/register/
2. Test upload to Test PyPI first
3. Verify installation from Test PyPI
4. Then upload to real PyPI

---

### 11. Documentation Files

**Status**: ✅ README.md exists

**Action**: 
- Ensure README.md is clear and complete
- Add installation instructions
- Add usage examples
- Note about vocabulary adapter being optional

---

### 12. .gitignore Updates

**Status**: ⚠️ Check if needed

**Action**: Ensure these are in `.gitignore`:
```
*.egg-info/
dist/
build/
*.egg
.pypirc  # Don't commit API tokens!
```

---

## 📋 Complete Checklist

### Pre-Publishing Steps

- [ ] Create `LICENSE` file
- [ ] Update `setup.py` with real email
- [ ] Update `setup.py` dependencies (if needed)
- [ ] Create `MANIFEST.in` (optional)
- [ ] Sync version numbers in `setup.py` and `soma/__init__.py`
- [ ] Create PyPI account
- [ ] Create Test PyPI account
- [ ] Get API tokens from PyPI
- [ ] Create `~/.pypirc` file (not in project)
- [ ] Install build tools: `pip install build twine`
- [ ] Update README.md if needed
- [ ] Test package locally: `pip install -e .`

### Build Steps

- [ ] Clean previous builds: `rm -rf dist/ build/ *.egg-info`
- [ ] Build package: `python -m build`
- [ ] Check build: `twine check dist/*`
- [ ] Test installation locally: `pip install dist/soma-1.0.0.tar.gz`

### Test PyPI Upload

- [ ] Upload to Test PyPI: `twine upload --repository testpypi dist/*`
- [ ] Test install from Test PyPI: `pip install -i https://test.pypi.org/simple/ soma`
- [ ] Verify functionality
- [ ] Fix any issues

### Production PyPI Upload

- [ ] Upload to PyPI: `twine upload dist/*`
- [ ] Verify on https://pypi.org/project/soma/
- [ ] Test installation: `pip install soma`
- [ ] Verify functionality

---

## 🚀 Quick Commands Reference

### Build Package
```bash
# Install build tools
pip install --upgrade build twine

# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build
python -m build

# Check
twine check dist/*
```

### Upload to Test PyPI
```bash
twine upload --repository testpypi dist/*
```

### Upload to PyPI
```bash
twine upload dist/*
```

### Test Installation
```bash
# From Test PyPI
pip install -i https://test.pypi.org/simple/ soma

# From PyPI (after upload)
pip install soma
```

---

## ⚠️ Important Notes

### What NOT to Include

- ❌ `node_modules/` (frontend dependencies)
- ❌ `frontend/` (React app - not needed for Python package)
- ❌ `tests/` (unless you want to include them)
- ❌ `docs/` (optional - can exclude)
- ❌ `.git/` folder
- ❌ `__pycache__/` folders
- ❌ Virtual environment folders

### What TO Include

- ✅ `soma/` package directory
- ✅ `src/` (if you want vocabulary adapter accessible)
- ✅ `LICENSE` file
- ✅ `README.md`
- ✅ `setup.py`
- ✅ `requirements.txt` (optional)

---

## 📦 Package Structure Decision

**Current**: Only `soma/` package included

**Decision Needed**: Should vocabulary adapter be included?

**Option A: Core only**
```python
# setup.py
packages=find_packages(include=['soma']),
```

**Option B: Include integration**
```python
# setup.py
packages=find_packages(include=['soma', 'src.integration']),
# or
packages=['soma', 'src.integration'],
```

**Option C: Include everything**
```python
# setup.py
packages=find_packages(exclude=['tests', 'frontend', 'node_modules']),
```

---

## 🎯 Recommended Approach

1. **Start Simple**: Include only `soma/` package (core tokenization)
2. **Make vocabulary adapter optional**: Install separately if needed
3. **Keep dependencies minimal**: Core package has no dependencies

**Reasoning**: 
- Simpler package
- Faster installation
- Users can install vocabulary adapter separately if needed
- Core functionality works without transformers

---

## 📝 Files You Need to Create/Update

### 1. LICENSE (Create)
```
Location: LICENSE
Content: MIT License text
```

### 2. setup.py (Update)
```
- Change author_email
- Update install_requires (if needed)
- Verify packages list
```

### 3. MANIFEST.in (Create - Optional)
```
Location: MANIFEST.in
Content: Include/exclude rules
```

### 4. .pypirc (Create - In home directory)
```
Location: ~/.pypirc (not in project)
Content: API token configuration
```

---

## ✅ Final Checklist Before Publishing

- [ ] LICENSE file created
- [ ] setup.py updated (email, dependencies)
- [ ] Version numbers synced
- [ ] README.md complete
- [ ] Package builds successfully
- [ ] Tests pass (if you have tests)
- [ ] Tested on Test PyPI
- [ ] API token configured
- [ ] Ready to publish!

---

**Last Updated**: Based on actual file check
**Status**: Checklist of everything needed


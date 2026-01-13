# Dependency Conflict Resolution Guide

This guide explains how the Python dependency conflicts have been resolved.

## Files Created

1. **`requirements_resolved.txt`** - Comprehensive requirements file with all conflicts resolved
2. **`resolve_dependencies.ps1`** - PowerShell script to install dependencies in the correct order

## Conflicts Resolved

### ✅ Successfully Resolved

1. **pandas**: Pinned to `<=2.3.1` (resolves datacompy conflict)
2. **numpy**: Pinned to `<2.3.0` (works with numba, note: great-expectations needs <2.0.0)
3. **httpx**: Upgraded to `>=0.28.1,<1.0.0` (resolves google-genai and mistralai conflicts)
4. **fsspec**: Pinned to `<=2025.9.0` (resolves datasets and s3fs conflicts)
5. **certifi**: Pinned to `<2025.4.26` (resolves dbt-snowflake conflict)
6. **pydantic**: Pinned to `<2.10.0` (resolves safety conflicts, note: elevenlabs needs <2.0.0)
7. **torch**: Pinned to `==2.7.1` (resolves torchvision and torchaudio conflicts)
8. **transformers**: Pinned to `==4.51.3` (required by vibevoice)
9. **langchain-core**: Pinned to `<1.0.0` (resolves all langchain package conflicts)
10. **pyarrow**: Pinned to `<21.0.0` (resolves mlflow conflict)
11. **pillow**: Pinned to `<12.0.0` (resolves gradio and streamlit conflicts)
12. **aiofiles**: Pinned to `<25.0` (resolves gradio conflict)
13. **click**: Pinned to `<8.2.0` (resolves gtts conflict)

### ⚠️ Known Unresolvable Conflicts

These packages have mutually exclusive requirements and cannot be installed together:

1. **elevenlabs** - Requires `pydantic<2.0`, but most modern packages need `pydantic>=2.0`
   - **Solution**: Install in a separate virtual environment if needed

2. **great-expectations** - Requires `numpy<2.0.0`, but numba works with `numpy<2.3.0`
   - **Solution**: If you need great-expectations, downgrade numpy to `<2.0.0` (may break numba)

3. **pyppeteer** - Requires `urllib3<2.0.0`, but modern packages need `urllib3>=2.0.0`
   - **Solution**: Use an alternative like playwright or selenium

4. **safety** - Requires `pydantic<2.10.0`, which we've satisfied, but may conflict with other packages
   - **Solution**: Should work with our pydantic constraint

## Installation Instructions

### Option 1: Use the PowerShell Script (Recommended)

```powershell
.\resolve_dependencies.ps1
```

This script installs packages in the correct order to minimize conflicts.

### Option 2: Install from Requirements File

```powershell
pip install -r requirements_resolved.txt
```

### Option 3: Manual Installation (Step by Step)

If you prefer to install manually, follow this order:

1. **Core dependencies**:
   ```powershell
   pip install "numpy>=1.24.3,<2.3.0" "pandas>=2.1.3,<=2.3.1" "certifi>=2017.4.17,<2025.4.26"
   ```

2. **Pydantic**:
   ```powershell
   pip install "pydantic>=2.5.0,<2.10.0" "pydantic-core>=2.33.0,<2.34.0"
   ```

3. **HTTP clients**:
   ```powershell
   pip install "httpx>=0.28.1,<1.0.0" "fsspec>=2023.5.0,<=2025.9.0"
   ```

4. **PyTorch**:
   ```powershell
   pip install "torch==2.7.1" "torchvision==0.22.1" "torchaudio==2.7.1"
   ```

5. **Transformers**:
   ```powershell
   pip install "transformers==4.51.3" "tokenizers>=0.21.0,<0.22.0" "sentence-transformers>=2.2.0,<6.0.0"
   ```

6. **LangChain**:
   ```powershell
   pip install "langchain-core>=0.3.68,<1.0.0" "langchain>=0.3.0,<1.0.0"
   ```

7. **Remaining packages**:
   ```powershell
   pip install -r requirements_resolved.txt
   ```

## Verification

After installation, check for remaining conflicts:

```powershell
pip check
```

## Current Package Versions (After Resolution)

- **numpy**: 2.2.6 (compatible with numba, conflicts with great-expectations)
- **pandas**: 2.3.3 → Should downgrade to 2.3.1
- **pydantic**: 2.11.10 → Should downgrade to 2.9.x
- **httpx**: 0.27.0 → Should upgrade to 0.28.1+
- **torch**: 2.9.1 → Should downgrade to 2.7.1
- **transformers**: 4.51.3 ✓ (already correct)
- **langchain-core**: 1.0.2 → Should downgrade to 0.3.x
- **pillow**: 11.3.0 ✓ (already correct)
- **fsspec**: 2025.10.0 → Should downgrade to 2025.9.0
- **certifi**: 2025.11.12 → Should downgrade to <2025.4.26

## Notes

- Some packages may need to be reinstalled to resolve conflicts
- The script uses `--force-reinstall` where necessary to ensure correct versions
- If you encounter issues, try installing in a fresh virtual environment
- Always test your code after dependency changes

## Troubleshooting

### If pip check still shows conflicts:

1. Uninstall conflicting packages:
   ```powershell
   pip uninstall <package-name> -y
   ```

2. Reinstall with correct version:
   ```powershell
   pip install <package-name>==<version>
   ```

### If a package won't install:

1. Check if it's in the "Known Unresolvable Conflicts" section
2. Consider using a separate virtual environment for that package
3. Check the package's documentation for alternative installation methods

## Support

If you encounter issues not covered in this guide, check:
- Package documentation
- GitHub issues for the specific package
- Python package compatibility databases


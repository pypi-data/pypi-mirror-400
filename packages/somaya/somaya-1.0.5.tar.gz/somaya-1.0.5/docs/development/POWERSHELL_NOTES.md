# PowerShell Usage Notes

## Running Scripts in PowerShell

PowerShell has a security feature that requires you to explicitly specify the path when running scripts in the current directory. You must use `.\` prefix.

### Correct Syntax

```powershell
# Setup
.\setup.bat

# Run server
.\run.bat

# Test setup
.\test_setup.bat

# Prepare for distribution
.\prepare_for_distribution.bat
```

### Why?

PowerShell doesn't automatically search the current directory for executables (unlike Command Prompt). This is a security feature to prevent accidentally running malicious scripts.

### Alternative: Use Command Prompt

If you prefer, you can use Command Prompt (cmd.exe) instead, where you don't need the `.\` prefix:

```cmd
setup.bat
run.bat
```

### Alternative: Use Python Directly

You can also run Python scripts directly:

```powershell
python start.py
python verify_installation.py
python run.py
```

## Quick Reference

| Task | PowerShell | Command Prompt | Python |
|------|-----------|----------------|--------|
| Setup | `.\setup.bat` | `setup.bat` | N/A |
| Run Server | `.\run.bat` | `run.bat` | `python start.py` |
| Verify | `python verify_installation.py` | `python verify_installation.py` | `python verify_installation.py` |
| Test | `.\test_setup.bat` | `test_setup.bat` | N/A |


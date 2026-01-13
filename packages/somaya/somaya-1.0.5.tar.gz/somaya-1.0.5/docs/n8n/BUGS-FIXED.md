# 🔧 Quick Fixes for Critical Bugs

## Fix 1: Use curl.exe instead of curl

Replace all `curl` with `curl.exe` in batch files:

```batch
REM Before:
curl -s http://localhost:8000/health

REM After:
curl.exe -s http://localhost:8000/health
```

## Fix 2: Use Absolute Paths

```batch
REM Before:
cd workflows

REM After:
cd /d "%~dp0workflows"
```

## Fix 3: Remove Unix Commands

```batch
REM Before:
type temp_response.txt | findstr /V "^$" | head -n 1

REM After:
type temp_response.txt | findstr /V "^$" | more +1
```

## Fix 4: Fix Variable Expansion

```batch
REM Add at top:
setlocal enabledelayedexpansion

REM In loops, use !var! instead of %var%
set /a COUNT+=1
echo [!COUNT!] Importing...
```

## Fix 5: Check Directory Exists

```batch
if not exist "%~dp0workflows" (
    echo ❌ Workflows directory not found!
    exit /b 1
)
```


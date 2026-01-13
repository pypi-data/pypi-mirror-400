# SOMA Installation Guide

Complete step-by-step installation instructions for Windows, Linux, and macOS.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Windows Installation](#windows-installation)
3. [Linux Installation](#linux-installation)
4. [macOS Installation](#macos-installation)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Operating System**: Windows 10+, Linux (Ubuntu 20.04+, Debian 11+), macOS 10.15+
- **Python**: 3.11 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 2GB free space
- **Internet**: Required for downloading dependencies

### Check Python Installation

**Windows:**
```cmd
python --version
```

**Linux/Mac:**
```bash
python3 --version
```

If Python is not installed or version is below 3.11:
- **Windows**: Download from [python.org](https://www.python.org/downloads/)
- **Linux**: `sudo apt-get install python3.11 python3.11-venv python3-pip` (Ubuntu/Debian)
- **macOS**: `brew install python@3.11` (using Homebrew) or download from [python.org](https://www.python.org/downloads/)

## Windows Installation

### Step 1: Clone or Download Repository

**Using Git:**
```cmd
git clone <repository-url>
cd SOMA
```

**Or download ZIP:**
1. Download repository as ZIP
2. Extract to desired location
3. Open Command Prompt in extracted folder

### Step 2: Automated Setup (Recommended)

Run the setup script:
```powershell
.\setup.bat
```

This will:
- Check Python version
- Create virtual environment
- Install all dependencies
- Verify installation

### Step 3: Manual Setup (Alternative)

If automated setup doesn't work:

**Create virtual environment:**
```cmd
python -m venv venv
```

**Activate virtual environment:**
```cmd
venv\Scripts\activate
```

**Upgrade pip:**
```cmd
python -m pip install --upgrade pip
```

**Install dependencies:**
```cmd
pip install -r requirements.txt
```

### Step 4: Verify Installation

```cmd
python verify_installation.py
```

### Step 5: Run the Server

**Using run script:**
```powershell
.\run.bat
```

**Or manually:**
```powershell
venv\Scripts\activate
python start.py
```

The server will start on `http://localhost:8000`

## Linux Installation

### Step 1: Clone or Download Repository

**Using Git:**
```bash
git clone <repository-url>
cd SOMA
```

**Or download ZIP:**
```bash
wget <repository-url>/archive/main.zip
unzip main.zip
cd SOMA-main
```

### Step 2: Automated Setup (Recommended)

Make script executable and run:
```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Check Python version
- Create virtual environment
- Install all dependencies
- Verify installation

### Step 3: Manual Setup (Alternative)

If automated setup doesn't work:

**Install system dependencies (if needed):**
```bash
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv python3-pip build-essential
```

**Create virtual environment:**
```bash
python3 -m venv venv
```

**Activate virtual environment:**
```bash
source venv/bin/activate
```

**Upgrade pip:**
```bash
pip install --upgrade pip
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

### Step 4: Verify Installation

```bash
python3 verify_installation.py
```

### Step 5: Run the Server

**Using run script:**
```bash
chmod +x run.sh
./run.sh
```

**Or manually:**
```bash
source venv/bin/activate
python3 start.py
```

The server will start on `http://localhost:8000`

## macOS Installation

### Step 1: Install Homebrew (if not installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 2: Install Python 3.11

```bash
brew install python@3.11
```

### Step 3: Clone or Download Repository

**Using Git:**
```bash
git clone <repository-url>
cd SOMA
```

**Or download ZIP:**
1. Download repository as ZIP
2. Extract to desired location
3. Open Terminal in extracted folder

### Step 4: Automated Setup (Recommended)

Make script executable and run:
```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Check Python version
- Create virtual environment
- Install all dependencies
- Verify installation

### Step 5: Manual Setup (Alternative)

If automated setup doesn't work:

**Create virtual environment:**
```bash
python3 -m venv venv
```

**Activate virtual environment:**
```bash
source venv/bin/activate
```

**Upgrade pip:**
```bash
pip install --upgrade pip
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

### Step 6: Verify Installation

```bash
python3 verify_installation.py
```

### Step 7: Run the Server

**Using run script:**
```bash
chmod +x run.sh
./run.sh
```

**Or manually:**
```bash
source venv/bin/activate
python3 start.py
```

The server will start on `http://localhost:8000`

## Verification

After installation, verify everything works:

```bash
# Windows
python verify_installation.py

# Linux/Mac
python3 verify_installation.py
```

The verification script checks:
- ✅ Python version (3.11+)
- ✅ All required packages installed
- ✅ File structure correct
- ✅ Basic imports work
- ✅ Server can start

## Troubleshooting

### Python Version Issues

**Problem**: "Python 3.11 or higher required"

**Solution**:
- **Windows**: Download Python 3.11+ from [python.org](https://www.python.org/downloads/)
- **Linux**: `sudo apt-get install python3.11`
- **macOS**: `brew install python@3.11`

### Virtual Environment Issues

**Problem**: "venv module not found"

**Solution**:
- **Windows**: `python -m pip install --upgrade pip virtualenv`
- **Linux**: `sudo apt-get install python3.11-venv`
- **macOS**: Usually included with Python

### Dependency Installation Fails

**Problem**: Packages fail to install

**Solutions**:
1. Upgrade pip: `pip install --upgrade pip`
2. Use virtual environment (always recommended)
3. Install build tools:
   - **Windows**: Install Visual C++ Build Tools
   - **Linux**: `sudo apt-get install build-essential python3-dev`
   - **macOS**: `xcode-select --install`

### Port Already in Use

**Problem**: "Address already in use" error

**Solution**:
```bash
# Find process using port 8000
# Windows:
netstat -ano | findstr :8000

# Linux/Mac:
lsof -i :8000

# Kill process or use different port:
PORT=8001 python start.py
```

### Import Errors

**Problem**: "ModuleNotFoundError" or "ImportError"

**Solutions**:
1. Ensure virtual environment is activated
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check you're in project root directory
4. Run `python verify_installation.py` to diagnose

### Permission Denied (Linux/Mac)

**Problem**: "Permission denied" when running scripts

**Solution**:
```bash
chmod +x setup.sh
chmod +x run.sh
```

### Windows Path Issues

**Problem**: "python is not recognized"

**Solution**:
1. Add Python to PATH during installation
2. Or use full path: `C:\Python311\python.exe`
3. Or use `py` launcher: `py -3.11`

### Large File Downloads

**Problem**: Slow dependency installation

**Solution**:
- Use pip cache: `pip install --cache-dir .pip-cache -r requirements.txt`
- Use faster mirror: `pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt`

### Memory Issues

**Problem**: Out of memory during installation

**Solution**:
- Close other applications
- Install dependencies one at a time if needed
- Use Docker instead (see Docker section in README)

## Next Steps

After successful installation:

1. **Start the server**: Use `run.sh`/`run.bat` or `python start.py`
2. **Access API docs**: Open `http://localhost:8000/docs` in browser
3. **Try CLI**: `python soma_cli.py tokenize --text "Hello world"`
4. **Read documentation**: Check [QUICK_START.md](QUICK_START.md) for usage examples

## Getting Help

If you encounter issues not covered here:

1. Run `python verify_installation.py` for diagnostics
2. Check server logs for error messages
3. Review [README.md](README.md) troubleshooting section
4. Check GitHub issues (if repository is on GitHub)

## Uninstallation

To remove SOMA:

1. Deactivate virtual environment: `deactivate` (or close terminal)
2. Delete project directory
3. Virtual environment is self-contained, no system cleanup needed


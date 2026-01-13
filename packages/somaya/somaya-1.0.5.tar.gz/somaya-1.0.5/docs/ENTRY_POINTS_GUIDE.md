# SOMA Entry Points Guide

## Overview

SOMA provides multiple entry points for different use cases. This guide explains when to use each one.

## Entry Points

### 1. `soma.cli:main` (setup.py entry point)

**Location:** Defined in `setup.py`  
**Command:** `soma` (after installation via `pip install -e .`)  
**Purpose:** Primary CLI entry point after package installation

**Usage:**
```bash
# After installation
pip install -e .
soma --help
```

**Features:**
- Standard package entry point
- Available after installation
- Uses `soma/cli.py`

---

### 2. `main.py` (Interactive Mode Selector)

**Location:** `main.py` (root directory)  
**Command:** `python main.py`  
**Purpose:** Interactive mode selector for different SOMA modes

**Usage:**
```bash
python main.py
```

**Modes:**
1. CLI Mode - Command line interface
2. Server Mode - Web API server (main)
3. Lightweight Mode - Minimal server
4. Direct Mode - Direct function calls

**Best For:**
- Interactive usage
- Trying different modes
- Development and testing

---

### 3. `run.py` (Production Server Starter)

**Location:** `run.py` (root directory)  
**Command:** `python run.py`  
**Purpose:** Cross-platform script to start the SOMA API server

**Usage:**
```bash
python run.py
python run.py --port 8080
```

**Features:**
- Automatic environment detection (Windows/Linux/Mac)
- Virtual environment detection and activation
- Dependency checking
- Port configuration
- Railway deployment ready

**Best For:**
- Production server deployment
- Cross-platform compatibility
- Railway/Heroku deployment
- Automated startup scripts

---

### 4. `soma_cli.py` (Full-Featured CLI)

**Location:** `soma_cli.py` (root directory)  
**Command:** `python soma_cli.py <command>`  
**Purpose:** Comprehensive CLI with tokenization, training, embedding, and testing

**Usage:**
```bash
# Tokenize
python soma_cli.py tokenize --text "Hello world" --method word

# Train
python soma_cli.py train --file data.txt --model-path model.pkl

# Generate embeddings
python soma_cli.py embed --text "Hello" --model-path model.pkl

# Run tests
python soma_cli.py test

# Show info
python soma_cli.py info
```

**Commands:**
- `tokenize` - Tokenize text/file/URL
- `train` - Train semantic embeddings
- `embed` - Generate embeddings
- `test` - Run tests
- `info` - Show system information

**Best For:**
- Advanced CLI operations
- Training models
- Generating embeddings
- Testing functionality

---

### 5. `start.py` (Railway Deployment)

**Location:** `start.py` (root directory)  
**Command:** Used by Railway automatically  
**Purpose:** Railway deployment startup script

**Usage:**
- Automatically called by Railway
- Reads `PORT` environment variable
- Starts uvicorn server

**Best For:**
- Railway deployment only
- Production deployment

---

## Comparison Table

| Entry Point | Use Case | Installation Required | Interactive | Server | CLI |
|------------|----------|---------------------|-------------|--------|-----|
| `soma` (setup.py) | Standard CLI | Yes | No | No | Yes |
| `main.py` | Mode selector | No | Yes | Yes | Yes |
| `run.py` | Server startup | No | No | Yes | No |
| `soma_cli.py` | Full CLI features | No | No | No | Yes |
| `start.py` | Railway deployment | No | No | Yes | No |

## Recommendations

### For Package Installation
Use: `soma` (setup.py entry point)
```bash
pip install -e .
soma --help
```

### For Development/Testing
Use: `main.py` or `soma_cli.py`
```bash
python main.py  # Interactive mode selector
python soma_cli.py tokenize --text "Hello"
```

### For Production Server
Use: `run.py` or `start.py`
```bash
python run.py  # Cross-platform
# Or Railway will use start.py automatically
```

### For Training/Embeddings
Use: `soma_cli.py`
```bash
python soma_cli.py train --file data.txt
python soma_cli.py embed --text "Hello"
```

## Quick Start

**New Users:**
1. Start with `python main.py` for interactive mode selection
2. Try `python soma_cli.py info` to see available features
3. Use `python run.py` to start the API server

**Developers:**
1. Install package: `pip install -e .`
2. Use `soma` command after installation
3. Use `python soma_cli.py` for advanced features

**Production:**
1. Use `python run.py` for standalone deployment
2. Use `start.py` for Railway deployment
3. Configure via environment variables

---

*Last Updated: 2025-01-17*


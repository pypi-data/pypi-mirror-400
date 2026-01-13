# SOMA Utilities Usage Guide

## Overview

SOMA provides utility modules for configuration, logging, and validation. This guide shows how to use them.

## Configuration Management

### Basic Usage

```python
from soma.utils.config import Config

# Get server port (reads PORT env var or defaults to 8000)
port = Config.get_port()

# Get server host (reads HOST env var or defaults to 0.0.0.0)
host = Config.get_host()

# Get log level (reads LOG_LEVEL env var or defaults to INFO)
log_level = Config.get_log_level()

# Get directories (reads env vars or uses defaults)
data_dir = Config.get_data_dir()      # DATA_DIR or "data"
models_dir = Config.get_models_dir()  # MODELS_DIR or "models"
output_dir = Config.get_output_dir()  # OUTPUT_DIR or "outputs"

# Get log file path (reads LOG_FILE env var or returns None)
log_file = Config.get_log_file()
```

### Environment Variables

Set these environment variables to configure SOMA:

```bash
# Server configuration
export PORT=8080
export HOST=0.0.0.0

# Logging
export LOG_LEVEL=DEBUG
export LOG_FILE=/path/to/soma.log

# Directories
export DATA_DIR=/path/to/data
export MODELS_DIR=/path/to/models
export OUTPUT_DIR=/path/to/outputs
```

**Alternative variable names** (with `SANTOK_` prefix):
- `SANTOK_PORT` instead of `PORT`
- `SANTOK_HOST` instead of `HOST`
- `SANTOK_LOG_LEVEL` instead of `LOG_LEVEL`
- etc.

---

## Input Validation

### Text Validation

```python
from soma.utils.validation import validate_text_input, ValidationError

try:
    text = validate_text_input("Hello world", "text")
    print(f"Valid text: {text}")
except ValidationError as e:
    print(f"Error: {e}")
```

### File Path Validation

```python
from soma.utils.validation import validate_file_path

# Validate path (file doesn't need to exist)
path = validate_file_path("data/file.txt", must_exist=False)

# Validate path (file must exist)
path = validate_file_path("data/file.txt", must_exist=True)
```

### Port Validation

```python
from soma.utils.validation import validate_port

try:
    port = validate_port(8080, "port")
    print(f"Valid port: {port}")
except ValidationError as e:
    print(f"Error: {e}")
```

### Integer Validation

```python
from soma.utils.validation import validate_positive_int

# Validate positive integer (minimum 1)
value = validate_positive_int(42, "value")

# Validate with custom minimum
value = validate_positive_int(100, "value", min_value=50)
```

### Choice Validation

```python
from soma.utils.validation import validate_choice

# Validate value is in choices list
method = validate_choice("word", ["word", "char", "space"], "method")
```

---

## Logging Configuration

### Setup Logging

```python
from soma.utils.logging_config import setup_logging, get_logger

# Set up logging with default settings
setup_logging()

# Set up with custom level
setup_logging(level="DEBUG")

# Set up with log file
setup_logging(level="INFO", log_file="soma.log")

# Set up with custom format
setup_logging(
    level="INFO",
    log_file="soma.log",
    format_string="%(levelname)s - %(message)s"
)
```

### Using Loggers

```python
from soma.utils.logging_config import get_logger

# Get logger for your module
logger = get_logger(__name__)

# Use logger instead of print
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")

# With formatting
logger.info("Processing %d items", count)
logger.error("Failed to process: %s", error_msg)
```

### Complete Example

```python
from soma.utils.config import Config
from soma.utils.logging_config import setup_logging, get_logger
from soma.utils.validation import validate_text_input, validate_port

# Set up logging from config
setup_logging(
    level=Config.get_log_level(),
    log_file=Config.get_log_file()
)

# Get logger
logger = get_logger(__name__)

# Validate inputs
try:
    text = validate_text_input("Hello", "text")
    port = validate_port(Config.get_port(), "port")
    
    logger.info("Starting server on port %d", port)
    logger.info("Processing text: %s", text)
    
except ValidationError as e:
    logger.error("Validation failed: %s", e)
```

---

## Integration Examples

### In Server Scripts

```python
# start.py or run.py
from soma.utils.config import Config
from soma.utils.logging_config import setup_logging, get_logger
from soma.utils.validation import validate_port

# Set up logging
setup_logging(
    level=Config.get_log_level(),
    log_file=Config.get_log_file()
)
logger = get_logger(__name__)

# Get and validate port
port = validate_port(Config.get_port(), "PORT")
logger.info("Starting server on port %d", port)
```

### In CLI Commands

```python
# soma/cli.py
from soma.utils.validation import validate_text_input, validate_file_path
from soma.utils.logging_config import get_logger

logger = get_logger(__name__)

def tokenize(text: str, file: str):
    if text:
        text = validate_text_input(text, "text")
    elif file:
        file_path = validate_file_path(file, must_exist=True, param_name="file")
        with open(file_path) as f:
            text = f.read()
    
    logger.info("Tokenizing text of length %d", len(text))
    # ... tokenization logic
```

### In Training Scripts

```python
# train_soma_complete.py
from soma.utils.config import Config
from soma.utils.logging_config import setup_logging, get_logger
from soma.utils.validation import validate_file_path

setup_logging(level="INFO")
logger = get_logger(__name__)

# Get directories from config
data_dir = Config.get_data_dir()
models_dir = Config.get_models_dir()

# Validate input file
input_file = validate_file_path("data/training.txt", must_exist=True)

logger.info("Training with data from %s", input_file)
logger.info("Saving models to %s", models_dir)
```

---

## Migration from Print Statements

### Before (Print Statements)

```python
print("Starting server...")
print(f"Port: {port}")
print(f"Error: {error}")
```

### After (Logging)

```python
from soma.utils.logging_config import get_logger

logger = get_logger(__name__)

logger.info("Starting server...")
logger.info("Port: %d", port)
logger.error("Error: %s", error)
```

### Benefits

1. **Structured Logging:** Logs include timestamps, levels, and module names
2. **Configurable Levels:** Filter logs by level (DEBUG, INFO, WARNING, ERROR)
3. **File Logging:** Can write logs to files for production
4. **Better Debugging:** Easier to trace issues with structured logs

---

## Best Practices

1. **Use Config for All Paths:**
   ```python
   # Good
   data_dir = Config.get_data_dir()
   
   # Bad
   data_dir = "data"  # Hardcoded
   ```

2. **Validate All Inputs:**
   ```python
   # Good
   text = validate_text_input(user_input, "text")
   
   # Bad
   text = user_input  # No validation
   ```

3. **Use Logging for All Messages:**
   ```python
   # Good
   logger.info("Processing complete")
   
   # Bad
   print("Processing complete")  # Not structured
   ```

4. **Set Up Logging Early:**
   ```python
   # At application startup
   setup_logging(level=Config.get_log_level())
   ```

---

## Error Handling

All validation functions raise `ValidationError` on failure:

```python
from soma.utils.validation import ValidationError, validate_text_input

try:
    text = validate_text_input("", "text")
except ValidationError as e:
    print(f"Validation failed: {e}")
    # Handle error appropriately
```

---

## Summary

- **Configuration:** Use `Config` class for all environment-based settings
- **Validation:** Use validation functions for all user inputs
- **Logging:** Use `get_logger()` instead of `print()` statements
- **Error Handling:** Catch `ValidationError` for validation failures

---

*Last Updated: 2025-01-17*


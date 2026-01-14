# Quick-Datalog
A lightweight Python logging tool with **colorful terminal output**, **automatic exception capture**, **sync/async support**, and **FATAL log level**. Designed for fast integration in Python projects, supporting log grading and date-based log file splitting.

[![PyPI Version](https://img.shields.io/pypi/v/quick-datalog.svg)](https://pypi.org/project/quick-datalog/)
[![Python Versions](https://img.shields.io/pypi/pyversions/quick-datalog.svg)](https://pypi.org/project/quick-datalog/)
[![License](https://img.shields.io/pypi/l/quick-datalog.svg)](https://github.com/huyuenshen/quick-datalog/blob/main/LICENSE)

## Features
- **Log Grading**: Supports 5 levels - DEBUG(0), INFO(1), WARN(2), ERROR(3), FATAL(4)
- **Colorful Output**: Distinct colors for better visibility:
  - DEBUG: Cyan
  - INFO: Green
  - WARN: Yellow
  - ERROR: Red
  - FATAL: Red background + White text
- **Auto Exception Capture**: One-line decorator for both sync/async functions, with fatal exception marking
- **Zero Configuration**: Automatically creates log directories and configuration files on first run
- **Date-based Splitting**: Generates separate log files for each day to avoid oversized files
- **Dual Mode Support**: Sync logging (core module) + Async logging (asynclog module)
- **Mode Switch**: Toggle debug/production mode with `-O` command-line argument

## Installation
### PyPI Installation (Recommended)
```bash
pip install quick-datalog
```

### Local Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/huyuenshen/quick-datalog.git
   cd quick-datalog
   ```
2. Install from source:
   ```bash
   pip install .
   ```

## Quick Start
### 1. Sync Logging (Core Module)
```python
from quick_datalog import Datalog, start_logger

# Initialize logger
logger = Datalog()

# Log messages of different levels
logger.log("This is a DEBUG message", typ=0)
logger.log("This is an INFO message", typ=1)
logger.log("This is a WARN message", typ=2)
logger.log("This is an ERROR message", typ=3)
logger.log("This is a FATAL message", typ=4)  # New FATAL level

# Exception capture with decorator (mark specific exceptions as FATAL)
@start_logger
def test_function():
    logger.log("Running sync test function", typ=1)
    raise KeyError("Critical error (marked as FATAL)")  # Triggers FATAL log

if __name__ == "__main__":
    try:
        test_function()
    except Exception:
        pass
```

### 2. Async Logging (asynclog Module)
For asynchronous functions, use the `asynclog` module to avoid blocking the event loop:
```python
import asyncio
from quick_datalog import asynclog

async def async_test_func():
    logger = asynclog.Datalog()
    await logger.log("This is an async INFO message", typ=1)
    await logger.log("This is an async FATAL message", typ=4)  # Async FATAL log
    await asyncio.sleep(1)  # Simulate async work (non-blocking)

# Async decorator with fatal exception marking
@asynclog.start_logger
async def wrapped_async_func():
    await async_test_func()
    raise KeyError("Async fatal error")  # Triggers FATAL log

if __name__ == "__main__":
    asyncio.run(wrapped_async_func())
```

### Mode Switch
- **Debug Mode (Default)**: Shows all log levels (DEBUG/INFO/WARN/ERROR/FATAL)
  ```bash
  python your_script.py
  ```
- **Production Mode**: Hides DEBUG level (shows INFO/WARN/ERROR/FATAL)
  ```bash
  python your_script.py -O
  ```

## Configuration
### Auto-generated Config File
On first run, a configuration file is created at `./Datalog/.config/Config.json` with the following default content:
```json
{
    "pattern": "[{time}][{func}][{level}]:{msg}",
    "file": "./Datalog/{date}.log.txt"
}
```

- **pattern**: Log format template (supports `{time}`, `{func}`, `{level}`, `{msg}`)
- **file**: Log file path (`{date}` is replaced with the current date, e.g., `2025-12-25.log.txt`)

### Custom Log Format
Modify the `pattern` field to customize the log format, e.g.:
```json
{
    "pattern": "[{time}] [{level}] [{func}] - {msg}"
}
```

## Compatibility
- **Python Versions**: 3.7+
- **Platforms**: Windows, macOS, Linux, Android (Python compilers like Pydroid)

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing
Issues and pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
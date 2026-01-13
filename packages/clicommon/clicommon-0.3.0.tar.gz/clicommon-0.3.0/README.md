# clicommon

A lightweight Python library providing common utilities for command-line applications. It simplifies logging, variable checking, and subprocess execution in CLI tools and scripts.

## Features

- **`bcheck`**: Check if a variable exists in the caller's scope and is truthy
- **`mlog`**: Flexible logging with colored output, timestamps, and exit codes
- **`rcmd`**: Simple wrapper for running shell commands with error handling

## Installation

```bash
pip install clicommon
```

Or using uv:

```bash
uv add clicommon
```

## Usage

### bcheck

Checks if a variable exists in the caller's scope and evaluates to True.

```python
from clicommon import bcheck

my_var = True
if bcheck("my_var"):
    print("Variable exists and is truthy")

if not bcheck("undefined_var"):
    print("Variable does not exist or is falsy")
```

### mlog

A versatile logging function with support for colors, timestamps, and exit codes.

```python
from clicommon import mlog

# Simple message
mlog("INFO", "Starting process")

# Use colors (COLORS must be set in scope)
COLORS = True
mlog("SUCCESS", "Operation completed successfully")

# Add timestamps (DATELOG must be set in scope)
DATELOG = True
mlog("WARN", "This is a warning")

# Enable debug output (DEBUG must be set in scope)
DEBUG = True
mlog("DEBUG", "Debug information")

# Exit with code
mlog("ERROR", "Fatal error occurred", exit_code=1)
```

#### Message Types and Default Colors

| Type | Color |
|------|-------|
| INFO | Green |
| SUCCESS | Green |
| WARN/WARNING | Yellow |
| FATAL/ERROR/CRITICAL | Red |
| TEST | Gray |
| DEBUG | Magenta |
| VERBOSE | Bright Cyan |
| BUILD_DEBUG/CODE_DEBUG | Bright Green |

#### Function Signature

```python
def mlog(msg_type, msg_string=None, exit_code=None, datelog=None, colors=None)
```

- `msg_type`: Type of message (determines color and verbosity filtering)
- `msg_string`: Message content (if None, msg_type becomes the message)
- `exit_code`: If provided, exit with this code after logging
- `datelog`: If True, add ISO8601 timestamp (or set `DATELOG=True` in scope)
- `colors`: If True, use ANSI colors (or set `COLORS=True` in scope)

### rcmd

Run shell commands with automatic error handling and logging.

```python
from clicommon import rcmd

# Simple command execution
output = rcmd("ls -la")
print(output)

# Commands that fail will automatically log an error and exit
```

## Development

Install development dependencies:

```bash
uv sync --dev
```

Run tests:

```bash
uv run pytest
```

Build the package:

```bash
uv build
```

## Publishing to PyPI

To publish a new release to PyPI:

1. Update the version in `pyproject.toml`
2. Commit your changes
3. Create and push a version tag:
   ```bash
   git tag v0.3.0
   git push origin v0.3.0
   ```
4. The GitHub workflow will automatically:
   - Run all tests
   - Build the package
   - Publish to PyPI (requires `PYPI_API_TOKEN` secret in GitHub)

**Important**: Before tagging, ensure you have added a `PYPI_API_TOKEN` secret to your GitHub repository settings.

To test the build locally:
```bash
uv build
```

## License

Apache License 2.0

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

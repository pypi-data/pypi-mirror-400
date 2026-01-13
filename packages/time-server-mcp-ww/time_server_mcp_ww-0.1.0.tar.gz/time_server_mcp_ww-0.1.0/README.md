# Time Server MCP

A time server tool built with FastMCP that provides current time information.

## Features

- Get current time with optional timezone support
- Simple command-line interface
- Easy to integrate as a library
- Built with FastMCP for efficient communication

## Installation

You can install Time Server MCP using pip:

```bash
pip install time-server-mcp
```

## Usage

### Command Line Interface

After installation, you can run the time server directly from the command line:

```bash
time-server
```

This will start the FastMCP server, which will be ready to accept requests for current time information.

### As a Library

You can also use the time server functionality in your own Python code:

```python
from time_server import get_current_time

# Get current time in system default timezone
time_now = get_current_time()
print(f"Current time: {time_now}")

# Get current time in a specific timezone
time_shanghai = get_current_time(timezone="Asia/Shanghai")
print(f"Current time in Shanghai: {time_shanghai}")

time_new_york = get_current_time(timezone="America/New_York")
print(f"Current time in New York: {time_new_york}")
```

### API Documentation

#### `get_current_time(timezone: Optional[str] = None) -> str`

Get the current time in a specified timezone.

**Parameters:**
- `timezone`: Optional timezone string, e.g., "Asia/Shanghai", "America/New_York". If not provided, system default timezone will be used.

**Returns:**
- Formatted current time string in the format "YYYY-MM-DD HH:MM:SS.SSSSSS Timezone Name".

**Example:**
```python
time = get_current_time("Europe/London")
# Output: 2023-12-25 15:30:45.123456 GMT
```

## Dependencies

- Python >= 3.8
- pytz >= 2023.3
- mcp-server >= 0.1.0

## License

MIT License

## Project Links

- [Homepage](https://github.com/yourusername/time-server-mcp)
- [Bug Tracker](https://github.com/yourusername/time-server-mcp/issues)

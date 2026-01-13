# EdgePulse Python SDK

[![PyPI version](https://badge.fury.io/py/edgepulse.svg)](https://badge.fury.io/py/edgepulse)
[![Python Support](https://img.shields.io/pypi/pyversions/edgepulse.svg)](https://pypi.org/project/edgepulse/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

The EdgePulse Python SDK provides monitoring and observability capabilities for Python applications. It allows you to track function executions, capture timing data, handle errors, and send telemetry to EdgePulse services.

## Installation

Install the EdgePulse SDK using pip:

```bash
pip install edgepulse
```

## Quick Start

1. **Set up your environment**:
   ```bash
   export EDGEPULSE_PROJECT_KEY="your-api-key-here"
   export EDGEPULSE_API_URL="https://api.edgepulse.com/api/Invocation"  # Optional
   ```

2. **Use the decorator to monitor functions**:
   ```python
   from Edgepulse import with_edgepulse

   @with_edgepulse
   def my_function(x, y):
       """Your function logic here."""
       return x + y

   # The function will now be monitored automatically
   result = my_function(1, 2)
   ```

## Features

- **Zero-configuration monitoring**: Simple decorator-based approach
- **Automatic timing**: Captures function execution duration
- **Error tracking**: Records exceptions with full stack traces  
- **Flexible telemetry**: Sends data to configurable EdgePulse endpoints
- **Type safety**: Full type hints for better development experience
- **No external dependencies**: Uses only Python standard library

## Configuration

The SDK uses environment variables for configuration:

- `EDGEPULSE_PROJECT_KEY` (required): Your EdgePulse API key
- `EDGEPULSE_API_URL` (optional): EdgePulse API endpoint (defaults to localhost for development)

## Advanced Usage

### Manual invocation tracking

```python
from Edgepulse import EdgePulseInvocation, store_invocation

# Create a custom invocation
invocation = EdgePulseInvocation.create(
    function_name="my_function",
    invoked_at="2026-01-02T10:30:00Z",
    status_code=200,
    duration_ms=150
)

# Store it
store_invocation(invocation)
```

### Custom HTTP client

```python
from Edgepulse import WebClient, store_invocation

# Use a custom client with different timeout
client = WebClient("https://api.edgepulse.com/api/Invocation", timeout=30)
store_invocation(invocation, client=client)
```

## Development

### Setting up development environment

```bash
git clone https://github.com/edgepulse/sdk-python.git
cd sdk-python
pip install -e ".[dev]"
```

## Requirements

- Python 3.9+

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- Documentation: Does not exists yet
- Issues: [https://github.com/jeremytrips/edgepulse.py/issues](https://github.com/edgepulse/sdk-python/issues)
- Email: jeremy.trips@gmail.com

## Contributing

We welcome contributions!
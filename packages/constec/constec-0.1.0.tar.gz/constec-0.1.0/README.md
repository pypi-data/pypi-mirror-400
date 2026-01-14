# Constec

Base library for the Constec ecosystem - provides shared utilities for working with Constec services.

## Installation

```bash
pip install constec
```

## What is this?

This is a foundational library that provides common utilities used across Constec client libraries. Most users will install this automatically as a dependency when installing specific Constec client packages like:

- **constec-erp** - Client for the Constec ERP API

If you're looking to interact with Constec services, install the specific client library you need instead of this base package.

## Usage

This library provides exception classes for error handling when working with Constec APIs:

```python
from constec.shared import (
    ConstecError,
    ConstecAPIError,
    ConstecConnectionError,
    ConstecValidationError,
    ConstecAuthenticationError,
    ConstecNotFoundError,
)

# Handle errors from Constec services
try:
    # Your Constec API calls here
    pass
except ConstecAuthenticationError:
    print("Authentication failed - check your credentials")
except ConstecNotFoundError:
    print("Resource not found")
except ConstecAPIError as e:
    print(f"API error: {e.message}")
    if e.status_code:
        print(f"Status code: {e.status_code}")
```

## Available Exceptions

- `ConstecError` - Base exception for all Constec errors
- `ConstecAPIError` - API request failures (includes status code and response data)
- `ConstecAuthenticationError` - Authentication failures
- `ConstecNotFoundError` - Resource not found (404)
- `ConstecConnectionError` - Connection failures
- `ConstecValidationError` - Data validation errors

## Requirements

- Python 3.9 or higher

## License

MIT

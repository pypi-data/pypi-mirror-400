# hotglue-etl-exceptions

Python module providing exception classes for Hotglue ETL operations.

## Installation

```bash
pip install -e .
```

## Usage

```python
from hotglue_etl_exceptions import InvalidCredentialsError, InvalidPayloadError

# Raise InvalidCredentialsError exception
raise InvalidCredentialsError("Invalid username or password")

# Raise InvalidPayloadError exception
raise InvalidPayloadError("Payload validation failed")
```

## Exported Classes

- `InvalidCredentialsError`: Exception raised when credentials are invalid
- `InvalidPayloadError`: Exception raised when payload is invalid


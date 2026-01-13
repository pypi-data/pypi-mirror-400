# Error Handling

Learn how to handle errors effectively in Vi SDK with comprehensive error information and recovery strategies.

## Overview

Vi SDK provides a structured error handling system with:

- **Specific error types** for different failure scenarios
- **Error codes** for programmatic handling
- **Helpful suggestions** for resolving issues
- **Retry indicators** for transient errors
- **Detailed context** about what went wrong

## Error Hierarchy

All errors inherit from the base `ViError` class:

```
ViError (base)
├── ViAuthenticationError
├── ViNotFoundError
├── ViRateLimitError
├── ViServerError
├── ViNetworkError
├── ViValidationError
│   ├── ViInvalidParameterError
│   ├── ViFileTooLargeError
│   └── ViInvalidFileFormatError
├── ViConflictError
├── ViTimeoutError
├── ViPermissionError
├── ViConfigurationError
├── ViOperationError
├── ViDownloadError
└── ViUploadError
```

## Basic Error Handling

### Catching All Errors

```python
from vi import ViError

try:
    client = vi.Client()
    dataset = client.datasets.get("dataset-id")
except ViError as e:
    print(f"Error: {e.error_code}")
    print(f"Message: {e.message}")
    if e.suggestion:
        print(f"Suggestion: {e.suggestion}")
```

### Catching Specific Errors

```python
from vi import (
    ViAuthenticationError,
    ViNotFoundError,
    ViValidationError
)

try:
    client = vi.Client(
        secret_key="invalid-key",
        organization_id="org-id"
    )
    dataset = client.datasets.get("dataset-id")

except ViAuthenticationError as e:
    print(f"Authentication failed: {e.message}")
    # Handle authentication error

except ViNotFoundError as e:
    print(f"Resource not found: {e.message}")
    # Handle not found error

except ViValidationError as e:
    print(f"Validation error: {e.message}")
    # Handle validation error
```

## Error Types

### ViAuthenticationError

Raised when authentication fails.

**Common causes:**
- Invalid API key
- Expired credentials
- Missing organization ID

**Example:**

```python
from vi import ViAuthenticationError

try:
    client = vi.Client(
        secret_key="invalid-key",
        organization_id="org-id"
    )
except ViAuthenticationError as e:
    print(f"Auth failed: {e.message}")
    # Re-prompt for credentials or refresh token
```

### ViNotFoundError

Raised when a requested resource doesn't exist.

**Example:**

```python
from vi import ViNotFoundError

try:
    dataset = client.datasets.get("nonexistent-id")
except ViNotFoundError as e:
    print(f"Dataset not found: {e.message}")
    # Create dataset or use different ID
```

### ViValidationError

Raised when input validation fails.

**Example:**

```python
from vi import ViValidationError, ViInvalidParameterError

try:
    assets = client.assets.list(
        dataset_id="",  # Invalid empty string
        pagination={"page_size": -1}  # Invalid negative value
    )
except ViInvalidParameterError as e:
    print(f"Invalid parameter '{e.parameter_name}': {e.message}")
except ViValidationError as e:
    print(f"Validation error: {e.message}")
```

### ViNetworkError

Raised when network operations fail.

**Example:**

```python
from vi import ViNetworkError

try:
    dataset = client.get_dataset("dataset-id")
except ViNetworkError as e:
    print(f"Network error: {e.message}")
    if e.is_retryable():
        # Implement retry logic
        pass
```

### ViRateLimitError

Raised when API rate limits are exceeded.

**Example:**

```python
from vi import ViRateLimitError
import time

try:
    # Bulk operation
    for i in range(1000):
        client.assets.get(dataset_id, asset_id)
except ViRateLimitError as e:
    print(f"Rate limited: {e.message}")
    # Wait and retry
    time.sleep(60)
```

### ViServerError

Raised when server errors occur (5xx).

**Example:**

```python
from vi import ViServerError

try:
    dataset = client.get_dataset("dataset-id")
except ViServerError as e:
    print(f"Server error: {e.message}")
    if e.is_retryable():
        # Server errors are often transient
        retry_with_backoff()
```

## Error Properties

Every `ViError` provides rich information:

```python
try:
    # Operation that might fail
    pass
except ViError as e:
    # Error code
    print(f"Code: {e.error_code}")  # e.g., "ResourceNotFound"

    # HTTP status code
    print(f"Status: {e.status_code}")  # e.g., 404

    # Human-readable message
    print(f"Message: {e.message}")

    # Helpful suggestion
    if e.suggestion:
        print(f"Suggestion: {e.suggestion}")

    # Original cause (if any)
    if e.cause:
        print(f"Caused by: {e.cause}")

    # Additional details
    if e.details:
        print(f"Details: {e.details}")

    # Check error type
    if e.is_client_error():  # 4xx
        print("Client error - check your input")
    elif e.is_server_error():  # 5xx
        print("Server error - try again later")

    # Check if retryable
    if e.is_retryable():
        print("This error is retryable")
```

## Retry Strategies

### Simple Retry

```python
from vi import ViError
import time

def retry_operation(func, max_retries=3, delay=1):
    """Retry an operation with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return func()
        except ViError as e:
            if not e.is_retryable():
                # Don't retry non-retryable errors
                raise

            if attempt == max_retries - 1:
                # Last attempt failed
                raise

            # Exponential backoff
            wait_time = delay * (2 ** attempt)
            print(f"Attempt {attempt + 1} failed, retrying in {wait_time}s...")
            time.sleep(wait_time)

# Usage
dataset = retry_operation(
    lambda: client.get_dataset("dataset-id")
)
```

### Advanced Retry with Decorators

```python
from functools import wraps
from vi import ViError
import time

def retry_on_error(max_retries=3, delay=1, backoff=2):
    """Decorator to retry operations on retryable errors."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except ViError as e:
                    if not e.is_retryable() or attempt == max_retries - 1:
                        raise

                    wait_time = delay * (backoff ** attempt)
                    print(f"Retrying after {wait_time}s...")
                    time.sleep(wait_time)
        return wrapper
    return decorator

# Usage
@retry_on_error(max_retries=3, delay=1, backoff=2)
def download_dataset(dataset_id):
    return client.get_dataset(dataset_id)

dataset = download_dataset("dataset-id")
```

### Retry with Tenacity

Using the `tenacity` library for production-grade retry logic:

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception
)
from vi import ViError

@retry(
    retry=retry_if_exception(lambda e: isinstance(e, ViError) and e.is_retryable()),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=60)
)
def download_with_retry(dataset_id):
    return client.get_dataset(dataset_id)

# Usage
dataset = download_with_retry("dataset-id")
```

## Error Context

Capture and log error context for debugging:

```python
import logging
from vi import ViError

logger = logging.getLogger(__name__)

try:
    dataset = client.get_dataset("dataset-id")
except ViError as e:
    # Log with full context
    logger.error(
        "Dataset download failed",
        extra={
            "error_code": e.error_code,
            "status_code": e.status_code,
            "message": e.message,
            "suggestion": e.suggestion,
            "details": e.details,
            "is_retryable": e.is_retryable(),
            "dataset_id": "dataset-id"
        }
    )
    raise
```

## Handling Specific Scenarios

### File Upload Errors

```python
from vi import (
    ViFileTooLargeError,
    ViInvalidFileFormatError,
    ViUploadError
)

try:
    result = client.assets.upload(
        dataset_id="dataset-id",
        paths="./images/"
    )
    # Check for errors using result properties
    if result.total_failed > 0:
        print(f"Warning: {result.total_failed} files failed to upload")
        # Access failed file paths if available
        if result.failed_files:
            for failed_file in result.failed_files:
                print(f"  - {failed_file}")
except ViFileTooLargeError as e:
    print(f"File too large: {e.message}")
    print(f"Max size: {e.max_size}")
    # Resize images or split upload

except ViInvalidFileFormatError as e:
    print(f"Invalid format: {e.message}")
    print(f"Supported: {e.supported_formats}")
    # Convert to supported format

except ViUploadError as e:
    print(f"Upload failed: {e.message}")
    # Retry or check network
```

### Download Errors

```python
from vi import ViDownloadError, ViTimeoutError

try:
    dataset = client.get_dataset(
        dataset_id="dataset-id",
        show_progress=True
    )
except ViTimeoutError as e:
    print(f"Download timed out: {e.message}")
    # Retry with longer timeout

except ViDownloadError as e:
    print(f"Download failed: {e.message}")
    # Check disk space, permissions
```

### Permission Errors

```python
from vi import ViPermissionError

try:
    dataset = client.datasets.delete("dataset-id")
except ViPermissionError as e:
    print(f"Permission denied: {e.message}")
    print(f"Suggestion: {e.suggestion}")
    # Request elevated permissions
```

## Best Practices

### 1. Be Specific with Error Handling

```python
# ✅ Good - handle specific errors
try:
    dataset = client.get_dataset("dataset-id")
except ViNotFoundError:
    # Create dataset
    pass
except ViAuthenticationError:
    # Refresh credentials
    pass

# ❌ Bad - catch everything
try:
    dataset = client.get_dataset("dataset-id")
except Exception:
    pass
```

### 2. Use Error Suggestions

```python
from vi import ViError

try:
    dataset = client.get_dataset("dataset-id")
except ViError as e:
    print(f"Error: {e.message}")
    if e.suggestion:
        # Show suggestion to user
        print(f"💡 {e.suggestion}")
```

### 3. Log Errors Properly

```python
import logging
from vi import ViError

logger = logging.getLogger(__name__)

try:
    dataset = client.get_dataset("dataset-id")
except ViError as e:
    # Log with structured data
    logger.error(
        "Operation failed",
        exc_info=True,
        extra={
            "error_code": e.error_code,
            "dataset_id": "dataset-id"
        }
    )
```

### 4. Graceful Degradation

```python
from vi import ViError

def get_dataset_safe(dataset_id, fallback=None):
    """Get dataset with fallback on error."""
    try:
        return client.get_dataset(dataset_id)
    except ViError as e:
        logger.warning(f"Failed to get dataset: {e.message}")
        return fallback

# Usage
dataset = get_dataset_safe("dataset-id", fallback=None)
if dataset is None:
    # Use alternative data source
    pass
```

### 5. Clean Up on Error

```python
from vi import ViError

temp_files = []
try:
    # Operation that creates temp files
    temp_files = create_temp_files()
    upload_files(temp_files)
except ViError as e:
    logger.error(f"Upload failed: {e.message}")
    raise
finally:
    # Clean up regardless of success/failure
    for temp_file in temp_files:
        temp_file.unlink()
```

## Error Recovery Examples

### Automatic Retry with Circuit Breaker

```python
from vi import ViError
import time

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.is_open = False

    def call(self, func, *args, **kwargs):
        if self.is_open:
            if time.time() - self.last_failure_time < self.timeout:
                raise Exception("Circuit breaker is open")
            self.is_open = False
            self.failure_count = 0

        try:
            result = func(*args, **kwargs)
            self.failure_count = 0
            return result
        except ViError as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.is_open = True

            raise

# Usage
breaker = CircuitBreaker()
dataset = breaker.call(client.get_dataset, "dataset-id")
```

## Testing Error Handling

```python
import pytest
from vi import ViNotFoundError

def test_handles_not_found():
    """Test that code handles not found errors."""
    with pytest.raises(ViNotFoundError):
        client.datasets.get("nonexistent-id")

def test_retry_logic():
    """Test retry logic works correctly."""
    attempts = []

    def failing_operation():
        attempts.append(1)
        if len(attempts) < 3:
            raise ViNetworkError("Simulated failure")
        return "success"

    result = retry_operation(failing_operation, max_retries=3)
    assert result == "success"
    assert len(attempts) == 3
```

## Summary

| Error Type | HTTP Status | Retryable | Common Cause |
|------------|-------------|-----------|--------------|
| `ViAuthenticationError` | 401 | No | Invalid credentials |
| `ViNotFoundError` | 404 | No | Resource doesn't exist |
| `ViPermissionError` | 403 | No | Insufficient permissions |
| `ViValidationError` | 400 | No | Invalid input |
| `ViConflictError` | 409 | No | Resource conflict |
| `ViRateLimitError` | 429 | Yes | Too many requests |
| `ViServerError` | 500-599 | Yes | Server issues |
| `ViNetworkError` | N/A | Yes | Network problems |
| `ViTimeoutError` | 408 | Yes | Operation timeout |

## See Also

- [Client API Reference](../api/client.md) - Client error handling
- [Examples](https://github.com/datature/Vi-SDK/tree/main/pypi/vi-sdk/examples/pypi/vi-sdk/examples) - Error handling examples
- [Logging Guide](logging.md) - Log errors effectively

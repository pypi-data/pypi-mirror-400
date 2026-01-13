---
title: "Errors API Reference"
excerpt: "Complete reference for error handling and error types"
category: "api-reference"
---

# Errors API Reference

Complete API reference for error handling. All custom exceptions and error types are documented here.

---

## Base Error

### ViError

The base class for all Vi SDK errors.

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `error_code` | `str` | Unique error code identifier |
| `status_code` | `int` | HTTP status code (if applicable) |
| `message` | `str` | Human-readable error message |
| `suggestion` | `str \| None` | Helpful suggestion for resolving the error |
| `cause` | `Exception \| None` | Original exception that caused this error |
| `details` | `dict \| None` | Additional error details |

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `is_retryable()` | `bool` | Returns `True` if the error is transient and can be retried |
| `is_client_error()` | `bool` | Returns `True` if this is a 4xx client error |
| `is_server_error()` | `bool` | Returns `True` if this is a 5xx server error |

**Example:**

```python
from vi import ViError

try:
    client.datasets.get("invalid-id")
except ViError as e:
    print(f"Error code: {e.error_code}")
    print(f"Message: {e.message}")
    if e.suggestion:
        print(f"Suggestion: {e.suggestion}")
    if e.is_retryable():
        print("This error can be retried")
```

---

## Authentication & Authorization Errors

### ViAuthenticationError

Raised when authentication fails.

**HTTP Status:** 401

**Retryable:** No

**Common causes:**
- Invalid API key
- Expired credentials
- Missing organization ID

```python
from vi import ViAuthenticationError

try:
    client = vi.Client(secret_key="invalid-key", organization_id="org-id")
except ViAuthenticationError as e:
    print(f"Authentication failed: {e.message}")
```

---

### ViPermissionError

Raised when the user doesn't have permission to perform an action.

**HTTP Status:** 403

**Retryable:** No

**Common causes:**
- Insufficient permissions
- Resource not accessible to user
- Organization restrictions

```python
from vi import ViPermissionError

try:
    client.datasets.delete("dataset-id")
except ViPermissionError as e:
    print(f"Permission denied: {e.message}")
```

---

## Resource Errors

### ViNotFoundError

Raised when a requested resource doesn't exist.

**HTTP Status:** 404

**Retryable:** No

```python
from vi import ViNotFoundError

try:
    dataset = client.datasets.get("nonexistent-id")
except ViNotFoundError as e:
    print(f"Not found: {e.message}")
```

---

### ViConflictError

Raised when there's a conflict with an existing resource.

**HTTP Status:** 409

**Retryable:** No

**Common causes:**
- Resource already exists
- Version conflict
- Concurrent modification

```python
from vi import ViConflictError

try:
    client.datasets.create(name="existing-name")
except ViConflictError as e:
    print(f"Conflict: {e.message}")
```

---

## Validation Errors

### ViValidationError

Raised when input validation fails.

**HTTP Status:** 400

**Retryable:** No

```python
from vi import ViValidationError

try:
    client.assets.list(dataset_id="")  # Empty ID
except ViValidationError as e:
    print(f"Validation error: {e.message}")
```

---

### ViInvalidParameterError

Raised when a specific parameter is invalid.

**HTTP Status:** 400

**Retryable:** No

**Additional Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `parameter_name` | `str` | Name of the invalid parameter |

```python
from vi import ViInvalidParameterError

try:
    client.assets.list(dataset_id="", pagination={"page_size": -1})
except ViInvalidParameterError as e:
    print(f"Invalid parameter '{e.parameter_name}': {e.message}")
```

---

### ViInvalidFileFormatError

Raised when a file format is not supported.

**HTTP Status:** 400

**Retryable:** No

**Additional Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `supported_formats` | `list[str]` | List of supported formats |

```python
from vi import ViInvalidFileFormatError

try:
    client.assets.upload(dataset_id="...", paths="file.xyz")
except ViInvalidFileFormatError as e:
    print(f"Invalid format: {e.message}")
    print(f"Supported: {e.supported_formats}")
```

---

### ViFileTooLargeError

Raised when a file exceeds the maximum allowed size.

**HTTP Status:** 400

**Retryable:** No

**Additional Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `max_size` | `int` | Maximum allowed file size in bytes |
| `file_size` | `int` | Actual file size in bytes |

```python
from vi import ViFileTooLargeError

try:
    client.assets.upload(dataset_id="...", paths="large_file.jpg")
except ViFileTooLargeError as e:
    print(f"File too large: {e.file_size} bytes (max: {e.max_size})")
```

---

## Network & Connection Errors

### ViNetworkError

Raised when network operations fail.

**HTTP Status:** N/A

**Retryable:** Yes

**Common causes:**
- No internet connection
- DNS resolution failure
- Connection refused

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

---

### ViTimeoutError

Raised when an operation times out.

**HTTP Status:** 408

**Retryable:** Yes

```python
from vi import ViTimeoutError

try:
    dataset = client.get_dataset("large-dataset-id")
except ViTimeoutError as e:
    print(f"Timeout: {e.message}")
```

---

## Rate Limiting

### ViRateLimitError

Raised when API rate limits are exceeded.

**HTTP Status:** 429

**Retryable:** Yes

**Additional Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `retry_after` | `int \| None` | Seconds to wait before retrying |

```python
from vi import ViRateLimitError
import time

try:
    for i in range(1000):
        client.assets.get(dataset_id, asset_id)
except ViRateLimitError as e:
    print(f"Rate limited: {e.message}")
    if e.retry_after:
        time.sleep(e.retry_after)
```

---

## Server Errors

### ViServerError

Raised when server errors occur (5xx).

**HTTP Status:** 500-599

**Retryable:** Yes

```python
from vi import ViServerError

try:
    dataset = client.get_dataset("dataset-id")
except ViServerError as e:
    print(f"Server error: {e.message}")
    if e.is_retryable():
        # Server errors are often transient
        pass
```

---

## Operation Errors

### ViOperationError

Raised when an operation fails.

**Retryable:** Varies

```python
from vi import ViOperationError

try:
    result = client.assets.upload(...)
except ViOperationError as e:
    print(f"Operation failed: {e.message}")
```

---

### ViUploadError

Raised when an upload operation fails.

**Retryable:** Yes

```python
from vi import ViUploadError

try:
    result = client.assets.upload(
        dataset_id="dataset-id",
        paths="./images/"
    )
except ViUploadError as e:
    print(f"Upload failed: {e.message}")
```

---

### ViDownloadError

Raised when a download operation fails.

**Retryable:** Yes

```python
from vi import ViDownloadError

try:
    dataset = client.get_dataset("dataset-id")
except ViDownloadError as e:
    print(f"Download failed: {e.message}")
```

---

## Configuration Errors

### ViConfigurationError

Raised when there's a configuration problem.

**Retryable:** No

```python
from vi import ViConfigurationError

try:
    client = vi.Client()  # Missing credentials
except ViConfigurationError as e:
    print(f"Configuration error: {e.message}")
```

---

## Error Summary Table

| Error Type | HTTP Status | Retryable | Common Cause |
|------------|-------------|-----------|--------------|
| `ViAuthenticationError` | 401 | No | Invalid credentials |
| `ViPermissionError` | 403 | No | Insufficient permissions |
| `ViNotFoundError` | 404 | No | Resource doesn't exist |
| `ViConflictError` | 409 | No | Resource conflict |
| `ViValidationError` | 400 | No | Invalid input |
| `ViInvalidParameterError` | 400 | No | Invalid parameter |
| `ViInvalidFileFormatError` | 400 | No | Unsupported file format |
| `ViFileTooLargeError` | 400 | No | File exceeds size limit |
| `ViRateLimitError` | 429 | Yes | Too many requests |
| `ViServerError` | 500-599 | Yes | Server issues |
| `ViNetworkError` | N/A | Yes | Network problems |
| `ViTimeoutError` | 408 | Yes | Operation timeout |
| `ViUploadError` | Varies | Yes | Upload failure |
| `ViDownloadError` | Varies | Yes | Download failure |
| `ViConfigurationError` | N/A | No | Configuration issue |

---

## See Also

- [Error Handling Guide](vi-sdk-error-handling) - Comprehensive error handling strategies
- [Client API](vi-sdk-client) - Client documentation

# Errors API

Complete API reference for error handling. All custom exceptions and error types are documented here.

## Base Error

::: vi.client.errors.base_error.ViError
    options:
      show_root_heading: true
      show_source: true
      heading_level: 2

## Error Code Enum

::: vi.client.errors.base_error.ViErrorCode
    options:
      show_root_heading: true
      show_source: false
      heading_level: 2

## Authentication & Authorization Errors

### ViAuthenticationError

::: vi.client.errors.errors.ViAuthenticationError
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

### ViPermissionError

::: vi.client.errors.errors.ViPermissionError
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

## Resource Errors

### ViNotFoundError

::: vi.client.errors.errors.ViNotFoundError
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

### ViConflictError

::: vi.client.errors.errors.ViConflictError
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

## Validation Errors

### ViValidationError

::: vi.client.errors.errors.ViValidationError
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

### ViInvalidParameterError

::: vi.client.errors.errors.ViInvalidParameterError
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

### ViInvalidFileFormatError

::: vi.client.errors.errors.ViInvalidFileFormatError
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

### ViFileTooLargeError

::: vi.client.errors.errors.ViFileTooLargeError
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

## Network & Connection Errors

### ViNetworkError

::: vi.client.errors.errors.ViNetworkError
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

### ViTimeoutError

::: vi.client.errors.errors.ViTimeoutError
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

## Rate Limiting

### ViRateLimitError

::: vi.client.errors.errors.ViRateLimitError
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

## Server Errors

### ViServerError

::: vi.client.errors.errors.ViServerError
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

## Operation Errors

### ViOperationError

::: vi.client.errors.errors.ViOperationError
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

### ViUploadError

::: vi.client.errors.errors.ViUploadError
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

### ViDownloadError

::: vi.client.errors.errors.ViDownloadError
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

## Configuration Errors

### ViConfigurationError

::: vi.client.errors.errors.ViConfigurationError
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

## Error Factory

### create_error_from_response

::: vi.client.errors.errors.create_error_from_response
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

## See Also

- [User Guide: Error Handling](../guide/error-handling.md)
- [Client API](client.md)

---
title: "Types API Reference"
excerpt: "Common types and parameters used throughout the SDK"
category: "api-reference"
---

# Types API Reference

Complete API reference for common types and parameters used throughout the SDK.

---

## Base Types

### ViStruct

Base class for all Vi API structs.

```python
from vi.api.types import ViStruct
```

All request and response models in the SDK inherit from this base class, which provides:

- Automatic camelCase to snake_case field name conversion
- Keyword-only initialization
- Efficient serialization/deserialization

---

### ViResponse

Base class for all Vi API responses.

```python
from vi.api.responses import ViResponse
```

All response models in the SDK inherit from this base class.

---

## Query Parameters

### QueryParamsMixin

Mixin class for converting structs to URL query parameters.

```python
from vi.api.types import QueryParamsMixin
```

This mixin provides utilities for converting struct fields to URL query parameters with proper naming conventions and value transformations.

**Class Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `_FIELD_MAPPINGS` | `dict[str, str]` | Custom field name mappings |
| `_BOOLEAN_FLAGS` | `set[str]` | Fields to treat as boolean flags |
| `_SKIP_DEFAULT_VALUES` | `dict[str, Any]` | Default values to skip in query |
| `_VALUE_MAPPINGS` | `dict[str, dict[Any, str]]` | Custom value transformations |

---

## Response Types

### ResourceMetadata

Metadata attached to API resources.

```python
from vi.api.responses import ResourceMetadata
```

| Property | Type | Description |
|----------|------|-------------|
| `time_created` | `int` | Unix timestamp when resource was created (milliseconds) |
| `last_updated` | `int` | Unix timestamp when resource was last updated (milliseconds) |
| `generation` | `int` | Resource generation number |
| `attributes` | `dict[str, str]` | Additional resource attributes |

**Example:**

```python
dataset = client.datasets.get("dataset_abc123")

print(f"Created: {dataset.metadata.time_created}")
print(f"Updated: {dataset.metadata.last_updated}")
print(f"Generation: {dataset.metadata.generation}")
```

---

### ResourceCondition

Condition information for resources with status tracking.

```python
from vi.api.responses import ResourceCondition
```

| Property | Type | Description |
|----------|------|-------------|
| `condition` | [`Condition`](#condition) | The condition type |
| `status` | [`ConditionStatus`](#conditionstatus) | The condition status |
| `last_transition_time` | `int` | Unix timestamp of last transition |
| `reason` | `str \| None` | Reason for the condition |
| `message` | `str \| None` | Detailed message |

**Example:**

```python
run = client.runs.get("run_abc123")

if run.status.conditions:
    latest = run.status.conditions[-1]
    print(f"Condition: {latest.condition.value}")
    print(f"Status: {latest.status.value}")
    if latest.message:
        print(f"Message: {latest.message}")
```

---

### User

User information in organization context.

```python
from vi.api.responses import User
```

| Property | Type | Description |
|----------|------|-------------|
| `workspace_role` | `str` | The user's role in the workspace |
| `datasets` | `dict[str, str]` | Mapping of dataset IDs to access roles |

**Example:**

```python
org = client.organizations.get()

for user_id, user in org.users.items():
    print(f"User: {user_id}")
    print(f"  Role: {user.workspace_role}")
    print(f"  Datasets: {len(user.datasets)}")
```

---

### DeletedResource

Base response for deleted resources.

```python
from vi.api.responses import DeletedResource
```

| Property | Type | Description |
|----------|------|-------------|
| `id` | `str` | ID of the deleted resource |
| `deleted` | `bool` | Whether the resource was deleted |

---

### Pagination

Generic pagination response.

```python
from vi.api.responses import Pagination
```

| Property | Type | Description |
|----------|------|-------------|
| `next_page` | `str \| None` | URL to next page |
| `prev_page` | `str \| None` | URL to previous page |
| `items` | `list[T]` | Items on current page |

---

## Enums

### Condition

Resource condition types.

```python
from vi.api.responses import Condition
```

| Value | Description |
|-------|-------------|
| `FINISHED` | Resource operation finished |
| `STARTED` | Resource operation started |
| `ALL` | All conditions |

> 📘 **Note**
>
> Unknown condition values from the API are automatically converted to snake_case enum members.

---

### ConditionStatus

Status values for resource conditions.

```python
from vi.api.responses import ConditionStatus
```

| Value | Description |
|-------|-------------|
| `WAITING` | Condition is waiting to be reached |
| `REACHED` | Condition has been reached |
| `FAILED_REACH` | Failed to reach condition |

---

## Logging Types

### LoggingConfig

Configuration for Vi SDK logging.

```python
from vi.logging.config import LoggingConfig
```

**Constructor:**

```python
config = LoggingConfig(
    level: LogLevel = LogLevel.INFO,
    format: LogFormat = LogFormat.PLAIN,
    enable_console: bool = True,
    enable_file: bool = False,
    log_file_path: str | Path | None = None,
    include_timestamp: bool = True,
    include_level: bool = True,
    include_logger_name: bool = True,
    include_thread_info: bool = False,
    include_process_info: bool = False,
    log_requests: bool = False,
    log_responses: bool = False,
    log_request_headers: bool = False,
    log_response_headers: bool = False,
    log_request_body: bool = False
)
```

**Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `level` | [`LogLevel`](#loglevel) | Log level to use | `LogLevel.INFO` |
| `format` | [`LogFormat`](#logformat) | Log format to use | `LogFormat.PLAIN` |
| `enable_console` | `bool` | Log to console | `True` |
| `enable_file` | `bool` | Log to file | `False` |
| `log_file_path` | `str \| Path \| None` | Path to log file | `None` |
| `include_timestamp` | `bool` | Include timestamp | `True` |
| `include_level` | `bool` | Include log level | `True` |
| `include_logger_name` | `bool` | Include logger name | `True` |
| `include_thread_info` | `bool` | Include thread info | `False` |
| `include_process_info` | `bool` | Include process info | `False` |
| `log_requests` | `bool` | Log HTTP requests | `False` |
| `log_responses` | `bool` | Log HTTP responses | `False` |
| `log_request_headers` | `bool` | Log request headers | `False` |
| `log_response_headers` | `bool` | Log response headers | `False` |
| `log_request_body` | `bool` | Log request body | `False` |

---

### LogLevel

Log levels supported by Vi SDK.

```python
from vi.logging.config import LogLevel
```

| Value | Description |
|-------|-------------|
| `CRITICAL` | Critical errors only |
| `ERROR` | Errors and above |
| `WARNING` | Warnings and above |
| `INFO` | Informational messages and above |
| `DEBUG` | Debug messages and above |
| `NOTSET` | No filtering |

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `level_int` | `int` | Integer value for the log level |

---

### LogFormat

Log formats supported by Vi SDK.

```python
from vi.logging.config import LogFormat
```

| Value | Description |
|-------|-------------|
| `JSON` | Structured JSON output |
| `PLAIN` | Simple text output |
| `PRETTY` | Colored, formatted output |

---

## Examples

### Working with Metadata

```python
from datetime import datetime

# Access creation time
dataset = client.datasets.get("dataset_abc123")
created = datetime.fromtimestamp(dataset.metadata.time_created / 1000)
print(f"Created: {created}")
```

### Checking Resource Conditions

```python
from vi.api.resources.runs.responses import Run

def get_run_status(run: Run) -> str:
    """Get the latest status of a run."""
    if not run.status.conditions:
        return "Unknown"

    latest = run.status.conditions[-1]
    return f"{latest.condition.value} ({latest.status.value})"

run = client.runs.get("run_abc123")
print(f"Status: {get_run_status(run)}")
```

### Configuring Logging

```python
from vi.logging.config import LoggingConfig, LogLevel, LogFormat

# Debug logging with JSON format
config = LoggingConfig(
    level=LogLevel.DEBUG,
    format=LogFormat.JSON,
    log_requests=True,
    log_responses=True
)

import vi
vi.configure_logging(config)
```

### Working with Users

```python
org = client.organizations.get()

# Find users with specific role
admins = [
    user_id for user_id, user in org.users.items()
    if user.workspace_role == "admin"
]

print(f"Admin users: {admins}")
```

---

## Type Imports Summary

```python
# Base types
from vi.api.types import ViStruct, QueryParamsMixin

# Response types
from vi.api.responses import (
    ViResponse,
    ResourceMetadata,
    ResourceCondition,
    User,
    DeletedResource,
    Pagination,
    Condition,
    ConditionStatus,
)

# Logging types
from vi.logging.config import (
    LoggingConfig,
    LogLevel,
    LogFormat,
)
```

---

## See Also

- [Pagination API](vi-sdk-pagination) - Pagination types
- [Client API](vi-sdk-client) - Client configuration
- [Logging Guide](vi-sdk-logging) - Logging configuration
- [Error Handling](vi-sdk-errors) - Error types

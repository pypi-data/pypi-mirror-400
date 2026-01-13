---
title: "Configuration"
excerpt: "Configure Vi SDK logging, timeouts, and other settings"
category: "getting-started"
---

# Configuration

Configure Vi SDK to match your requirements with logging, timeouts, and other settings.

---

## Overview

Vi SDK provides several configuration options:

- **Logging**: Structured logging with JSON, plain text, or pretty-printed formats
- **HTTP Client**: Timeout settings, retry behavior
- **Performance**: Connection pooling, concurrent operations
- **Dataset Loaders**: Data loading options

---

## Logging Configuration

Vi SDK includes comprehensive structured logging capabilities.

### Basic Logging Setup

```python
import vi
from vi.logging import LoggingConfig, LogLevel, LogFormat

# Create logging configuration
logging_config = LoggingConfig(
    level=LogLevel.INFO,
    format=LogFormat.JSON,
    enable_console=True,
    enable_file=True
)

# Initialize client with logging
client = vi.Client(
    secret_key="your-secret-key",
    organization_id="your-organization-id",
    logging_config=logging_config
)
```

### Log Levels

Available log levels (from most to least verbose):

```python
from vi.logging import LogLevel

LogLevel.DEBUG      # Detailed information for debugging
LogLevel.INFO       # General informational messages
LogLevel.WARNING    # Warning messages
LogLevel.ERROR      # Error messages
LogLevel.CRITICAL   # Critical errors
```

---

## Log Formats

### JSON (Structured)

```python
from vi.logging import LogFormat

logging_config = LoggingConfig(
    format=LogFormat.JSON
)
```

Output:

```json
{
  "timestamp": "2025-10-01T10:30:45.123Z",
  "level": "INFO",
  "logger": "api.client",
  "message": "Initializing Vi SDK client",
  "endpoint": "https://api.vi.datature.com",
  "has_secret_key": true
}
```

### Plain Text

```python
logging_config = LoggingConfig(
    format=LogFormat.PLAIN
)
```

Output:

```
2025-10-01 10:30:45,123 - INFO - api.client - Initializing Vi SDK client
```

### Pretty (Development)

```python
logging_config = LoggingConfig(
    format=LogFormat.PRETTY
)
```

Output:

```json
{
  "timestamp": "2025-10-01T10:30:45.123Z",
  "level": "INFO",
  "logger": "api.client",
  "message": "Initializing Vi SDK client",
  "endpoint": "https://api.vi.datature.com"
}
```

---

## Logging Output Destinations

Control where logs are written:

```python
logging_config = LoggingConfig(
    enable_console=True,   # Print to console
    enable_file=True,      # Write to file
    log_file_path=None     # Auto-generate path, or specify custom
)
```

Auto-generated log files are stored in:

- **Linux/macOS**: `~/.datature/vi/logs/YYYYMMDD_HHMMSS_mmm.log`
- **Windows**: `%USERPROFILE%\.datature\vi\logs\YYYYMMDD_HHMMSS_mmm.log`

---

## Logging HTTP Requests and Responses

Configure what to log for HTTP operations:

```python
logging_config = LoggingConfig(
    log_requests=True,           # Log outgoing requests
    log_responses=True,          # Log incoming responses
    log_request_headers=False,   # Don't log auth tokens
    log_response_headers=False,
    log_request_body=False,      # Can contain sensitive data
    log_response_body=False,     # Can be large
    max_request_body_size=1024,  # Limit logged body size (bytes)
    max_response_body_size=1024
)
```

> ⚠️ **Security Warning**
>
> Avoid logging request headers and bodies in production, as they may contain sensitive data like API keys.

---

## Environment-Based Configuration

Override configuration via environment variables:

```bash
# Log level
export VI_LOG_LEVEL=DEBUG

# Log format
export VI_LOG_FORMAT=json

# Enable/disable outputs
export VI_ENABLE_CONSOLE=true
export VI_ENABLE_FILE=true

# HTTP logging
export VI_LOG_REQUESTS=true
export VI_LOG_RESPONSES=false

# Custom log file
export VI_LOG_FILE=/var/log/vi.log
```

Then use default configuration:

```python
import vi

# Automatically uses environment variables
client = vi.Client(
    secret_key="your-secret-key",
    organization_id="your-organization-id"
)
```

---

## Complete Logging Example

```python
from vi import Client
from vi.logging import LoggingConfig, LogLevel, LogFormat

# Production configuration
prod_logging = LoggingConfig(
    level=LogLevel.WARNING,
    format=LogFormat.JSON,
    enable_console=False,
    enable_file=True,
    log_file_path="/var/log/vi-prod.log",
    log_requests=True,
    log_responses=False,
    log_request_headers=False,
    log_response_headers=False
)

# Development configuration
dev_logging = LoggingConfig(
    level=LogLevel.DEBUG,
    format=LogFormat.PRETTY,
    enable_console=True,
    enable_file=True,
    log_requests=True,
    log_responses=True,
    log_request_body=True,
    log_response_body=True,
    max_request_body_size=4096,
    max_response_body_size=4096
)

# Use appropriate configuration
import os
env = os.getenv("ENVIRONMENT", "development")
logging_config = prod_logging if env == "production" else dev_logging

client = Client(
    secret_key="your-secret-key",
    organization_id="your-organization-id",
    logging_config=logging_config
)
```

---

## HTTP Client Configuration

### Timeout Settings

Configure request timeouts:

```python
from vi.client.http.requester import Requester
from httpx import Timeout

# Custom timeout configuration
timeout = Timeout(
    connect=10.0,  # Connection timeout (seconds)
    read=30.0,     # Read timeout (seconds)
    write=30.0,    # Write timeout (seconds)
    pool=5.0       # Pool timeout (seconds)
)

# Create client with custom timeout
from vi.client.auth import SecretKeyAuth

auth = SecretKeyAuth(
    secret_key="your-secret-key",
    organization_id="your-organization-id"
)

requester = Requester(
    auth=auth,
    base_url="https://api.vi.datature.com",
    timeout=timeout
)

client = Client(requester)
```

### Retry Configuration

Control retry behavior for failed requests:

```python
requester = Requester(
    auth=auth,
    base_url="https://api.vi.datature.com",
    max_retries=3  # Retry up to 3 times
)
```

Default retry behavior:

- **Retryable errors**: Network errors, timeouts, 5xx server errors
- **Non-retryable errors**: 4xx client errors (except 429 rate limit)
- **Backoff strategy**: Exponential backoff with jitter

### Connection Pooling

Connection pooling is automatically configured for optimal performance:

- Upload operations: 8-32 concurrent connections (CPU-dependent)
- Download operations: 8-64 concurrent connections (CPU-dependent)

---

## Performance Tuning

### Concurrent Operations

Control parallelism for upload/download:

```python
# Uploads and downloads automatically use optimal concurrency
# based on CPU count: min(max((cpu_count or 4) * 2, 8), 32/64)

# Upload with progress tracking
# Large folders are automatically batched
result = client.assets.upload(
    dataset_id="your-dataset-id",
    paths="path/to/large/folder/",
    wait_until_done=True
)
print(f"✓ Uploaded: {result.total_succeeded} assets")
# Returns list of sessions (one per batch)
```

### Memory Management

For large dataset operations:

```python
from vi.dataset.loaders import ViDataset

# Load dataset (lazy loading - doesn't load all data into memory)
dataset = ViDataset("./data/large-dataset")

# Iterate efficiently
for asset, annotations in dataset.training.iter_pairs():
    # Process one pair at a time
    # Assets are loaded on-demand, not all at once
    process(asset, annotations)
```

### Progress Tracking

Control progress bar visibility:

```python
# Download with progress
dataset = client.get_dataset(
    dataset_id="your-dataset-id",
    save_dir="./data",
    show_progress=True  # Show progress bars (default)
)

# Download without progress (for scripts/CI)
dataset = client.get_dataset(
    dataset_id="your-dataset-id",
    save_dir="./data",
    show_progress=False  # No progress bars
)
```

---

## Dataset Loader Configuration

### Split Configuration

Customize how dataset splits are loaded:

```python
from vi.dataset.loaders import ViDataset

# Load specific splits
dataset = ViDataset("./data/dataset-id")

# Access only training data
for asset, annotations in dataset.training.iter_pairs():
    train_model(asset, annotations)

# Access only validation data
for asset, annotations in dataset.validation.iter_pairs():
    validate_model(asset, annotations)

# Access dump (all data)
for asset, annotations in dataset.dump.iter_pairs():
    process_all_data(asset, annotations)
```

### Visualization Configuration

Configure visualization output:

```python
from PIL import Image

# Visualize with default settings
for visualized_image in dataset.training.visualize():
    visualized_image.show()

# Or save to disk
for i, visualized_image in enumerate(dataset.training.visualize()):
    visualized_image.save(f"visualization_{i}.png")
```

---

## Configuration Best Practices

### 1. Environment-Specific Configuration

Use different configurations for different environments:

```python
import os
from vi import Client
from vi.logging import LoggingConfig, LogLevel, LogFormat

def get_client():
    env = os.getenv("ENVIRONMENT", "development")

    if env == "production":
        logging_config = LoggingConfig(
            level=LogLevel.WARNING,
            format=LogFormat.JSON,
            enable_console=False,
            enable_file=True,
            log_requests=False,
            log_responses=False
        )
    elif env == "staging":
        logging_config = LoggingConfig(
            level=LogLevel.INFO,
            format=LogFormat.JSON,
            enable_console=True,
            enable_file=True,
            log_requests=True
        )
    else:  # development
        logging_config = LoggingConfig(
            level=LogLevel.DEBUG,
            format=LogFormat.PRETTY,
            enable_console=True,
            enable_file=True,
            log_requests=True,
            log_responses=True
        )

    return Client(
        secret_key=os.getenv("DATATURE_VI_SECRET_KEY"),
        organization_id=os.getenv("DATATURE_VI_ORGANIZATION_ID"),
        logging_config=logging_config
    )

client = get_client()
```

### 2. Centralized Configuration

Create a configuration module:

```python
# config.py
import os
from vi.logging import LoggingConfig, LogLevel, LogFormat

# Base configuration
BASE_CONFIG = {
    "endpoint": os.getenv(
        "VI_ENDPOINT",
        "https://api.vi.datature.com"
    )
}

# Logging configurations
LOGGING_CONFIGS = {
    "production": LoggingConfig(
        level=LogLevel.WARNING,
        format=LogFormat.JSON,
        enable_console=False,
        enable_file=True
    ),
    "development": LoggingConfig(
        level=LogLevel.DEBUG,
        format=LogFormat.PRETTY,
        enable_console=True,
        enable_file=True,
        log_requests=True,
        log_responses=True
    )
}

def get_logging_config(env=None):
    env = env or os.getenv("ENVIRONMENT", "development")
    return LOGGING_CONFIGS.get(env, LOGGING_CONFIGS["development"])
```

Then use it:

```python
# main.py
import vi
from config import get_logging_config

client = vi.Client(
    secret_key="your-secret-key",
    organization_id="your-organization-id",
    logging_config=get_logging_config()
)
```

### 3. Configuration Validation

Validate configuration on startup:

```python
import vi
from vi import ViConfigurationError

def create_validated_client(secret_key, organization_id, logging_config=None):
    """Create client with validation."""
    if not secret_key:
        raise ViConfigurationError("Secret key is required")

    if not organization_id:
        raise ViConfigurationError("Organization ID is required")

    try:
        client = vi.Client(
            secret_key=secret_key,
            organization_id=organization_id,
            logging_config=logging_config
        )

        # Test connection
        client.organizations.info()

        return client
    except Exception as e:
        raise ViConfigurationError(f"Failed to initialize client: {e}")
```

---

## Configuration Summary

| Category | Options | Default |
|----------|---------|---------|
| **Log Level** | DEBUG, INFO, WARNING, ERROR, CRITICAL | INFO |
| **Log Format** | JSON, PLAIN, PRETTY | JSON |
| **Console Output** | true, false | false |
| **File Output** | true, false | true |
| **Request Logging** | true, false | true |
| **Response Logging** | true, false | false |
| **Connect Timeout** | seconds | 10.0 |
| **Read/Write Timeout** | seconds | 60.0 |
| **Max Retries** | integer | 3 |

---

## Next Steps

- **[User Guide](vi-sdk-overview)** - Learn about core features and operations
- **[Error Handling](vi-sdk-error-handling)** - Handle errors and exceptions effectively
- **[Logging Guide](vi-sdk-logging)** - Deep dive into structured logging

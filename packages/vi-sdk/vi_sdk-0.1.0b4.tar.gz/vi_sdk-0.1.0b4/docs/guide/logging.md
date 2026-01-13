# Logging

Learn how to configure and use the Vi SDK's structured logging system.

## Overview

The Vi SDK provides a comprehensive logging system with:

- Multiple output formats (JSON, plain text, pretty JSON)
- Configurable log levels
- File and console output
- Request/response logging
- Structured log fields
- Environment variable configuration
- Performance monitoring

## Quick Start

```python
from vi import Client
from vi.logging import LoggingConfig, LogLevel

# Configure logging
logging_config = LoggingConfig(
    level=LogLevel.INFO,
    enable_console=True,
    enable_file=True
)

# Create client with logging
client = Client(
    secret_key="...",
    organization_id="...",
    logging_config=logging_config
)
```

## Log Levels

Available log levels (from most to least verbose):

- `DEBUG`: Detailed diagnostic information
- `INFO`: General informational messages
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical error messages

```python
from vi.logging import LogLevel

# Different log levels
configs = {
    "development": LoggingConfig(level=LogLevel.DEBUG),
    "production": LoggingConfig(level=LogLevel.INFO),
    "critical_only": LoggingConfig(level=LogLevel.CRITICAL)
}
```

## Log Formats

### JSON Format

Structured logs in JSON format (best for log aggregation):

```python
from vi.logging import LogFormat

config = LoggingConfig(
    format=LogFormat.JSON,
    enable_file=True,
    log_file_path="logs/app.jsonl"
)

client = Client(logging_config=config)
```

Example output:

```json
{
  "timestamp": "2025-10-01T10:30:45.123Z",
  "level": "INFO",
  "logger": "api.client",
  "message": "Dataset download complete",
  "dataset_id": "dataset_abc123",
  "elapsed_time": 45.2
}
```

### Plain Text Format

Simple readable format:

```python
config = LoggingConfig(
    format=LogFormat.PLAIN,
    enable_console=True
)
```

Example output:

```
2025-10-01 10:30:45 [INFO] api.client: Dataset download complete (dataset_id=dataset_abc123, elapsed_time=45.2)
```

### Pretty Format

Colorized, human-readable format (best for development):

```python
config = LoggingConfig(
    format=LogFormat.PRETTY,
    enable_console=True
)
```

## Output Destinations

### Console Output

```python
# Log to console
config = LoggingConfig(
    enable_console=True,
    enable_file=False  # Console only
)
```

### File Output

```python
# Log to file
config = LoggingConfig(
    enable_console=False,
    enable_file=True,
    log_file_path="logs/app.log"
)
```

### Both Console and File

```python
# Log to both
config = LoggingConfig(
    enable_console=True,
    enable_file=True,
    log_file_path="logs/app.log"
)
```

### Custom Log File Path

```python
from pathlib import Path

# Custom log directory
log_dir = Path("./my_logs")
log_dir.mkdir(exist_ok=True)

config = LoggingConfig(
    enable_file=True,
    log_file_path=str(log_dir / "vi_sdk.jsonl")
)
```

### Auto-Generated Log Files

```python
# Auto-generate timestamped log files
config = LoggingConfig(
    enable_file=True,
    log_file_path=None  # Will create ~/.datature/vi/logs/run_TIMESTAMP.jsonl
)
```

## Log Fields

### Include Metadata

```python
config = LoggingConfig(
    include_timestamp=True,  # Include timestamp
    include_level=True,  # Include log level
    include_logger_name=True,  # Include logger name
    include_thread_info=True,  # Include thread ID and name
    include_process_info=True,  # Include process ID and name
)
```

### Extra Fields

Add custom fields to all log entries:

```python
config = LoggingConfig(
    extra_fields={
        "app_name": "my_app",
        "environment": "production",
        "version": "1.0.0",
        "user_id": "user_123"
    }
)
```

Example log with extra fields:

```json
{
  "timestamp": "2025-10-01T10:30:45.123Z",
  "level": "INFO",
  "message": "Request completed",
  "app_name": "my_app",
  "environment": "production",
  "version": "1.0.0",
  "user_id": "user_123"
}
```

## HTTP Request/Response Logging

### Log Requests

```python
config = LoggingConfig(
    log_requests=True,  # Log outgoing requests
    log_request_headers=True,  # Include headers
    log_request_body=True,  # Include body
    max_request_body_size=1024  # Max body size to log (bytes)
)
```

### Log Responses

```python
config = LoggingConfig(
    log_responses=True,  # Log incoming responses
    log_response_headers=True,  # Include headers
    log_response_body=True,  # Include body (can be large!)
    max_response_body_size=2048  # Max body size to log
)
```

### Complete HTTP Logging

```python
# Full HTTP traffic logging
config = LoggingConfig(
    level=LogLevel.DEBUG,
    log_requests=True,
    log_responses=True,
    log_request_headers=True,
    log_response_headers=True,
    log_request_body=True,
    log_response_body=False,  # Usually too large
    max_request_body_size=10240,  # 10KB
    enable_file=True
)
```

## Environment Variable Configuration

Override configuration with environment variables:

```bash
# Log level
export VI_LOG_LEVEL=DEBUG

# Output destinations
export VI_LOG_ENABLE_CONSOLE=true
export VI_LOG_ENABLE_FILE=true

# Format
export VI_LOG_FORMAT=json

# Custom log file
export VI_LOG_FILE_PATH=/var/log/vi_sdk.log

# HTTP logging
export VI_LOG_REQUESTS=true
export VI_LOG_RESPONSES=false

# Body size limits
export VI_LOG_MAX_REQUEST_BODY_SIZE=5120
export VI_LOG_MAX_RESPONSE_BODY_SIZE=10240
```

### Respect Environment Variables

```python
# Allow environment variables to override config
config = LoggingConfig(
    level=LogLevel.INFO,  # Default
    respect_environment=True  # Environment vars can override
)

# Environment variable VI_LOG_LEVEL=DEBUG will override INFO
client = Client(logging_config=config)
```

## Advanced Configuration

### Log Rotation

```python
config = LoggingConfig(
    enable_file=True,
    log_file_path="logs/app.log",
    max_log_size=10 * 1024 * 1024,  # 10 MB
    # Logs will rotate when reaching max_log_size
)
```

### Different Configs for Different Environments

```python
import os

def get_logging_config():
    """Get logging config based on environment."""
    env = os.getenv("ENVIRONMENT", "development")

    if env == "production":
        return LoggingConfig(
            level=LogLevel.INFO,
            format=LogFormat.JSON,
            enable_console=False,
            enable_file=True,
            log_requests=False,
            log_responses=False
        )
    elif env == "staging":
        return LoggingConfig(
            level=LogLevel.DEBUG,
            format=LogFormat.JSON,
            enable_console=True,
            enable_file=True,
            log_requests=True,
            log_responses=False
        )
    else:  # development
        return LoggingConfig(
            level=LogLevel.DEBUG,
            format=LogFormat.PRETTY,
            enable_console=True,
            enable_file=False,
            log_requests=True,
            log_responses=True
        )

# Usage
config = get_logging_config()
client = Client(logging_config=config)
```

## Using the Logger Directly

### Get Logger Instance

```python
from vi.logging import get_logger

# Get logger
logger = get_logger("my_component")

# Log messages
logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical error")
```

### Log with Context

```python
# Add context fields
logger.info(
    "Processing dataset",
    dataset_id="dataset_abc123",
    asset_count=1000,
    elapsed_time=45.2
)
```

Output:

```json
{
  "timestamp": "2025-10-01T10:30:45.123Z",
  "level": "INFO",
  "logger": "my_component",
  "message": "Processing dataset",
  "dataset_id": "dataset_abc123",
  "asset_count": 1000,
  "elapsed_time": 45.2
}
```

### Log Exceptions

```python
try:
    # Some operation
    risky_operation()
except Exception as e:
    logger.error(
        "Operation failed",
        error=str(e),
        error_type=type(e).__name__,
        exc_info=True  # Include traceback
    )
```

## Integration with Standard Logging

### Bridge to Python Logging

```python
import logging

# Get Vi logger
vi_logger = get_logger("vi.operations")

# Use with standard logging
python_logger = logging.getLogger("my_app")
python_logger.setLevel(logging.INFO)

# Log to both
vi_logger.info("Vi SDK operation")
python_logger.info("Application operation")
```

### Forward to External Systems

```python
import logging
from logging.handlers import SysLogHandler

# Add syslog handler
syslog_handler = SysLogHandler(address=('localhost', 514))
logging.getLogger().addHandler(syslog_handler)

# Vi SDK logs will also go to syslog
client = Client(logging_config=LoggingConfig(level=LogLevel.INFO))
```

## Best Practices

### 1. Use Appropriate Log Levels

```python
# ✅ Good - appropriate levels
logger.debug("Detailed internal state")  # Development only
logger.info("Request completed successfully")  # Normal operations
logger.warning("Retrying after timeout")  # Recoverable issues
logger.error("Failed to process request")  # Errors requiring attention
logger.critical("Database connection lost")  # Critical failures

# ❌ Bad - wrong levels
logger.info("Variable x = 123")  # Too detailed, use DEBUG
logger.error("Request completed")  # Not an error, use INFO
```

### 2. Structure Your Log Messages

```python
# ✅ Good - structured with context
logger.info(
    "Dataset downloaded",
    dataset_id=dataset_id,
    size_mb=file_size / 1024 / 1024,
    duration_seconds=elapsed_time
)

# ❌ Bad - unstructured string
logger.info(f"Downloaded dataset {dataset_id}, size {file_size}, took {elapsed_time}s")
```

### 3. Don't Log Sensitive Data

```python
# ✅ Good - mask sensitive data
logger.info(
    "Authentication successful",
    user_id=user_id,
    api_key="****" + api_key[-4:]  # Only last 4 chars
)

# ❌ Bad - logging secrets
logger.info(f"Authenticated with key: {api_key}")  # NEVER!
```

### 4. Use Appropriate Output for Environment

```python
# Production: JSON to file
production_config = LoggingConfig(
    level=LogLevel.INFO,
    format=LogFormat.JSON,
    enable_console=False,
    enable_file=True
)

# Development: Pretty to console
dev_config = LoggingConfig(
    level=LogLevel.DEBUG,
    format=LogFormat.PRETTY,
    enable_console=True,
    enable_file=False
)
```

### 5. Monitor Performance Impact

```python
# Minimize performance impact in production
config = LoggingConfig(
    level=LogLevel.INFO,  # Not DEBUG
    log_requests=False,  # Disabled
    log_responses=False,  # Disabled
    log_request_body=False,  # Disabled
    log_response_body=False  # Disabled
)
```

## Common Workflows

### Debug Request/Response Cycle

```python
# Enable detailed HTTP logging
debug_config = LoggingConfig(
    level=LogLevel.DEBUG,
    format=LogFormat.PRETTY,
    enable_console=True,
    log_requests=True,
    log_responses=True,
    log_request_headers=True,
    log_response_headers=True,
    log_request_body=True,
    max_request_body_size=10240
)

client = Client(logging_config=debug_config)

# Perform operation - all HTTP details will be logged
dataset = client.datasets.get("dataset_id")
```

### Centralized Logging

```python
# Configure for log aggregation system
config = LoggingConfig(
    level=LogLevel.INFO,
    format=LogFormat.JSON,  # Structured for parsing
    enable_file=True,
    log_file_path="/var/log/vi_sdk/app.jsonl",
    extra_fields={
        "service": "vi_sdk_client",
        "environment": os.getenv("ENV", "production"),
        "host": socket.gethostname()
    }
)
```

### Performance Monitoring

```python
import time

logger = get_logger("performance")

def monitored_operation():
    """Operation with performance monitoring."""
    start_time = time.time()

    try:
        # Your operation
        result = expensive_operation()

        # Log success metrics
        elapsed = time.time() - start_time
        logger.info(
            "Operation completed",
            duration_seconds=elapsed,
            status="success"
        )

        return result

    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(
            "Operation failed",
            duration_seconds=elapsed,
            status="error",
            error=str(e)
        )
        raise
```

## Troubleshooting

### Logs Not Appearing

```python
# Check configuration
config = LoggingConfig(
    level=LogLevel.DEBUG,  # Lower log level
    enable_console=True,  # Enable console
    enable_file=True  # Enable file
)

# Verify logger is configured
logger = get_logger("test")
logger.info("Test message")
```

### Log File Not Created

```python
from pathlib import Path

# Ensure directory exists
log_dir = Path("./logs")
log_dir.mkdir(parents=True, exist_ok=True)

config = LoggingConfig(
    enable_file=True,
    log_file_path=str(log_dir / "app.log")
)
```

### Too Many Logs

```python
# Reduce log level
config = LoggingConfig(
    level=LogLevel.WARNING,  # Only warnings and above
    log_requests=False,  # Disable request logging
    log_responses=False  # Disable response logging
)
```

### Parse JSON Logs

```python
import json

# Read JSON log file
with open("logs/app.jsonl") as f:
    for line in f:
        log_entry = json.loads(line)
        if log_entry["level"] == "ERROR":
            print(f"Error: {log_entry['message']}")
```

## See Also

- [Configuration Guide](../getting-started/configuration.md) - General configuration
- [Error Handling Guide](error-handling.md) - Logging errors
- [API Reference](../api/client.md) - Client logging options

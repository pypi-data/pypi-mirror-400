# Resource Management

The Vi SDK implements proper resource management patterns to ensure HTTP connections and other resources are properly released when no longer needed. This guide covers best practices for managing client lifecycle.

## Context Manager Support

The Vi SDK client implements the Python context manager protocol (`__enter__` and `__exit__`), enabling automatic resource cleanup using the `with` statement.

### Basic Usage (Recommended)

Always use the context manager pattern for automatic cleanup:

```python
import vi

# Recommended: Automatic cleanup with context manager
with vi.Client(
    secret_key="your-secret-key",
    organization_id="your-org-id"
) as client:
    datasets = client.datasets.list()
    # Use client for all operations
    # Resources automatically cleaned up on exit
```

### Manual Cleanup

If you cannot use a context manager, ensure you manually call `close()`:

```python
import vi

client = vi.Client(
    secret_key="your-secret-key",
    organization_id="your-org-id"
)

try:
    datasets = client.datasets.list()
    # Perform operations
finally:
    client.close()  # Ensure cleanup
```

## Resource Lifecycle

### Client States

The client has two states:

1. **Open**: Client is active and can make API requests
2. **Closed**: Client is closed and resources are released

Check the state using the `is_closed` property:

```python
client = vi.Client(secret_key="...", organization_id="...")

print(client.is_closed)  # False

client.close()
print(client.is_closed)  # True
```

### Idempotent Close

The `close()` method is idempotent and can be called multiple times safely:

```python
client = vi.Client(secret_key="...", organization_id="...")

client.close()  # First close
client.close()  # Safe - no-op
client.close()  # Still safe - no-op
```

### Preventing Reuse of Closed Clients

Attempting to use a closed client in a context manager raises a `RuntimeError`:

```python
client = vi.Client(secret_key="...", organization_id="...")
client.close()

try:
    with client:  # ❌ Error
        pass
except RuntimeError as e:
    print(e)  # "Cannot use closed client in context manager"
```

## Exception Handling

Context managers ensure cleanup even when exceptions occur:

```python
try:
    with vi.Client(secret_key="...", organization_id="...") as client:
        datasets = client.datasets.list()
        if not datasets.items:
            raise ValueError("No datasets found")
except ValueError as e:
    print(e)
    # Client is still properly closed
```

## Connection Pool Configuration

For high-concurrency workloads, configure the connection pool:

```python
with vi.Client(
    secret_key="...",
    organization_id="...",
    max_connections=200,              # Max concurrent connections
    max_keepalive_connections=50,     # Keep-alive pool size
) as client:
    # Optimized for high throughput
    datasets = client.datasets.list()
```

### Connection Pool Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_connections` | 100 | Maximum number of concurrent HTTP connections |
| `max_keepalive_connections` | 20 | Maximum keep-alive connections in pool |

**When to adjust:**

- **Increase `max_connections`**: For high-concurrency applications making many parallel requests
- **Increase `max_keepalive_connections`**: For applications making frequent sequential requests to improve performance

## Best Practices

### ✅ DO: Use Context Managers

```python
# ✅ Best practice
with vi.Client(secret_key="...", organization_id="...") as client:
    datasets = client.datasets.list()
```

### ✅ DO: Use try/finally for Manual Cleanup

```python
# ✅ Good for non-context manager scenarios
client = vi.Client(secret_key="...", organization_id="...")
try:
    datasets = client.datasets.list()
finally:
    client.close()
```

### ✅ DO: Create New Client for Each Session

```python
# ✅ Each operation gets fresh client
def process_data():
    with vi.Client(secret_key="...", organization_id="...") as client:
        return client.datasets.list()
```

### ❌ DON'T: Reuse Closed Clients

```python
# ❌ Bad - Don't reuse closed clients
client = vi.Client(secret_key="...", organization_id="...")
client.close()
datasets = client.datasets.list()  # Error!
```

### ❌ DON'T: Forget to Close

```python
# ❌ Bad - Resources may leak
client = vi.Client(secret_key="...", organization_id="...")
datasets = client.datasets.list()
# No close() call - resources not released
```

### ❌ DON'T: Store Client Globally

```python
# ❌ Bad - Long-lived clients
GLOBAL_CLIENT = vi.Client(secret_key="...", organization_id="...")

def my_function():
    return GLOBAL_CLIENT.datasets.list()  # Risky

# Better: Create client per operation
def my_function():
    with vi.Client(secret_key="...", organization_id="...") as client:
        return client.datasets.list()
```

## Advanced Patterns

### Multiple Operations in Single Context

```python
with vi.Client(secret_key="...", organization_id="...") as client:
    # Perform multiple operations
    datasets = client.datasets.list()

    for dataset in datasets.items:
        assets = client.assets.list(dataset.dataset_id)
        annotations = client.annotations.list(
            dataset.dataset_id, asset_id=asset.asset_id
        )

    runs = client.runs.list()
    # All operations share same connection pool
    # Automatic cleanup after block
```

### Nested Context Managers

```python
# Each client manages its own resources
with vi.Client(secret_key="...", organization_id="...") as client1:
    datasets1 = client1.datasets.list()

    with vi.Client(secret_key="...", organization_id="...") as client2:
        datasets2 = client2.datasets.list()
        # Both clients active

    # client2 closed, client1 still active
```

### Custom Logging with Resource Management

```python
from vi.logging import LoggingConfig, LogLevel

logging_config = LoggingConfig(
    level=LogLevel.DEBUG,
    enable_console=True
)

with vi.Client(
    secret_key="...",
    organization_id="...",
    logging_config=logging_config
) as client:
    # Detailed logs show resource lifecycle
    datasets = client.datasets.list()
    # Logs will show:
    # - Client initialization
    # - Connection pool setup
    # - Request lifecycle
    # - Resource cleanup
```

## Performance Considerations

### Connection Reuse

The SDK uses connection pooling to reuse HTTP connections for better performance:

```python
with vi.Client(secret_key="...", organization_id="...") as client:
    # First request establishes connection
    datasets = client.datasets.list()

    # Subsequent requests reuse connection (faster)
    dataset_id = datasets.items[0].dataset_id
    assets = client.assets.list(dataset_id)
    asset_id = assets.items[0].asset_id
    annotations = client.annotations.list(dataset_id, asset_id)
```

### Short-Lived vs Long-Lived Clients

**Short-lived (Recommended for most cases):**

```python
def process_dataset(dataset_id):
    with vi.Client(secret_key="...", organization_id="...") as client:
        return client.datasets.get(dataset_id)

# Each call gets fresh client
for dataset_id in dataset_ids:
    process_dataset(dataset_id)
```

**Long-lived (For high-throughput scenarios):**

```python
with vi.Client(
    secret_key="...",
    organization_id="...",
    max_connections=200,
    max_keepalive_connections=50
) as client:
    # Process many items with same client
    for dataset_id in dataset_ids:
        dataset = client.datasets.get(dataset_id)
        process(dataset)
```

## Troubleshooting

### Client Already Closed Error

**Problem:** Attempting to use a closed client

```python
client = vi.Client(secret_key="...", organization_id="...")
client.close()
datasets = client.datasets.list()  # RuntimeError
```

**Solution:** Create a new client instance

```python
client = vi.Client(secret_key="...", organization_id="...")
datasets = client.datasets.list()
```

### Resource Leaks

**Problem:** Not closing clients in long-running applications

```python
# ❌ Leaks resources
for _ in range(1000):
    client = vi.Client(secret_key="...", organization_id="...")
    client.datasets.list()
    # No close() call
```

**Solution:** Always use context managers

```python
# ✅ Proper cleanup
for _ in range(1000):
    with vi.Client(secret_key="...", organization_id="...") as client:
        client.datasets.list()
```

### Connection Pool Exhaustion

**Problem:** Too many concurrent requests with default settings

```python
# May exhaust connection pool
with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
    futures = [executor.submit(make_request) for _ in range(200)]
```

**Solution:** Increase connection pool size

```python
with vi.Client(
    secret_key="...",
    organization_id="...",
    max_connections=250,  # Accommodate concurrent requests
) as client:
    with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
        futures = [executor.submit(make_request, client) for _ in range(200)]
```

## See Also

- [Client API Reference](../api/client.md): Complete client documentation
- [Configuration Guide](../getting-started/configuration.md): Client configuration options
- [Error Handling](error-handling.md): Handling errors and exceptions
- [Examples](../examples/index.md): Practical usage examples

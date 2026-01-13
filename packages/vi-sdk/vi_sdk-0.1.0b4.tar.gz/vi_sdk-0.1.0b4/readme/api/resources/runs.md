---
title: "Runs API Reference"
excerpt: "Manage training runs and their configurations"
category: "api-reference"
---

# Runs API Reference

Complete API reference for training run operations. List and manage training runs.

---

## Run Resource

Access runs through `client.runs`.

---

## Methods

### list()

List all training runs.

```python
# Basic listing
runs = client.runs.list()

for run in runs.items:
    print(f"Run: {run.run_id}")
    print(f"Created: {run.metadata.time_created}")
```

```python
# With custom pagination
from vi.api.types import PaginationParams

runs = client.runs.list(pagination=PaginationParams(page_size=50))

for run in runs.items:
    print(f"{run.run_id}")
```

```python
# Using dict for pagination
runs = client.runs.list(pagination={"page_size": 50})
```

```python
# Iterate all pages with status
for page in client.runs.list():
    for run in page.items:
        status = "Unknown"
        if run.status.conditions:
            status = run.status.conditions[-1].condition.value
        print(f"{run.run_id}: {status}")
```

```python
# Find completed runs
completed_runs = []

for page in client.runs.list():
    for run in page.items:
        if run.status.conditions:
            latest = run.status.conditions[-1]
            if latest.condition.value == "Succeeded":
                completed_runs.append(run)

print(f"Found {len(completed_runs)} completed runs")
```

```python
# Collect all runs
all_runs = list(client.runs.list().all_items())
print(f"Total runs: {len(all_runs)}")
```

**Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `pagination` | [`PaginationParams`](vi-sdk-pagination#paginationparams)` \| dict` | Pagination settings | `PaginationParams()` |

**Returns:** [`PaginatedResponse`](vi-sdk-pagination#paginatedresponse)`[`[`Run`](#run)`]`

---

### get()

Get a specific run.

```python
# Basic usage
run = client.runs.get("run_abc123")

print(f"Run ID: {run.run_id}")
print(f"Organization: {run.organization_id}")
```

```python
# Check run status
run = client.runs.get("run_abc123")

if run.status.conditions:
    latest = run.status.conditions[-1]
    print(f"Status: {latest.condition.value}")
    print(f"Message: {latest.message}")
```

```python
# Access flow configuration
run = client.runs.get("run_abc123")

print(f"Flow Name: {run.spec.flow.name}")
print(f"Schema: {run.spec.flow.schema}")
print(f"Blocks: {len(run.spec.flow.blocks)}")

if run.spec.training_project:
    print(f"Training Dataset: {run.spec.training_project}")
```

```python
# Display detailed information
run = client.runs.get("run_abc123")
run.info()  # Prints formatted run summary
```

```python
# Wait for run completion
import time

def wait_for_run(run_id: str, max_wait: int = 3600, check_interval: int = 30) -> str:
    """Wait for a run to complete."""
    start_time = time.time()

    while time.time() - start_time < max_wait:
        run = client.runs.get(run_id)

        if run.status.conditions:
            latest = run.status.conditions[-1]
            status = latest.condition.value

            print(f"Status: {status}")

            if status in ["Succeeded", "Failed", "Error", "Cancelled"]:
                return status

        time.sleep(check_interval)

    raise TimeoutError("Run did not complete in time")

status = wait_for_run("run_abc123")
if status == "Succeeded":
    model = client.get_model("run_abc123")
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `run_id` | `str` | Run identifier |

**Returns:** [`Run`](#run)

---

## Response Types

### Run

Main run response object.

```python
from vi.api.resources.runs.responses import Run
```

| Property | Type | Description |
|----------|------|-------------|
| `organization_id` | `str` | Organization ID |
| `run_id` | `str` | Unique identifier |
| `spec` | [`RunSpec`](#runspec) | Run specification |
| `status` | [`RunStatus`](#runstatus) | Run status |
| `metadata` | [`ResourceMetadata`](vi-sdk-types#resourcemetadata) | Metadata |
| `self_link` | `str` | API link |
| `etag` | `str` | Entity tag |

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `info()` | `None` | Display formatted run information |

---

### RunSpec

```python
from vi.api.resources.runs.responses import RunSpec
```

| Property | Type | Description |
|----------|------|-------------|
| `flow` | [`FlowSpec`](vi-sdk-flows-api#flowspec) | Flow specification |
| `killed_at` | `int \| None` | Kill timestamp (if terminated) |
| `training_project` | `str \| None` | Training project/dataset ID |

---

### RunStatus

```python
from vi.api.resources.runs.responses import RunStatus
```

| Property | Type | Description |
|----------|------|-------------|
| `log` | `str` | Log URL or path |
| `observed_generation` | `int` | Observed generation number |
| `conditions` | `list[`[`ResourceCondition`](vi-sdk-types#resourcecondition)`]` | Status conditions |

---

## Condition Values

The `condition` field in [`ResourceCondition`](vi-sdk-types#resourcecondition) can have these values:

| Value | Description |
|-------|-------------|
| `Pending` | Run is pending |
| `Running` | Run is in progress |
| `Succeeded` | Run completed successfully |
| `Failed` | Run failed |
| `Error` | Run encountered an error |
| `Cancelled` | Run was cancelled |

---

## See Also

- [Models Guide](vi-sdk-models) - Working with models
- [Models API](vi-sdk-models-api) - Model operations
- [Flows API](vi-sdk-flows-api) - Flow operations
- [Types API](vi-sdk-types) - Common types
- [Pagination API](vi-sdk-pagination) - Pagination utilities

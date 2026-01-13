---
title: "Flows API Reference"
excerpt: "Access training configurations and pipeline specifications"
category: "api-reference"
---

# Flows API Reference

Complete API reference for flow operations. Access training configurations, flow definitions, and pipeline specifications through this resource.

---

## Flow Resource

Access flows through `client.flows`.

Flows represent training workflows that define how models are trained, including dataset configuration, model architecture, hyperparameters, and training schedules. Flows can be executed to create training runs.

---

## Methods

### list()

List all training flows.

```python
# Basic listing
flows = client.flows.list()

for flow in flows.items:
    print(f"Flow: {flow.flow_id}")
    print(f"Created: {flow.metadata.time_created}")
```

```python
# Iterate through all pages with details
for page in client.flows.list():
    for flow in page.items:
        print(f"Flow: {flow.flow_id}")
        print(f"  Name: {flow.spec.name}")
        print(f"  Created: {flow.metadata.time_created}")
        print(f"  Blocks: {len(flow.spec.blocks)}")
```

```python
# Find recent flows (last 7 days)
from datetime import datetime, timedelta

cutoff = (datetime.now() - timedelta(days=7)).timestamp() * 1000

recent_flows = []
for page in client.flows.list():
    for flow in page.items:
        if flow.metadata.time_created > cutoff:
            recent_flows.append(flow)

print(f"Found {len(recent_flows)} recent flows")
```

```python
# Collect all flows
all_flows = list(client.flows.list().all_items())
print(f"Total flows: {len(all_flows)}")
```

**Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `pagination` | [`PaginationParams`](vi-sdk-pagination#paginationparams) | Pagination settings | `None` |

**Returns:** [`PaginatedResponse`](vi-sdk-pagination#paginatedresponse)`[`[`Flow`](#flow)`]`

---

### get()

Get a specific training flow.

```python
# Basic usage
flow = client.flows.get("flow_abc123")

print(f"Flow ID: {flow.flow_id}")
print(f"Name: {flow.spec.name}")
print(f"Blocks: {len(flow.spec.blocks)}")
```

```python
# Display detailed information
flow = client.flows.get("flow_abc123")
flow.info()  # Prints formatted flow summary
```

```python
# Inspect flow blocks
flow = client.flows.get("flow_abc123")

print(f"Flow: {flow.spec.name}")
print(f"Blocks ({len(flow.spec.blocks)}):")

for i, block in enumerate(flow.spec.blocks, 1):
    print(f"  {i}. {block.block}")
    if block.settings:
        for key, value in list(block.settings.items())[:3]:
            print(f"      {key}: {value}")
```

```python
# Access flow settings
flow = client.flows.get("flow_abc123")

# Global settings
print("Global Settings:")
for key, value in flow.spec.settings.items():
    print(f"  {key}: {value}")

# Tolerations
print("\nTolerations:")
for key, values in flow.spec.tolerations.items():
    print(f"  {key}: {values}")
```

```python
# Access specific properties
flow = client.flows.get("flow_abc123")

print(f"Organization: {flow.organization_id}")
print(f"Schema: {flow.spec.schema}")
print(f"ETag: {flow.etag}")

if flow.spec.training_project:
    print(f"Training Project: {flow.spec.training_project}")
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `flow_id` | `str` | Flow identifier |

**Returns:** [`Flow`](#flow)

---

### delete()

Delete a training flow.

```python
# Delete a flow
deleted = client.flows.delete("flow_abc123")
```

```python
# Delete with confirmation
flow = client.flows.get("flow_abc123")
print(f"About to delete flow: {flow.spec.name}")
print(f"  Blocks: {len(flow.spec.blocks)}")

confirm = input("Delete? (yes/no): ")
if confirm.lower() == "yes":
    client.flows.delete("flow_abc123")
    print("Deleted.")
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `flow_id` | `str` | Flow identifier |

**Returns:** `DeletedFlow`

---

## Response Types

### Flow

Main flow response object.

```python
from vi.api.resources.flows.responses import Flow
```

| Property | Type | Description |
|----------|------|-------------|
| `organization_id` | `str` | Organization ID |
| `flow_id` | `str` | Unique identifier |
| `spec` | [`FlowSpec`](#flowspec) | Flow specification |
| `metadata` | [`ResourceMetadata`](vi-sdk-types#resourcemetadata) | Metadata |
| `self_link` | `str` | API link |
| `etag` | `str` | Entity tag |

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `info()` | `None` | Display formatted flow information |

---

### FlowSpec

```python
from vi.api.resources.flows.responses import FlowSpec
```

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | Display name |
| `schema` | `str` | Schema version identifier |
| `tolerations` | `dict[str, list[str]]` | Toleration rules |
| `settings` | `dict[str, Any]` | Global settings |
| `blocks` | `list[`[`FlowBlock`](#flowblock)`]` | Pipeline blocks |
| `training_project` | `str \| None` | Training project/dataset ID |

---

### FlowBlock

```python
from vi.api.resources.flows.responses import FlowBlock
```

| Property | Type | Description |
|----------|------|-------------|
| `block` | `str` | Block type identifier |
| `settings` | `dict[str, Any]` | Block-specific settings |
| `style` | `dict[str, Any]` | UI/display styling |

---

## See Also

- [Models Guide](vi-sdk-models) - Training models
- [Runs API](vi-sdk-runs-api) - Training runs
- [Models API](vi-sdk-models-api) - Model operations
- [Types API](vi-sdk-types) - Common types
- [Pagination API](vi-sdk-pagination) - Pagination utilities

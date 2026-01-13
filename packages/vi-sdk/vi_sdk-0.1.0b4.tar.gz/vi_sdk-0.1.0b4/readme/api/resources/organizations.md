---
title: "Organizations API Reference"
excerpt: "Access organization information and manage resources"
category: "api-reference"
---

# Organizations API Reference

Complete API reference for organization operations. Access organization information, manage resources, and navigate organization hierarchy through this resource.

---

## Organization Resource

Access organizations through `client.organizations`.

This class provides methods to access organization information including billing, users, datasets, and features.

---

## Methods

### info()

Display formatted information about the current organization.

This method prints a formatted summary of the organization to the console. It does not return a value - use `get()` to retrieve an Organization object for programmatic access.

```python
# Display formatted organization info
client.organizations.info()  # Prints formatted organization summary
```

**Returns:** `None` (prints to console)

---

### get()

Get the current organization object for programmatic access.

```python
# Basic usage
org = client.organizations.get()

print(f"Organization: {org.name}")
print(f"ID: {org.organization_id}")
print(f"Datasets: {len(org.datasets)}")
```

```python
# Get complete organization details
import vi

client = vi.Client()
org = client.organizations.get()

print(f"Organization: {org.name}")
print(f"ID: {org.organization_id}")
print(f"Plan: {org.billing.tier}")
print(f"Datasets: {len(org.datasets)}")
print(f"Users: {len(org.users)}")
```

```python
# List organization users
from vi.api.responses import User

org = client.organizations.get()

print("Organization Users:")
for user_id, user in org.users.items():
    print(f"  {user_id}: {user.workspace_role}")

    if user.datasets:
        print(f"    Datasets: {len(user.datasets)}")
```

```python
# Check organization features
org = client.organizations.get()

print("Enabled Features:")
for feature, enabled in org.features.items():
    status = "✓" if enabled else "✗"
    print(f"  {status} {feature}")
```

```python
# Check organization status
org = client.organizations.get()

# Check lock status
if org.lock_status.is_locked:
    print(f"⚠️ Organization is locked")
    if org.lock_status.lockDate:
        from datetime import datetime
        lock_date = datetime.fromtimestamp(org.lock_status.lockDate / 1000)
        print(f"   Locked on: {lock_date}")
else:
    print("✓ Organization is active")

# Check billing status
print(f"Billing Tier: {org.billing.tier}")
print(f"Billing Email: {org.billing.email}")
```

```python
# List all datasets in organization
org = client.organizations.get()

print(f"Datasets in {org.name}:")
for dataset_id in org.datasets:
    dataset = client.datasets.get(dataset_id)
    print(f"  {dataset.name} ({dataset_id})")
    print(f"    Assets: {dataset.statistic.asset_total}")
    print(f"    Annotations: {dataset.statistic.annotation_total}")
```

```python
# Get organization metadata
from datetime import datetime

org = client.organizations.get()

print("Organization Metadata:")
if org.metadata.create_date:
    created = datetime.fromtimestamp(org.metadata.create_date / 1000)
    print(f"  Created: {created}")

print(f"  Public: {org.metadata.is_public}")

if org.metadata.account_manager:
    print(f"  Account Manager: {org.metadata.account_manager}")

if org.metadata.sales_engineer:
    print(f"  Sales Engineer: {org.metadata.sales_engineer}")
```

```python
# Display info method on organization object
org = client.organizations.get()
org.info()  # Prints formatted organization summary
```

**Returns:** [`Organization`](#organization)

---

## Response Types

### Organization

Main organization response object.

```python
from vi.api.resources.organizations.responses import Organization
```

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | Display name |
| `kind` | `str` | Organization type |
| `organization_id` | `str` | Unique identifier |
| `last_access` | `int` | Last access timestamp |
| `datasets` | `list[str]` | List of dataset IDs |
| `billing` | [`OrganizationBilling`](#organizationbilling) | Billing information |
| `users` | `dict[str, `[`User`](vi-sdk-types#user)`]` | Users mapping |
| `metadata` | [`OrganizationMetadata`](#organizationmetadata) | Organization metadata |
| `features` | `dict` | Enabled features |
| `lock_status` | [`OrganizationLockStatus`](#organizationlockstatus) | Lock status |
| `self_link` | `str` | API link |
| `etag` | `str` | Entity tag |

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `info()` | `None` | Display formatted organization information |

---

### OrganizationBilling

```python
from vi.api.resources.organizations.responses import OrganizationBilling
```

| Property | Type | Description |
|----------|------|-------------|
| `payer` | `str` | Payment entity |
| `email` | `str` | Billing email |
| `subscriber_id` | `str` | Subscriber identifier |
| `ledger` | `list` | Billing ledger entries |
| `tier` | `str` | Current billing tier |

---

### OrganizationMetadata

```python
from vi.api.resources.organizations.responses import OrganizationMetadata
```

| Property | Type | Description |
|----------|------|-------------|
| `create_date` | `int \| None` | Creation timestamp |
| `is_public` | `bool \| None` | Public visibility |
| `account_manager` | `str \| None` | Account manager |
| `sales_engineer` | `str \| None` | Sales engineer |

---

### OrganizationLockStatus

```python
from vi.api.resources.organizations.responses import OrganizationLockStatus
```

| Property | Type | Description |
|----------|------|-------------|
| `is_locked` | `bool` | Lock status |
| `lockDate` | `int \| None` | Lock timestamp |

---

## See Also

- [Getting Started: Authentication](vi-sdk-authentication) - Initial setup
- [Client API](vi-sdk-client) - Client configuration
- [Datasets API](vi-sdk-datasets-api) - Dataset management
- [Types API](vi-sdk-types) - Common types (User)

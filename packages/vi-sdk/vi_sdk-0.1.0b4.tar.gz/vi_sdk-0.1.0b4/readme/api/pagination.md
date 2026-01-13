---
title: "Pagination API Reference"
excerpt: "Handle paginated responses and iterate through large result sets"
category: "api-reference"
---

# Pagination API Reference

Complete API reference for pagination. Handle paginated responses and iterate through large result sets.

---

## PaginatedResponse

The `PaginatedResponse` class wraps paginated API responses and provides iteration utilities.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `items` | `list[T]` | Items in the current page |
| `page` | `int` | Current page number |
| `page_size` | `int` | Number of items per page |
| `total` | `int \| None` | Total number of items (if available) |
| `has_next` | `bool` | Whether there are more pages |

### Methods

#### all_items()

Iterate through all items across all pages.

```python
# Get all datasets
for dataset in client.datasets.list().all_items():
    print(dataset.name)
```

**Returns:** `Iterator[T]`

---

## Iteration Patterns

### Iterate Pages

```python
# Iterate page by page
for page in client.datasets.list():
    print(f"Page {page.page}: {len(page.items)} items")
    for dataset in page.items:
        print(f"  - {dataset.name}")
```

### Iterate All Items

```python
# Iterate all items across pages
for dataset in client.datasets.list().all_items():
    print(dataset.name)
```

### First Page Only

```python
# Get just the first page
first_page = client.datasets.list()
print(f"Got {len(first_page.items)} datasets")

for dataset in first_page.items:
    print(dataset.name)
```

### Collect All Items

```python
# Collect all items into a list
all_datasets = []
for page in client.datasets.list():
    all_datasets.extend(page.items)

print(f"Total: {len(all_datasets)} datasets")
```

---

## PaginationParams

Configure pagination parameters when making requests.

### Constructor

```python
from vi.api.types import PaginationParams

pagination = PaginationParams(
    page_size=50,
    page=1
)
```

### Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `page_size` | `int` | Number of items per page | `20` |
| `page` | `int` | Page number to retrieve | `1` |

### Usage

```python
from vi.api.types import PaginationParams

# Custom page size
pagination = PaginationParams(page_size=100)

# List with custom pagination
datasets = client.datasets.list(pagination=pagination)
print(f"Got {len(datasets.items)} items")

# Specific page
pagination = PaginationParams(page_size=50, page=2)
second_page = client.datasets.list(pagination=pagination)
```

---

## Examples

### Process Items in Batches

```python
def process_all_datasets(client, batch_size=50):
    """Process datasets in batches."""
    pagination = PaginationParams(page_size=batch_size)

    processed = 0
    for page in client.datasets.list(pagination=pagination):
        for dataset in page.items:
            process_dataset(dataset)
            processed += 1

        print(f"Processed {processed} datasets...")

    return processed

total = process_all_datasets(client)
print(f"Processed {total} datasets total")
```

### Filter While Iterating

```python
# Find datasets matching criteria
matching_datasets = []

for page in client.datasets.list():
    for dataset in page.items:
        if "training" in dataset.name.lower():
            matching_datasets.append(dataset)

print(f"Found {len(matching_datasets)} training datasets")
```

### Stop Early

```python
# Find first matching dataset
target_dataset = None

for page in client.datasets.list():
    for dataset in page.items:
        if dataset.name == "target-name":
            target_dataset = dataset
            break
    if target_dataset:
        break

if target_dataset:
    print(f"Found: {target_dataset.dataset_id}")
```

### Count Total Items

```python
# Count all items
total = 0
for page in client.datasets.list():
    total += len(page.items)

print(f"Total datasets: {total}")

# Or using all_items
total = sum(1 for _ in client.datasets.list().all_items())
```

---

## Best Practices

### Memory-Efficient Iteration

```python
# ✅ Good - process as you go
for page in client.datasets.list():
    for dataset in page.items:
        process(dataset)  # Process immediately

# ❌ Bad - load all into memory
all_datasets = list(client.datasets.list().all_items())
for dataset in all_datasets:  # Uses more memory
    process(dataset)
```

### Use Appropriate Page Size

```python
# For quick overview, use smaller page size
pagination = PaginationParams(page_size=10)
preview = client.datasets.list(pagination=pagination)

# For bulk processing, use larger page size
pagination = PaginationParams(page_size=100)
for page in client.datasets.list(pagination=pagination):
    process_batch(page.items)
```

---

## See Also

- [Client API](vi-sdk-client) - Client documentation
- [Datasets API](vi-sdk-datasets-api) - Dataset listing
- [Assets API](vi-sdk-assets-api) - Asset listing

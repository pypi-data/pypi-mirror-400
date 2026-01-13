---
title: "Authentication API Reference"
excerpt: "Handle credentials, tokens, and authentication configuration"
category: "api-reference"
---

# Authentication API Reference

Complete API reference for authentication. Handle credentials, tokens, and authentication configuration.

---

## Authentication Class

Abstract base class for Vi API authentication.

```python
from vi.client.auth import Authentication
```

All authentication methods must inherit from this class and implement the `get_headers()` method to provide authentication headers for HTTP requests.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `organization_id` | `str` | The organization identifier for the authenticated session |

### Methods

#### get_headers()

Get authentication headers for HTTP requests.

```python
headers = auth.get_headers()
# {'Authorization': 'Bearer dtvi_...', 'Organization-Id': 'org-uuid'}
```

**Returns:** `dict[str, str]` - Dictionary of HTTP headers including authentication credentials

---

## SecretKeyAuth Class

Secret key authentication for Vi API.

```python
from vi.client.auth import SecretKeyAuth
```

This class handles authentication using a secret key and organization ID. Credentials can be provided in three ways (in order of precedence):

1. Direct parameters
2. Configuration file
3. Environment variables

### Constructor

```python
auth = SecretKeyAuth(
    secret_key: str | None = None,
    organization_id: str | None = None,
    config_file: str | Path | None = None
)
```

**Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `secret_key` | `str \| None` | Your Vi API secret key. Must start with `dtvi_`. | `None` |
| `organization_id` | `str \| None` | Your organization UUID. | `None` |
| `config_file` | `str \| Path \| None` | Path to JSON configuration file. | `None` |

**Raises:**

| Exception | Condition |
|-----------|-----------|
| `ViConfigurationError` | If secret_key or organization_id is missing, invalid, or if config_file cannot be read |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `secret_key` | `str` | The API secret key for authentication |
| `organization_id` | `str` | The organization identifier |

### Methods

#### get_headers()

Get authentication headers for HTTP requests.

```python
headers = auth.get_headers()
print(headers)
# {'Authorization': 'Bearer dtvi_abc123...', 'Organization-Id': 'org-uuid-123'}
```

**Returns:** `dict[str, str]` - Dictionary of headers to include in requests

---

## Usage Examples

### Direct Credentials

```python
from vi.client.auth import SecretKeyAuth

auth = SecretKeyAuth(
    secret_key="dtvi_your_secret_key",
    organization_id="your_organization_id"
)
```

### From Environment Variables

```python
import os
from vi.client.auth import SecretKeyAuth

# Set environment variables
os.environ["DATATURE_VI_SECRET_KEY"] = "dtvi_your_key"
os.environ["DATATURE_VI_ORGANIZATION_ID"] = "your_org_id"

# Auto-loads from environment
auth = SecretKeyAuth()
```

### From Config File

```python
from vi.client.auth import SecretKeyAuth

# Config file should contain:
# {"secret_key": "dtvi_...", "organization_id": "org-..."}
auth = SecretKeyAuth(config_file="~/datature/vi/config.json")
```

### With Client

```python
import vi

# The Client class uses SecretKeyAuth internally
client = vi.Client(
    secret_key="dtvi_your_secret_key",
    organization_id="your_organization_id"
)

# Or with environment variables
client = vi.Client()  # Auto-loads credentials
```

---

## Config File Format

The configuration file should be a JSON file with the following structure:

```json
{
  "secret_key": "dtvi_your_secret_key",
  "organization_id": "your_organization_uuid"
}
```

### Example Locations

- `~/.datature/vi/config.json` (recommended)
- `./config.json` (project-local)
- Any path passed to `config_file` parameter

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATATURE_VI_SECRET_KEY` | Your Vi API secret key |
| `DATATURE_VI_ORGANIZATION_ID` | Your organization UUID |

---

## Key Format

The secret key must:

- Start with `dtvi_` prefix
- Be a valid API key from your Datature account

> ⚠️ **Security Warning**
>
> Never commit your secret key to version control. Use environment variables or config files that are excluded from your repository.

---

## See Also

- [Getting Started: Authentication](vi-sdk-authentication) - Setup guide
- [Client API](vi-sdk-client) - Using authentication with the client

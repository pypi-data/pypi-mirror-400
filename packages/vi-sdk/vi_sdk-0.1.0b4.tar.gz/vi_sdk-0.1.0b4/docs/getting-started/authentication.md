# Authentication

Learn how to authenticate with the Vi platform using different methods.

## Overview

Vi SDK supports multiple authentication methods:

1. **Direct credentials** - Pass credentials directly to the client
2. **Environment variables** - Store credentials in environment variables
3. **Configuration file** - Use a JSON configuration file
4. **Config file + environment** - Combine both approaches

## Getting Your Credentials

Before authenticating, you need to obtain:

- **Secret Key**: Your API secret key
- **Organization ID**: Your organization identifier

### From Datature Vi

1. Log in to [Datature Vi](https://vi.datature.com)
2. Navigate to **Settings** → **API Keys**
3. Click **Generate New Key**
4. Copy your Secret Key and Organization ID

!!! warning "Security"
    Never commit your secret key to version control. Always use environment variables or secure configuration files.

## Method 1: Direct Credentials

Pass credentials directly when initializing the client:

```python
import vi

client = vi.Client(
    secret_key="dtvi_abc123...",
    organization_id="xyz789..."
)
```

**Pros:**

- Simple and straightforward
- Good for quick scripts and testing

**Cons:**

- Not suitable for production
- Risk of exposing credentials in code

## Method 2: Environment Variables

Store credentials in environment variables:

### Setting Environment Variables

=== "Linux/macOS"

    ```bash
    # Add to ~/.bashrc or ~/.zshrc
    export DATATURE_VI_SECRET_KEY="dtvi_abc123..."
    export DATATURE_VI_ORGANIZATION_ID="xyz789..."
    ```

=== "Windows (PowerShell)"

    ```powershell
    $env:DATATURE_VI_SECRET_KEY="dtvi_abc123..."
    $env:DATATURE_VI_ORGANIZATION_ID="xyz789..."
    ```

=== "Windows (CMD)"

    ```cmd
    set DATATURE_VI_SECRET_KEY=dtvi_abc123...
    set DATATURE_VI_ORGANIZATION_ID=xyz789...
    ```

=== ".env File"

    ```bash
    # .env
    DATATURE_VI_SECRET_KEY=dtvi_abc123...
    DATATURE_VI_ORGANIZATION_ID=xyz789...
    ```

    Then use python-dotenv:

    ```python
    from dotenv import load_dotenv
    load_dotenv()
    ```

### Using in Code

```python
import os
import vi

client = vi.Client(
    secret_key=os.getenv("DATATURE_VI_SECRET_KEY"),
    organization_id=os.getenv("DATATURE_VI_ORGANIZATION_ID")
)
```

**Pros:**

- Keeps credentials out of code
- Industry standard practice
- Easy to manage per environment

**Cons:**

- Requires environment configuration
- Can be forgotten when deploying

## Method 3: Configuration File

Store credentials in a JSON configuration file:

### Creating the Config File

Create `~/datature/vi/config.json`:

```json
{
  "secret_key": "dtvi_abc123...",
  "organization_id": "xyz789..."
}
```

!!! tip "File Permissions"
    Secure your config file:

    ```bash
    chmod 600 ~/datature/vi/config.json
    ```

### Using in Code

```python
import vi

client = vi.Client(
    config_file="~/datature/vi/config.json"
)
```

You can also use a custom path:

```python
client = vi.Client(
    config_file="/path/to/your/config.json"
)
```

**Pros:**

- Clean and organized
- Easy to switch between environments
- Supports multiple profiles

**Cons:**

- File must be present on system
- Requires file management

## Method 4: Hybrid Approach

Combine configuration file with environment variable overrides:

```python
import os
import vi

# Load from config file, but allow environment overrides
client = vi.Client(
    secret_key=os.getenv("DATATURE_VI_SECRET_KEY"),  # Override if present
    organization_id=os.getenv("DATATURE_VI_ORGANIZATION_ID"),
    config_file="~/datature/vi/config.json"  # Fallback
)
```

This approach provides flexibility for different deployment scenarios.

## Authentication Testing

Verify your authentication is working:

```python
import vi
from vi import ViAuthenticationError

try:
    client = vi.Client(
        secret_key="your-secret-key",
        organization_id="your-organization-id"
    )

    # Test by fetching organization info
    org = client.organizations.info()
    print(f"✓ Authentication successful!")
    print(f"  Organization: {org.name}")
    print(f"  Organization ID: {org.organization_id}")

except ViAuthenticationError as e:
    print(f"✗ Authentication failed: {e.message}")
    print(f"  Suggestion: {e.suggestion}")
except Exception as e:
    print(f"✗ Unexpected error: {e}")
```

## Multiple Organizations

If you work with multiple organizations, create separate clients:

```python
import vi

# Production organization
prod_client = vi.Client(
    secret_key="dtvi_abc123...",
    organization_id="xyz789..."
)

# Development organization
dev_client = vi.Client(
    secret_key="dtvi_def456...",
    organization_id="qrs012..."
)

# Use appropriate client
datasets = prod_client.datasets.list()
```

## Best Practices

### 1. Never Hardcode Credentials

❌ **Bad:**

```python
client = vi.Client(
    secret_key="dtvi_abc123...",  # Hardcoded!
    organization_id="xyz789..."
)
```

✅ **Good:**

```python
import os
client = vi.Client(
    secret_key=os.getenv("DATATURE_VI_SECRET_KEY"),
    organization_id=os.getenv("DATATURE_VI_ORGANIZATION_ID")
)
```

### 2. Use Different Keys for Different Environments

```python
import os

environment = os.getenv("ENVIRONMENT", "development")

if environment == "production":
    client = vi.Client(config_file="~/.datature/prod-config.json")
else:
    client = vi.Client(config_file="~/.datature/dev-config.json")
```

### 3. Rotate Keys Regularly

- Generate new API keys periodically
- Revoke old keys after rotation
- Update all services using the old key

### 4. Limit Key Permissions

When creating API keys on the platform:

- Only grant necessary permissions
- Use separate keys for different services
- Monitor key usage

### 5. Secure Storage

- Use environment variables in production
- Store config files with restricted permissions
- Use secret management services (AWS Secrets Manager, HashiCorp Vault, etc.)

## Advanced: Secret Management Services

### AWS Secrets Manager

```python
import boto3
import json
import vi

def get_vi_credentials():
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId='vi-credentials')
    secret = json.loads(response['SecretString'])
    return secret['secret_key'], secret['organization_id']

secret_key, org_id = get_vi_credentials()
vi_client = vi.Client(secret_key=secret_key, organization_id=org_id)
```

### HashiCorp Vault

```python
import hvac
import vi

vault_client = hvac.Client(url='http://localhost:8200')
vault_client.token = 'your-vault-token'

secret = vault_client.secrets.kv.v2.read_secret_version(
    path='vi'
)

vi_client = vi.Client(
    secret_key=secret['data']['data']['secret_key'],
    organization_id=secret['data']['data']['organization_id']
)
```

### Google Cloud Secret Manager

```python
from google.cloud import secretmanager
import json
import vi

def get_secret(project_id, secret_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return json.loads(response.payload.data.decode('UTF-8'))

credentials = get_secret("my-project", "vi-credentials")
vi_client = vi.Client(
    secret_key=credentials['secret_key'],
    organization_id=credentials['organization_id']
)
```

## Troubleshooting

### Invalid API Key

```python
ViAuthenticationError: Authentication failed - Invalid API key
```

**Solutions:**

1. Verify your secret key is correct
2. Check if the key has been revoked
3. Ensure no extra whitespace in the key

### Organization Not Found

```python
ViAuthenticationError: Organization not found
```

**Solutions:**

1. Verify your organization ID is correct
2. Check if you have access to the organization
3. Ensure the organization is active

### Permission Denied

```python
ViPermissionError: Permission denied
```

**Solutions:**

1. Check your API key permissions
2. Verify your organization role
3. Contact your organization administrator

### Connection Refused

```python
ViNetworkError: Connection refused
```

**Solutions:**

1. Check your internet connection
2. Verify the endpoint URL is correct
3. Check if a firewall is blocking the connection

## Next Steps

<div class="grid cards" markdown>

-   :material-cog:{ .lg .middle } __Configuration__

    ---

    Configure logging, timeouts, and other settings

    [:octicons-arrow-right-24: Configuration guide](configuration.md)

-   :material-shield-lock:{ .lg .middle } __Error Handling__

    ---

    Learn how to handle authentication errors

    [:octicons-arrow-right-24: Error handling guide](../guide/error-handling.md)

-   :material-book-open:{ .lg .middle } __User Guide__

    ---

    Continue with the user guide

    [:octicons-arrow-right-24: User guide](../guide/overview.md)

</div>

## Summary

| Method | Use Case | Security |
|--------|----------|----------|
| Direct credentials | Testing, quick scripts | ⚠️ Low |
| Environment variables | Production, CI/CD | ✅ High |
| Configuration file | Local development | ✅ Medium |
| Secret management | Enterprise, cloud | ✅ Very High |

Choose the method that best fits your use case and security requirements.

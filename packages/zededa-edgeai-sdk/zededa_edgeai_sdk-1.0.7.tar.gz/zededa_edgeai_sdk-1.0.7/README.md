# Zededa EdgeAI SDK

The Zededa EdgeAI SDK provides both a pluggable command-line interface and a Python library for authenticating with the Zededa EdgeAI backend and preparing ML tooling environments.

## Highlights

- 🧩 **Modular command registry** – each CLI sub-command lives in its own module under `zededa_edgeai_sdk.commands`, making it easy to add new commands such as `catalog` or `model` without touching existing code.
- 🧠 **Typed service layer** – shared HTTP, authentication, catalog, and storage logic is encapsulated under `zededa_edgeai_sdk.services`, so workflows reuse the same battle-tested primitives.
- 🔐 **Secure OAuth login** – browser-based authentication with automatic callback port discovery and detailed debug logging when needed.
- ⚙️ **Environment bootstrap** – exports MLflow and MinIO credentials into your shell and keeps helpers available for Python embedding.

## Installation

```bash
pip install zededa-edgeai-sdk
```

To work from source:

```bash
git clone https://github.com/zededa/edgeai-sdk.git
cd edgeai-sdk
pip install -e .
```

## CLI Usage

Every action is exposed as a sub-command. The current release ships the `login`, `catalog`, and `set-catalog-context` commands; future commands (for models, etc.) follow the same structure.

```bash
# Interactive OAuth login with optional catalog selection
zededa-edgeai login

# Login for a specific catalog using the default backend
zededa-edgeai login --catalog zededa

# Non-interactive login with credentials
zededa-edgeai login --email user@example.com --prompt-password

# Override backend URL and enable debug logging
EDGEAI_SERVICE_URL=https://custom.backend.local \
  zededa-edgeai login --debug
```

After a successful login the CLI launches a child shell with the relevant environment variables applied. Exit that shell to return to your previous context.

### Catalog Management

List available catalogs and switch between catalogs with an authenticated shell session:

```bash
# List all available catalogs
zededa-edgeai catalog --list

# Switch to a catalog and launch authenticated shell (recommended)
zededa-edgeai set-catalog-context zededa

# List catalogs with custom backend URL and debug logging  
EDGEAI_SERVICE_URL=https://custom.backend.local \
  zededa-edgeai catalog --list --debug

# Switch to catalog with debug logging
zededa-edgeai set-catalog-context production --debug

# Override service URL for one-time use
zededa-edgeai set-catalog-context staging --service-url https://staging.backend.com
```

The catalog list shows all catalogs you have access to, highlighting your current catalog. The `set-catalog-context` command switches to a catalog and launches an authenticated shell session with all required environment variables set, similar to the login command.

### Available Options

#### Login Command
```
zededa-edgeai login [-h]
                    [--catalog CATALOG]
                    [--email EMAIL]
                    [--password PASSWORD]
                    [--prompt-password]
                    [--service-url SERVICE_URL]
                    [--debug]
```

#### Catalog Listing Command
```
zededa-edgeai catalog [-h]
                      [--list]
                      [--service-url SERVICE_URL]
                      [--debug]
```

#### Set Catalog Context Command
```
zededa-edgeai set-catalog-context [-h]
                                  catalog
                                  [--service-url SERVICE_URL]
                                  [--debug]
```

## Python Usage

Use the high-level client, the module helpers, or the command workflow directly:

### Authentication
```python
from zededa_edgeai_sdk.client import ZededaEdgeAIClient

client = ZededaEdgeAIClient()
creds = client.login(catalog_id="zededa")
print(creds["environment"]["MLFLOW_TRACKING_URI"])
```

### Catalog Management
```python
from zededa_edgeai_sdk.client import ZededaEdgeAIClient

# Using the client
client = ZededaEdgeAIClient()

# List available catalogs (prints formatted output by default)
client.list_catalogs()
# Output:
# Available Catalogs:
# ==================
#  1. demo1
#  2. demo2 (current)
#  3. zededa
#  4. production
#  5. staging
#
# Total: 5 catalogs
# Current catalog: demo2
# User: alice@company.com

# Get catalog data as dictionary (formatted=False)
catalogs = client.list_catalogs(formatted=False)
print(f"Available catalogs: {catalogs['available_catalogs']}")

# Switch to a catalog
creds = client.switch_catalog("production")

# Or using the module-level convenience functions
from zededa_edgeai_sdk import list_catalogs, switch_catalog

# List catalogs (formatted output)
list_catalogs()

# Get catalog data as dictionary
catalogs = list_catalogs(formatted=False)

# Switch catalog
creds = switch_catalog("production")
```

### Direct Command Usage
Call the command workflows directly if you need finer-grained control:

```python
from zededa_edgeai_sdk.commands.login import execute_login
from zededa_edgeai_sdk.commands.catalogs import execute_catalog_switch, execute_catalog_list

# Login
credentials = execute_login("zededa", debug=True)

# List catalogs
catalog_info = execute_catalog_list(debug=True)

# Switch catalogs (updates environment variables only)
credentials = execute_catalog_switch("production", debug=True)
```

Environment variables can be cleared programmatically via `zededa_edgeai_sdk.client.logout()` or `zededa_edgeai_sdk.environment.clear_environment()`.

## External Providers and Model Import

Manage external model sources and import models into your catalogs.

### CLI Usage

#### External Provider Management

```bash
# List all external providers
zededa-edgeai external-providers list

# Create a new HuggingFace provider
zededa-edgeai external-providers create \
  --name "My HuggingFace" \
  --type huggingface \
  --url "https://huggingface.co" \
  --config '{"token": "hf_xxxxx"}'

# Get provider details (use provider name)
zededa-edgeai external-providers get "My HuggingFace"

# Update provider configuration (use provider name)
zededa-edgeai external-providers update "My HuggingFace" \
  --name "Updated HuggingFace" \
  --config '{"token": "new_token"}'

# Test provider connection (use provider name)
zededa-edgeai external-providers test-connection "My HuggingFace"

# Browse provider models (use provider name)
zededa-edgeai external-providers browse "My HuggingFace" \
  --search "yolo" \
  --path "/models"

# Delete a provider (use provider name)
zededa-edgeai external-providers delete "My HuggingFace"
```

#### Import Job Management

```bash
# RECOMMENDED: Upload files from your local machine
zededa-edgeai import-jobs upload \
  --provider-name "local-provider" \
  --catalog-id my-catalog \
  --model-name "My Local Model" \
  --files /path/to/model.pt /path/to/config.json \
  --model-version "1.0" \
  --metadata '{"framework": "pytorch", "task": "classification"}' \
  --wait

# Upload a single file
zededa-edgeai import-jobs upload \
  --provider-name "local-provider" \
  --catalog-id my-catalog \
  --model-name "My Model" \
  --files /home/user/models/model.pt \
  --wait

# Create an import job from external provider (returns immediately)
zededa-edgeai import-jobs create \
  --provider-name "My HuggingFace" \
  --model-identifier "user/model-name" \
  --model-name "My Imported Model" \
  --model-version "1.0"

# Create and wait for completion
zededa-edgeai import-jobs create \
  --provider-name "My HuggingFace" \
  --model-identifier "user/model-name" \
  --wait

# List all import jobs
zededa-edgeai import-jobs list

# Filter by catalog and status
zededa-edgeai import-jobs list \
  --catalog-id catalog-456 \
  --status completed

# Get job status
zededa-edgeai import-jobs get job-id-789

# Cancel a running job
zededa-edgeai import-jobs cancel job-id-789

# Retry a failed job
zededa-edgeai import-jobs retry job-id-789

# Delete a job record
zededa-edgeai import-jobs delete job-id-789
```

### Python Usage

#### External Provider Management

```python
from zededa_edgeai_sdk.client import ZededaEdgeAIClient

client = ZededaEdgeAIClient()

# List providers
providers = client.list_external_providers(limit=50, page=1, search="azure")

# Create provider
provider = client.create_external_provider({
    "name": "My Azure",
    "type": "azure",
    "url": "https://azure.microsoft.com",
    "config": {"subscription_id": "sub-123", "token": "token-xxx"},
    "description": "Azure ML provider"
})

# Get provider
provider = client.get_external_provider("provider-id-123")

# Update provider
updated = client.update_external_provider("provider-id-123", {
    "name": "Updated Azure",
    "config": {"token": "new-token"}
})

# Test connection
result = client.test_provider_connection("provider-id-123")
print(f"Connection test: {result['success']}")

# Browse provider
items = client.browse_provider("provider-id-123", path="/models", search="yolo")

# Delete provider
success = client.delete_external_provider("provider-id-123")
```

#### Model Import

```python
from zededa_edgeai_sdk.client import ZededaEdgeAIClient

client = ZededaEdgeAIClient()

# RECOMMENDED: Upload files from your local machine
job = client.upload_model_from_local_files(
    provider_id="local-provider-id",
    catalog_id="my-catalog",
    model_name="My Local Model",
    file_paths="/path/to/model.pt",  # Single file
    # Or multiple files:
    # file_paths=["/path/to/model.pt", "/path/to/config.json"],
    import_config={
        "model_version": "1.0",
        "metadata": {"framework": "pytorch", "task": "classification"}
    },
    wait=True
)
print(f"Upload completed: {job['status']}")

# Import model from external provider (async)
job = client.import_model_from_external_provider({
    "provider_id": "provider-123",
    "model_identifier": "organization/model-name",
    "catalog_id": "catalog-456",
    "model_name": "My Model",
    "model_version": "1.0",
    "metadata": {"task": "object-detection"}
})
print(f"Import job created: {job['job_id']}")

# Import and wait for completion
job = client.import_model_from_external_provider({
    "provider_id": "provider-123",
    "model_identifier": "organization/model-name",
    "catalog_id": "catalog-456"
}, wait=True)
print(f"Import completed: {job['status']}")

# List jobs
jobs = client.list_import_jobs(limit=20, page=1, catalog_id="catalog-456", status="completed")

# Get job status
job = client.get_import_job("job-id-789")
print(f"Status: {job['status']}, Progress: {job.get('progress', 0)}%")

# Cancel job
result = client.cancel_import_job("job-id-789")

# Retry failed job
result = client.retry_import_job("job-id-789")

# Delete job
result = client.delete_import_job("job-id-789")
```

#### Module-Level Convenience Functions

```python
from zededa_edgeai_sdk.client import (
    list_external_providers,
    create_external_provider,
    import_model_from_external_provider,
    list_import_jobs
)

# List providers
providers = list_external_providers(limit=50)

# Create provider
provider = create_external_provider({
    "name": "HuggingFace Hub",
    "type": "huggingface",
    "url": "https://huggingface.co"
})

# Import model
job = import_model_from_external_provider({
    "provider_id": provider["id"],
    "model_identifier": "facebook/detr-resnet-50",
    "catalog_id": "my-catalog"
}, wait=True)

# List jobs
jobs = list_import_jobs(status="completed")
```

#### Provider Types

Supported provider types:
- `huggingface` - HuggingFace Hub
- `azure` - Azure ML
- `mlflow` - MLflow Registry
- `s3` - AWS S3
- `blob` - Azure Blob Storage
- `local` - Local filesystem
- `sagemaker` - AWS SageMaker

#### Import Job Statuses

- `pending` - Job created, waiting to start
- `running` - Currently executing
- `completed` - Successfully finished
- `failed` - Execution failed
- `cancelled` - User cancelled

## Architecture Overview

```
zededa_edgeai_sdk/
├── commands/              # CLI sub-command modules
│   ├── login.py           # CLI handler + reusable login workflow helper
│   ├── catalogs.py        # CLI handler + catalog listing workflow
│   └── set_catalog_context.py # CLI handler for catalog switching with shell launch
├── services/              # Low-level backend interactions
│   ├── http.py            # Debug-aware HTTP client built on requests
│   ├── auth.py            # OAuth browser flow and callback server
│   ├── catalogs.py        # Catalog discovery and token scoping helpers
│   └── storage.py         # MinIO credential retrieval
├── environment.py         # Environment application/sanitisation helpers
├── client.py              # Public high-level Python API
└── zededa_edgeai_sdk.py   # Service coordination facade
```

Adding a new command means:

1. Create `zededa_edgeai_sdk/commands/<command>.py` with a `CommandSpec`
   registration function.
2. Implement the workflow using the shared services.
3. Optionally expose convenient helpers from `client.py` or `__init__.py`.

The CLI automatically discovers commands from the registry.

## Environment Variables

The login workflow applies the following variables to the current process and any spawned shells:

- `ZEDEDA_CURRENT_CATALOG`
- `ZEDEDA_ACCESS_TOKEN`
- `MLFLOW_TRACKING_TOKEN`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `MLFLOW_S3_ENDPOINT_URL`
- `MLFLOW_TRACKING_URI`
- `MINIO_BUCKET`
- `ZEDEDA_BACKEND_URL`

Use `zededa_edgeai_sdk.environment.APPLIED_ENVIRONMENT_KEYS` for the authoritative list.

## Development

```bash
# Run unit tests (creates/uses the local virtual environment)
./.venv/bin/python -m unittest discover -s tests

# Lint or format as needed
ruff check
black zededa_edgeai_sdk tests
```

All new features should include a matching command module and, when 
backend access is required, a focused service module.

## Troubleshooting

- Pass `--debug` to log all HTTP requests/responses with sensitive fields masked.
- If the browser doesn't open automatically, copy the printed URL into a browser window manually.
- To retry a failed OAuth flow, simply rerun the command; a fresh callback port is selected automatically.

## Support

- File an issue at [github.com/zededa/edgeai-sdk](https://github.com/zededa/edgeai-sdk)
- Email support@zededa.com

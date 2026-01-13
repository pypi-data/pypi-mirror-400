# hashimportai

Python SDK for executing HashImport workflows using hashlets.

## Installation

```bash
pip install hashimportai
```

For development or to install from source, see [PUBLISHING.md](PUBLISHING.md).

## Quick Start

### Complete Example with Subscribers

```python
import asyncio
from hashimportai import WorkflowRunner

# Define subscriber callbacks for each action
def on_vault_linker(action_name, response):
    print(f"[Subscriber] {action_name} completed: {response}")

def on_upload_pdf(action_name, response):
    print(f"[Subscriber] {action_name} completed: {response}")
    if response and response.get("data"):
        result = response.get("data", {}).get("result", {})
        if isinstance(result, dict) and "linked_output" in result:
            print(f"  -> Uploaded file: {result['linked_output']}")

def on_esign_pdf(action_name, response):
    print(f"[Subscriber] {action_name} completed: {response}")

def on_esign_signed_url(action_name, response):
    print(f"[Subscriber] {action_name} completed: {response}")
    if response and response.get("data"):
        result = response.get("data", {}).get("result", {})
        if isinstance(result, dict) and "url" in result:
            print(f"  -> Signed URL: {result['url']}")

# Create subscribers dictionary mapping action names to callbacks
subscribers = {
    "vault_linker": on_vault_linker,
    "upload_pdf": on_upload_pdf,
    "esign_pdf": on_esign_pdf,
    "esign_signed_url": on_esign_signed_url,
}

async def main():
    # Option 1: Pass credentials directly (recommended)
    runner = WorkflowRunner(
        workflow_id="69576bd6af6515a54826291c",
        multi_part_actions=["upload_pdf"],
        subscribers=subscribers,
        api_key="your-api-key",
        base_url="http://localhost:6003/api/v1"
    )
    
    form_data = {
        "vault_linker": {"hashlet_id": "694d1e4bb731610cf532267b"},
        "upload_pdf": {"file": "tmp/document.pdf"},  # Relative to current working directory
        "esign_pdf": {
            "filename": "is_link",  # Will be auto-populated from upload_pdf output
            "creator_id": "1234567890",
            "purpose": "test",
            "email": "john.doe@example.com",
            "company_full_name": "John Doe",
            "location": "123 Main St, Anytown, USA",
            "sig_x1": 100,
            "sig_y1": 100,
            "sig_x2": 200,
            "sig_y2": 200,
            "sign_page": 1,
        },
        "esign_signed_url": {"filename": "document.pdf"},
    }
    
    await runner.run("hashhub-fc77bf01", form_data)

asyncio.run(main())
```

### Option 2: Use Environment Variables

```bash
export HASHIMPORTAI_API_KEY="your-api-key"
export HASHIMPORTAI_BASE_URL="http://localhost:6003/api/v1"
```

```python
import asyncio
from hashimportai import WorkflowRunner

async def main():
    # Credentials loaded from environment variables
    runner = WorkflowRunner(
        workflow_id="your-workflow-id",
        multi_part_actions=["upload_pdf"],
        subscribers=subscribers  # Optional: can be None or empty dict
    )
    
    form_data = {
        "upload_pdf": {"file": "document.pdf"}
    }
    
    await runner.run("hashhub-xxx", form_data)

asyncio.run(main())
```

## Configuration

### API Key and Base URL

You can provide credentials in two ways:

1. **Direct parameters** (recommended for scripts):
   ```python
   runner = WorkflowRunner(
       workflow_id="...",
       multi_part_actions=["..."],
       api_key="your-api-key",
       base_url="http://localhost:6003/api/v1"
   )
   ```

2. **Environment variables** (recommended for production):
   ```bash
   export HASHIMPORTAI_API_KEY="your-api-key"
   export HASHIMPORTAI_BASE_URL="http://localhost:6003/api/v1"
   ```

### Subscribers (Callbacks)

Subscribers allow you to handle responses from each action:

```python
subscribers = {
    "action_name": lambda action, response: print(f"{action} completed: {response}")
}
```

Each callback receives:
- `action_name`: The name of the action that completed
- `response`: The response data from the action execution

## File Paths

File paths in `form_data` are resolved relative to your **current working directory**, not the SDK directory:

- `{"file": "document.pdf"}` → looks for `./document.pdf` in your current directory
- `{"file": "tmp/document.pdf"}` → looks for `./tmp/document.pdf` in your current directory
- `{"file": "/absolute/path/to/file.pdf"}` → uses absolute path as-is

## Auto-linking Actions

Use `"is_link"` as a value to automatically link outputs between actions:

```python
form_data = {
    "upload_pdf": {"file": "document.pdf"},
    "esign_pdf": {
        "filename": "is_link",  # Will be replaced with output from upload_pdf
        # ... other fields
    }
}
```

The SDK automatically extracts the `linked_output` from the previous action and replaces `"is_link"` with the actual filename.
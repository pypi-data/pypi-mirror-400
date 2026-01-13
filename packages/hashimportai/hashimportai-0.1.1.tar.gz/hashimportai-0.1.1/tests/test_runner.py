"""
Integration test example - run with: python -m pytest tests/test_runner.py -v
Or run directly: python tests/test_runner.py
"""

import sys
from pathlib import Path
import asyncio

# Add src to path for imports
sdk_dir = Path(__file__).parent.parent
if str(sdk_dir / "src") not in sys.path:
    sys.path.insert(0, str(sdk_dir / "src"))

from hashimportai import WorkflowRunner


# Define subscriber callbacks for each action
def on_vault_linker(action_name, response):
    print(f"[Subscriber] {action_name} completed: {response}")

def on_upload_pdf(action_name, response):
    print(f"[Subscriber] {action_name} completed: {response}")

def on_esign_pdf(action_name, response):
    print(f"[Subscriber] {action_name} completed: {response}")

def on_esign_signed_url(action_name, response):
    print(f"[Subscriber] {action_name} completed: {response}")

# Create subscribers dictionary mapping action names to callbacks
subscribers = {
    "vault_linker": on_vault_linker,
    "upload_pdf": on_upload_pdf,
    "esign_pdf": on_esign_pdf,
    "esign_signed_url": on_esign_signed_url,
}

runner = WorkflowRunner(
    "695929219652ded369c9a6a7",
    ["upload_pdf"],
    subscribers=subscribers,
    api_key="oj/qzud7VeCdU24MCigzzcCIQSHFOadDOCKHbiY4ADQ=",
    base_url="http://localhost:6003/api/v1",
)

form_data = {
    "vault_linker": {"hashlet_id": "695927309652ded369c9a6a2"},
    "upload_pdf": {"file": "tmp/document.pdf"},
    "esign_pdf": {
        "filename": "is_link",
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
    "esign_signed_url": {"filename": "dfsdfs.pdf"},
}
asyncio.run(runner.run("hashhub-fc77bf01", form_data))

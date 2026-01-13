import httpx
from .errors import AuthenticationError
import os
from pathlib import Path   
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class HashImportClient:
    """
    HashImport AI SDK Client
    
    Usage:
        # Option 1: Pass credentials directly
        client = HashImportClient(
            api_key="your-api-key",
            base_url="http://localhost:6003"
        )
        
        # Option 2: Use environment variables
        # Set HASHIMPORTAI_API_KEY and HASHIMPORTAI_BASE_URL
        client = HashImportClient()
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        """
        Initialize HashImportClient
        
        Args:
            api_key: API key for authentication. If not provided, uses HASHIMPORTAI_API_KEY env var.
            base_url: Base URL for the API. If not provided, uses HASHIMPORTAI_BASE_URL env var.
        
        Raises:
            ValueError: If api_key or base_url is not provided and not found in environment.
        """
        # Get API key: parameter > environment variable
        self.app_key = api_key or os.getenv("HASHIMPORTAI_API_KEY") or os.getenv("APP_KEY", "")
        
        # Get base URL: parameter > environment variable
        self.base_url = (base_url or os.getenv("HASHIMPORTAI_BASE_URL") or os.getenv("BASE_URL", "")).rstrip("/")
        
        if not self.base_url:
            raise ValueError(
                "base_url is required. Provide it as a parameter or set HASHIMPORTAI_BASE_URL environment variable."
            )
        if not self.app_key:
            raise ValueError(
                "api_key is required. Provide it as a parameter or set HASHIMPORTAI_API_KEY environment variable."
            )

    def _headers(self):
        return {
            "X-App-Key": self.app_key,
            "Accept": "application/json"
        }

    async def fetch_workflow(self, workflow_id: str):
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/external/hashsdkactions/{workflow_id}/workflow",
                headers=self._headers()
            )

            if resp.status_code == 401:
                raise AuthenticationError("Invalid App Key")

            # resp.raise_for_status()
            return resp.json()
    
    async def fetch_manifest(self, hash_value: str):
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/external/hashsdkactions/{hash_value}/manifest",
                headers=self._headers()
            )

            if resp.status_code == 401:
                raise AuthenticationError("Invalid App Key")

            # resp.raise_for_status()
            return resp.json()
    
    async def execute_action_json(self, hash_value: str, action_name: str, payload: dict):       
        # print(f"payload: {payload}")     

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/external/hashsdkactions/{hash_value}/actions/{action_name}",
                headers=self._headers(),
                json={"payload": payload}
            )

            if resp.status_code == 401:
                raise AuthenticationError("Invalid App Key")

            return resp.json()
    
    async def execute_action_multipart(self, hash_value: str, action_name: str, payload: dict):
        async with httpx.AsyncClient() as client:        
            files = {}
            
            # Check for "file" key (simple file path)
            if "file" in payload:
                # Use user's current working directory, not SDK directory
                file_path_str = payload["file"]
                
                # If it's an absolute path, use it as-is
                # If it's a relative path, resolve from current working directory
                if os.path.isabs(file_path_str):
                    file_path = Path(file_path_str)
                else:
                    # Resolve relative to user's current working directory
                    file_path = Path.cwd() / file_path_str
                
                if file_path.exists():
                    with open(file_path, "rb") as f:
                        file_content = f.read()
                    files = {
                        "file": (file_path.name, file_content)
                    }
                else:
                    logger.warning(f"File not found: {file_path}")
                     
            # Prepare form data with JSON payload (without file references)
            data = {}
            
            headers = self._headers()
            # httpx will automatically set Content-Type for multipart when files are provided
            
            resp = await client.post(
                f"{self.base_url}/external/hashsdkactions/{hash_value}/actions/{action_name}/multipart",
                headers=headers,
                data=data,
                files=files if files else None
            )

            if resp.status_code == 401:
                raise AuthenticationError("Invalid App Key")

            return resp.json()

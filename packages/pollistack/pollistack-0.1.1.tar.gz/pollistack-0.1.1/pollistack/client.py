import httpx
import json
from typing import Optional, Dict, Any, List

class PolliClient:
    def __init__(
        self, 
        api_key: str, 
        base_url: str = "https://api.meridian-labs.ai"
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

    async def chat(self, prompt: str, user_id: Optional[str] = None, app_id: Optional[str] = None, model: str = "qwen-coder", **kwargs) -> str:
        """Send a prompt to the agent and get a response."""
        # Handle both user_id and userId for SDK consistency
        target_user = user_id or kwargs.get("userId")
        
        if not target_user:
            raise ValueError("user_id (or userId) is required for PolliClient.chat()")

        url = f"{self.base_url}/chat"
        headers = self.headers.copy()
        headers["x-user-id"] = target_user
        if app_id:
            headers["X-App-ID"] = app_id
        
        payload = {
            "prompt": prompt,
            "user_id": target_user,
            "model": model
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json().get("response", "")

    async def sync(self, query: str, user_id: Optional[str] = None, content: Optional[str] = None, app_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Synchronize memory and retrieve context in one call."""
        target_user = user_id or kwargs.get("userId")
        if not target_user:
            raise ValueError("user_id (or userId) is required for PolliClient.sync()")

        url = f"{self.base_url}/sync"
        headers = self.headers.copy()
        headers["x-user-id"] = target_user
        if app_id:
            headers["X-App-ID"] = app_id
        
        payload = {
            "query": query,
            "content": content,
            "user_id": target_user
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()

    async def retrieve(self, query: str, user_id: Optional[str] = None, app_id: Optional[str] = None, **kwargs) -> str:
        """Retrieve relevant context for a query."""
        target_user = user_id or kwargs.get("userId")
        if not target_user:
            raise ValueError("user_id (or userId) is required for PolliClient.retrieve()")

        url = f"{self.base_url}/retrieve"
        headers = self.headers.copy()
        headers["x-user-id"] = target_user
        if app_id:
            headers["X-App-ID"] = app_id
        
        payload = {
            "query": query,
            "user_id": target_user
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json().get("context", "")

    async def remember(self, prompt: str, response: str, user_id: Optional[str] = None, app_id: Optional[str] = None, **kwargs) -> Dict[str, str]:
        """Manually trigger memory extraction from an interaction."""
        target_user = user_id or kwargs.get("userId")
        if not target_user:
            raise ValueError("user_id (or userId) is required for PolliClient.remember()")

        url = f"{self.base_url}/remember"
        headers = self.headers.copy()
        headers["x-user-id"] = target_user
        if app_id:
            headers["X-App-ID"] = app_id
        
        payload = {
            "prompt": prompt,
            "response": response,
            "user_id": target_user
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            return resp.json()

    async def get_graph(self, user_id: Optional[str] = None, limit: int = 50, app_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Fetch the current memory graph."""
        target_user = user_id or kwargs.get("userId")
        if not target_user:
            raise ValueError("user_id (or userId) is required for PolliClient.get_graph()")

        url = f"{self.base_url}/graph"
        params = {"limit": limit}
        headers = self.headers.copy()
        headers["x-user-id"] = target_user
        if app_id:
            headers["X-App-ID"] = app_id
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()

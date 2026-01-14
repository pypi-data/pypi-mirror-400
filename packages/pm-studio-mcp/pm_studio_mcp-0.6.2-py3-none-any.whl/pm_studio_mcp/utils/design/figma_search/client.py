"""
Figma API client for making HTTP requests.
"""
import os
import httpx
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class FigmaClient:
    """HTTP client for Figma API."""
    
    BASE_URL = "https://api.figma.com/v1"
    
    def __init__(self):
        self.token = os.getenv("FIGMA_TOKEN")
        if not self.token:
            logger.warning("FIGMA_TOKEN not found in environment variables")
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for Figma API requests."""
        if not self.token:
            raise ValueError("FIGMA_TOKEN is required")
        
        return {
            "X-Figma-Token": self.token,
            "Content-Type": "application/json"
        }
    
    async def get_file(self, file_key: str) -> Dict[str, Any]:
        """Get Figma file data."""
        url = f"{self.BASE_URL}/files/{file_key}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=self._get_headers())
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 403:
                raise Exception("not_found_or_forbidden")
            elif response.status_code == 404:
                raise Exception("not_found_or_forbidden")
            else:
                raise Exception("network_error")
    
    async def get_nodes(self, file_key: str, node_ids: str) -> Dict[str, Any]:
        """Get specific nodes from a Figma file."""
        url = f"{self.BASE_URL}/files/{file_key}/nodes"
        params = {"ids": node_ids}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=self._get_headers(), params=params)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 403:
                raise Exception("not_found_or_forbidden")
            elif response.status_code == 404:
                raise Exception("not_found_or_forbidden")
            else:
                raise Exception("network_error")

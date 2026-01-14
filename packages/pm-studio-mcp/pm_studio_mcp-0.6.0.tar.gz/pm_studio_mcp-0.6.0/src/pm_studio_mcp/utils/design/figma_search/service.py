"""
Figma search service for processing and traversing node trees.
"""
from typing import Dict, List, Optional, Union, Any
import logging

from .client import FigmaClient
from .models import FigmaSearchResult, FigmaError

logger = logging.getLogger(__name__)

# Maximum number of nodes to prevent runaway recursion
MAX_NODES = 20000


class FigmaSearchService:
    """Service for searching and traversing Figma files and nodes."""
    
    def __init__(self):
        self.client = FigmaClient()
        self.node_count = 0
    
    def _normalize_node_id(self, node_id: str) -> str:
        """Convert node ID from URL format (9-5662) to API format (9:5662) if needed."""
        # If it contains hyphens but no colons, convert hyphens to colons
        if '-' in node_id and ':' not in node_id:
            return node_id.replace('-', ':')
        return node_id
    
    def _build_node_link(self, file_key: str, node_id: str) -> str:
        """Build Figma link for a node."""
        encoded_node_id = node_id.replace(":", "%3A")
        return f"https://www.figma.com/file/{file_key}?type=design&node-id={encoded_node_id}"
    
    def _traverse_node(self, node: Dict[str, Any], file_key: str, depth: Union[int, str], current_depth: int = 0) -> Dict[str, Any]:
        """Traverse a node and its children up to specified depth."""
        if self.node_count >= MAX_NODES:
            raise Exception("node_cap_exceeded")
        
        self.node_count += 1
        
        node_id = node.get("id", "")
        node_type = node.get("type", "")
        node_name = node.get("name", node_type)
        
        result = {
            "type": node_type,
            "name": node_name,
            "link": self._build_node_link(file_key, node_id)
        }
        
        # Add characters if it's a TEXT node named "description"
        if node_type == "TEXT" and node_name.lower() == "description":
            characters = node.get("characters")
            if characters:
                result["characters"] = characters
        
        # Include children if depth allows
        should_include_children = (
            (depth == "all") or 
            (isinstance(depth, int) and current_depth < depth)
        )
        
        if should_include_children and "children" in node:
            children = []
            for child in node["children"]:
                child_result = self._traverse_node(child, file_key, depth, current_depth + 1)
                children.append(child_result)
            
            if children:
                result["children"] = children
        
        return result
    
    def _count_nodes(self, node: Dict[str, Any]) -> int:
        """Count total nodes in a tree."""
        count = 1
        if "children" in node:
            for child in node["children"]:
                count += self._count_nodes(child)
        return count
    
    def _count_pages(self, document: Dict[str, Any]) -> int:
        """Count pages (CANVAS nodes) in a document."""
        if not document.get("children"):
            return 0
        
        return len([child for child in document["children"] if child.get("type") == "CANVAS"])
    
    async def search_file(self, file_key: str, depth: Union[int, str] = 1) -> Dict[str, Any]:
        """Search a Figma file from the root document."""
        try:
            self.node_count = 0
            data = await self.client.get_file(file_key)
            
            document = data.get("document")
            if not document:
                return {"error": {"message": "File has no document", "code": "bad_request"}}
            
            # Count total nodes and pages
            total_node_count = self._count_nodes(document)
            page_count = self._count_pages(document)
            
            # Build root node info
            root = {
                "type": document.get("type", "DOCUMENT"),
                "name": document.get("name", "Document"),
                "link": f"https://www.figma.com/file/{file_key}?type=design"
            }
            
            # Process children based on depth
            children = []
            if document.get("children") and depth != 0:
                for child in document["children"]:
                    child_result = self._traverse_node(child, file_key, depth, 1)
                    children.append(child_result)
            
            return {
                "resolved": {
                    "kind": "file",
                    "fileKey": file_key,
                    "nodeId": None,
                    "depth": depth,
                    "nodeCount": total_node_count,
                    "pageCount": page_count
                },
                "root": root,
                "children": children
            }
            
        except Exception as e:
            error_message = str(e)
            if error_message == "not_found_or_forbidden":
                return {"error": {"message": "File not found or access denied", "code": "not_found_or_forbidden"}}
            elif error_message == "network_error":
                return {"error": {"message": "Network error occurred", "code": "network_error"}}
            elif error_message == "node_cap_exceeded":
                return {"error": {"message": f"Node count exceeded maximum limit of {MAX_NODES}", "code": "node_cap_exceeded"}}
            else:
                return {"error": {"message": f"Unexpected error: {error_message}", "code": "network_error"}}
    
    async def search_node(self, file_key: str, node_id: str, depth: Union[int, str] = 1) -> Dict[str, Any]:
        """Search a specific node in a Figma file."""
        try:
            self.node_count = 0
            
            # Normalize node_id format (convert hyphens to colons if needed)
            normalized_node_id = self._normalize_node_id(node_id)
            
            data = await self.client.get_nodes(file_key, normalized_node_id)
            
            nodes = data.get("nodes", {})
            if normalized_node_id not in nodes:
                return {"error": {"message": "Node not found", "code": "invalid_node_id"}}
            
            node = nodes[normalized_node_id]
            if not node or "document" not in node:
                return {"error": {"message": "Invalid node data", "code": "invalid_node_id"}}
            
            node_data = node["document"]
            
            # Count total nodes (just this subtree)
            total_node_count = self._count_nodes(node_data)
            
            # Build root node info (use original node_id for consistency)
            root = {
                "type": node_data.get("type", "NODE"),
                "name": node_data.get("name", node_data.get("type", "Node")),
                "link": self._build_node_link(file_key, normalized_node_id)
            }
            
            # Process children based on depth
            children = []
            if node_data.get("children") and depth != 0:
                for child in node_data["children"]:
                    child_result = self._traverse_node(child, file_key, depth, 1)
                    children.append(child_result)
            
            return {
                "resolved": {
                    "kind": "node",
                    "fileKey": file_key,
                    "nodeId": normalized_node_id,
                    "depth": depth,
                    "nodeCount": total_node_count,
                    "pageCount": 0  # Pages are only counted at file level
                },
                "root": root,
                "children": children
            }
            
        except Exception as e:
            error_message = str(e)
            if error_message == "not_found_or_forbidden":
                return {"error": {"message": "Node not found or access denied", "code": "not_found_or_forbidden"}}
            elif error_message == "network_error":
                return {"error": {"message": "Network error occurred", "code": "network_error"}}
            elif error_message == "node_cap_exceeded":
                return {"error": {"message": f"Node count exceeded maximum limit of {MAX_NODES}", "code": "node_cap_exceeded"}}
            else:
                return {"error": {"message": f"Unexpected error: {error_message}", "code": "network_error"}}
    
    async def search_figma_node(self, file_key: str, search_type: str, node_id: Optional[str] = None, depth: Union[int, str] = 1) -> Dict[str, Any]:
        """Main entry point for Figma node search."""
        # Validate inputs
        if search_type not in ["file", "node"]:
            return {"error": {"message": "search_type must be 'file' or 'node'", "code": "bad_request"}}
        
        if isinstance(depth, int) and depth < 1:
            return {"error": {"message": "depth must be >= 1 or 'all'", "code": "bad_request"}}
        
        if depth != "all" and not isinstance(depth, int):
            return {"error": {"message": "depth must be an integer >= 1 or 'all'", "code": "bad_request"}}
        
        if not file_key:
            return {"error": {"message": "file_key is required", "code": "bad_request"}}
        
        # Handle search type
        if search_type == "file":
            return await self.search_file(file_key, depth)
        else:  # search_type == "node"
            if not node_id:
                return {"error": {"message": "node_id is required for node search", "code": "missing_node_id"}}
            return await self.search_node(file_key, node_id, depth)

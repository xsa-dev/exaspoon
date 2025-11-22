"""Simplified MCP tool client using native spoon_ai MCP tools."""

from __future__ import annotations

import logging
from typing import Any, Optional

from fastmcp.client.transports import SSETransport
from spoon_ai.agents.mcp_client_mixin import MCPClientMixin
from spoon_ai.tools import ToolManager
from spoon_ai.tools.mcp_tool import MCPTool

logger = logging.getLogger(__name__)


class MCPToolClient(MCPClientMixin):
    """Simplified MCP client using native spoon_ai MCP tools.

    This client connects to MCP server via SSE and provides tools
    that can be used by LLM through automatic tool calling.
    """

    def __init__(
        self,
        base_url: str,
        supabase_rest_url: Optional[str] = None,
        supabase_service_key: Optional[str] = None,
    ) -> None:
        """Initialize MCP client with SSE transport and timeout protection."""
        # Convert HTTP URL to SSE endpoint
        sse_url = base_url.rstrip("/")
        if not sse_url.endswith("/sse"):
            sse_url = f"{sse_url}/sse"

        # Add timeout configuration to transport
        transport = SSETransport(sse_url)

        # Initialize MCPClientMixin with transport
        MCPClientMixin.__init__(self, mcp_transport=transport)

        self.base_url = base_url
        self.supabase_rest_url = supabase_rest_url
        self.supabase_service_key = supabase_service_key

        # Cache for tool manager
        self._tool_manager: Optional[ToolManager] = None
        self._connection_timeout = 10.0  # 10-second connection timeout

    def get_tool_manager(self) -> ToolManager:
        """Get or create ToolManager with MCP tools.

        This creates a single MCPTool that can call any tool on the server.
        """
        if self._tool_manager is not None:
            return self._tool_manager

        # Create MCP tool configuration
        mcp_config = {
            "url": self.base_url.rstrip("/") + "/sse",
            "transport": "sse",
        }

        # Create single MCP tool that can call any server tool
        mcp_tool = MCPTool(
            name="exaspoon_db_tools",
            description="Access to ExaSpoon database tools via MCP (create_transaction, search_similar_transactions, upsert_category, etc.)",
            mcp_config=mcp_config,
        )

        self._tool_manager = ToolManager([mcp_tool])
        return self._tool_manager

    # Direct MCP tool methods for backward compatibility
    async def create_transaction(self, **payload: Any) -> Any:
        """Create a transaction via MCP tool."""
        return await self.call_mcp_tool("create_transaction", **payload)

    async def search_similar_transactions(self, query: str, limit: int = 5) -> Any:
        """Search similar transactions via MCP tool."""
        return await self.call_mcp_tool(
            "search_similar_transactions", query=query, limit=limit
        )

    async def upsert_category(self, **payload: Any) -> Any:
        """Upsert category via MCP tool."""
        return await self.call_mcp_tool("upsert_category", **payload)

    async def search_similar_categories(self, query: str, limit: int = 5) -> Any:
        """Search similar categories via MCP tool."""
        return await self.call_mcp_tool(
            "search_similar_categories", query=query, limit=limit
        )

    async def list_accounts(self, **payload: Any) -> Any:
        """List accounts via MCP tool."""
        return await self.call_mcp_tool("list_accounts", **payload)

    async def upsert_account(self, **payload: Any) -> Any:
        """Upsert account via MCP tool."""
        return await self.call_mcp_tool("upsert_account", **payload)

    async def call_mcp_tool(self, tool_name: str, **kwargs: Any) -> Any:
        """Override to add timeout protection."""
        import asyncio
        
        try:
            # Add timeout to MCP tool calls
            result = await asyncio.wait_for(
                super().call_mcp_tool(tool_name, **kwargs),
                timeout=self._connection_timeout
            )
            return result
        except asyncio.TimeoutError:
            logger.error(f"MCP tool '{tool_name}' timed out after {self._connection_timeout}s")
            return {"error": f"Tool '{tool_name}' timed out. MCP server may be unavailable."}
        except Exception as e:
            logger.error(f"MCP tool '{tool_name}' failed: {e}")
            return {"error": f"Tool '{tool_name}' failed: {str(e)}"}

"""HTTP wrapper around MCP server tools.

The real Model Context Protocol runs over stdio. For this MVP we assume an
HTTP bridge (for example `npx mcp-cli serve http`) that exposes endpoints of the
form `POST {base_url}/tools/<tool_name>` with payload `{ "input": {...} }`.
This keeps the Python runtime simple while still documenting how agents call the
MCP server.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

import requests


@dataclass
class MCPDbClient:
    """Very small HTTP client used by agents to reach MCP DB tools."""

    base_url: Optional[str] = None
    supabase_rest_url: Optional[str] = None
    supabase_service_key: Optional[str] = None

    def _require_base(self) -> str:
        if not self.base_url:
            raise RuntimeError("EXASPOON_MCP_URL is not configured")
        return self.base_url.rstrip("/")

    def _post(self, tool_name: str, payload: Dict[str, Any]) -> Any:
        url = f"{self._require_base()}/tools/{tool_name}"
        response = requests.post(url, json={"input": payload}, timeout=30)
        if response.status_code >= 400:
            raise RuntimeError(f"Tool {tool_name} failed: {response.text}")
        data = response.json()
        return data.get("result", data)

    def create_transaction(self, **payload: Any) -> Any:
        return self._post("create_transaction", payload)

    def search_similar_transactions(self, query: str, limit: int = 5) -> Any:
        return self._post(
            "search_similar_transactions", {"query": query, "limit": limit}
        )

    def upsert_category(self, **payload: Any) -> Any:
        return self._post("upsert_category", payload)

    def search_similar_categories(self, query: str, limit: int = 5) -> Any:
        return self._post("search_similar_categories", {"query": query, "limit": limit})

    def list_accounts(self, **payload: Any) -> Any:
        return self._post("list_accounts", payload)

    def upsert_account(self, **payload: Any) -> Any:
        return self._post("upsert_account", payload)

    # Supabase REST passthrough for analytics ---------------------------------
    def _require_supabase(self) -> tuple[str, str]:
        if not (self.supabase_rest_url and self.supabase_service_key):
            raise RuntimeError("Supabase REST credentials are required for analytics")
        return self.supabase_rest_url.rstrip("/"), self.supabase_service_key

    def fetch_transactions_by_period(
        self, start: datetime, end: datetime
    ) -> list[dict[str, Any]]:
        rest_url, service_key = self._require_supabase()
        params = {
            "select": "amount,currency,category_id,occurred_at",
            "and": f"(occurred_at.gte.{start.isoformat()},occurred_at.lt.{end.isoformat()})",
        }
        headers = {
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json",
        }
        response = requests.get(
            f"{rest_url}/transactions", params=params, headers=headers, timeout=30
        )
        if response.status_code >= 400:
            raise RuntimeError(f"Failed to fetch transactions: {response.text}")
        return response.json()

    def fetch_category_lookup(self) -> dict[str, str]:
        rest_url, service_key = self._require_supabase()
        params = {"select": "id,name"}
        headers = {
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
        }
        response = requests.get(
            f"{rest_url}/categories", params=params, headers=headers, timeout=30
        )
        if response.status_code >= 400:
            raise RuntimeError(f"Failed to fetch categories: {response.text}")
        items = response.json()
        return {item["id"]: item["name"] for item in items}

    # Synchronous wrappers for backward compatibility with MCPToolClient
    def upsert_account_sync(self, **payload: Any) -> Any:
        """Synchronous wrapper for upsert_account."""
        return self.upsert_account(**payload)

    def create_transaction_sync(self, **payload: Any) -> Any:
        """Synchronous wrapper for create_transaction."""
        return self.create_transaction(**payload)

    def search_similar_transactions_sync(self, query: str, limit: int = 5) -> Any:
        """Synchronous wrapper for search_similar_transactions."""
        return self.search_similar_transactions(query, limit)

    def search_similar_categories_sync(self, query: str, limit: int = 5) -> Any:
        """Synchronous wrapper for search_similar_categories."""
        return self.search_similar_categories(query, limit)

    @staticmethod
    def supabase_rest_endpoint(project_url: str) -> str:
        return f"{project_url.rstrip('/')}/rest/v1"

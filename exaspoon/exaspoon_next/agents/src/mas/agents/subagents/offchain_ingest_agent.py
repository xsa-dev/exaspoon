"""Agent that ingests off-chain transactions via natural language."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import dateparser
from spoon_ai.agents import SpoonReactAI

from src.common.llm_client import LLMClient
from src.common.tools.mcp_tool_client import MCPToolClient
from src.common.tools.spoonos_style_base import load_prompt


class OffchainIngestAgent(SpoonReactAI):
    """Parses user text and stores a transaction through MCP."""

    def __init__(self, llm: LLMClient, db_client: MCPToolClient) -> None:
        system_prompt = load_prompt("offchain_ingest")
        # Initialize with tools from MCP client
        tool_manager = db_client.get_tool_manager()
        super().__init__(llm=llm, system_prompt=system_prompt, tools=tool_manager)
        self.db = db_client

    async def ingest_freeform(self, text: str) -> Dict[str, Any]:
        occurred_at = self._parse_datetime(text)
        amount, currency = self._parse_amount_currency(text)
        direction = self._infer_direction(text)
        account_name = self._infer_account_name(text)

        # Use MCPToolClient async methods only
        account = await self.db.upsert_account(
            name=account_name,
            type="offchain",
            currency=currency,
            institution="manual-input",
        )
        transaction = await self.db.create_transaction(
            account_id=account["id"],
            amount=amount,
            currency=currency,
            direction=direction,
            occurred_at=occurred_at.isoformat(),
            description=text,
            raw_source="offchain_ingest_agent",
        )

        return {"account": account, "transaction": transaction}

    async def run(self, request: Optional[str] = None) -> str:
        """Let SpoonReactAI handle the ingestion automatically using tools."""
        # The system prompt already contains the ingestion instructions
        # SpoonReactAI will automatically use the available MCP tools
        return await super().run(request)

    def _parse_datetime(self, text: str) -> datetime:
        parsed = dateparser.parse(text, languages=["ru", "en"]) if text else None
        if parsed is None:
            return datetime.now(timezone.utc)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed

    def _parse_amount_currency(self, text: str) -> tuple[float, str]:
        match = re.search(r"(-?\d+[\s\d]*(?:[\.,]\d{1,2})?)", text)
        if not match:
            raise ValueError("Could not determine amount in text")
        amount_str = match.group(1).replace(" ", "").replace(",", ".")
        amount = float(amount_str)
        lower = text.lower()
        currency = "RUB"
        if "€" in text or "euro" in lower:
            currency = "EUR"
        elif "$" in text or "usd" in lower or "dollar" in lower:
            currency = "USD"
        elif "usdt" in lower:
            currency = "USDT"
        return amount, currency

    def _infer_direction(self, text: str) -> str:
        lower = text.lower()
        income_markers = [
            "received",
            "got",
            "income",
            "earned",
            "deposited",
            "credited",
        ]
        if any(word in lower for word in income_markers):
            return "income"
        transfer_markers = ["transferred", "sent", "transfer", "moved"]
        if any(word in lower for word in transfer_markers):
            return "transfer"
        return "expense"

    def _infer_account_name(self, text: str) -> str:
        # English patterns
        match = re.search(r"card\s+(\w+)", text, flags=re.IGNORECASE)
        if match:
            return f"{match.group(1).capitalize()} Card"
        match = re.search(r"account\s+(\w+)", text, flags=re.IGNORECASE)
        if match:
            return f"{match.group(1).capitalize()} Account"
        # Fallback account patterns for backward compatibility
        match = re.search(r"card\s+(\w+)", text, flags=re.IGNORECASE)
        if match:
            return f"{match.group(1).capitalize()} Card"
        match = re.search(r"account\s+(\w+)", text, flags=re.IGNORECASE)
        if match:
            return f"{match.group(1).capitalize()} Account"
        return "OffChain Inbox"

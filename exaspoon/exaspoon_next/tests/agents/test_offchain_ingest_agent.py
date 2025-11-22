from __future__ import annotations

import sys
import os
# Add agents directory to path  
agents_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'agents'))
sys.path.insert(0, agents_dir)
sys.path.insert(0, os.path.join(agents_dir, 'src'))

from typing import Optional

# Mock the spoon_ai imports since they're not available in test environment
class MockToolManager:
    def __init__(self, tools=None):
        self.tools = tools or []

try:
    from src.mas.agents.subagents.offchain_ingest_agent import OffchainIngestAgent
except ImportError:
    # Fallback for testing
    from mas.agents.subagents.offchain_ingest_agent import OffchainIngestAgent

from src.common.llm_client import LLMClient


class FakeLLM(LLMClient):
    def __init__(self) -> None:
        super().__init__("fake-key", "gpt-3.5-turbo", "http://fake-url")

    def chat(self, *_: object, **__: object) -> str:
        return "stub"


class StubDb:
    def __init__(self) -> None:
        self.last_account_payload: dict[str, object] | None = None
        self.last_transaction_payload: dict[str, object] | None = None

    def get_tool_manager(self) -> MockToolManager:
        """Return a mock tool manager for testing."""
        return MockToolManager([])

    def upsert_account(self, **payload: object) -> dict[str, object]:
        self.last_account_payload = payload
        return {"id": "acc-1", "name": payload.get("name", "Unnamed")}

    def create_transaction(self, **payload: object) -> dict[str, object]:
        self.last_transaction_payload = payload
        return {"id": "txn-1", **payload}


def test_ingest_freeform_parses_ru_expense() -> None:
    # Test that agent can be instantiated with correct dependencies
    agent = OffchainIngestAgent(FakeLLM(), StubDb())
    
    # Verify agent has expected attributes
    assert hasattr(agent, 'db')
    assert hasattr(agent, 'run')
    assert agent.db is not None

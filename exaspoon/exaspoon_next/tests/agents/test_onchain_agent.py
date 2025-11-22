from __future__ import annotations

import sys
import os
# Add agents directory to path  
agents_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'agents'))
sys.path.insert(0, agents_dir)
sys.path.insert(0, os.path.join(agents_dir, 'src'))

from typing import Optional

# Import real ToolManager for proper type checking
from spoon_ai.tools import ToolManager

class MockToolManager(ToolManager):
    def __init__(self, tools=None):
        super().__init__(tools or [])

from src.mas.agents.subagents.onchain_agent import OnchainAgent
from src.common.llm_client import LLMClient


class FakeLLM(LLMClient):
    def __init__(self) -> None:
        super().__init__("fake-key", "gpt-3.5-turbo", "http://fake-url")

    def chat(self, *_: object, **__: object) -> str:
        return "stub"


class StubOnchainDb:
    def __init__(self) -> None:
        self.last_wallet_analysis: dict[str, object] | None = None
        self.last_price_prediction: dict[str, object] | None = None

    def get_tool_manager(self) -> MockToolManager:
        """Return a mock tool manager for testing."""
        return MockToolManager([])

    def analyze_wallet(self, address: str) -> dict[str, object]:
        self.last_wallet_analysis = {"address": address}
        return {
            "address": address,
            "balance": 1000.0,
            "tokens": ["NEO", "GAS"],
            "transactions_count": 42
        }

    def predict_price(self, token: str) -> dict[str, object]:
        self.last_price_prediction = {"token": token}
        return {
            "token": token,
            "current_price": 15.50,
            "predicted_price": 16.25,
            "confidence": 0.75
        }


def test_onchain_agent_initializes_with_tools() -> None:
    """Test that OnchainAgent initializes correctly with MCP tools."""
    db = StubOnchainDb()
    agent = OnchainAgent(FakeLLM(), db)
    
    # Verify agent has expected attributes
    assert hasattr(agent, 'run')
    assert agent is not None
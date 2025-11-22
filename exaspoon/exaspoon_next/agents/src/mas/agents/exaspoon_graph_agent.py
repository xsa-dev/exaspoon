"""StateGraph-based EXASPOON orchestrator using proper spoon_ai.graph API."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, TypedDict

from spoon_ai.graph import END, GraphAgent, StateGraph

from src.common.config import Settings
from src.common.llm_client import LLMClient
from src.common.tools.mcp_tool_client import MCPToolClient
from src.mas.agents.subagents import (
    AnalyticsAgent,
    CategorizationAgent,
    OffchainIngestAgent,
    OnchainAgent,
    OntologyAgent,
)


class ExaSpoonState(TypedDict, total=False):
    """State container for EXASPOON graph."""

    input: str
    user_query: str
    intent: str
    routed_agent: str
    routing_reason: str
    routing_confidence: float
    routing_metadata: Dict[str, Any]
    agent_response: str
    execution_log: List[str]
    output: str


@dataclass
class AgentBundle:
    ontology: OntologyAgent
    onchain: OnchainAgent
    offchain_ingest: OffchainIngestAgent
    categorization: CategorizationAgent
    analytics: AnalyticsAgent


class ExaSpoonGraphAgent:
    """EXASPOON orchestrator using StateGraph API with Memory."""

    _INTENT_ROUTE_MAP: Dict[str, str] = {
        "offchain": "offchain_ingest",
        "ingest": "offchain_ingest",
        "expense": "offchain_ingest",
        "analytics": "analytics",
        "report": "analytics",
        "balance": "analytics",
        "onchain": "onchain",
        "defi": "onchain",
        "categor": "categorization",
        "ontology": "ontology",
    }

    _KEYWORD_FALLBACKS: Dict[str, Tuple[str, ...]] = {
        "offchain_ingest": (
            "spent",
            "bought",
            "record",
            "expense",
            "received",
            "deposit",
            "paid",
            "purchased",
            "cost",
            "saved",
            "added",
        ),
        "analytics": (
            "summary",
            "report",
            "balance",
            "total",
            "overview",
            "statement",
            "history",
            "records",
            "insights",
        ),
        "onchain": (
            "defi",
            "wallet",
            "onchain",
            "blockchain",
            "crypto",
            "token",
            "nft",
            "ethereum",
            "bitcoin",
        ),
        "categorization": (
            "category",
            "categorize",
            "classify",
            "organize",
            "group",
            "label",
        ),
    }

    def __init__(
        self,
        settings: Settings,
        persist_session: bool = False,
        use_mcp_tool: bool = True,
    ) -> None:
        llm = LLMClient(
            settings.openai_api_key, settings.model_name, settings.openai_base_url
        )
        # Use native MCP tool client
        db_client = MCPToolClient(
            base_url=settings.mcp_base_url or "http://127.0.0.1:8787",
            supabase_rest_url=settings.supabase_url,
            supabase_service_key=settings.supabase_service_key,
        )

        self.bundle = AgentBundle(
            ontology=OntologyAgent(llm, db_client),
            onchain=OnchainAgent(llm, db_client),
            offchain_ingest=OffchainIngestAgent(llm, db_client),
            categorization=CategorizationAgent(llm, db_client),
            analytics=AnalyticsAgent(llm, db_client),
        )
        self._agent_map: Dict[str, Any] = {
            "ontology": self.bundle.ontology,
            "onchain": self.bundle.onchain,
            "offchain_ingest": self.bundle.offchain_ingest,
            "categorization": self.bundle.categorization,
            "analytics": self.bundle.analytics,
        }
        self._llm = llm
        self._state_graph = self._build_graph()

        # Configure memory path
        if persist_session:
            memory_path = str(Path.home() / ".spoon_ai" / "exaspoon")
            session_id = "exaspoon_cli"
        else:
            # Use temporary in-memory path for stateless mode
            memory_path = str(Path.home() / ".spoon_ai" / "exaspoon" / "temp")
            session_id = "exaspoon_cli_temp"

        self._graph_agent = GraphAgent(
            name="exaspoon_graphagent",
            graph=self._state_graph,
            memory_path=memory_path,
            session_id=session_id,
        )

    async def arun(self, text: str) -> str:
        """Async runner used by CLI/tests."""
        result = await self._graph_agent.run(text)
        # Extract output from state if it's a dict, otherwise return as-is
        if isinstance(result, dict):
            return result.get("output", str(result))
        return str(result)

    def handle_user_message(self, text: str) -> str:
        """Synchronous shim around the async agent."""
        return asyncio.run(self.arun(text))

    def _build_graph(self) -> StateGraph:
        """Create the StateGraph using proper spoon_ai.graph API."""

        def append_log(state: ExaSpoonState, entry: str) -> List[str]:
            log = list(state.get("execution_log", []))
            log.append(entry)
            # keep state history bounded
            return log[-8:]

        async def bootstrap_node(state: ExaSpoonState) -> Dict[str, Any]:
            query = str(state.get("input", "") or "").strip()
            log = append_log(state, f"bootstrap: len={len(query)}")
            return {"user_query": query, "execution_log": log}

        async def intent_node(state: ExaSpoonState) -> Dict[str, Any]:
            query = state.get("user_query", "")
            if not query:
                log = append_log(state, "intent:empty")
                route, reason, confidence, metadata = "ontology", "empty_query", 0.0, {}
                return {
                    "intent": "idle",
                    "routed_agent": route,
                    "routing_reason": reason,
                    "routing_confidence": confidence,
                    "routing_metadata": metadata,
                    "execution_log": log,
                }

            # Use LLM for intent analysis
            intent_prompt = (
                "Determine user intent from the following request. "
                "Choose one category: offchain, ingest, expense, analytics, report, "
                "balance, onchain, defi, categor, ontology. "
                "Return only the category name."
            )
            try:
                messages = [
                    {"role": "system", "content": intent_prompt},
                    {"role": "user", "content": query},
                ]
                # Use async chat method since we're in an async context
                intent_category = await self._llm.achat(messages, temperature=0.2)
                intent_category = intent_category.strip().lower()
            except Exception as exc:
                route, reason, confidence, metadata = self._resolve_route(None, query)
                log = append_log(state, f"intent:error:{exc}")
                return {
                    "intent": "fallback",
                    "routed_agent": route,
                    "routing_reason": reason,
                    "routing_confidence": confidence,
                    "routing_metadata": metadata,
                    "execution_log": log,
                }

            route, reason, confidence, metadata = self._resolve_route_from_intent(
                intent_category, query
            )
            log = append_log(state, f"intent:{intent_category}->{route}")
            return {
                "intent": intent_category,
                "routed_agent": route,
                "routing_reason": reason,
                "routing_confidence": confidence,
                "routing_metadata": metadata,
                "execution_log": log,
            }

        async def dispatch_node(state: ExaSpoonState) -> Dict[str, Any]:
            agent_name = state.get("routed_agent", "ontology")
            query = state.get("user_query", "")
            if not query:
                log = append_log(state, f"dispatch:{agent_name}:skip-empty")
                return {
                    "agent_response": "Please enter a request so I can help you.",
                    "execution_log": log,
                }
            try:
                response = await self._execute_agent(agent_name, query)
                log = append_log(state, f"dispatch:{agent_name}:ok")
            except Exception as exc:
                response = f"Error during agent {agent_name} operation: {exc}"
                log = append_log(state, f"dispatch:{agent_name}:error")
            return {"agent_response": response, "execution_log": log}

        def finalize_node(state: ExaSpoonState) -> Dict[str, Any]:
            agent_name = state.get("routed_agent", "ontology")
            intent = state.get("intent", "unknown")
            response = state.get("agent_response", "Agent did not return a response.")
            log = append_log(state, f"finalize:{agent_name}")
            decorated = f"[agent={agent_name} intent={intent}] {response}"
            return {"output": decorated, "execution_log": log}

        # Build graph using StateGraph API
        graph = StateGraph(ExaSpoonState)

        # Add nodes
        graph.add_node("bootstrap", bootstrap_node)
        graph.add_node("analyze_intent", intent_node)
        graph.add_node("dispatch_agent", dispatch_node)
        graph.add_node("finalize", finalize_node)

        # Add edges
        graph.add_edge("bootstrap", "analyze_intent")
        graph.add_edge("analyze_intent", "dispatch_agent")
        graph.add_edge("dispatch_agent", "finalize")
        graph.add_edge("finalize", END)

        # Set entry point
        graph.set_entry_point("bootstrap")

        return graph

    def _resolve_route_from_intent(
        self, intent_category: str, query: str
    ) -> Tuple[str, str, float, Dict[str, Any]]:
        """Resolve route from intent category."""
        normalized = intent_category.lower()
        for prefix, agent_name in self._INTENT_ROUTE_MAP.items():
            if normalized.startswith(prefix):
                return agent_name, f"intent:{normalized}", 0.8, {}
        # Fallback to keyword routing
        return self._resolve_route(None, query)

    def _resolve_route(
        self,
        intent: Optional[Any],
        query: str,
    ) -> Tuple[str, str, float, Dict[str, Any]]:
        """Decide which downstream agent should be executed."""

        if intent:
            normalized = (getattr(intent, "category", "") or "").lower()
            for prefix, agent_name in self._INTENT_ROUTE_MAP.items():
                if normalized.startswith(prefix):
                    confidence = getattr(intent, "confidence", 0.8)
                    metadata = getattr(intent, "metadata", {})
                    return agent_name, f"intent:{normalized}", confidence, metadata

        keyword_agent = self._keyword_route(query)
        return keyword_agent, "keywords", 0.45, {}

    def _keyword_route(self, query: str) -> str:
        lowered = query.lower()
        for agent_name, keywords in self._KEYWORD_FALLBACKS.items():
            if any(keyword in lowered for keyword in keywords):
                return agent_name
        return "ontology"

    async def _execute_agent(self, agent_name: str, text: str) -> str:
        import asyncio

        from spoon_ai.schema import AgentState

        agent = self._agent_map.get(agent_name, self.bundle.ontology)

        original_max_steps = getattr(agent, "max_steps", 10)
        agent.max_steps = 5  # Reduce from 10 to 5 for faster termination

        # Add infinite loop protection
        try:
            # Run with timeout protection
            result = await asyncio.wait_for(
                agent.run(text),
                timeout=30.0,  # 30-second timeout
            )

            # Check for loop indicators in result
            if isinstance(result, str):
                step_count = result.count("Step ")
                if step_count >= 4:  # If we see 4+ steps, likely inefficient
                    # Try to extract meaningful content
                    lines = result.split("\n")
                    meaningful_lines = [
                        line
                        for line in lines
                        if not line.startswith("Step ") and line.strip()
                    ]
                    if meaningful_lines:
                        return "\n".join(
                            meaningful_lines[-2:]
                        )  # Return last meaningful lines
                    else:
                        return "Agent completed but may have been inefficient. Please try again."

                # Check for stuck patterns
                if "Stuck in loop" in result or "Resetting state" in result:
                    return (
                        "Agent encountered a loop. Please try a more specific request."
                    )

            return result

        except asyncio.TimeoutError:
            # Reset agent state on timeout
            if hasattr(agent, "clear"):
                agent.clear()
            return "Operation timed out. The agent may be stuck. Please try a simpler request."
        except Exception as e:
            # Reset on any error
            if hasattr(agent, "clear"):
                agent.clear()
            return f"Error during processing: {str(e)}. Please try again."
        finally:
            # Restore original max_steps
            if hasattr(agent, "max_steps"):
            if hasattr(agent, 'max_steps'):
                agent.max_steps = original_max_steps

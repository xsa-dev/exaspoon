# UPDATED: Native MCP Integration via tool calling

The project now supports native MCP protocol through `MCPToolClient`, which:
- Uses `SSETransport` to connect to MCP server
- Provides MCP tools through `ToolManager` for automatic tool calling
- Maintains backward compatibility with existing HTTP client

### Usage

By default, `ExaSpoonGraphAgent` uses `MCPToolClient` (can be disabled via `use_mcp_tool=False`):

```python
agent = ExaSpoonGraphAgent(settings, use_mcp_tool=True)  # Default is True
```

### Architecture

1. **MCPToolClient** - new client using `MCPClientMixin` and `SSETransport`
2. **Synchronous Wrappers** - for backward compatibility with existing agents
3. **ToolManager Integration** - ready for automatic tool calling via LLM

---

# MCP Usage Analysis in Project vs Example from spoon-core

## Comparison of Approaches

### Example from spoon-core (SpoonThirdWebagent.py)

**Architecture:**
- Uses `SpoonReactAI` - agent with ReAct pattern
- Uses `MCPClientMixin` for MCP server integration
- Uses `SSETransport` to connect to MCP server
- Uses `ToolManager` for tool management
- MCP tools automatically available to LLM via tool calling

**Key Features:**
```python
class SpoonThirdWebMCP(SpoonReactAI, MCPClientMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        MCPClientMixin.__init__(self, mcp_transport=SSETransport("http://127.0.0.1:8765/sse"))
```

**How it Works:**
1. `SpoonReactAI` automatically gets access to MCP tools via `MCPClientMixin`
2. LLM can automatically call MCP tools during conversation
3. Tools are registered in `ToolManager` and available via tool calling API

### Current Project Implementation

**Architecture:**
- Uses `StateGraph` and `GraphAgent` for agent orchestration
- Uses custom `MCPDbClient` - HTTP client for manual MCP calls
- Agents inherit from `ToolCallAgent` and call MCP tools explicitly in code

**Key Features:**
```python
class OffchainIngestAgent(ToolCallAgent):
    def __init__(self, llm: LLMClient, db_client: MCPDbClient):
        # ...
        self.db = db_client
    
    def run(self, task: str) -> str:
        record = self.ingest_freeform(task)
        # Explicit MCP tool calls via HTTP client
        account = self.db.upsert_account(...)
        transaction = self.db.create_transaction(...)
```

**How it Works:**
1. MCP tools are called explicitly in Python code
2. LLM has no direct access to MCP tools via tool calling
3. All tool call logic is encapsulated in agent methods

## Key Differences

| Aspect | spoon-core Example | Current Project |
|--------|-------------------|-----------------|
| **Agent Pattern** | ReAct (SpoonReactAI) | StateGraph with explicit routing |
| **MCP Access** | Via MCPClientMixin + automatic tool calling | Via HTTP client + explicit calls |
| **LLM Integration** | Automatic via ToolManager | Manual via Python code |
| **MCP Transport** | SSETransport | HTTP requests (not native MCP) |
| **Flexibility** | LLM decides when to call tools | Developer controls all calls |

## Advantages of Current Approach

1. **Explicit Control**: Developer fully controls when and how MCP tools are called
2. **Determinism**: Agent behavior is predictable and easy to debug
3. **Simplicity**: No need to configure tool calling and manage MCP sessions
4. **Agent Graph**: StateGraph allows creating complex workflows with explicit routing

## Advantages of Example Approach

1. **Automation**: LLM can independently decide when to call tools
2. **Flexibility**: Agent can adapt to new tools without code changes
3. **Native MCP**: Uses standard MCP protocol via SSETransport
4. **ReAct Pattern**: Allows agent to "think" and "act" cyclically

## Recommendations

### To Keep Current Approach:
- Current implementation works well for deterministic workflows
- HTTP client works but doesn't use native MCP protocol
- Can be improved by adding SSETransport support to `MCPDbClient`

### To Transition to Example Approach:
1. **For Individual Agents**: Can create agents based on `SpoonReactAI` for tasks requiring flexibility
2. **Hybrid Approach**: Use `StateGraph` for orchestration, but use `SpoonReactAI` agents within nodes
3. **Migration**: Gradually transition agents to use `MCPClientMixin` instead of HTTP client

### Specific Improvements:

1. **Add SSETransport to MCPDbClient:**
```python
from fastmcp.client.transports import SSETransport

class MCPDbClient:
    def __init__(self, base_url: str, use_sse: bool = True):
        if use_sse:
            self._transport = SSETransport(base_url)
            # Use MCPClient instead of requests
        else:
            # Current HTTP implementation
```

2. **Create Hybrid Agent:**
```python
from spoon_ai.agents.spoon_react import SpoonReactAI
from spoon_ai.agents.mcp_client_mixin import MCPClientMixin

class ExaSpoonReactAgent(SpoonReactAI, MCPClientMixin):
    """Agent with automatic MCP tool access"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        MCPClientMixin.__init__(self, mcp_transport=SSETransport(kwargs.get('mcp_url')))
```

3. **Integrate into StateGraph:**
```python
# In ExaSpoonGraphAgent can add node with SpoonReactAI agent
async def react_node(state: ExaSpoonState) -> Dict[str, Any]:
    react_agent = ExaSpoonReactAgent(...)
    response = await react_agent.run(state.get("user_query", ""))
    return {"agent_response": response}
```

## Conclusions

Current implementation is **correct** and well-suited for deterministic workflows with explicit routing. However, if more flexibility and automation are needed, consider using `SpoonReactAI` with `MCPClientMixin` for individual agents or in a hybrid approach.

Key difference: **explicit control vs automation via tool calling**.
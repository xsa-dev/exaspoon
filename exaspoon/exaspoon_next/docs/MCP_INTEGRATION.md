# MCP Integration via tool calling

## Overview

The project currently uses FastMCP on Python for MCP integration, with plans to migrate to a native Rust implementation for enhanced performance and type safety. The current `MCPToolClient` connects to MCP server via SSE and provides tools for automatic tool calling via LLM.

## Current Implementation Status

### Current: FastMCP Python Implementation
- **Status**: ✅ Production-ready and currently deployed
- **Technology**: FastMCP framework on Python
- **Features**: Basic database operations with proven reliability
- **Transport**: HTTP API integration
- **Use Case**: Production environment with stable functionality

### Planned: Rust MCP Server Migration
- **Status**: 🚀 Planned migration for enhanced performance
- **Technology**: Native Rust MCP server using `rmcp` crate
- **Benefits**: Type safety, enhanced performance, compile-time guarantees
- **Transport**: Server-Sent Events (SSE) for better real-time communication
- **Use Case**: Future production with optimized performance

## Migration Benefits

| Aspect | FastMCP Python | Rust MCP Server |
|--------|---------------|-----------------|
| **Performance** | Good | Excellent |
| **Type Safety** | Runtime checks | Compile-time guarantees |
| **Memory Safety** | Manual management | Rust ownership system |
| **Integration** | HTTP API | Native SpoonOS/Neo integration |
| **Reliability** | Proven in production | Expected improvements |

## Architecture

### MCPToolClient

New client (`src/common/tools/mcp_tool_client.py`) that:
- Inherits from `MCPClientMixin` in `spoon_ai`
- Uses `SSETransport` to connect to MCP server
- Provides synchronous wrappers for backward compatibility
- Integrates with `ToolManager` for automatic tool calling

### Usage

By default, `ExaSpoonGraphAgent` uses `MCPToolClient`:

```python
from src.common.config import load_settings
from src.mas.agents.exaspoon_graph_agent import ExaSpoonGraphAgent

settings = load_settings()
# Default use_mcp_tool=True
agent = ExaSpoonGraphAgent(settings)

# Or explicitly specify
agent = ExaSpoonGraphAgent(settings, use_mcp_tool=True)  # Use MCPToolClient
agent = ExaSpoonGraphAgent(settings, use_mcp_tool=False)  # Use old HTTP client
```

### Configuration

MCP server must be available at the URL specified in `EXASPOON_MCP_URL` (default `http://127.0.0.1:8787`).

Client automatically adds `/sse` to URL for SSE endpoint:
- `http://127.0.0.1:8787` → `http://127.0.0.1:8787/sse`
- `http://127.0.0.1:8787/sse` → `http://127.0.0.1:8787/sse` (no change)

### Available Tools

MCP server provides the following tools:
- `create_transaction` - create transaction
- `search_similar_transactions` - search similar transactions
- `upsert_category` - create/update category
- `search_similar_categories` - search similar categories
- `list_accounts` - list accounts
- `upsert_account` - create/update account

### Backward Compatibility

All agents updated to support both clients:
- `OffchainIngestAgent` - uses synchronous wrappers for `MCPToolClient`
- `CategorizationAgent` - uses synchronous wrappers for `MCPToolClient`
- `AnalyticsAgent` - works with both clients

### Automatic Tool Calling

`MCPToolClient` provides `get_tool_manager()`, which can be used for automatic tool calling:

```python
from src.common.tools.mcp_tool_client import MCPToolClient
from spoon_ai.tools import ToolManager

client = MCPToolClient(base_url="http://127.0.0.1:8787")
tool_manager = client.get_tool_manager()

# Tools now available to LLM via tool calling
```

### Differences from HTTP Client

| Aspect | HTTP Client (MCPDbClient) | MCP Client (MCPToolClient) |
|--------|---------------------------|----------------------------|
| Protocol | HTTP POST requests | SSE (Server-Sent Events) |
| Tool calling | No | Yes, via ToolManager |
| Native MCP | No | Yes |
| Synchronous | Synchronous | Asynchronous with sync wrappers |

## Usage Example

```python
from src.common.tools.mcp_tool_client import MCPToolClient

# Create client
client = MCPToolClient(
    base_url="http://127.0.0.1:8787",
    supabase_rest_url="https://your-project.supabase.co/rest/v1",
    supabase_service_key="your-service-key"
)

# Synchronous usage (for backward compatibility)
account = client.upsert_account_sync(
    name="Test Account",
    type="offchain",
    currency="USD"
)

transaction = client.create_transaction_sync(
    account_id=account["id"],
    amount=100.0,
    currency="USD",
    direction="expense",
    occurred_at="2024-01-01T00:00:00Z",
    description="Test transaction"
)

# Asynchronous usage
import asyncio

async def main():
    account = await client.upsert_account(
        name="Test Account",
        type="offchain",
        currency="USD"
    )
    print(account)

asyncio.run(main())
```

## Migration

To migrate existing code:

1. Replace `MCPDbClient` with `MCPToolClient` in initialization
2. Use synchronous wrappers (`_sync` methods) for existing code
3. Or rewrite as async for better performance

## Migration Roadmap

### Phase 1: Current FastMCP Implementation ✅
- FastMCP Python server deployed and operational
- Basic database operations working in production
- HTTP API integration with Python clients
- Proven reliability and stability

### Phase 2: Rust MCP Server Development 🔄
- Native Rust MCP server implementation using `rmcp` crate
- Type-safe database operations
- Enhanced performance benchmarks
- Comprehensive testing and validation

### Phase 3: Migration Planning 📋
- Backward compatibility strategy
- Migration timeline and milestones
- Risk assessment and mitigation
- Production deployment strategy

### Phase 4: Production Migration 🚀
- Gradual migration from FastMCP to Rust
- Performance monitoring and optimization
- Documentation updates and training
- Full production deployment

## Migration Benefits Summary

### Performance Improvements
- **Faster Execution**: Rust's zero-cost abstractions and optimized memory management
- **Better Resource Utilization**: Efficient memory usage and CPU performance
- **Enhanced Concurrency**: Safe multi-threading capabilities

### Type Safety & Reliability
- **Compile-Time Guarantees**: Catch errors at compile time vs runtime
- **Memory Safety**: Rust's ownership system prevents common memory issues
- **Thread Safety**: Built-in protection against data races

### Integration Benefits
- **Native SpoonOS/Neo Integration**: Better alignment with ecosystem
- **Enhanced Tool Calling**: Improved MCP protocol implementation
- **Future-Proof Architecture**: Scalable foundation for new features

## Troubleshooting

### MCP Server Connection Error

Ensure:
- MCP server is running and accessible
- URL is correctly specified in `EXASPOON_MCP_URL`
- SSE endpoint is available (usually `/sse`)

### Error "RuntimeError: EXASPOON_MCP_URL is not configured"

Set environment variable:
```bash
export EXASPOON_MCP_URL=http://127.0.0.1:8787
```

Or add to `.env`:
```
EXASPOON_MCP_URL=http://127.0.0.1:8787
```
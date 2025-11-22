# ExaSpoon2 - Prometheus AI Web Interface

FastAPI-based web interface for ExaSpoon chat agents with session support, MCP integration, SSE streaming, and data visualization for hybrid finance (on-chain + off-chain).

## Features

- **Session-based Agents**: Agent management with initialization status and reinitialization endpoint
- **Streaming Chat**: Server-Sent Events (`/api/chat/stream`) and standard chat (`/api/chat`)
- **Data Visualization**: Live charts - monthly totals, category breakdown, account summaries
- **MCP Integration**: MCP health checks, displaying available tools per session
- **Microservices Architecture**: Separate services for MCP Gateway and FastAPI application
- **Docker Support**: Full containerization with docker-compose
- **Spoon AI SDK**: Integration with proprietary SDK for tools and agents

## Quick Start

### Option 1: Local Development

1. **Install Dependencies**
```bash
# Using uv (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip sync uv.lock

# Or using pip
python -m venv .venv
source .venv/bin/activate
pip install -e .
cd spoon-core && pip install -e . && cd ..
```

2. **Environment Setup**
Create `.env` file in project root:
```env
# OpenAI/OpenRouter
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1  # or your URL
OPENAI_MODEL=gpt-4
EMBEDDING_MODEL=text-embedding-3-small

# Supabase (recommended)
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_service_key

# Additional providers (optional)
ANTHROPIC_API_KEY=your_anthropic_key
GEMINI_API_KEY=your_gemini_key
TAVILY_API_KEY=your_tavily_key

# Local development
PRIVATE_KEY=your_private_key
DATABASE_URL=sqlite:///./spoonai.db
REDIS_HOST=redis
REDIS_PORT=6379
```

3. **Run in Development Mode**
```bash
make dev
# Or manually:
make -j2 dev  # Parallel execution
```

Open `http://localhost:5556/`

### Option 2: Docker

```bash
# Start all services
make docker-dev

# With logs
make docker-dev-logs

# Stop
make docker-stop

# Check status
make docker-status
```

## Architecture

```
exaspoon2/
├── src/                        # Main source code
│   ├── app.py                  # FastAPI server and API endpoints
│   ├── exaspoon_agent.py       # ExaSpoon agent wrapper
│   ├── chart_service.py        # Service for charts and visualization
│   └── exaspoon_mcp_gateway.py # MCP Gateway server
├── spoon-core/                 # Spoon AI SDK
│   ├── spoon_ai/              # Main SDK package
│   │   ├── agents/           # Agents (ReAct, RAG, Custom, etc.)
│   │   ├── tools/            # Tools (Turnkey, NeoFS, Crypto, etc.)
│   │   ├── llm/              # LLM providers and management
│   │   ├── memory/           # Memory management
│   │   ├── payments/         # Payment systems (X402)
│   │   ├── monitoring/       # Monitoring and alerts
│   │   └── graph/            # Graph Engine for complex workflows
│   └── pyproject.toml        # SDK configuration
├── templates/
│   └── page.html             # HTML interface template
├── static/                   # Static files (CSS, JS, images)
├── docker-compose.yaml       # Docker configuration for all services
├── Dockerfile               # Container configuration
├── Makefile                 # Development and deployment commands
├── pyproject.toml           # Project configuration
└── uv.lock                 # Dependencies lock file
```

## API Endpoints

### Core
- `GET /` — Main page (injects session id)
- `POST /api/chat` — Non-streaming chat
- `POST /api/chat/stream` — Server-Sent Events streaming chat
- `GET /api/status` — Agent and MCP status for session
- `GET /api/agent/tools` — List of tools for session
- `POST /api/agent/reinitialize` — Reinitialize agent for session
- `GET /api/sessions` — Active sessions

### Charts and Data
- `GET /api/chart/monthly-totals?months=N` — Monthly totals
- `GET /api/chart/category-breakdown?months=N` — Category breakdown
- `GET /api/chart/accounts` — Account summary

### MCP Gateway (port 8766)
- `GET /` — MCP Gateway health check
- `POST /mcp/call` — MCP tool invocation
- `GET /mcp/tools` — Available tools

## MCP Integration

The project includes MCP Gateway for integration with external tools:

### Built-in Spoon AI Tools:
- **Turnkey**: Crypto wallet and key management
- **NeoFS**: Decentralized storage operations
- **Crypto tools**: Blockchain and cryptocurrency analysis
- **X402 Payment**: Payment system integration
- **Social Media**: Twitter, Telegram, Discord integration
- **Monitoring**: System alerts and monitoring

### Connecting External MCP Servers:
Add to `docker-compose.yaml`:
```yaml
external-mcp:
  image: your-mcp-server
  environment:
    - MCP_SERVER_URL=http://your-mcp-server:port
  networks:
    - exaspoon-network
```

## Development

### Running Tests
```bash
# Syntax and imports
make test-syntax

# Agent tests
make test-agent

# All tests
make test
```

### Working with Code
```bash
# Interactive agent console
make console

# Restart services
make stop && make dev

# Docker commands
make docker-shell          # Shell in FastAPI container
make docker-shell-gateway  # Shell in MCP Gateway container
make docker-logs          # All service logs
```

### Adding New Tools

1. Create tool in `spoon-core/spoon_ai/tools/`
2. Register in `spoon-core/spoon_ai/tools/tool_manager.py`
3. Restart MCP Gateway:
```bash
docker-compose restart mcp-gateway
```

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: OpenAI API key
- `OPENAI_BASE_URL`: OpenAI API base URL
- `OPENAI_MODEL`: Model to use (gpt-4, gpt-3.5-turbo, etc.)
- `SUPABASE_URL/KEY`: Supabase access credentials
- `REDIS_HOST/PORT`: Redis for caching
- `DATABASE_URL`: Database (sqlite/postgres)

### LLM Provider Setup
Multiple providers supported:
- OpenAI (standard)
- OpenRouter (Claude, Llama, etc. models)
- Anthropic Claude
- Google Gemini

## Troubleshooting

### MCP Not Responding
```bash
# Check status
curl http://localhost:8766/

# Restart Gateway
docker-compose restart mcp-gateway

# Check logs
make docker-logs | grep mcp-gateway
```

### Empty Charts
- Load test data via seeds/
- Add transaction via chat: "spent 700₽ on coffee yesterday"
- Check Supabase connection

### Streaming Issues
- Disable AdBlockers for localhost:5556
- Check CORS settings
- Ensure uvicorn logs stream events

### Dependency Issues
```bash
# Full reinstall
rm -rf .venv
uv venv
uv pip sync uv.lock
```

## Requirements

- Python 3.12+
- Redis (optional, for caching)
- Docker & Docker Compose (for containerization)
- Node.js (for frontend development, optional)

## License

MIT License - see [LICENSE](spoon-core/LICENSE) for details

## Contacts and Support

- GitHub Issues: Report problems
- Documentation: `spoon-core/README.md`
- Configuration examples: see `docker-compose.yaml`

---

**ExaSpoon2** - Part of the SpoonAI ecosystem for creating intelligent financial assistants with the ability to work with both on-chain and off-chain data.
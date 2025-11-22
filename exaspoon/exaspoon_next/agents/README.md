# EXASPOON Agents

Python 3.11 multi-agent harness inspired by SpoonOS. The entrypoint is `main.py`, which launches a CLI that routes questions to specialized agents (`ontology`, `onchain`, `offchain_ingest`, `categorization`, `analytics`). The package metadata lives in `pyproject.toml`, so you can `pip install .` or use `uv`.

## Context7 Graph System

`ExaSpoonGraphAgent` is implemented with XSpoonAI's Context7 stack (`spoon_ai.graph`). The graph is defined declaratively via `GraphTemplate`/`NodeSpec` and executed by the SDK's `GraphAgent`, which adds optional persistent memory, intent analysis, and declarative routing. The CLI instantiates the agent in stateless mode so no conversation payloads land on disk. Update `requirements.txt` (or `uv pip sync`) to install `spoon-ai-sdk` before running the CLI.

## Setup

```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env  # or export OPENAI_API_KEY, OPENAI_BASE_URL, SUPABASE_URL, SUPABASE_SERVICE_KEY, EXASPOON_MCP_URL
python -m agents.main
```

With [uv](https://github.com/astral-sh/uv):

```
uv venv
source .venv/bin/activate
uv pip sync requirements.txt  # or `uv pip install .`
python -m agents.main
```

From the repository root you can also rely on the Makefile helpers:

- `make agent-install`
- `make agent-run`
- `make agent-test`

The CLI runs an infinite loop until you type `exit`/`quit`. Agents connect to OpenAI for chat + embeddings and to the MCP DB server via the lightweight HTTP wrapper inside `tools/mcp_db_tool.py`.

## Tests

```
pytest
```

Tests live in `tests/agents/` and exercise ingestion parsing, categorization responses, and analytics rollups by stubbing MCP clients.

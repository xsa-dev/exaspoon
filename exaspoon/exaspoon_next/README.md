# EXASPOON

EXASPOON is a finance + DeFi command center that blends on-chain and off-chain accounts, categorizes activity with embeddings, and exposes a multi-agent control surface. The repo contains three pillars:

1. **SQL migrations** for Supabase/Postgres+pgvector.
2. **`mcp/exaspoon-db-mcp`** – MCP server that exposes typed tools for managing accounts, transactions, and semantic search backed by Supabase.
3. **`agents/`** – Python multi-agent runtime inspired by SpoonOS, featuring a GraphAgent orchestrating specialized sub-agents.

## Getting Started

### 1. Environment

Copy `.env.example` to `.env` (or export variables another way):

```
cp .env.example .env
```

Set the following values:

- `OPENAI_API_KEY` – used for embeddings + LLM calls.
- `OPENAI_BASE_URL` – optional custom endpoint (for Azure/OpenAI-compatible proxies).
- `SUPABASE_URL` / `SUPABASE_SERVICE_KEY` – Supabase Project URL + service role key with pgvector enabled.
- `EXASPOON_MCP_URL` – HTTP bridge endpoint for the MCP server (defaults to `http://127.0.0.1:8787`).

### 2. Database

1. Ensure the `vector` extension is available (Supabase already ships it).
2. Apply the SQL files in order:
   ```
   psql "$SUPABASE_CONNECTION" -f sql/01_enable_pgvector.sql
   psql "$SUPABASE_CONNECTION" -f sql/02_schema_core.sql
   psql "$SUPABASE_CONNECTION" -f sql/03_functions_rag.sql
   ```
   Replace `SUPABASE_CONNECTION` with a connection string or run the scripts via Supabase SQL editor.

### 3. MCP Server (`exaspoon-db-mcp`)

```
cd mcp/exaspoon-db-mcp
cp .env.example .env
cargo run
```

Configure `.env` with:

- `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`
- `OPENAI_API_KEY`
- Optional `OPENAI_BASE_URL` / `OPENAI_BASEURL` (for Azure/proxy endpoints)
- Optional `EMBEDDING_MODEL` (defaults to `text-embedding-3-large`)

The server is now implemented in Rust using the `rmcp` SDK and `supabase-rs`. Use `cargo run --release` (or `cargo build --release`) when you need an optimized binary. It exposes MCP tools such as `create_transaction`, `search_similar_transactions`, `upsert_category`, `search_similar_categories`, `list_accounts`, and `upsert_account`. Configure your MCP-compatible client to connect (e.g., via `npx mcp-cli`).

### 4. Python Agents

```
cd agents
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m agents.main
```

Using [uv](https://github.com/astral-sh/uv) instead of `pip`:

```
cd agents
uv venv
source .venv/bin/activate
uv pip sync requirements.txt  # or `uv pip install .`
uv run python -m agents.main
```

The CLI launches a minimal REPL around the `ExaSpoonGraphAgent`. Type natural language instructions like “вчера с карты тратил 700₽ на кофе” to ingest off-chain transactions or “итоги за май 2024” to request analytics.

Convenience Make targets from the repo root:

- `make agent-install` – install Python requirements
- `make agent-run` – launch the CLI
- `make agent-test` – run pytest

### 5. Tests

From the repo root (virtualenv active):

```
pytest
```

The suite currently covers off-chain ingestion parsing, categorization agent scaffolding, and analytics aggregation.

### Project Layout

```
README.md
.env.example
sql/
  01_enable_pgvector.sql
  02_schema_core.sql
  03_functions_rag.sql
mcp/
  exaspoon-db-mcp/
    Cargo.toml
    .env.example
    src/
      main.rs
      config.rs
      embedding.rs
      models.rs
      server.rs
      supabase.rs
agents/
  requirements.txt
  pyproject.toml
  README.md
  main.py
  config.py
  llm_client.py
  exaspoon_graph_agent.py
  subagents/
    ...
  tools/
    ...
```

## Notes

- Python targets 3.11 with type hints and docstrings for core classes.
- Rust targets the MCP server with `supabase-rs` for database access and the official `rmcp` SDK for transport/tool handling.
- The repository is intentionally lightweight but consistent so you can extend each component quickly.

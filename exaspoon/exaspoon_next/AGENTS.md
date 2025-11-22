# Repository Guidelines

## Language and Localization Policy

**Primary Language**: English is the primary language for all code comments, documentation, prompts, and commit messages.

**Multilingual Support**: 
- All user-facing text and prompts should be written in English first
- Localization can be added as a secondary layer, but English must always be the base language
- Code comments must be in English
- Error messages should be in English
- Agent prompts and system messages must be in English

**Rationale**: 
- Ensures code maintainability across international teams
- Facilitates collaboration and code reviews
- Provides consistent developer experience
- Simplifies debugging and troubleshooting

## Build, Test, and Development Commands

### Python Agents
- **Install dependencies**: `make agent-install` (installs all dependencies including spoon-ai-sdk)
- **Run CLI**: `make agent-run` (launches interactive CLI for working with agents)
- **Run tests**: `make agent-test` (runs all tests) or `pytest tests/agents/test_<name>.py -v`
- **Single test**: `pytest tests/agents/test_offchain_ingest_agent.py::test_function_name -v`
- **Code formatting**: `ruff format .` (formats code)
- **Code linting**: `ruff check . --fix` (checks and fixes code)

### Rust MCP Server
- **Development**: `cd mcp/exaspoon-db-mcp && cargo run` 
- **Production**: `cd mcp/exaspoon-db-mcp && cargo run --release`
- **Build**: `cd mcp/exaspoon-db-mcp && cargo build`

### Database Setup
- **Apply migrations**: Execute SQL files in order from `sql/` directory
- **Migration order**: `01_enable_pgvector.sql` → `02_schema_core.sql` → `03_functions_rag.sql`

### Environment Configuration
- **Copy env file**: `cp .env.example .env`
- **Configure**: Edit `.env` with your API keys and settings
- **Required variables**: `OPENAI_API_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`

### Troubleshooting Installation
- **Python version**: Requires Python 3.12+ (project uses `>=3.12.0,<=3.14`)
- **Dependency conflicts**: If you encounter issues with `neo-mamba`, try:
  ```bash
  # Use uv for dependency management
  USE_UV=1 make agent-install
  ```
- **Virtual environment**: Ensure you're using a clean virtual environment
- **spoon-ai-sdk**: Installed from XSpoonAi/spoon-core GitHub repository

## Code Style & Naming Conventions
- **Python**: Target 3.12+, full type hints, snake_case files/functions, PascalCase classes. Use `ruff format` + `ruff check`.
- **Rust**: Standard `cargo fmt` + `cargo clippy`. Use `snake_case` for functions, `PascalCase` for types.
- **Imports**: Sort with `ruff --select I` (Python) or `rustfmt` (Rust).
- **Error handling**: Use `Result<T>` types (Rust) and explicit exception handling (Python).

## Project Structure
- `agents/src/` – Python multi-agent runtime with MAS (multi-agent system)
- `mcp/exaspoon-db-mcp/` – Rust MCP server for database operations
- `tests/` – Mirror `agents/src/` structure, pytest modules named `test_*.py`
- `prompts/` – Agent prompt templates in Markdown
- `sql/` – Database migrations and schema definitions

## Testing Guidelines
Write pytest tests mirroring source structure. Use stubs/fakes for external dependencies. Maintain ≥85% coverage. Store fixtures in `tests/conftest.py`.

## Migration Notes

### XSpoonAI Context7 Stack Migration
This project has been migrated to use the XSpoonAI Context7 stack:

- **Graph**: StateGraph for orchestration and routing
- **Agents**: SpoonReactAI for automatic tool calling
- **MCP Servers**: Native spoon_ai MCP integration
- **LLM**: LLMManager for unified provider support

### Prompt Migration
All agent prompts should be migrated to English:

1. **Current prompts** are located in `prompts/` directory
2. **Migration process**:
   - Translate existing Russian prompts to English
   - Maintain the same functionality and intent
   - Update agent system prompts accordingly
3. **Priority prompts to migrate**:
   - `offchain_ingest_prompt.md` - Transaction ingestion
   - `analytics_prompt.md` - Financial analytics
   - `categorization_prompt.md` - Transaction categorization
   - `ontology_prompt.md` - Domain ontology
   - `onchain_prompt.md` - Blockchain/DeFi operations

### Code Migration Status
✅ **Completed**:
- All agents migrated from ToolCallAgent to SpoonReactAI
- MCP integration updated to use native spoon_ai tools
- LLM client migrated to LLMManager
- Configuration updated to support config.json + .env
- StateGraph orchestration enhanced

✅ **Completed**:
- Prompt translation to English
- Russian comments and messages translated to English
- Code style compliance with English-first policy
- Updated keyword fallbacks to support both English and Russian

🔄 **In Progress**:
- Test updates for new architecture
- Documentation updates

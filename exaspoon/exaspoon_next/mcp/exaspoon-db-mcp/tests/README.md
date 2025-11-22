# MCP Server Tests

This directory contains tests for the ExaSpoon MCP server.

## Running Tests

### Rust Tests

To run the Rust tests for the MCP server:

```bash
cd mcp/exaspoon-db-mcp
cargo test
```

### Python Tests

To run the Python tests for the MCP bridge:

```bash
cd exaspoon
python -m pytest tests/mcp/test_mcp_bridge.py -v
```

Note: The Python tests may require additional dependencies to be installed first:

```bash
cd agents
pip install -r requirements.txt
```

## Test Structure

- `common/mod.rs` - Common test utilities and mocks
- `test_config.rs` - Tests for configuration loading and validation
- `test_models.rs` - Tests for data models and serialization
- `test_embedding.rs` - Tests for embedding service
- `test_supabase.rs` - Tests for database operations
- `integration_tests.rs` - Integration tests for complete server functionality
- `../tests/mcp/test_mcp_bridge.py` - Integration tests for MCP bridge

## Test Coverage

The tests cover the following functionality:

1. Configuration loading and validation
2. Data model serialization and deserialization
3. Embedding service functionality
4. Database operations (transactions, categories, accounts)
5. Server tool handlers (create transaction, search similar, upsert category/account)
6. MCP bridge HTTP endpoints and server lifecycle
7. Error handling and edge cases

## Troubleshooting

If you encounter issues running the tests:

1. Make sure all dependencies are installed:
   - For Rust: `cargo build` should succeed
   - For Python: `pip install -r requirements.txt` should succeed

2. Check environment variables:
   - Some tests expect specific environment variables to be set
   - Run `cargo test --lib` to skip integration tests if needed

3. For Python test issues:
   - Check that the `mcp` directory is in the Python path
   - Verify all imports are correct
   - Make sure `httpx` is installed for async HTTP testing

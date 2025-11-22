# Exaspoon DB MCP Server

A Supabase-backed MCP server for ExaSpoon with enhanced logging and flexible TLS configuration.

## Features

- Enhanced logging with structured output
- Performance metrics for all operations
- Flexible TLS configuration options
- Semantic search over transactions and categories
- Account and transaction management

## Enhanced Logging

The application includes comprehensive logging to help with monitoring, debugging, and maintenance:

- **Structured Logging**: All logs are structured with timestamps and context fields
- **Performance Metrics**: Each operation includes timing information
- **Configurable Verbosity**: Log levels can be adjusted via environment variables
- **Error Context**: Errors include detailed context for easier debugging
- **Instrumentation**: Key functions use tracing instrumentation for better observability

## TLS Configuration

The application supports flexible TLS configuration to resolve compatibility issues:

### Environment Variables

- `USE_NATIVE_TLS`: Set to `true` to use native TLS instead of rustls (default: false)
- `TLS_MIN_VERSION`: Specify minimum TLS version (default: "1.2")
- `DANGER_ACCEPT_INVALID_CERTS`: Disable certificate verification for testing only (default: false)

### Examples

```bash
# Use native TLS with TLS 1.1
USE_NATIVE_TLS=true TLS_MIN_VERSION=1.1 cargo run

# Disable certificate verification (testing only)
DANGER_ACCEPT_INVALID_CERTS=true cargo run

# Maximum compatibility
USE_NATIVE_TLS=true TLS_MIN_VERSION=1.1 DANGER_ACCEPT_INVALID_CERTS=true cargo run
```

For detailed troubleshooting information, see [TLS_TROUBLESHOOTING.md](TLS_TROUBLESHOOTING.md).

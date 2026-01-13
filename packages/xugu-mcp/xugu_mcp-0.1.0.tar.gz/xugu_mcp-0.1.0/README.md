# XuguDB MCP Server

[![PyPI Version](https://img.shields.io/pypi/v/xugu-mcp)](https://pypi.org/project/xugu-mcp/)
[![Python Version](https://img.shields.io/pypi/pyversions/xugu-mcp)](https://pypi.org/project/xugu-mcp/)
[![License](https://img.shields.io/pypi/l/xugu-mcp)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Model Context Protocol (MCP) server for [XuguDB](https://docs.xugudb.com/content/development/python) (虚谷数据库) with full DDL/DML support, multi-LLM provider integration, and Chat2SQL (natural language to SQL) capabilities.

## Features

- **Full Database Operations**: Support for SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP
- **Schema Introspection**: List tables, describe table structure, view relationships
- **Chat2SQL**: Convert natural language queries to SQL using LLMs (Claude, OpenAI, local models)
- **Multi-LLM Support**: Flexible LLM provider configuration (Claude, OpenAI, zAI/Zhipu, Local/Ollama)
- **Connection Pooling**: Efficient database connection management
- **Audit Logging**: Comprehensive operation logging for security
- **Query Optimization**: EXPLAIN support and optimization suggestions

## Installation

### Prerequisites

- Python 3.11+
- XuguDB database instance
- (Optional) LLM API key for Chat2SQL features

### Install with uv

```bash
# Clone the repository
git clone <repository-url>
cd xugu-mcp

# Install dependencies
uv sync

# Or install in development mode
uv pip install -e ".[dev]"
```

### Install with pip

```bash
pip install -e .
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Key configuration:

```bash
# Database
XUGU_DB_HOST=localhost
XUGU_DB_PORT=5138
XUGU_DB_DATABASE=SYSTEM
XUGU_DB_USER=SYSDBA
XUGU_DB_PASSWORD=your_password

# LLM (for Chat2SQL)
CHAT2SQL_MODE=lightweight  # 'lightweight' (default, no API key) or 'standalone' (requires API key)
LLM_PROVIDER=claude  # or openai, zai, zhipu, local, ollama
LLM_MODEL=claude-3-5-sonnet-20241022
LLM_API_KEY=your_api_key  # Only required for standalone mode
LLM_BASE_URL=  # Optional custom API URL
LLM_TEMPERATURE=0.0
LLM_MAX_TOKENS=4096
```

### Config File

You can also use `config/config.yaml` for configuration (overrides by env vars).

### LLM Providers

The server supports multiple LLM providers for Chat2SQL features:

| Provider | Description | Default Model | API Key Required |
|----------|-------------|---------------|------------------|
| **claude** | Anthropic Claude | claude-3-5-sonnet-20241022 | Yes |
| **openai** | OpenAI GPT | gpt-4o-mini | Yes |
| **zai** | zAI (Zhipu AI / 智谱) | glm-4 | Yes |
| **zhipu** | Same as zai | glm-4 | Yes |
| **local** | Local models via Ollama | llama3.2 | No |
| **ollama** | Same as local | llama3.2 | No |

**Provider-specific notes:**
- **zAI/Zhipu**: API base URL defaults to `https://open.bigmodel.cn/api/paas/v4/`
- **Local/Ollama**: Expects Ollama running at `http://localhost:11434/v1/`

**Chat2SQL Modes:**

#### Lightweight Mode (Default)
- **No LLM API key required**
- MCP provides schema context and SQL validation
- Your existing LLM (Claude in Claude Desktop, etc.) generates the SQL
- Lower latency, better context awareness
- Set `CHAT2SQL_MODE=lightweight` (or leave unset, as it's the default)

#### Standalone Mode
- **Requires LLM_API_KEY** to be configured
- MCP generates SQL using internal LLM
- Useful for API-only access or when client-side LLM is not available
- Set `CHAT2SQL_MODE=standalone` and configure `LLM_API_KEY`

**Chat2SQL Requirements by Mode:**

| Mode | API Key Required | Use Case |
|------|------------------|----------|
| **lightweight** | No | Claude Desktop, local development with LLM |
| **standalone** | Yes | API-only access, remote servers |

**General Notes:**
- Other database operations (query, schema, DML, DDL) work without any LLM configuration
- Cloud providers (claude, openai, zai, zhipu) require `LLM_API_KEY` for standalone mode
- Local providers (local, ollama) do not require API key but need Ollama running

**Available models:**
- Claude: claude-3-5-sonnet, claude-3-5-haiku, claude-3-opus
- OpenAI: gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo
- zAI: glm-4, glm-4-plus, glm-4-air, glm-4-flash
- Local: llama3.2, qwen2.5, mistral, codellama, gemma

## Usage

### Running the Server

The XuguDB MCP Server supports **two transport modes** for different use cases:

---

### Mode 1: Stdio Mode (Local Development)

**Best for:** Local development, Claude Desktop integration

**Transport:** Standard input/output (stdio)

**Startup command:**

```bash
# Using uv (recommended)
uv run xugu-mcp

# Or directly with Python
python -m xugu_mcp.main
```

**How it works:**
- Runs as a local subprocess
- Communicates via stdin/stdout
- Used by Claude Desktop for local MCP connections
- No network port required

---

### Mode 2: HTTP/SSE Mode (Remote/Network)

**Best for:** Remote servers, network access, multiple clients

**Transport:** HTTP with Server-Sent Events (SSE)

**Startup command:**

```bash
# Set environment variables
export XUGU_DB_HOST=your_database_host
export XUGU_DB_PORT=5138
export XUGU_DB_DATABASE=SYSTEM
export XUGU_DB_USER=SYSDBA
export XUGU_DB_PASSWORD=your_password

# Optional: Configure HTTP server
export HTTP_SERVER_HOST=0.0.0.0    # Listen on all interfaces
export HTTP_SERVER_PORT=8000       # HTTP port

# Start HTTP server
uv run xugu-mcp-http

# Or directly with Python
python -m xugu_mcp.http_server
```

**HTTP Server will start on:** `http://0.0.0.0:8000` (default)

**HTTP Endpoints:**
- **SSE Connection:** `http://your-host:8000/sse` - Server-Sent Events for streaming
- **Message POST:** `http://your-host:8000/messages/` - Client message endpoint

**HTTP Server Configuration Options:**

```bash
# Server binding
HTTP_SERVER_HOST=0.0.0.0          # 0.0.0.0 for all interfaces, 127.0.0.1 for local only
HTTP_SERVER_PORT=8000             # HTTP port number

# Security (optional)
HTTP_SERVER_ENABLE_CORS=false     # Enable CORS for web clients
HTTP_SERVER_ENABLE_AUTH=false     # Enable authentication
HTTP_SERVER_AUTH_TOKEN=token      # Authentication token

# Endpoints (usually no need to change)
HTTP_SERVER_SSE_ENDPOINT=/sse     # SSE connection endpoint
HTTP_SERVER_MESSAGE_ENDPOINT=/messages/  # Message POST endpoint
```

---

### Mode Comparison

| Feature | Stdio Mode | HTTP/SSE Mode |
|---------|------------|---------------|
| **Transport** | Standard I/O | HTTP (SSE) |
| **Use Case** | Local development | Remote/network access |
| **Command** | `uv run xugu-mcp` | `uv run xugu-mcp-http` |
| **Port Required** | No | Yes (default: 8000) |
| **Remote Access** | No | Yes |
| **Multiple Clients** | No | Yes |
| **Claude Desktop** | ✅ Native support | ✅ Via URL |
| **Configuration** | `claude_desktop_config.json` | `claude_desktop_config_http.json` |

---

### Claude Desktop Configuration

#### Option 1: Stdio Mode (Local)

Use this for local development with stdio transport:

**Location:** `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)

```json
{
  "mcpServers": {
    "xugu": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/Users/sp/workspace/xugu/xugu-mcp",
        "xugu-mcp"
      ],
      "env": {
        "XUGU_DB_HOST": "10.147.20.226",
        "XUGU_DB_PORT": "5138",
        "XUGU_DB_DATABASE": "SYSTEM",
        "XUGU_DB_USER": "SYSDBA",
        "XUGU_DB_PASSWORD": "SYSDBA",
        "LLM_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

#### Option 2: HTTP/SSE Mode (Remote/Network)

Use this for remote server or when you need network access:

```json
{
  "mcpServers": {
    "xugu-remote": {
      "url": "http://127.0.0.1:8000/sse",
      "transport": "sse"
    }
  }
}
```

**Note:** For HTTP mode, make sure the HTTP server is running before starting Claude Desktop:

```bash
# Terminal 1: Start HTTP server
XUGU_DB_HOST=10.147.20.226 \
XUGU_DB_PORT=5138 \
XUGU_DB_DATABASE=SYSTEM \
XUGU_DB_USER=SYSDBA \
XUGU_DB_PASSWORD=SYSDBA \
uv run xugu-mcp-http

# Terminal 2: Start Claude Desktop (it will connect to the running server)
open -a "Claude Desktop"
```

#### Option 3: Both Modes Simultaneously

You can run both modes at the same time:

```json
{
  "mcpServers": {
    "xugu-local": {
      "command": "uv",
      "args": ["run", "--directory", "/Users/sp/workspace/xugu/xugu-mcp", "xugu-mcp"],
      "env": {
        "XUGU_DB_HOST": "10.147.20.226",
        "XUGU_DB_PORT": "5138",
        "XUGU_DB_DATABASE": "SYSTEM",
        "XUGU_DB_USER": "SYSDBA",
        "XUGU_DB_PASSWORD": "SYSDBA"
      }
    },
    "xugu-remote": {
      "url": "http://127.0.0.1:8000/sse",
      "transport": "sse"
    }
  }
}
```

---

### Quick Start Examples

#### Local Development (Stdio)

```bash
# 1. Configure environment
export XUGU_DB_HOST=10.147.20.226
export XUGU_DB_PORT=5138
export XUGU_DB_DATABASE=SYSTEM
export XUGU_DB_USER=SYSDBA
export XUGU_DB_PASSWORD=SYSDBA

# 2. Start server (stdio mode)
uv run xugu-mcp

# 3. Claude Desktop will automatically connect
```

#### Remote Server (HTTP/SSE)

```bash
# 1. Configure environment
export XUGU_DB_HOST=10.147.20.226
export XUGU_DB_PORT=5138
export XUGU_DB_DATABASE=SYSTEM
export XUGU_DB_USER=SYSDBA
export XUGU_DB_PASSWORD=SYSDBA
export HTTP_SERVER_HOST=0.0.0.0
export HTTP_SERVER_PORT=8000

# 2. Start HTTP server
uv run xugu-mcp-http

# 3. Test SSE endpoint
curl http://localhost:8000/sse

# Expected response:
# event: endpoint
# data: /messages/?session_id=<session_id>

# 4. Configure Claude Desktop to use HTTP URL
# See configuration examples above
```

### Troubleshooting

#### Port Already in Use

```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
export HTTP_SERVER_PORT=8001
uv run xugu-mcp-http
```

#### Connection Refused

```bash
# Check if HTTP server is running
curl http://localhost:8000/sse

# Check server logs for errors
# Make sure XUGU_DB_* variables are set correctly
```

#### Stdio Mode Not Responding

```bash
# Verify the command works
uv run xugu-mcp

# Check Python version (requires 3.11+)
python --version

# Reinstall dependencies if needed
uv sync
```

## MCP Tools

### Query Execution

| Tool | Description |
|------|-------------|
| `execute_query` | Execute SELECT query with optional limit |
| `explain_query` | Get query execution plan |
| `execute_batch` | Execute multiple queries in transaction |

### Schema Introspection

| Tool | Description |
|------|-------------|
| `list_tables` | List all tables with metadata |
| `describe_table` | Get detailed table structure |
| `get_table_stats` | Get table statistics (row count, size) |
| `list_indexes` | List indexes for tables |
| `get_foreign_keys` | Get foreign key relationships |
| `search_tables` | Search tables by name pattern |
| `list_views` | List all database views |
| `list_columns` | Get detailed column information |

### DML Operations

| Tool | Description |
|------|-------------|
| `insert_rows` | Insert single or multiple rows |
| `update_rows` | Update rows matching WHERE clause |
| `delete_rows` | Delete rows matching WHERE clause |
| `upsert_rows` | Insert or update rows (UPSERT) |
| `truncate_table` | Truncate table (fast delete all) |
| `bulk_import` | Bulk import data in batches |

### DDL Operations

| Tool | Description |
|------|-------------|
| `create_database` | Create a new database |
| `drop_database` | Drop a database |
| `create_schema` | Create a new schema |
| `drop_schema` | Drop a schema |
| `create_table` | Create a new table with columns and constraints |
| `drop_table` | Drop a table with optional cascade |
| `alter_table` | Alter table structure (add/drop/alter columns) |
| `create_index` | Create an index on a table |
| `drop_index` | Drop an index |
| `create_view` | Create a view from SELECT statement |
| `drop_view` | Drop a view |
| `backup_table` | Create a backup copy of a table |

### Chat2SQL Operations

Chat2SQL supports two modes:

#### Lightweight Mode (Default)
- **No LLM API key required** - Uses your existing LLM (Claude in Claude Desktop, etc.)
- MCP provides schema context and validation only
- Lower latency, better context awareness

| Tool | Description |
|------|-------------|
| `get_schema_for_llm` | Get database schema for LLM to generate SQL |
| `validate_sql_only` | Validate SQL security and syntax |
| `execute_validated_sql` | Execute validated SELECT queries |
| `get_table_schema_for_llm` | Get detailed table schema |
| `suggest_sql_from_schema` | Validate and improve user SQL |
| `get_lightweight_mode_info` | Get lightweight mode information |

#### Standalone Mode
- **Requires LLM_API_KEY** - MCP generates SQL using internal LLM
- Useful for API-only access

| Tool | Description |
|------|-------------|
| `natural_language_query` | Convert natural language to SQL and execute |
| `explain_sql` | Explain SQL query in natural language |
| `suggest_query` | Suggest SQL for natural language question |
| `validate_sql` | Validate SQL with security checks |
| `optimize_query` | Get optimization suggestions |
| `fix_sql` | Fix SQL based on error message |
| `get_schema_context` | Get relevant schema for query |
| `clear_schema_cache` | Clear schema cache |
| `get_schema_info` | Get schema cache information |

### Security & Audit

| Tool | Description |
|------|-------------|
| `get_audit_log` | Get recent audit log entries |
| `get_audit_statistics` | Get audit statistics for recent period |
| `get_rate_limit_stats` | Get rate limiter statistics |
| `list_roles` | List all available roles |
| `get_role_details` | Get details of a specific role |
| `check_permission` | Check if a role has permission for an operation |
| `get_security_status` | Get overall security status |

### Admin & Management

| Tool | Description |
|------|-------------|
| `health_check` | Perform health check on the MCP server |
| `get_server_metrics` | Get comprehensive server metrics |
| `get_connections` | Get database connection pool information |
| `test_query` | Test database connectivity |
| `get_server_info` | Get server information and configuration |
| `reload_config` | Reload configuration |
| `get_query_history` | Get recent query history from audit log |
| `clear_all_caches` | Clear all server caches |
| `diagnose_connection` | Diagnose database connection issues |

### Database Info

| Tool | Description |
|------|-------------|
| `get_database_info` | Get database version and info |

## MCP Resources

| Resource URI | Description |
|--------------|-------------|
| `schema://database/tables` | Complete table catalog |
| `schema://database/info` | Database metadata |
| `schema://database/relationships` | Foreign key relationships |
| `schema://database/indexes` | All database indexes |
| `schema://database/views` | All view definitions |
| `schema://database/table/{name}` | Specific table schema |
| `meta://database/info` | Database version and config |
| `meta://database/stats` | Database statistics |

## Development Status

### Completed ✅

- **Phase 1**: Foundation framework
  - Project structure with all directories
  - Configuration management with Pydantic
  - Database connection manager with transactions
  - Logging and error handling utilities
  - Basic MCP server with query tools

- **Phase 2**: Query tools and Schema introspection
  - 13 MCP tools (query, schema, database info)
  - 8 MCP resources (tables, relationships, indexes, views, metadata)
  - Schema exploration tools (indexes, foreign keys, views)

- **Phase 3**: DML Operations
  - 6 DML tools (insert, update, delete, upsert, truncate, bulk_import)
  - Single row and batch operations
  - Parameterized WHERE clause support
  - Batch processing for large datasets

- **Phase 4**: DDL Operations
  - 8 DDL tools (create_table, drop_table, alter_table, create_index, drop_index, create_view, drop_view, backup_table)
  - Table and index management
  - View creation and management
  - Table backup functionality

- **Phase 5**: LLM Integration
  - 4 LLM providers (Claude, OpenAI, zAI/Zhipu, Local/Ollama)
  - LLM base interface and provider factory
  - Support for streaming responses
  - Multi-model support per provider

- **Phase 6**: Chat2SQL Engine
  - 9 Chat2SQL tools (NL to SQL, explain, validate, optimize, fix)
  - Schema manager with intelligent caching
  - SQL validator with security checks
  - SQL sanitizer for injection prevention
  - Prompt builder with few-shot learning

- **Phase 7**: Security & Audit
  - 7 Security & Audit tools (audit log, statistics, roles, permissions)
  - Comprehensive audit logging for all operations
  - Rate limiting with sliding window and token bucket
  - Role-based access control (5 predefined roles)
  - Query execution hooks (pre/post/error)
  - Per-client rate limiting
  - Slow query tracking

- **Phase 8**: Production Readiness
  - 9 Admin & Management tools (health check, metrics, diagnostics)
  - System metrics collection (CPU, memory, disk usage)
  - Database connection pool monitoring
  - Query history retrieval from audit log
  - Cache management
  - Connection diagnostics
  - Server information retrieval

### In Progress 🚧

### Planned 📋

## HTTP Deployment

### Production Deployment

For production deployment, it's recommended to use:

1. **Reverse Proxy**: Use Nginx or Traefik as a reverse proxy
2. **Process Manager**: Use systemd, supervisor, or PM2
3. **SSL/TLS**: Enable HTTPS for secure communication

#### Example Nginx Configuration

```nginx
upstream xugu_mcp {
    server localhost:8000;
}

server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location /sse {
        proxy_pass http://xugu_mcp;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
    }

    location /messages/ {
        proxy_pass http://xugu_mcp;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Example Systemd Service

```ini
[Unit]
Description=XuguDB MCP HTTP Server
After=network.target

[Service]
Type=simple
User=xugu
WorkingDirectory=/path/to/xugu-mcp
Environment="PATH=/path/to/uv/.local/bin"
ExecStart=/path/to/uv/.local/bin/uv run xugu-mcp-http
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir uv && \
    uv pip install --system -e .

ENV HTTP_SERVER_HOST=0.0.0.0
ENV HTTP_SERVER_PORT=8000

EXPOSE 8000

CMD ["uv", "run", "xugu-mcp-http"]
```

Build and run:

```bash
docker build -t xugu-mcp .
docker run -d -p 8000:8000 --env-file .env xugu-mcp
```

### Monitoring

The HTTP server exposes several endpoints for monitoring:

- **Health Check**: Use the `health_check` tool
- **Metrics**: Use the `get_server_metrics` tool
- **Audit Log**: Use the `get_audit_log` tool

Example using curl:

```bash
# Health check (if you add a dedicated HTTP endpoint)
curl http://your-host:8000/health

# Get server metrics via MCP tool
# (This requires an MCP client)
```

## Development

### Project Structure

```
xugu-mcp/
├── src/xugu_mcp/
│   ├── main.py              # MCP server entry point (stdio mode)
│   ├── http_server.py       # MCP server entry point (HTTP/SSE mode)
│   ├── config/              # Configuration management
│   ├── db/                  # Database connection & operations
│   ├── llm/                 # LLM provider implementations
│   ├── chat2sql/            # Chat2SQL engine
│   ├── mcp_tools/           # MCP tool implementations
│   ├── mcp_resources/       # MCP resource implementations
│   ├── security/            # Security & audit
│   └── utils/               # Utilities
├── config/                  # Configuration files
├── tests/                   # Test suite
└── pyproject.toml           # Project configuration
```

### Running Tests

```bash
uv run pytest
```

### Code Quality

```bash
# Format code
uv run black src/

# Lint
uv run ruff check src/

# Type check
uv run mypy src/
```

## Security

- **SQL Injection Prevention**: Parameterized queries and input validation
- **Audit Logging**: All database operations are logged
- **Rate Limiting**: Configurable query rate limits
- **Connection Security**: SSL/TLS support for database connections

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## References

- [XuguDB Python Documentation](https://docs.xugudb.com/content/development/python)
- [Model Context Protocol](https://modelcontextprotocol.io/docs/)

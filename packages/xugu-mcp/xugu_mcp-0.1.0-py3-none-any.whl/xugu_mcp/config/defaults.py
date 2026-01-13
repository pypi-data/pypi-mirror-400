"""
Default configuration values for XuguDB MCP Server.

These defaults can be overridden by environment variables or config.yaml.
"""

# Default configuration structure (used for config.yaml generation)
DEFAULT_CONFIG = {
    "server": {
        "name": "xugu-mcp-server",
        "version": "0.1.0",
        "log_level": "INFO",
        "host": "localhost",
        "port": 8000,
    },
    "database": {
        "host": "localhost",
        "port": 5138,
        "database": "SYSTEM",
        "user": "SYSDBA",
        "password": "",  # Use XUGU_DB_PASSWORD env var in production
        "charset": "utf8",
        "usessl": "off",
        "pool": {
            "min_size": 2,
            "max_size": 10,
            "max_overflow": 5,
            "timeout": 30,
        },
    },
    "llm": {
        "provider": "claude",
        "model": "claude-3-5-sonnet-20241022",
        "temperature": 0.0,
        "max_tokens": 4096,
        "timeout": 60,
        "claude": {
            "api_key": "",  # Use LLM_API_KEY env var
            "api_url": "https://api.anthropic.com",
        },
        "openai": {
            "api_key": "",  # Use LLM_API_KEY env var
            "api_url": "https://api.openai.com/v1",
            "model": "gpt-4",
        },
        "local": {
            "api_url": "http://localhost:11434",  # Ollama default
            "model": "llama2",
        },
    },
    "chat2sql": {
        "enable_schema_cache": True,
        "schema_cache_ttl": 3600,
        "use_examples": True,
        "max_examples": 3,
        "enable_validation": True,
        "allow_ddl": True,
        "suggest_optimizations": True,
    },
    "security": {
        "enable_audit_log": True,
        "audit_log_path": "/var/log/xugu-mcp/audit.log",
        "allowed_operations": [
            "SELECT",
            "INSERT",
            "UPDATE",
            "DELETE",
            "CREATE",
            "ALTER",
            "DROP",
        ],
        "blocked_patterns": [
            "DROP DATABASE",
            "ALTER SYSTEM",
        ],
        "rate_limit_enabled": False,
        "rate_limit_max_queries": 100,
        "max_query_execution_time": 300,
        "result_set_max_rows": 10000,
    },
}

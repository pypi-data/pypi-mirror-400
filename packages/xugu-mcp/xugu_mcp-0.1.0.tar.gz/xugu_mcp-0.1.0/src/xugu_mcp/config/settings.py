"""
Configuration management for XuguDB MCP Server.

Uses Pydantic Settings for environment-based configuration with validation.
"""
from typing import Literal, Optional, ClassVar
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class XuguDBConfig(BaseSettings):
    """XuguDB database connection configuration."""

    host: str = Field(default="localhost", description="Database host address")
    port: int = Field(default=5138, description="Database port", ge=1, le=65535)
    database: str = Field(default="SYSTEM", description="Database name")
    user: str = Field(default="SYSDBA", description="Database user")
    password: str = Field(default="", description="Database password")
    charset: str = Field(default="utf8", description="Character encoding")
    usessl: str = Field(default="off", description="SSL connection (on/off/true/false)")

    # Connection pool settings
    pool_min_size: int = Field(default=2, description="Minimum pool size", ge=0)
    pool_max_size: int = Field(default=10, description="Maximum pool size", ge=1)
    pool_max_overflow: int = Field(default=5, description="Maximum overflow connections", ge=0)
    pool_timeout: int = Field(default=30, description="Connection timeout (seconds)", ge=1)

    @field_validator("usessl")
    @classmethod
    def normalize_usessl(cls, v: str) -> str:
        """Normalize SSL setting to 'on' or 'off'."""
        if v.lower() in ("true", "on", "yes"):
            return "on"
        return "off"

    model_config = SettingsConfigDict(
        env_prefix="XUGU_DB_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class LLMConfig(BaseSettings):
    """LLM provider configuration."""

    provider: Literal["claude", "openai", "zai", "zhipu", "local", "ollama"] = Field(
        default="claude",
        description="LLM provider (claude, openai, zai, zhipu, local, ollama)"
    )
    model: str = Field(default="claude-3-5-sonnet-20241022", description="Model name")
    api_key: Optional[str] = Field(default=None, description="API key for the provider")
    base_url: Optional[str] = Field(default=None, description="Custom API base URL")
    temperature: float = Field(default=0.0, description="Temperature for generation", ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, description="Maximum tokens to generate", ge=1)

    # Provider-specific settings
    timeout: int = Field(default=60, description="Request timeout (seconds)", ge=1)

    # Default models per provider (class variable)
    DEFAULT_MODELS: ClassVar[dict[str, str]] = {
        "claude": "claude-3-5-sonnet-20241022",
        "openai": "gpt-4o-mini",
        "zai": "glm-4",
        "zhipu": "glm-4",
        "local": "llama3.2",
        "ollama": "llama3.2",
    }

    def get_default_model(self) -> str:
        """Get default model for the current provider."""
        return self.DEFAULT_MODELS.get(self.provider, self.model)

    def is_configured(self) -> bool:
        """Check if LLM is properly configured.

        Returns True if:
        - Provider is local/ollama (no API key needed), or
        - Provider is cloud-based and API key is set
        """
        if self.provider in ("local", "ollama"):
            return True
        return bool(self.api_key)

    model_config = SettingsConfigDict(
        env_prefix="LLM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class Chat2SQLConfig(BaseSettings):
    """Chat2SQL engine configuration."""

    # Chat2SQL mode
    mode: Literal["lightweight", "standalone"] = Field(
        default="lightweight",
        description="""
        Chat2SQL mode:
        - lightweight: MCP provides schema + validation only; client LLM generates SQL (no API key needed)
        - standalone: MCP generates SQL using internal LLM (requires LLM_API_KEY configuration)
        """
    )

    # Schema caching
    enable_schema_cache: bool = Field(default=True, description="Enable schema caching")
    schema_cache_ttl: int = Field(default=3600, description="Schema cache TTL (seconds)", ge=0)

    # Few-shot examples
    use_examples: bool = Field(default=True, description="Use few-shot examples")
    max_examples: int = Field(default=3, description="Maximum few-shot examples", ge=0, le=10)

    # SQL validation
    enable_validation: bool = Field(default=True, description="Enable SQL validation")
    allow_ddl: bool = Field(default=True, description="Allow DDL operations")

    # Query optimization
    suggest_optimizations: bool = Field(default=True, description="Suggest query optimizations")

    model_config = SettingsConfigDict(
        env_prefix="CHAT2SQL_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class SecurityConfig(BaseSettings):
    """Security and audit configuration."""

    # Audit logging
    enable_audit_log: bool = Field(default=True, description="Enable audit logging")
    audit_log_path: str = Field(default="./logs/audit.log", description="Audit log file path")

    # SQL restrictions
    allowed_operations: list[str] = Field(
        default=["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP"],
        description="Allowed SQL operations"
    )
    blocked_patterns: list[str] = Field(
        default=["DROP DATABASE", "ALTER SYSTEM"],
        description="Blocked SQL patterns"
    )

    # Rate limiting
    rate_limit_enabled: bool = Field(default=False, description="Enable rate limiting")
    rate_limit_max_queries: int = Field(default=100, description="Max queries per minute", ge=1)

    # Query limits
    max_query_execution_time: int = Field(default=300, description="Max query time (seconds)", ge=1)
    result_set_max_rows: int = Field(default=10000, description="Max result rows", ge=1)

    model_config = SettingsConfigDict(
        env_prefix="SECURITY_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class MCPServerConfig(BaseSettings):
    """MCP server configuration."""

    name: str = Field(default="xugu-mcp-server", description="Server name")
    version: str = Field(default="0.1.0", description="Server version")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level"
    )

    model_config = SettingsConfigDict(
        env_prefix="MCP_SERVER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class HTTPServerConfig(BaseSettings):
    """HTTP/SSE server configuration."""

    # Server settings
    host: str = Field(default="0.0.0.0", description="HTTP server host (0.0.0.0 for all interfaces)")
    port: int = Field(default=8000, description="HTTP server port", ge=1, le=65535)

    # CORS settings
    enable_cors: bool = Field(default=False, description="Enable CORS")
    cors_origins: list[str] = Field(
        default=["*"],
        description="Allowed CORS origins"
    )

    # SSE settings
    sse_endpoint: str = Field(default="/sse", description="SSE endpoint path")
    message_endpoint: str = Field(default="/messages/", description="Message POST endpoint path")

    # Security
    enable_auth: bool = Field(default=False, description="Enable authentication")
    auth_token: Optional[str] = Field(default=None, description="Authentication token")

    model_config = SettingsConfigDict(
        env_prefix="HTTP_SERVER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class Settings(BaseSettings):
    """Global application settings."""

    xugu: XuguDBConfig = Field(default_factory=XuguDBConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    chat2sql: Chat2SQLConfig = Field(default_factory=Chat2SQLConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    mcp_server: MCPServerConfig = Field(default_factory=MCPServerConfig)
    http: HTTPServerConfig = Field(default_factory=HTTPServerConfig)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get global settings instance (singleton)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings():
    """Reset settings (useful for testing)."""
    global _settings
    _settings = None

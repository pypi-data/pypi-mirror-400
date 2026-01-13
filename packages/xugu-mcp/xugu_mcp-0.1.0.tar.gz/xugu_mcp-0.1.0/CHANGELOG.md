# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-01-05

### Added
- Initial release of XuguDB MCP Server
- Full DDL/DML support for XuguDB (虚谷数据库)
- Schema introspection tools (list_tables, describe_table, get_table_stats, etc.)
- Chat2SQL functionality with lightweight and standalone modes
- Multi-LLM provider support (Claude, OpenAI, zAI/Zhipu, Local/Ollama)
- Connection pooling and management
- Comprehensive audit logging and security features
- Rate limiting and role-based access control
- HTTP/SSE server mode for remote access
- Stdio mode for local development and Claude Desktop integration
- Cross-platform xgcondb driver support (Windows, macOS, Linux x86_64/ARM64)

### MCP Tools (50+ tools)
- Query Execution: execute_query, explain_query, execute_batch
- Schema Introspection: list_tables, describe_table, list_columns, list_indexes, etc.
- DML Operations: insert_rows, update_rows, delete_rows, upsert_rows, bulk_import
- DDL Operations: create_table, drop_table, alter_table, create_index, drop_index, etc.
- Chat2SQL (Lightweight): get_schema_for_llm, validate_sql_only, execute_validated_sql
- Chat2SQL (Standalone): natural_language_query, explain_sql, suggest_query, optimize_query
- Security & Audit: get_audit_log, get_audit_statistics, get_security_status
- Admin & Management: health_check, get_server_metrics, diagnose_connection

### Security
- SQL injection prevention with parameterized queries
- Comprehensive audit logging for all operations
- Rate limiting with configurable thresholds
- Role-based access control (5 predefined roles)

### Documentation
- Complete README with installation and configuration instructions
- Claude Desktop configuration examples for stdio and HTTP/SSE modes
- Production deployment guides (Nginx, systemd, Docker)

[Unreleased]: https://github.com/xugudb/xugu-mcp/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/xugudb/xugu-mcp/releases/tag/v0.1.0

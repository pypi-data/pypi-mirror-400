"""
Schema Manager for Chat2SQL engine.

Handles schema extraction, caching, and retrieval for context building.
"""
import hashlib
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from ..db import operations
from ..config.settings import get_settings
from ..utils.logging import get_logger
from ..mcp_tools import schema_tools

logger = get_logger(__name__)


@dataclass
class TableSchema:
    """Schema information for a table."""

    table_name: str
    columns: List[Dict[str, Any]]
    primary_keys: List[str]
    foreign_keys: List[Dict[str, Any]]
    indexes: List[Dict[str, Any]]
    row_count: int = 0
    sample_data: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "table_name": self.table_name,
            "columns": self.columns,
            "primary_keys": self.primary_keys,
            "foreign_keys": self.foreign_keys,
            "indexes": self.indexes,
            "row_count": self.row_count,
            "sample_data": self.sample_data,
        }


@dataclass
class DatabaseSchema:
    """Complete database schema."""

    schema_name: str
    tables: Dict[str, TableSchema] = field(default_factory=dict)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "schema_name": self.schema_name,
            "tables": {
                name: table.to_dict()
                for name, table in self.tables.items()
            },
            "relationships": self.relationships,
            "last_updated": self.last_updated.isoformat(),
        }


class SchemaManager:
    """Manager for database schema with caching."""

    def __init__(self, cache_ttl: int = 3600):
        """Initialize schema manager.

        Args:
            cache_ttl: Cache time-to-live in seconds
        """
        self.cache_ttl = cache_ttl
        self._schema_cache: Optional[DatabaseSchema] = None
        self._table_cache: Dict[str, TableSchema] = {}
        self._cache_timestamp: Optional[datetime] = None
        self.settings = get_settings()

    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid."""
        if self._cache_timestamp is None:
            return False
        age = datetime.now() - self._cache_timestamp
        return age < timedelta(seconds=self.cache_ttl)

    def _generate_cache_key(self, query: str) -> str:
        """Generate cache key for a query."""
        return hashlib.md5(query.encode()).hexdigest()

    async def get_database_schema(
        self,
        force_refresh: bool = False,
        include_system: bool = False,
    ) -> DatabaseSchema:
        """Get complete database schema.

        Args:
            force_refresh: Force refresh of cache
            include_system: Include system tables

        Returns:
            DatabaseSchema object
        """
        if not force_refresh and self._is_cache_valid() and self._schema_cache:
            return self._schema_cache

        try:
            schema_name = self.settings.xugu.database
            tables_list = operations.list_tables(schema_name, include_system)

            tables = {}
            relationships = []

            for table_info in tables_list:
                table_name = table_info["table_name"]

                # Skip if table_name is None
                if table_name is None:
                    continue

                # Skip system tables if not requested
                if not include_system and table_name.startswith("SYS_"):
                    continue

                try:
                    table_schema = await self.get_table_schema(table_name, force_refresh)
                    tables[table_name] = table_schema

                    # Collect relationships
                    for fk in table_schema.foreign_keys:
                        relationships.append({
                            "from_table": table_name,
                            "to_table": fk.get("referenced_table"),
                            "from_columns": fk.get("columns", []),
                            "to_columns": fk.get("referenced_columns", []),
                        })

                except Exception as e:
                    logger.warning(f"Failed to get schema for {table_name}: {e}")
                    continue

            self._schema_cache = DatabaseSchema(
                schema_name=schema_name,
                tables=tables,
                relationships=relationships,
                last_updated=datetime.now(),
            )
            self._cache_timestamp = datetime.now()

            return self._schema_cache

        except Exception as e:
            logger.error(f"Failed to get database schema: {e}")
            # Return cached schema if available
            if self._schema_cache:
                return self._schema_cache
            raise

    async def get_table_schema(
        self,
        table_name: str,
        force_refresh: bool = False,
    ) -> TableSchema:
        """Get schema for a specific table.

        Args:
            table_name: Name of the table
            force_refresh: Force refresh of cache

        Returns:
            TableSchema object
        """
        cache_key = table_name

        if not force_refresh and cache_key in self._table_cache:
            return self._table_cache[cache_key]

        try:
            # Get column information
            columns_info = operations.get_table_info(table_name)
            columns = []

            for col in columns_info.get("columns", []):
                columns.append({
                    "name": col.get("column_name"),
                    "type": col.get("data_type"),
                    "nullable": col.get("is_nullable", True),  # Now boolean
                    "default": col.get("column_default"),
                    "comment": col.get("comments", ""),
                })

            # Get primary keys from get_table_info result
            primary_keys = columns_info.get("primary_key", [])
            # Also check if there are any columns marked as primary key in comments (legacy)
            for col in columns:
                comment = col.get("comment", "")
                if comment and isinstance(comment, str) and comment.lower() == "primary key":
                    pk_col = col.get("name")
                    if pk_col and pk_col not in primary_keys:
                        primary_keys.append(pk_col)

            # Get foreign keys
            foreign_keys = []
            try:
                fk_result = await self._get_foreign_keys(table_name)
                foreign_keys = fk_result
            except Exception:
                pass

            # Get indexes
            indexes = []
            try:
                idx_result = await schema_tools.list_indexes(table_name)
                if idx_result.get("success"):
                    indexes_data = idx_result.get("indexes", [])
                    indexes = indexes_data if isinstance(indexes_data, list) else []
            except Exception:
                pass

            # Get row count
            row_count = 0
            try:
                count_result = operations.execute_query(
                    f"SELECT COUNT(*) FROM {table_name}"
                )
                if count_result.rows:
                    row_count = count_result.rows[0][0] if count_result.rows[0] else 0
            except Exception:
                pass

            # Get sample data (first 3 rows)
            sample_data = []
            try:
                sample_result = operations.execute_query(
                    f"SELECT * FROM {table_name} LIMIT 3"
                )
                if sample_result.rows and sample_result.columns:
                    for row in sample_result.rows[:3]:
                        row_dict = {}
                        for i, col_name in enumerate(sample_result.columns):
                            row_dict[col_name] = row[i] if i < len(row) else None
                        sample_data.append(row_dict)
            except Exception:
                pass

            table_schema = TableSchema(
                table_name=table_name,
                columns=columns,
                primary_keys=primary_keys,
                foreign_keys=foreign_keys,
                indexes=indexes,
                row_count=row_count,
                sample_data=sample_data,
            )

            self._table_cache[cache_key] = table_schema
            return table_schema

        except Exception as e:
            logger.error(f"Failed to get table schema for {table_name}: {e}")
            raise

    async def get_relevant_tables(
        self,
        query: str,
        limit: int = 10,
    ) -> List[str]:
        """Get relevant tables for a natural language query.

        Args:
            query: Natural language query
            limit: Maximum number of tables to return

        Returns:
            List of relevant table names
        """
        # Simple keyword matching - can be enhanced with embeddings
        query_lower = query.lower()

        schema = await self.get_database_schema()
        table_scores = []

        for table_name, table_schema in schema.tables.items():
            # Skip if table_name is None
            if table_name is None:
                continue

            score = 0

            # Check table name match
            if table_name.lower() in query_lower:
                score += 10

            # Check column names match
            for col in table_schema.columns:
                col_name = col.get("name")
                if col_name is None:
                    continue
                col_name_lower = col_name.lower()
                if col_name_lower in query_lower:
                    score += 2

            table_scores.append((table_name, score))

        # Sort by score and return top tables
        table_scores.sort(key=lambda x: x[1], reverse=True)
        return [name for name, score in table_scores[:limit] if score > 0]

    async def get_schema_context(
        self,
        query: str,
        max_tables: int = 5,
    ) -> Dict[str, Any]:
        """Get schema context for a query.

        Args:
            query: Natural language query
            max_tables: Maximum tables to include

        Returns:
            Schema context dictionary
        """
        relevant_tables = await self.get_relevant_tables(query, max_tables)

        context = {
            "query": query,
            "relevant_tables": [],
            "relationships": [],
        }

        schema = await self.get_database_schema()

        for table_name in relevant_tables[:max_tables]:
            if table_name in schema.tables:
                table_schema = schema.tables[table_name]
                context["relevant_tables"].append(table_schema.to_dict())

        # Add relevant relationships
        table_names_set = set(relevant_tables[:max_tables])
        for rel in schema.relationships:
            if rel["from_table"] in table_names_set or rel["to_table"] in table_names_set:
                context["relationships"].append(rel)

        return context

    def clear_cache(self):
        """Clear all cached schema data."""
        self._schema_cache = None
        self._table_cache.clear()
        self._cache_timestamp = None
        logger.info("Schema cache cleared")

    async def _get_foreign_keys(self, table_name: str) -> List[Dict[str, Any]]:
        """Get foreign key information for a table.

        Args:
            table_name: Name of the table

        Returns:
            List of foreign key definitions
        """
        # This would typically query the database's foreign key constraints
        # For now, return empty list as implementation depends on XuguDB's metadata tables
        return []

    def get_schema_summary(self) -> Dict[str, Any]:
        """Get summary of cached schema.

        Returns:
            Schema summary
        """
        if self._schema_cache:
            return {
                "schema_name": self._schema_cache.schema_name,
                "table_count": len(self._schema_cache.tables),
                "relationship_count": len(self._schema_cache.relationships),
                "last_updated": self._schema_cache.last_updated.isoformat(),
                "cache_age_seconds": (
                    datetime.now() - self._cache_timestamp
                ).total_seconds() if self._cache_timestamp else None,
            }
        return {
            "schema_name": None,
            "table_count": 0,
            "relationship_count": 0,
            "last_updated": None,
            "cache_age_seconds": None,
        }

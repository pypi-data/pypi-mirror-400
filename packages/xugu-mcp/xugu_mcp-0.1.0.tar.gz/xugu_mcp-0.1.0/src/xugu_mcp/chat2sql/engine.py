"""
Chat2SQL Engine - Natural Language to SQL conversion.

Main engine that orchestrates schema management, SQL generation,
validation, and execution.
"""
import re
from typing import Dict, Any, List
from dataclasses import dataclass

from ..llm import LLMProviderFactory, LLMMessage, LLMResponse
from ..llm.base import BaseLLMProvider
from ..config.settings import get_settings
from ..utils.logging import get_logger

from .schema_manager import SchemaManager
from .sql_validator import SQLValidator, ValidationResult
from .sql_sanitizer import SQLSanitizer
from .prompt_builder import PromptBuilder

logger = get_logger(__name__)


@dataclass
class Chat2SQLResult:
    """Result of natural language to SQL conversion."""

    question: str
    sql: str
    is_valid: bool
    explanation: str | None = None
    validation_result: ValidationResult | None = None
    execution_result: Any | None = None
    error: str | None = None


@dataclass
class SQLOptimizationResult:
    """Result of SQL optimization analysis."""

    sql: str
    suggestions: List[str]
    optimized_sql: str | None = None
    explanation: str | None = None


class Chat2SQLEngine:
    """Engine for converting natural language to SQL."""

    def __init__(
        self,
        llm_provider: BaseLLMProvider | None = None,
        cache_ttl: int = 3600,
    ):
        """Initialize Chat2SQL engine.

        Args:
            llm_provider: LLM provider to use (creates from settings if None)
            cache_ttl: Schema cache TTL in seconds
        """
        self.settings = get_settings()
        self.schema_manager = SchemaManager(cache_ttl=cache_ttl)
        self.validator = SQLValidator()
        self.sanitizer = SQLSanitizer()
        self.prompt_builder = PromptBuilder(
            max_examples=self.settings.chat2sql.max_examples,
        )

        # Create LLM provider if not provided
        if llm_provider is None:
            llm_config = {
                "provider": self.settings.llm.provider,
                "api_key": self.settings.llm.api_key or "",
                "model": self.settings.llm.model,
                "temperature": self.settings.llm.temperature,
                "max_tokens": self.settings.llm.max_tokens,
                "timeout": self.settings.llm.timeout,
                "base_url": self.settings.llm.base_url,
            }
            llm_provider = LLMProviderFactory.create_from_dict(llm_config)

        self.llm = llm_provider

    async def natural_language_to_sql(
        self,
        question: str,
        validate: bool = True,
        sanitize: bool = True,
    ) -> Chat2SQLResult:
        """Convert natural language question to SQL.

        Args:
            question: Natural language question
            validate: Whether to validate the generated SQL
            sanitize: Whether to sanitize the generated SQL

        Returns:
            Chat2SQLResult with SQL and metadata
        """
        try:
            # Get schema context
            schema_context = await self.schema_manager.get_schema_context(
                question,
                max_tables=5,
            )

            # Select relevant examples
            relevant_examples = self.prompt_builder.select_relevant_examples(question)

            # Build prompt
            prompt = self.prompt_builder.build_chat2sql_prompt(
                question=question,
                schema_context=schema_context,
                examples=relevant_examples,
            )

            # Generate SQL using LLM
            messages = [
                LLMMessage(role="system", content="You are a SQL expert. Generate SQL queries based on natural language questions and database schema."),
                LLMMessage(role="user", content=prompt),
            ]

            response: LLMResponse = await self.llm.generate(messages)

            if response.error:
                return Chat2SQLResult(
                    question=question,
                    sql="",
                    is_valid=False,
                    error=f"LLM error: {response.error}",
                )

            # Extract SQL from response
            sql = self._extract_sql(response.content)

            if not sql:
                return Chat2SQLResult(
                    question=question,
                    sql="",
                    is_valid=False,
                    error="Failed to extract SQL from LLM response",
                )

            # Sanitize SQL
            if sanitize:
                sql = self.sanitizer.sanitize(sql)

            # Validate SQL
            validation_result = None
            is_valid = True

            if validate and self.settings.chat2sql.enable_validation:
                validation_result = self.validator.validate(
                    sql,
                    allow_ddl=self.settings.chat2sql.allow_ddl,
                )
                is_valid = validation_result.is_valid

            return Chat2SQLResult(
                question=question,
                sql=sql,
                is_valid=is_valid,
                validation_result=validation_result,
            )

        except Exception as e:
            logger.error(f"Natural language to SQL conversion failed: {e}")
            return Chat2SQLResult(
                question=question,
                sql="",
                is_valid=False,
                error=str(e),
            )

    async def explain_sql(self, sql: str) -> str:
        """Explain a SQL query in natural language.

        Args:
            sql: SQL query to explain

        Returns:
            Natural language explanation
        """
        try:
            # Build prompt
            prompt = self.prompt_builder.build_sql_explanation_prompt(sql)

            # Generate explanation using LLM
            messages = [
                LLMMessage(role="system", content="You are a SQL expert. Explain SQL queries in clear, simple language."),
                LLMMessage(role="user", content=prompt),
            ]

            response: LLMResponse = await self.llm.generate(messages)

            if response.error:
                return f"Error generating explanation: {response.error}"

            return response.content.strip()

        except Exception as e:
            logger.error(f"SQL explanation failed: {e}")
            return f"Error: {str(e)}"

    async def optimize_sql(
        self,
        sql: str,
        schema_context: Dict[str, Any] | None = None,
    ) -> SQLOptimizationResult:
        """Get optimization suggestions for SQL query.

        Args:
            sql: SQL query to optimize
            schema_context: Optional schema context

        Returns:
            SQLOptimizationResult with suggestions
        """
        try:
            # Get basic suggestions from validator
            suggestions = self.validator.suggest_optimizations(sql)

            # Build prompt for LLM-based optimization
            if schema_context is None:
                # Try to infer schema from SQL
                table_names = self._extract_table_names(sql)
                schema_context = {"relevant_tables": []}
                for table_name in table_names:
                    try:
                        table_schema = await self.schema_manager.get_table_schema(table_name)
                        schema_context["relevant_tables"].append(table_schema.to_dict())
                    except Exception:
                        pass

            prompt = self.prompt_builder.build_sql_optimization_prompt(
                sql=sql,
                schema_context=schema_context,
            )

            # Generate optimization suggestions using LLM
            messages = [
                LLMMessage(role="system", content="You are a SQL performance expert. Provide optimization suggestions."),
                LLMMessage(role="user", content=prompt),
            ]

            response: LLMResponse = await self.llm.generate(messages)

            llm_suggestions = response.content.strip() if not response.error else None

            if llm_suggestions:
                suggestions.append(f"AI Suggestions: {llm_suggestions}")

            return SQLOptimizationResult(
                sql=sql,
                suggestions=suggestions,
            )

        except Exception as e:
            logger.error(f"SQL optimization failed: {e}")
            return SQLOptimizationResult(
                sql=sql,
                suggestions=[f"Error: {str(e)}"],
            )

    async def fix_sql(
        self,
        sql: str,
        error_message: str,
    ) -> str:
        """Fix SQL query based on error message.

        Args:
            sql: SQL query with error
            error_message: Error message from database

        Returns:
            Fixed SQL query
        """
        try:
            # Get schema context
            table_names = self._extract_table_names(sql)
            schema_context = {"relevant_tables": []}
            for table_name in table_names:
                try:
                    table_schema = await self.schema_manager.get_table_schema(table_name)
                    schema_context["relevant_tables"].append(table_schema.to_dict())
                except Exception:
                    pass

            # Build prompt
            prompt = self.prompt_builder.build_sql_correction_prompt(
                sql=sql,
                error_message=error_message,
                schema_context=schema_context,
            )

            # Generate fixed SQL using LLM
            messages = [
                LLMMessage(role="system", content="You are a SQL expert. Fix SQL queries with errors."),
                LLMMessage(role="user", content=prompt),
            ]

            response: LLMResponse = await self.llm.generate(messages)

            if response.error:
                return sql  # Return original if fix fails

            # Extract fixed SQL
            fixed_sql = self._extract_sql(response.content)
            return fixed_sql if fixed_sql else sql

        except Exception as e:
            logger.error(f"SQL fix failed: {e}")
            return sql  # Return original on error

    async def validate_sql(
        self,
        sql: str,
    ) -> ValidationResult:
        """Validate SQL query.

        Args:
            sql: SQL query to validate

        Returns:
            ValidationResult with issues
        """
        return self.validator.validate(
            sql,
            allow_ddl=self.settings.chat2sql.allow_ddl,
        )

    async def suggest_query(
        self,
        question: str,
    ) -> str:
        """Suggest a SQL query for a natural language question (without validation).

        Args:
            question: Natural language question

        Returns:
            Suggested SQL query
        """
        result = await self.natural_language_to_sql(
            question,
            validate=False,
            sanitize=False,
        )
        return result.sql

    def _extract_sql(self, text: str) -> str:
        """Extract SQL query from LLM response.

        Args:
            text: LLM response text

        Returns:
            Extracted SQL query
        """
        # Remove markdown code blocks
        text = re.sub(r"```sql\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"```\s*", "", text)

        # Extract SQL (look for SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP)
        text = text.strip()

        # Find the start of SQL
        sql_keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP", "TRUNCATE", "WITH"]
        for keyword in sql_keywords:
            pattern = rf"\b{keyword}\b"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                text = text[match.start():]
                break

        # Extract until end or last semicolon
        # Remove any trailing explanation text
        lines = []
        for line in text.split("\n"):
            line_stripped = line.strip()
            if line_stripped and not line_stripped.startswith("#"):
                lines.append(line)
            elif line_stripped.startswith("#"):
                break

        sql = "\n".join(lines).strip()

        # Remove trailing non-SQL text
        for separator in ["\n\n", "\nExplanation", "\nNote:", "\n---"]:
            if separator in sql:
                sql = sql.split(separator)[0]

        return sql.strip()

    def _extract_table_names(self, sql: str) -> List[str]:
        """Extract table names from SQL query.

        Args:
            sql: SQL query

        Returns:
            List of table names
        """
        tables = []
        sql_upper = sql.upper()

        # Extract from FROM clause
        from_match = re.search(r"FROM\s+(\w+)", sql_upper)
        if from_match:
            tables.append(from_match.group(1))

        # Extract from JOIN clauses
        join_matches = re.findall(r"JOIN\s+(\w+)", sql_upper)
        tables.extend(join_matches)

        # Extract from UPDATE clause
        update_match = re.search(r"UPDATE\s+(\w+)", sql_upper)
        if update_match:
            tables.append(update_match.group(1))

        # Extract from INSERT INTO clause
        insert_match = re.search(r"INSERT\s+INTO\s+(\w+)", sql_upper)
        if insert_match:
            tables.append(insert_match.group(1))

        return list(set(tables))

    def clear_schema_cache(self):
        """Clear the schema cache."""
        self.schema_manager.clear_cache()

    def get_schema_info(self) -> Dict[str, Any]:
        """Get schema cache information.

        Returns:
            Schema cache information
        """
        return self.schema_manager.get_schema_summary()

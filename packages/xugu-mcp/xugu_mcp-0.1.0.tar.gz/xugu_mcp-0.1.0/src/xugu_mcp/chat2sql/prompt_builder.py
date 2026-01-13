"""
Prompt Builder for Chat2SQL engine.

Builds prompts for LLM with schema context and few-shot examples.
"""
import json
from typing import List, Dict, Any
from dataclasses import dataclass

from ..utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class Example:
    """A few-shot example for prompt."""

    question: str
    sql: str
    explanation: str | None = None

    def format(self) -> str:
        """Format example for prompt."""
        example = f"Question: {self.question}\n"
        example += f"SQL: {self.sql}\n"
        if self.explanation:
            example += f"Explanation: {self.explanation}\n"
        return example


class PromptBuilder:
    """Builder for Chat2SQL prompts."""

    # Few-shot examples
    EXAMPLES = [
        Example(
            question="Show me all users who registered in the last 7 days",
            sql="SELECT * FROM users WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'",
            explanation="Filter users by creation date within last 7 days",
        ),
        Example(
            question="Get the total sales for each product category",
            sql="SELECT category, SUM(amount) as total_sales FROM sales JOIN products ON sales.product_id = products.id GROUP BY category",
            explanation="Join sales with products and group by category to sum amounts",
        ),
        Example(
            question="Find customers who have made more than 5 purchases",
            sql="SELECT customer_id, COUNT(*) as purchase_count FROM orders GROUP BY customer_id HAVING COUNT(*) > 5",
            explanation="Group by customer and filter groups with HAVING clause",
        ),
        Example(
            question="List the top 10 products by revenue",
            sql="SELECT p.name, SUM(oi.quantity * oi.price) as revenue FROM products p JOIN order_items oi ON p.id = oi.product_id GROUP BY p.id, p.name ORDER BY revenue DESC LIMIT 10",
            explanation="Join products with order items, group by product, sum revenue, order descending, limit to 10",
        ),
        Example(
            question="Count how many users we have in each city",
            sql="SELECT city, COUNT(*) as user_count FROM users GROUP BY city",
            explanation="Group users by city and count records in each group",
        ),
    ]

    def __init__(self, max_examples: int = 3):
        """Initialize prompt builder.

        Args:
            max_examples: Maximum few-shot examples to include
        """
        self.max_examples = max_examples

    def build_chat2sql_prompt(
        self,
        question: str,
        schema_context: Dict[str, Any],
        examples: List[Example] | None = None,
    ) -> str:
        """Build prompt for natural language to SQL conversion.

        Args:
            question: Natural language question
            schema_context: Database schema context
            examples: Optional few-shot examples (uses defaults if None)

        Returns:
            Complete prompt for LLM
        """
        prompt = self._build_system_prompt()
        prompt += self._build_schema_section(schema_context)
        prompt += self._build_examples_section(examples)
        prompt += self._build_question_section(question)

        return prompt

    def _build_system_prompt(self) -> str:
        """Build system prompt with instructions."""
        return """You are a SQL expert. Convert natural language questions into SQL queries.

Rules:
1. Use only the tables and columns listed in the schema
2. Use proper JOIN syntax when relating tables
3. Use proper WHERE clauses for filtering
4. Use GROUP BY and HAVING for aggregations
5. Use LIMIT for result sets that might be large
6. Always use proper table aliases for clarity
7. Return only the SQL query, no explanations or markdown

SQL Syntax:
- Use standard SQL syntax compatible with XuguDB
- For dates: CURRENT_DATE, CURRENT_TIMESTAMP, INTERVAL 'X days'
- For strings: Use single quotes 'value'
- For NULL: Use IS NULL or IS NOT NULL
- For patterns: Use LIKE with % wildcards

"""

    def _build_schema_section(self, schema_context: Dict[str, Any]) -> str:
        """Build schema section of prompt.

        Args:
            schema_context: Schema context dictionary

        Returns:
            Schema section string
        """
        section = "## Database Schema\n\n"

        # Add tables
        if schema_context.get("relevant_tables"):
            section += "### Tables\n\n"
            for table in schema_context["relevant_tables"]:
                section += f"**{table['table_name']}**\n"
                section += "Columns:\n"
                for col in table.get("columns", []):
                    nullable = "NULL" if col.get("nullable") else "NOT NULL"
                    default = f" DEFAULT {col['default']}" if col.get("default") else ""
                    section += f"  - {col['name']}: {col['type']}{nullable}{default}\n"

                if table.get("primary_keys"):
                    section += f"Primary Key: {', '.join(table['primary_keys'])}\n"

                if table.get("sample_data"):
                    section += "Sample data:\n"
                    for row in table["sample_data"][:2]:  # Show 2 sample rows
                        section += f"  {json.dumps(row, ensure_ascii=False)}\n"

                section += "\n"

        # Add relationships
        if schema_context.get("relationships"):
            section += "### Relationships\n\n"
            for rel in schema_context["relationships"]:
                section += f"- {rel['from_table']}.{', '.join(rel['from_columns'])} "
                section += f"→ {rel['to_table']}.{', '.join(rel['to_columns'])}\n"
            section += "\n"

        return section

    def _build_examples_section(
        self,
        examples: List[Example] | None = None,
    ) -> str:
        """Build few-shot examples section.

        Args:
            examples: Few-shot examples to use

        Returns:
            Examples section string
        """
        if examples is None:
            examples = self.EXAMPLES[: self.max_examples]

        section = "## Examples\n\n"

        for i, example in enumerate(examples, 1):
            section += f"### Example {i}\n\n"
            section += example.format()
            section += "\n"

        return section

    def _build_question_section(self, question: str) -> str:
        """Build question section.

        Args:
            question: Natural language question

        Returns:
            Question section string
        """
        return f"""## Question

{question}

## SQL Query

Provide the SQL query for the above question:
"""

    def build_sql_explanation_prompt(
        self,
        sql: str,
    ) -> str:
        """Build prompt for SQL explanation.

        Args:
            sql: SQL query to explain

        Returns:
            Explanation prompt
        """
        return f"""You are a SQL expert. Explain the following SQL query in clear, simple language.

SQL Query:
{sql}

Provide:
1. A brief summary of what the query does
2. Step-by-step explanation of each part
3. Any potential performance considerations

Explanation:
"""

    def build_sql_optimization_prompt(
        self,
        sql: str,
        schema_context: Dict[str, Any] | None = None,
    ) -> str:
        """Build prompt for SQL optimization suggestions.

        Args:
            sql: SQL query to optimize
            schema_context: Optional schema context

        Returns:
            Optimization prompt
        """
        prompt = f"""You are a SQL performance expert. Analyze the following SQL query and provide optimization suggestions.

SQL Query:
{sql}
"""

        if schema_context:
            prompt += "\n### Schema Context\n\n"
            for table in schema_context.get("relevant_tables", []):
                prompt += f"Table: {table['table_name']}\n"
                if table.get("indexes"):
                    prompt += f"Indexes: {', '.join(table['indexes'])}\n"
                prompt += f"Row count: {table.get('row_count', 'unknown')}\n\n"

        prompt += """
Provide suggestions for:
1. Index improvements
2. Query restructuring
3. Performance optimizations
4. Potential bottlenecks

Suggestions:
"""
        return prompt

    def build_sql_correction_prompt(
        self,
        sql: str,
        error_message: str,
        schema_context: Dict[str, Any] | None = None,
    ) -> str:
        """Build prompt for SQL error correction.

        Args:
            sql: SQL query with error
            error_message: Error message from database
            schema_context: Optional schema context

        Returns:
            Correction prompt
        """
        prompt = f"""You are a SQL expert. Fix the following SQL query that has an error.

SQL Query:
{sql}

Error Message:
{error_message}
"""

        if schema_context:
            prompt += "\n### Available Schema\n\n"
            for table in schema_context.get("relevant_tables", []):
                prompt += f"Table: {table['table_name']}\n"
                prompt += f"Columns: {', '.join([c['name'] for c in table.get('columns', [])])}\n\n"

        prompt += """
Provide the corrected SQL query. Only return the SQL, no explanations.

Corrected SQL:
"""
        return prompt

    def select_relevant_examples(
        self,
        question: str,
        examples: List[Example] | None = None,
    ) -> List[Example]:
        """Select most relevant few-shot examples for a question.

        Args:
            question: Natural language question
            examples: Available examples (uses defaults if None)

        Returns:
            List of relevant examples
        """
        if examples is None:
            examples = self.EXAMPLES

        question_lower = question.lower()

        # Score examples by keyword matching
        scored_examples = []
        for example in examples:
            score = 0
            example_lower = example.question.lower() + " " + example.sql.lower()

            # Keywords that suggest similarity
            keywords = [
                "select", "join", "where", "group by", "order by",
                "count", "sum", "avg", "max", "min",
                "limit", "having",
            ]

            for keyword in keywords:
                if keyword in question_lower and keyword in example_lower:
                    score += 1

            # Check for common patterns
            if "top" in question_lower or "limit" in question_lower:
                if "LIMIT" in example.sql.upper():
                    score += 2

            if "total" in question_lower or "sum" in question_lower or "count" in question_lower:
                if any(agg in example.sql.upper() for agg in ["SUM", "COUNT", "AVG"]):
                    score += 2

            if "more than" in question_lower or "greater than" in question_lower:
                if "HAVING" in example.sql.upper() or ">" in example.sql:
                    score += 2

            scored_examples.append((example, score))

        # Sort by score and return top examples
        scored_examples.sort(key=lambda x: x[1], reverse=True)
        return [ex for ex, score in scored_examples[: self.max_examples]]

    def format_schema_for_prompt(
        self,
        schema_context: Dict[str, Any],
    ) -> str:
        """Format schema context for inclusion in prompt.

        Args:
            schema_context: Schema context dictionary

        Returns:
            Formatted schema string
        """
        return self._build_schema_section(schema_context)

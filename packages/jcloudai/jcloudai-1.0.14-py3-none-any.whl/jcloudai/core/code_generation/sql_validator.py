"""SQL Validator for validating and correcting generated SQL using LLM."""

import json
import logging
import re
from typing import Optional, Tuple

from jcloudai.agent.state import AgentState
from jcloudai.core.prompts.validate_sql_prompt import ValidateSQLPrompt

# SQL 校验日志器
sql_validation_logger = logging.getLogger("jcloudai.sql_validation")


class SQLValidator:
    """Validates generated SQL using LLM.
    
    This class extracts SQL from generated code, validates it against
    the user query and schema using LLM, and corrects it if needed.
    """

    def __init__(self, context: AgentState):
        """Initialize the SQL validator.
        
        Args:
            context: The agent state containing LLM config and dataframes.
        """
        self._context = context

    def validate_and_correct(
        self,
        code: str,
        user_query: str
    ) -> Tuple[str, bool]:
        """Validate SQL in the generated code and correct if needed.
        
        Args:
            code: The generated Python code containing SQL.
            user_query: The original user query.
            
        Returns:
            Tuple[str, bool]: (potentially corrected code, whether correction was made)
        """
        try:
            # 1. Extract SQL from code
            sql = self._extract_sql_from_code(code)
            if not sql:
                sql_validation_logger.debug(
                    "[SQL_VALIDATION] No SQL found in code, skipping validation"
                )
                return code, False

            sql_validation_logger.debug(
                f"[SQL_VALIDATION] Extracted SQL:\n{sql}"
            )

            # 2. Call LLM to validate SQL
            validation_result = self._validate_sql(sql, user_query)
            sql_validation_logger.debug(
                f"[SQL_VALIDATION] Validation result: {validation_result}"
            )

            # 3. If SQL is valid, return original code
            if validation_result.get("is_valid", True):
                sql_validation_logger.debug(
                    "[SQL_VALIDATION] SQL is valid, no correction needed"
                )
                return code, False

            # 4. If SQL is invalid, replace with corrected SQL
            corrected_sql = validation_result.get("corrected_sql")
            if corrected_sql:
                sql_validation_logger.debug(
                    f"[SQL_VALIDATION] Correcting SQL to:\n{corrected_sql}"
                )
                corrected_code = self._replace_sql_in_code(code, sql, corrected_sql)
                return corrected_code, True

            # No corrected SQL provided, return original
            sql_validation_logger.warning(
                "[SQL_VALIDATION] SQL invalid but no correction provided"
            )
            return code, False

        except Exception as e:
            # On any error, skip validation and return original code
            sql_validation_logger.error(
                f"[SQL_VALIDATION] Error during validation: {e}"
            )
            return code, False

    def _extract_sql_from_code(self, code: str) -> Optional[str]:
        """Extract SQL from execute_sql_query() call.

        Args:
            code: The generated Python code.

        Returns:
            The extracted SQL string, or None if not found.
        """
        # Pattern 1: Direct string argument - execute_sql_query("...") or execute_sql_query('...')
        direct_patterns = [
            r'execute_sql_query\s*\(\s*"""(.+?)"""\s*\)',  # Triple double quotes
            r"execute_sql_query\s*\(\s*'''(.+?)'''\s*\)",  # Triple single quotes
            r'execute_sql_query\s*\(\s*"(.+?)"\s*\)',      # Double quotes
            r"execute_sql_query\s*\(\s*'(.+?)'\s*\)",      # Single quotes
        ]

        for pattern in direct_patterns:
            matches = re.findall(pattern, code, re.DOTALL)
            if matches:
                return matches[0].strip()

        # Pattern 2: Variable argument - sql_query = "..."; execute_sql_query(sql_query)
        # First find the variable name used in execute_sql_query()
        var_match = re.search(r'execute_sql_query\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\)', code)
        if var_match:
            var_name = var_match.group(1)
            # Now find the variable assignment with triple quotes
            var_patterns = [
                rf'{var_name}\s*=\s*"""(.+?)"""',  # Triple double quotes
                rf"{var_name}\s*=\s*'''(.+?)'''",  # Triple single quotes
                rf'{var_name}\s*=\s*"(.+?)"',      # Double quotes (single line)
                rf"{var_name}\s*=\s*'(.+?)'",      # Single quotes (single line)
            ]
            for pattern in var_patterns:
                matches = re.findall(pattern, code, re.DOTALL)
                if matches:
                    return matches[0].strip()

        return None

    def _validate_sql(self, sql: str, user_query: str) -> dict:
        """Call LLM to validate SQL.
        
        Args:
            sql: The SQL to validate.
            user_query: The original user query.
            
        Returns:
            A dict with validation result including is_valid, issues, corrected_sql.
        """
        prompt = ValidateSQLPrompt(
            context=self._context,
            user_query=user_query,
            generated_sql=sql,
        )

        self._context.logger.log("[SQL_VALIDATION] Calling LLM for SQL validation...")
        response = self._context.config.llm.call(prompt, self._context)
        self._context.logger.log(f"[SQL_VALIDATION] LLM response: {response}")
        
        return self._parse_validation_response(response)

    def _parse_validation_response(self, response: str) -> dict:
        """Parse LLM validation response.
        
        Args:
            response: The raw LLM response string.
            
        Returns:
            A dict with validation result. Defaults to is_valid=True on parse failure.
        """
        try:
            # Try to extract JSON from response
            # Handle case where response might have markdown code blocks
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Try to find raw JSON object
            json_match = re.search(r'\{[^{}]*"is_valid"[^{}]*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            # Try to parse entire response as JSON
            return json.loads(response)
            
        except json.JSONDecodeError as e:
            sql_validation_logger.warning(
                f"[SQL_VALIDATION] Failed to parse response as JSON: {e}"
            )
            return {"is_valid": True}  # Default to valid on parse failure

    def _replace_sql_in_code(self, code: str, old_sql: str, new_sql: str) -> str:
        """Replace SQL in the generated code.
        
        Args:
            code: The original generated code.
            old_sql: The original SQL to replace.
            new_sql: The new SQL to use.
            
        Returns:
            The code with SQL replaced.
        """
        return code.replace(old_sql, new_sql)


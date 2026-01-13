"""Prompt for validating generated SQL against user query and schema."""

from jcloudai.core.prompts.base import BasePrompt


class ValidateSQLPrompt(BasePrompt):
    """Prompt to validate generated SQL against user query and schema.
    
    This prompt is used to verify that the generated SQL correctly answers
    the user's question, with focus on:
    - Field selection: Are the correct fields selected?
    - Condition filtering: Are WHERE conditions correct?
    """

    template_path = "validate_sql_prompt.tmpl"

    def to_json(self):
        """Convert prompt to JSON for API calls.
        
        Returns:
            dict: JSON representation of the prompt including datasets,
                  user query, generated SQL, and system prompt.
        """
        context = self.props["context"]
        user_query = self.props["user_query"]
        generated_sql = self.props["generated_sql"]
        memory = context.memory

        # Prepare datasets info
        datasets = [dataset.to_json() for dataset in context.dfs]

        return {
            "datasets": datasets,
            "user_query": user_query,
            "generated_sql": generated_sql,
            "system_prompt": memory.agent_description if memory else None,
            "prompt": self.to_string(),
        }


import os
import json
import logging
from typing import List, Dict, Any

try:
    import litellm
except ImportError:
    litellm = None

logger = logging.getLogger(__name__)

class TaskSuggester:
    """
    Analyzes project context and suggests actionable tasks using an LLM.
    """
    def __init__(self, model_name: str = "openrouter/xiaomi/mimo-v2-flash:free"):
        self.model_name = os.getenv("ONECODER_MODEL", model_name)
        self.api_key = os.getenv("OPENROUTER_API_KEY")

    def suggest_next_tasks(self, context: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Generates task suggestions based on sprint context.
        """
        if not litellm or not self.api_key:
            logger.warning("LLM dependencies not met. Returning empty suggestions.")
            return []

        prompt = self._construct_prompt(context)
        
        try:
            response = litellm.completion(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                api_key=self.api_key,
                base_url="https://openrouter.ai/api/v1",
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return self._parse_response(content)
        except Exception as e:
            logger.error(f"Task suggestion failed: {e}")
            return []

    def _construct_prompt(self, context: List[Dict[str, Any]]) -> str:
        sprints_str = json.dumps(context, indent=2)
        return f"""
        You are an expert Agile Technical Project Manager and Architect.
        Analyze the following context from recent sprints (goals, completed tasks, learnings, backlogs) and suggest 3-5 high-impact next tasks.
        
        Focus on:
        1. carrying over important incomplete work.
        2. applying 'learnings' to improved workflows or automated fixes.
        3. logically progressing towards sprint goals.

        Context:
        {sprints_str}

        Return a JSON object with a key "suggestions" containing a list of objects, each with:
        - "title": Short, actionable title (e.g., "Implement retry logic for API").
        - "rationale": Why this is important based on context.
        - "type": One of "feature", "fix", "chore", "governance".
        
        Example:
        {{
            "suggestions": [
                {{ "title": "...", "rationale": "...", "type": "..." }}
            ]
        }}
        """

    def _parse_response(self, content: str) -> List[Dict[str, str]]:
        try:
            data = json.loads(content)
            if isinstance(data, dict) and "suggestions" in data:
                return data["suggestions"]
            elif isinstance(data, list):
                return data
            return []
        except json.JSONDecodeError:
            # Simple fallback extraction if JSON fails
            import re
            suggestions = []
            matches = re.findall(r'"title":\s*"(.*?)"', content)
            for m in matches:
                suggestions.append({"title": m, "rationale": "Extracted from text", "type": "task"})
            return suggestions

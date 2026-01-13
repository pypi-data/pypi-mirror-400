
import re
from typing import Any, Dict, Optional, List
from rank_bm25 import BM25Okapi
from .registry import registry

class DynamicToolExecutor:
    """
    Manages discovery and execution of tools using BM25 for ranking.
    """
    def __init__(self):
        self.registry = registry

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\w+', text.lower())

    async def find_and_execute_tool(self, query: str, **tool_args) -> Any:
        """
        Finds the best tool for the query using BM25 and executes it.
        """
        tools = self.registry.list_tools()
        if not tools:
            return "No tools registered in the system."

        # Prepare corpus
        tool_descriptions = [tool.description for tool in tools]
        tokenized_corpus = [self._tokenize(doc) for doc in tool_descriptions]
        
        # Init BM25
        bm25 = BM25Okapi(tokenized_corpus)
        
        # Query
        tokenized_query = self._tokenize(query)
        scores = bm25.get_scores(tokenized_query)
        
        # Find best
        best_index = scores.argmax()
        best_score = scores[best_index]
        best_tool = tools[best_index]

        print(f"[DynamicToolExecutor] Selected tool: '{best_tool.name}' (Score: {best_score:.4f}) for query: '{query}'")
        
        # Heuristic threshold could be added here, but for now we just take the top one
        if best_score == 0:
             print(f"[DynamicToolExecutor] Warning: Zero score match for query '{query}'. Defaulting to '{best_tool.name}'")

        try:
            return await best_tool.execute_async(**tool_args)
        except Exception as e:
            return f"Error executing tool '{best_tool.name}': {e}"

# Global executor instance
executor = DynamicToolExecutor()

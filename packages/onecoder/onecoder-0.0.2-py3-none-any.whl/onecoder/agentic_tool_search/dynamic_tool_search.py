# onecoder/agentic_tool_search/dynamic_tool_search.py

import inspect
import numpy as np

class DynamicToolExecutor:
    """
    Manages the dynamic finding and execution of tools based on semantic search.
    """
    def __init__(self, model, registry):
        self.model = model
        self.registry = registry

    def _cosine_similarity(self, v1, v2):
        """Calculates the cosine similarity between two vectors."""
        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        return dot_product / (norm_v1 * norm_v2) if norm_v1 > 0 and norm_v2 > 0 else 0.0

    async def find_and_execute_tool(self, query: str, tool_args: dict = None) -> dict:
        """
        Dynamically finds and executes the most appropriate tool for a given query.

        This function performs a semantic search over the descriptions of all
        registered tools to find the best match for the user's query. Once the
        tool is identified, it is executed with the provided arguments.

        Args:
            query: The natural language query describing the task.
            tool_args: A dictionary of arguments to be passed to the selected tool.

        Returns:
            The result of the executed tool, or an error message if no
            suitable tool is found.
        """
        if tool_args is None:
            tool_args = {}

        # 1. Find the best tool using semantic search
        tool_descriptions = self.registry.get_all_tool_descriptions()
        query_embedding = self.model.encode(query)
        description_embeddings = self.model.encode(tool_descriptions)

        similarities = [self._cosine_similarity(query_embedding, desc_emb) for desc_emb in description_embeddings]
        best_tool_index = np.argmax(similarities)
        best_tool_description = tool_descriptions[best_tool_index]
        best_tool_name = self.registry.get_tool_name_from_description(best_tool_description)

        # 2. Execute the best tool
        tool_function = self.registry.get_tool_function(best_tool_name)
        if tool_function:
            print(f"Agent decided to use tool: '{best_tool_name}' for query: '{query}'")

            sig = inspect.signature(tool_function)
            valid_args = {key: value for key, value in tool_args.items() if key in sig.parameters}

            if 'query' in sig.parameters:
                valid_args['query'] = query

            result = await tool_function(**valid_args)
            return result
        else:
            return {"error": "Could not find a suitable tool for the query."}

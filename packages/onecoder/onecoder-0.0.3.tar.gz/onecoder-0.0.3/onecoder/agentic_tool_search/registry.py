# onecoder/agentic_tool_search/registry.py

class ToolRegistry:
    """A simple, in-memory registry for discoverable tools."""
    def __init__(self):
        self._tools = {}
        self.tool_metadata = []

    def register(self, tool_function, name, description, data_source=None):
        """Registers a tool, making it available for search and execution."""
        self._tools[name] = {
            "function": tool_function,
            "data_source": data_source
        }
        self.tool_metadata.append({
            "name": name,
            "description": description,
        })

    def get_tool_function(self, name):
        return self._tools.get(name, {}).get("function")

    def get_tool_data_source(self, name):
        return self._tools.get(name, {}).get("data_source")

    def get_all_tool_descriptions(self):
        return [item['description'] for item in self.tool_metadata]

    def get_tool_name_from_description(self, description):
        for item in self.tool_metadata:
            if item['description'] == description:
                return item['name']
        return None

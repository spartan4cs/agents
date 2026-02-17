from typing import Dict
from mcp.interfaces import Tool


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        return self._tools.get(name)

    def get_schemas(self):
        return [tool.schema for tool in self._tools.values()]

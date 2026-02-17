from abc import ABC, abstractmethod
from typing import Dict, Any


class Tool(ABC):
    """
    Abstract base class for all tools the MCP agent can call.

    Concrete tools (like a calculator or weather tool) should inherit from this
    class and fill in:
    - `name`: unique identifier the LLM will use in tool calls
    - `description`: human-readable description shown to the LLM
    - `schema`: JSON schema describing input parameters for the tool
    """

    # Public attributes expected on every tool implementation
    name: str
    description: str
    schema: Dict[str, Any]

    @abstractmethod
    def execute(self, **kwargs) -> str:
        """
        Execute the tool with keyword arguments coming from the LLM.

        Implementations should:
        - Validate/parse `kwargs` according to `schema`
        - Perform the tool's core logic (e.g. math, API call, DB query)
        - Return a string result that will be sent back to the LLM
        """
        pass

import json
import logging
from mcp.registry import ToolRegistry  # Registry that knows about all tools
from llm.client import LLMClient  # Thin wrapper around the underlying LLM API


logger = logging.getLogger(__name__)  # Module-level logger for debug/error logs


class MCPOrchestrator:
    """
    Core orchestration loop for the MCP-style agent.

    Responsibilities:
    - Call the LLM with the current conversation `messages`
    - Detect when the LLM wants to call a tool
    - Execute that tool using the `ToolRegistry`
    - Feed the tool result back to the LLM as a new message
    - Repeat until the LLM returns a normal assistant reply (no tool calls)
    """

    def __init__(self, registry: ToolRegistry):
        """
        `registry` holds all tools the agent is allowed to use.
        We also create an `LLMClient` instance for talking to the model.
        """
        self.registry = registry
        self.llm = LLMClient()

    def run(self, user_input: str) -> str:
        """
        Main entry point.

        Takes a raw user string, runs the LLM + tool loop, and returns the
        final natural-language response from the model.
        """

        # Start the conversation with a system prompt and the user's message
        messages = [
    {
        "role": "system",
        "content": """
      You are a secure banking assistant.

You have access to tools that allow you to perform banking operations. When a user asks about their account balance or requests banking information, you MUST use the appropriate tool to retrieve this information.

Available tools are provided to you - use them when they match the user's request:
- If a user asks about their account balance, use the get_balance tool with their account_id
- If a user needs calculations, use the calculator tool

You can ONLY call tools that are explicitly provided.
You must NEVER invent new tool names.
You must NEVER attempt direct database access.
If no tool matches the user's request, respond with a normal answer explaining what you can help with.
        """
    },
    {"role": "user", "content": user_input}
]



        # Loop up to N times to avoid infinite tool-calling cycles
        for _ in range(5):  # safety loop limit
            # Ask the LLM what to do next, passing available tool schemas
            tool_schemas = self.registry.get_schemas()
            # Log tool schemas for debugging
            if tool_schemas:
                logger.info(f"Passing {len(tool_schemas)} tools to LLM: {[s.get('function', {}).get('name', 'unknown') for s in tool_schemas]}")
                # Log full schema for first tool to debug format issues
                if len(tool_schemas) > 0:
                    logger.debug(f"First tool schema: {tool_schemas[0]}")
            else:
                logger.warning("No tools available in registry!")
            
            try:
                # Ensure we're passing tools correctly - Groq expects a list or None
                tools_to_send = tool_schemas if tool_schemas else None
                logger.info(f"Sending request with {len(tool_schemas) if tool_schemas else 0} tools")
                
                response = self.llm.chat(
                    messages,
                    tools=tools_to_send,
                )
            except Exception as e:
                logger.error(f"LLM API call failed: {e}")
                logger.error(f"Tools being sent: {tool_schemas}")
                logger.error(f"Tool count: {len(tool_schemas) if tool_schemas else 0}")
                if tool_schemas:
                    for i, schema in enumerate(tool_schemas):
                        logger.error(f"Tool {i}: {schema}")
                raise

            # The LLM's latest assistant message (may or may not include tool calls)
            message = response.choices[0].message

            # If the model wants to call a tool, handle it
            if message.tool_calls:
                # For now we only support a single tool call per turn
                tool_call = message.tool_calls[0]
                tool_name = tool_call.function.name
                # Tool arguments are JSON in string form; parse into a dict
                args = json.loads(tool_call.function.arguments)

                # Look up the concrete tool implementation by name
                tool = self.registry.get(tool_name)

                if not tool:
                    # This means the LLM asked for a tool we never registered
                    raise ValueError(f"Tool {tool_name} not found")

                try:
                    # Call the tool with the parsed arguments
                    result = tool.execute(**args)
                except Exception as e:
                    # Log the traceback and send an error string back to the LLM
                    logger.exception("Tool execution failed")
                    result = f"Error: {str(e)}"

                # Add the assistant's tool-call message to the history
                messages.append(message)
                # Then add the tool's result as a special "tool" message
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    }
                )
            else:
                # No tool calls: this is a final natural-language answer
                return message.content

        # Safety fallback in case the LLM keeps requesting tools too many times
        return "Max tool iterations reached"

from fastapi import FastAPI  # Web framework for building the HTTP API
from pydantic import BaseModel  # For request/response data validation
from mcp.registry import ToolRegistry  # Holds all available tools
from mcp.orchestrator import MCPOrchestrator  # Orchestrates tool calls based on input
from tools.balance import BalanceTool
from tools.calculator import CalculatorTool  # Example tool implementation



# Create the FastAPI application instance
app = FastAPI()

# Create a registry and register all tools the MCP server can use
registry = ToolRegistry()

# Register tools with error handling
try:
    calc_tool = CalculatorTool()
    registry.register(calc_tool)
    print(f"Registered tool: {calc_tool.name}")
except Exception as e:
    print(f"Error registering CalculatorTool: {e}")

try:
    balance_tool = BalanceTool()
    registry.register(balance_tool)
    print(f"Registered tool: {balance_tool.name}")
except Exception as e:
    print(f"Error registering BalanceTool: {e}")

# Verify registration
print(f"Total tools registered: {len(registry.get_schemas())}")
for schema in registry.get_schemas():
    print(f"  - {schema.get('function', {}).get('name', 'unknown')}")

# Orchestrator decides which tool(s) to call for a given message
orchestrator = MCPOrchestrator(registry)


class ChatRequest(BaseModel):
    """
    Schema for incoming chat requests.

    `message` is the raw text the user sends, which will be passed
    to the MCP orchestrator so it can decide which tools to use.
    """

    message: str


@app.post("/chat")
def chat(req: ChatRequest):
    """
    Chat endpoint.

    - Receives a JSON body that matches `ChatRequest`
    - Passes the `message` field to the MCP orchestrator
    - Returns whatever the orchestrator produces as `response`
    """

    # Run the orchestrator on the incoming message
    result = orchestrator.run(req.message)

    # Wrap the result in a JSON response
    return {"response": result}

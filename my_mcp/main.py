from fastapi import FastAPI  # Web framework for building the HTTP API
from pydantic import BaseModel  # For request/response data validation
from mcp.registry import ToolRegistry  # Holds all available tools
from mcp.orchestrator import MCPOrchestrator  # Orchestrates tool calls based on input
from tools.calculator import CalculatorTool  # Example tool implementation

# Create the FastAPI application instance
app = FastAPI()

# Create a registry and register all tools the MCP server can use
registry = ToolRegistry()
registry.register(CalculatorTool())  # Add the calculator tool to the registry

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

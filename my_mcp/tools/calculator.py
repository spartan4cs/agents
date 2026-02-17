from mcp.interfaces import Tool  # Base interface that all tools must implement
import ast  # Python's abstract syntax tree module, used for safe parsing
import operator  # Provides function versions of arithmetic operators

class CalculatorTool(Tool):
    """
    Simple calculator tool that can safely evaluate basic arithmetic expressions.

    This is intentionally limited (no variables, no function calls, etc.) and
    only supports a restricted set of operators to avoid arbitrary code execution.
    """

    # These fields are required by the `Tool` interface
    name = "calculator"
    description = "Safely evaluate arithmetic expressions"

    # JSON schema describing how the LLM should call this tool
    schema = {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {
                    # The only argument this tool accepts: a math expression as text
                    "expression": {
                        "type": "string",
                    }
                },
                "required": ["expression"],
            },
        },
    }

    def execute(self, expression: str) -> str:
        """
        Entry point called by the orchestrator.

        - `expression` is a string like "1 + 2 * 3"
        - We delegate to `safe_eval` and always return the result as a string.
        """
        return str(self.safe_eval(expression))

    def safe_eval(self, expr):
        """
        Safely evaluate a limited arithmetic expression using Python's AST.

        We:
        - Parse the expression into an AST
        - Recursively walk the tree
        - Only allow numeric literals and a small set of binary operators
        """

        # Map from AST operator types to their corresponding Python functions
        allowed_operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
        }

        def eval_node(node):
            """
            Recursively evaluate supported AST nodes.

            - If it's a binary operation (BinOp), evaluate left and right, then apply
              the corresponding operator from `allowed_operators`.
            - If it's a number literal, just return its value.
            - Anything else is rejected as unsafe.
            """
            if isinstance(node, ast.BinOp):
                return allowed_operators[type(node.op)](
                    eval_node(node.left),
                    eval_node(node.right),
                )
            elif isinstance(node, ast.Num):
                return node.n
            else:
                # Reject any unsupported node types to prevent unsafe behavior
                raise ValueError("Unsafe expression")

        # Parse the expression as a single expression (`mode='eval'`) and evaluate
        return eval_node(ast.parse(expr, mode="eval").body)

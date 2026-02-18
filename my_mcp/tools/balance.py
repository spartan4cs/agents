import requests
from mcp.interfaces import Tool

class BalanceTool(Tool):
    name = "get_balance"
    description = "Retrieve the current account balance for a user. Use this tool when users ask about their balance, account balance, how much money they have, or similar balance-related queries."

    schema = {
        "type": "function",
        "function": {
            "name": "get_balance",
            "description": "Retrieve the current account balance for a user. Use this tool when users ask about their balance, account balance, how much money they have, or similar balance-related queries.",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_id": {
                        "type": "string",
                        "description": "User account ID"
                    }
                },
                "required": ["account_id"]
            }
        }
    }

    def execute(self, account_id: str) -> str:
        url = f"http://localhost:8080/api/accounts/balance/{account_id}"
        
        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            return "Error retrieving balance"

        data = response.json()
        return f"{data['balance']} {data['currency']}"


retrieve_memory = {
    "type": "function",
    "name": "retrieve_memory",
    "description": "Retrieves relevant memories based on a search query. After receiving useful results, use them to answer the user rather than repeatedly calling the tool.",
    "parameters": {
        "type": "object",
        "properties": {
            "search_query": {
                "type": "string",
                "description": "The search query to find relevant memories."
            },
            "k": {
                "type": "integer",
                "description": "The number of top relevant memories to retrieve.",
                "default": 3
            },
        },
        "required": ["search_query"],
        "additionalProperties": False,
    },
    "strict": True
}
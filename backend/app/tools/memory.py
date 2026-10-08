
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

save_memory = {
    "type": "function",
    "name": "save_memory",
    "description": "Saves a new memory to the memory store. Only store important information that is relevant to the user. Avoid storing trivial or irrelevant details. ",
    "parameters": {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": "The generic category of the memory, e.g., 'music', 'preferences', 'family', etc."
            },
            "tags": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "A list of 3 to 7 tags associated with the memory for better organization and retrieval."
            },
            "content": {
                "type": "string",
                "description": "The content of the memory to be saved."
            },
        },
        "required": ["category", "tags", "content"],
        "additionalProperties": False,
    },
    "strict": True
}
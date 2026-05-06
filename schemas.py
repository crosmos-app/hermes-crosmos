"""Tool schemas, what the LLM sees."""

CROSMOS_REMEMBER = {
    "name": "crosmos_remember",
    "description": (
        "Store information into the Crosmos memory engine. "
        "Use this when the user shares personal information, preferences, experiences, "
        "instructions, corrections, or any facts worth remembering across conversations. "
        "The content is automatically decomposed into entities and relationships and "
        "linked to the current session for later lookback."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "The information to remember. Single fact or multi-sentence description.",
            },
            "space_name": {
                "type": "string",
                "description": (
                    "Memory space name (optional). Pass when the user mentions a specific "
                    "space. If omitted, the configured default space is used."
                ),
            },
        },
        "required": ["content"],
    },
}

CROSMOS_RECALL = {
    "name": "crosmos_recall",
    "description": (
        "Search the Crosmos memory layer for relevant memories. "
        "Use when the user asks about themselves, past preferences, experiences, "
        "or anything that requires recalling stored context. "
        "Returns scored memories with original source text."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Natural language search query.",
            },
            "space_name": {
                "type": "string",
                "description": "Memory space name (optional).",
            },
            "limit": {
                "type": "integer",
                "description": "Max results to return (1-50, default 10).",
                "default": 10,
            },
            "include_source": {
                "type": "boolean",
                "description": "Include original source text alongside extracted memories (default true).",
                "default": True,
            },
        },
        "required": ["query"],
    },
}

CROSMOS_FORGET = {
    "name": "crosmos_forget",
    "description": (
        "Soft-delete a memory from the knowledge graph. "
        "Use when the user explicitly asks to remove specific information. "
        "The memory is excluded from future searches but preserved in graph history."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "memory_id": {
                "type": "string",
                "description": "UUID of the memory to forget (from crosmos_recall results).",
            },
        },
        "required": ["memory_id"],
    },
}

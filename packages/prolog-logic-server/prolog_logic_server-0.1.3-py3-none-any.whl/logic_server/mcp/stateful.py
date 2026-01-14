#!/usr/bin/env python3
"""
Stateful MCP Server for Logical Reasoning

Extends the basic MCP server with session support for accumulating
facts and rules across multiple reasoning operations.

Features:
- Session management (create, destroy, list)
- Fact operations (assert, retract, query)
- Rule operations (assert, retract)
- Stateful solving over accumulated facts and rules
- Thread-safe session storage

Usage:
    python -m logic_server.mcp.stateful

Configuration for Claude Desktop (~/.config/claude/claude_desktop_config.json):
    {
      "mcpServers": {
        "logic-reasoning": {
          "command": "/absolute/path/to/python3",
          "args": ["-m", "logic_server.mcp.stateful"]
        }
      }
    }

Example Multi-Turn Conversation:
    User: "Create a reasoning session"
    Claude: [calls create_session] → session_id="abc123"

    User: "Add three people: Alice, Bob, Carol"
    Claude: [calls assert_facts with person facts]

    User: "Add constraint: Alice cannot own a cat"
    Claude: [calls assert_facts with forbidden fact]

    User: "Now add pets and query"
    Claude: [calls assert_facts then query]
"""

from __future__ import annotations

import json
import sys
from typing import Any, Iterable

# MCP imports
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
except ImportError:
    print("ERROR: MCP SDK not installed. Run: pip install mcp", file=sys.stderr)
    sys.exit(1)

from jsonschema import Draft202012Validator

# Import both stateless and stateful logic
from logic_server.core import formatting
from logic_server.core.session import (
    create_session,
    destroy_session,
    assert_facts,
    assert_rules,
    query,
    list_predicates,
    validate_query
)


# Initialize MCP server
server = Server("logic-reasoning")

CREATE_SESSION_INPUT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "metadata": {
            "type": "object",
            "description": "Optional metadata (e.g., task name, user info)",
            "additionalProperties": True
        }
    },
    "additionalProperties": False
}

DESTROY_SESSION_INPUT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "session_id": {
            "type": "string",
            "description": "Session ID to destroy"
        }
    },
    "required": ["session_id"],
    "additionalProperties": False
}

LIST_SESSIONS_INPUT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {},
    "additionalProperties": False
}

ASSERT_FACTS_INPUT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "session_id": {
            "type": "string",
            "description": "Target session ID"
        },
        "facts": {
            "type": "array",
            "description": "Facts to add to the session in Prolog syntax",
            "items": {"type": "string"}
        }
    },
    "required": ["session_id", "facts"],
    "additionalProperties": False
}

ASSERT_RULES_INPUT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "session_id": {
            "type": "string",
            "description": "Target session ID"
        },
        "rules": {
            "type": "array",
            "description": "Rules to add to the session",
            "items": {"type": ["string", "object"]}
        }
    },
    "required": ["session_id", "rules"],
    "additionalProperties": False
}

RETRACT_FACTS_INPUT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "session_id": {
            "type": "string",
            "description": "Target session ID"
        },
        "facts": {
            "type": "array",
            "description": "Facts to remove in Prolog syntax (must match exactly)",
            "items": {"type": "string"}
        }
    },
    "required": ["session_id", "facts"],
    "additionalProperties": False
}

RETRACT_RULES_INPUT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "session_id": {
            "type": "string",
            "description": "Target session ID"
        },
        "rules": {
            "type": "array",
            "description": "Rules to remove (must match exactly)",
            "items": {"type": "string"}
        }
    },
    "required": ["session_id", "rules"],
    "additionalProperties": False
}

QUERY_FACTS_INPUT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "session_id": {
            "type": "string",
            "description": "Target session ID"
        },
        "predicate": {
            "type": "string",
            "description": "Optional predicate filter (e.g., 'person', 'forbidden')"
        }
    },
    "required": ["session_id"],
    "additionalProperties": False
}

QUERY_INPUT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "session_id": {
            "type": "string",
            "description": "Session ID with accumulated facts"
        },
        "max_solutions": {
            "type": "integer",
            "description": "Maximum solutions to return",
            "default": 5
        },
        "offset": {
            "type": "integer",
            "minimum": 0,
            "default": 0
        },
        "limit": {
            "type": "integer",
            "minimum": 1
        },
        "format": {
            "type": "string",
            "enum": ["raw", "table", "grouped"],
            "default": "raw"
        },
        "group_by": {
            "type": "string",
            "description": "Variable name to group by when format is grouped"
        },
        "return_csv": {
            "type": "boolean",
            "default": False
        },
        "query": {
            "type": "string",
            "description": "Query in Prolog syntax: predicate(arg1, arg2)"
        }
    },
    "required": ["session_id", "query"],
    "additionalProperties": False
}

VALIDATE_QUERY_INPUT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "session_id": {
            "type": "string",
            "description": "Session ID with accumulated facts"
        },
        "query": {
            "type": "string",
            "description": "Query to validate in Prolog syntax"
        }
    },
    "required": ["session_id", "query"],
    "additionalProperties": False
}

LIST_PREDICATES_INPUT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "session_id": {
            "type": "string",
            "description": "Session ID to inspect"
        }
    },
    "required": ["session_id"],
    "additionalProperties": False
}

GET_SESSION_STATS_INPUT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "session_id": {
            "type": "string",
            "description": "Session ID to inspect"
        }
    },
    "required": ["session_id"],
    "additionalProperties": False
}

ASSERT_PATTERN_INPUT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "session_id": {"type": "string"},
        "pattern": {
            "type": "string",
            "description": "Prolog fact pattern template with '_' placeholders"
        },
        "bindings": {
            "type": "array",
            "items": {
                "oneOf": [
                    {"type": "object"},
                    {"type": "array"}
                ]
            }
        }
    },
    "required": ["session_id", "pattern", "bindings"],
    "additionalProperties": False
}

UNDO_LAST_INPUT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "session_id": {"type": "string"}
    },
    "required": ["session_id"],
    "additionalProperties": False
}

CHECKPOINT_INPUT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "session_id": {"type": "string"},
        "name": {"type": "string"}
    },
    "required": ["session_id", "name"],
    "additionalProperties": False
}

LIST_CHECKPOINTS_INPUT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "session_id": {"type": "string"}
    },
    "required": ["session_id"],
    "additionalProperties": False
}

SET_SESSION_OPTIONS_INPUT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "session_id": {"type": "string"},
        "max_solutions": {"type": "integer"},
        "page_size": {"type": "integer"}
    },
    "required": ["session_id"],
    "additionalProperties": False
}

DIFF_SESSIONS_INPUT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "session_id_a": {"type": "string"},
        "session_id_b": {"type": "string"}
    },
    "required": ["session_id_a", "session_id_b"],
    "additionalProperties": False
}

EXPORT_SESSION_INPUT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "session_id": {"type": "string"}
    },
    "required": ["session_id"],
    "additionalProperties": False
}

INPUT_SCHEMAS = {
    "create_session": CREATE_SESSION_INPUT_SCHEMA,
    "destroy_session": DESTROY_SESSION_INPUT_SCHEMA,
    "assert_facts": ASSERT_FACTS_INPUT_SCHEMA,
    "assert_rules": ASSERT_RULES_INPUT_SCHEMA,
    "query": QUERY_INPUT_SCHEMA,
    "validate_query": VALIDATE_QUERY_INPUT_SCHEMA,
    "list_predicates": LIST_PREDICATES_INPUT_SCHEMA,
}


def _format_validation_errors(errors: Iterable) -> list[str]:
    formatted: list[str] = []
    for error in errors:
        path = "arguments"
        for part in error.absolute_path:
            if isinstance(part, int):
                path += f"[{part}]"
            else:
                path += f".{part}"
        formatted.append(f"{path}: {error.message}")
    return formatted


def _validate_arguments(schema: dict, arguments: Any) -> list[str]:
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(arguments), key=lambda err: err.path)
    return _format_validation_errors(errors)


def _apply_formatting(result: dict, arguments: dict[str, Any]) -> dict:
    if not result.get("success"):
        return result
    output_format = arguments.get("format", "raw")
    if output_format == "raw":
        return result
    solutions = result.get("solutions", [])
    try:
        formatted = formatting.format_solutions(
            solutions,
            output_format,
            group_by=arguments.get("group_by"),
            return_csv=arguments.get("return_csv", False),
        )
    except ValueError as exc:
        return {
            "success": False,
            "error": str(exc),
            "query": result.get("query"),
        }
    result["formatted"] = formatted
    return result

@server.list_tools()
async def list_tools() -> list[Tool]:
    """Register available tools with the MCP client."""
    return [
        # Session management
        Tool(
            name="create_session",
            description="""
Create a new reasoning session for accumulating facts and rules across multiple turns.

Returns a session_id that you'll use for subsequent operations.
Sessions persist facts and rules across calls, enabling complex multi-step reasoning.

IMPORTANT:
- Always use MCP tools for logic reasoning; do not solve locally.
- When editing code, open a session, assert relevant facts/rules, and query for risks before making changes.
- Arguments must be valid JSON and match the schema.

COMPLETE EXAMPLE WORKFLOW:
1. session_id = create_session()
2. assert_facts(session_id, [
     "person(alice).",
     "age(alice, 30)."
   ])
3. assert_rules(session_id, [
     "adult(X) :- person(X), age(X, A), A >= 18"
   ])
4. query(session_id, "adult(X)") → finds alice
5. destroy_session(session_id) # Cleanup when done

USE CASES:
- Document analysis: Extract facts from text, query for insights
- Logic puzzles: Build constraints incrementally, solve step-by-step
- Multi-turn reasoning: Add facts as conversation progresses
            """.strip(),
            inputSchema=CREATE_SESSION_INPUT_SCHEMA
        ),

        Tool(
            name="destroy_session",
            description="""
Destroy a reasoning session and free its resources.

Call this when you're done with a multi-turn reasoning task to clean up.
            """.strip(),
            inputSchema=DESTROY_SESSION_INPUT_SCHEMA
        ),

        # Fact operations
        Tool(
            name="assert_facts",
            description="""
Add facts to an existing reasoning session.

Facts accumulate across calls - you can build up complex knowledge incrementally.

IMPORTANT:
- Use this tool to add facts; do not solve logic locally.
- Facts must be valid Prolog syntax.

FACT FORMAT:
Facts are Prolog terms ending with a period: "predicate(arg1, arg2, ...)."

EXAMPLES:
- Simple: "person(alice)."
- With attributes: "age(alice, 30)."
- Relationships: "owns(alice, cat)."
- Multiple args: "located_at(house1, '123 Main St', nyc)."
- Lists: "likes(alice, [cat, dog])."
- Strings: "name(alice, \"Alice Smith\")."

WORKFLOW:
1. Add entities: person(alice), person(bob)
2. Add properties: age(alice, 30), age(bob, 25)
3. Add relationships: friends(alice, bob)
4. Query: friends(alice, X) → finds bob
            """.strip(),
            inputSchema=ASSERT_FACTS_INPUT_SCHEMA
        ),

        Tool(
            name="assert_rules",
            description="""
Add logic rules to an existing reasoning session for deriving new facts.

Rules can be provided with or without trailing periods - the system handles both formats.

IMPORTANT:
- Use this tool to add rules; do not solve logic locally.
- Arguments must be valid JSON and match the schema.

RULE FORMAT:
"head(Args) :- body1(Args), body2(Args), ..."

STRUCTURED RULE FORMAT:
{"head": {predicate,args}, "body": [{predicate,args} | {op,left,right}, ...]}

The :- means "if" - the head is true IF all body conditions are true.

EXAMPLES:
- Simple derivation: "adult(X) :- person(X), age(X, A), A >= 18"
- Relationships: "sibling(X, Y) :- parent(P, X), parent(P, Y), X \\= Y"
- Multi-hop: "grandparent(X, Z) :- parent(X, Y), parent(Y, Z)"
- With constraints: "can_vote(X) :- citizen(X), age(X, A), A >= 18"
- Calculations: "total_cost(T) :- license_fee(L), support_fee(S), T is L + S"

USAGE:
1. Add facts: person(alice), age(alice, 25)
2. Add rule: adult(X) :- person(X), age(X, A), A >= 18
3. Query: adult(X) → finds alice (because 25 >= 18)
            """.strip(),
            inputSchema=ASSERT_RULES_INPUT_SCHEMA
        ),

        Tool(
            name="query",
            description="""
Query using all accumulated facts and rules in the session.

This runs a logic query over ALL facts and rules added to the session across all
previous assert_facts and assert_rules calls.

IMPORTANT:
- Always use MCP tools for logic reasoning; do not solve locally.
- Arguments must be valid JSON and match the schema.

QUERY FORMAT:
"predicate(arg1, Variable, arg3)"

STRUCTURED QUERY FORMAT:
{"predicate": "person", "args": [{"var": "X"}]}

Variables (capitalized) get bound to values. Constants (lowercase/numbers) must match exactly.

EXAMPLES:
- Find all: "person(X)" → returns all people
- Match specific: "age(alice, A)" → finds alice's age
- Multiple vars: "friends(X, Y)" → finds all friend pairs
- With constants: "owns(alice, P)" → finds what alice owns
- Derived facts: "grandparent(G, alice)" → uses rules to find alice's grandparents
- Constraints: "age(X, A), A > 18" → finds people over 18

COMMON PATTERNS:
- List all entities: entity(X)
- Check existence: person(alice) → returns {} if true, or count=0 if false
- Find related: owns(alice, X) → finds all things alice owns
- Multi-condition: person(X), age(X, A), A >= 21, citizen(X) → complex filtering

OUTPUT OPTIONS:
- format: "raw" | "table" | "grouped"
- group_by: variable name for grouped output
- offset/limit: pagination over solutions
- return_csv: include CSV when using table format

Note: Queries can end with "." or not - both work.
            """.strip(),
            inputSchema=QUERY_INPUT_SCHEMA
        ),

        Tool(
            name="validate_query",
            description="""
Validate a query against the session without executing it.

Returns schema errors and warnings (like unknown predicates).
            """.strip(),
            inputSchema=VALIDATE_QUERY_INPUT_SCHEMA
        ),

        Tool(
            name="list_predicates",
            description="""
List predicates present in a session's facts and rules.
            """.strip(),
            inputSchema=LIST_PREDICATES_INPUT_SCHEMA
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Execute a tool call from the MCP client."""

    result: Any = None
    arguments = arguments or {}

    schema = INPUT_SCHEMAS.get(name)
    if schema is None:
        result = {"success": False, "error": f"Unknown tool: {name}"}
        return [
            TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )
        ]

    validation_errors = _validate_arguments(schema, arguments)
    if validation_errors:
        result = {
            "success": False,
            "error": "Invalid tool arguments",
            "details": validation_errors,
            "expected_schema": schema
        }
        return [
            TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )
        ]

    try:
        # Session management
        if name == "create_session":
            session_id = create_session(metadata=arguments.get("metadata"))
            result = {
                "success": True,
                "session_id": session_id,
                "message": "Session created. Use assert_facts to add facts."
            }

        elif name == "destroy_session":
            session_id = arguments.get("session_id")
            if not session_id:
                result = {"success": False, "error": "session_id is required"}
            else:
                success = destroy_session(session_id)
                result = {
                    "success": success,
                    "message": "Session destroyed" if success else "Session not found"
                }

        # Fact operations
        elif name == "assert_facts":
            session_id = arguments.get("session_id")
            facts = arguments.get("facts")
            if not session_id:
                result = {"success": False, "error": "session_id is required"}
            elif facts is None:
                result = {"success": False, "error": "facts is required"}
            else:
                result = assert_facts(session_id=session_id, facts=facts)

        elif name == "assert_rules":
            session_id = arguments.get("session_id")
            rules = arguments.get("rules")
            if not session_id:
                result = {"success": False, "error": "session_id is required"}
            elif rules is None:
                result = {"success": False, "error": "rules is required"}
            else:
                result = assert_rules(session_id=session_id, rules=rules)

        elif name == "query":
            session_id = arguments.get("session_id")
            if not session_id:
                result = {"success": False, "error": "session_id is required"}
            else:
                result = query(
                    session_id=session_id,
                    max_solutions=arguments.get("max_solutions"),
                    offset=arguments.get("offset", 0),
                    limit=arguments.get("limit"),
                    query=arguments.get("query"),
                )
                result = _apply_formatting(result, arguments)

        elif name == "validate_query":
            session_id = arguments.get("session_id")
            if not session_id:
                result = {"success": False, "error": "session_id is required"}
            else:
                result = validate_query(
                    session_id=session_id,
                    query=arguments.get("query"),
                )

        elif name == "list_predicates":
            session_id = arguments.get("session_id")
            if not session_id:
                result = {"success": False, "error": "session_id is required"}
            else:
                result = list_predicates(session_id)

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        result = {"success": False, "error": str(e)}

    # Return formatted result
    return [
        TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )
    ]


async def main():
    """Run the MCP server."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

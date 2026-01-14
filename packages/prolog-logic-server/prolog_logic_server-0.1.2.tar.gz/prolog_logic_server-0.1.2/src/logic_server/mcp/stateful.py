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
from typing import Any, Optional

# MCP imports
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
except ImportError:
    print("ERROR: MCP SDK not installed. Run: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Import both stateless and stateful logic
from logic_server.core.solver import prolog_query
from logic_server.core.session import (
    create_session,
    destroy_session,
    list_sessions,
    assert_facts,
    assert_rules,
    retract_facts,
    retract_rules,
    query_facts,
    query,
    get_session_stats
)


# Initialize MCP server
server = Server("logic-reasoning")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """Register available tools with the MCP client."""
    return [
        # Original stateless tool (backward compatible)
        Tool(
            name="prolog_query",
            description="""
[STATELESS] Run a one-shot logic query. All facts and rules provided in one call.

This is a stateless tool - each call is independent. For multi-turn reasoning
with accumulated facts, use create_session and the session-based tools instead.

EXAMPLE:
prolog_query(
  facts=[
    {"predicate": "person", "args": ["alice"]},
    {"predicate": "age", "args": ["alice", 30]}
  ],
  query="age(alice, A)"
) → returns [{"A": 30}]

WHEN TO USE:
- One-shot queries: You have all facts and need one answer
- Simple lookups: No need to accumulate facts across turns
- Quick checks: Test logic without creating a session

WHEN TO USE SESSIONS INSTEAD:
- Multi-turn conversations: Building facts incrementally
- Complex reasoning: Adding facts/rules as you learn more
- Document analysis: Extracting facts progressively
            """.strip(),
            inputSchema={
                "type": "object",
                "properties": {
                    "facts": {
                        "type": "array",
                        "description": "Complete list of facts for this puzzle",
                        "items": {
                            "type": "object",
                            "properties": {
                                "predicate": {"type": "string"},
                                "args": {"type": "array"}
                            },
                            "required": ["predicate", "args"]
                        }
                    },
                    "max_solutions": {
                        "type": "integer",
                        "default": 5
                    },
                    "query": {
                        "type": "string",
                        "description": "Query in predicate(arg1, arg2) form"
                    }
                },
                "required": ["facts", "query"]
            }
        ),

        # Session management
        Tool(
            name="create_session",
            description="""
Create a new reasoning session for accumulating facts and rules across multiple turns.

Returns a session_id that you'll use for subsequent operations.
Sessions persist facts and rules across calls, enabling complex multi-step reasoning.

COMPLETE EXAMPLE WORKFLOW:
1. session_id = create_session()
2. assert_facts(session_id, [
     {"predicate": "person", "args": ["alice"]},
     {"predicate": "age", "args": ["alice", 30]}
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
            inputSchema={
                "type": "object",
                "properties": {
                    "metadata": {
                        "type": "object",
                        "description": "Optional metadata (e.g., task name, user info)",
                        "additionalProperties": True
                    }
                }
            }
        ),

        Tool(
            name="destroy_session",
            description="""
Destroy a reasoning session and free its resources.

Call this when you're done with a multi-turn reasoning task to clean up.
            """.strip(),
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session ID to destroy"
                    }
                },
                "required": ["session_id"]
            }
        ),

        Tool(
            name="list_sessions",
            description="""
List all active reasoning sessions with their statistics.

Shows session IDs, fact counts, age, and metadata.
            """.strip(),
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),

        # Fact operations
        Tool(
            name="assert_facts",
            description="""
Add facts to an existing reasoning session.

Facts accumulate across calls - you can build up complex knowledge incrementally.

FACT FORMAT:
Each fact is: {"predicate": "name", "args": [arg1, arg2, ...]}

EXAMPLES:
- Simple: {"predicate": "person", "args": ["alice"]}
- With attributes: {"predicate": "age", "args": ["alice", 30]}
- Relationships: {"predicate": "owns", "args": ["alice", "cat"]}
- Multiple args: {"predicate": "located_at", "args": ["house1", "123 Main St", "NYC"]}

WORKFLOW:
1. Add entities: person(alice), person(bob)
2. Add properties: age(alice, 30), age(bob, 25)
3. Add relationships: friends(alice, bob)
4. Query: friends(alice, X) → finds bob
            """.strip(),
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Target session ID"
                    },
                    "facts": {
                        "type": "array",
                        "description": "Facts to add to the session",
                        "items": {
                            "type": "object",
                            "properties": {
                                "predicate": {"type": "string"},
                                "args": {"type": "array"}
                            },
                            "required": ["predicate", "args"]
                        }
                    }
                },
                "required": ["session_id", "facts"]
            }
        ),

        Tool(
            name="assert_rules",
            description="""
Add logic rules to an existing reasoning session for deriving new facts.

Rules can be provided with or without trailing periods - the system handles both formats.

RULE FORMAT:
"head(Args) :- body1(Args), body2(Args), ..."

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
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Target session ID"
                    },
                    "rules": {
                        "type": "array",
                        "description": "Rules to add to the session",
                        "items": {"type": "string"}
                    }
                },
                "required": ["session_id", "rules"]
            }
        ),

        Tool(
            name="retract_facts",
            description="""
Remove specific facts from a reasoning session.

Use this to correct mistakes or remove constraints.
            """.strip(),
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Target session ID"
                    },
                    "facts": {
                        "type": "array",
                        "description": "Facts to remove (must match exactly)",
                        "items": {
                            "type": "object",
                            "properties": {
                                "predicate": {"type": "string"},
                                "args": {"type": "array"}
                            },
                            "required": ["predicate", "args"]
                        }
                    }
                },
                "required": ["session_id", "facts"]
            }
        ),

        Tool(
            name="retract_rules",
            description="""
Remove specific rules from a reasoning session.
            """.strip(),
            inputSchema={
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
                "required": ["session_id", "rules"]
            }
        ),

        Tool(
            name="query_facts",
            description="""
Query the accumulated facts in a session.

Use this to inspect what facts have been added, optionally filtering by predicate.
            """.strip(),
            inputSchema={
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
                "required": ["session_id"]
            }
        ),

        Tool(
            name="query",
            description="""
Query using all accumulated facts and rules in the session.

This runs a logic query over ALL facts and rules added to the session across all
previous assert_facts and assert_rules calls.

QUERY FORMAT:
"predicate(arg1, Variable, arg3)"

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

Note: Queries can end with "." or not - both work.
            """.strip(),
            inputSchema={
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
                    "query": {
                        "type": "string",
                        "description": "Query in predicate(arg1, arg2) form"
                    }
                },
                "required": ["session_id", "query"]
            }
        ),

        Tool(
            name="get_session_stats",
            description="""
Get detailed statistics about a reasoning session.

Shows total facts, facts by predicate type, session age, and metadata.
            """.strip(),
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session ID to inspect"
                    }
                },
                "required": ["session_id"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Execute a tool call from the MCP client."""

    result: Any = None

    try:
        # Stateless tool (original)
        if name == "prolog_query":
            result = prolog_query(
                facts=arguments.get("facts", []),
                base_knowledge=None,
                rules_program=None,
                query=arguments.get("query", ""),
                max_solutions=arguments.get("max_solutions", 5)
            )

        # Session management
        elif name == "create_session":
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

        elif name == "list_sessions":
            sessions = list_sessions()
            result = {
                "success": True,
                "sessions": sessions,
                "count": len(sessions)
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

        elif name == "retract_facts":
            session_id = arguments.get("session_id")
            facts = arguments.get("facts")
            if not session_id:
                result = {"success": False, "error": "session_id is required"}
            elif facts is None:
                result = {"success": False, "error": "facts is required"}
            else:
                result = retract_facts(session_id=session_id, facts=facts)

        elif name == "retract_rules":
            session_id = arguments.get("session_id")
            rules = arguments.get("rules")
            if not session_id:
                result = {"success": False, "error": "session_id is required"}
            elif rules is None:
                result = {"success": False, "error": "rules is required"}
            else:
                result = retract_rules(session_id=session_id, rules=rules)

        elif name == "query_facts":
            session_id = arguments.get("session_id")
            if not session_id:
                result = {"success": False, "error": "session_id is required"}
            else:
                result = query_facts(
                    session_id=session_id,
                    predicate=arguments.get("predicate")
                )

        elif name == "query":
            session_id = arguments.get("session_id")
            if not session_id:
                result = {"success": False, "error": "session_id is required"}
            else:
                result = query(
                    session_id=session_id,
                    max_solutions=arguments.get("max_solutions", 5),
                    query=arguments.get("query"),
                )

        elif name == "get_session_stats":
            session_id = arguments.get("session_id")
            if not session_id:
                result = {"success": False, "error": "session_id is required"}
            else:
                stats = get_session_stats(session_id)
                if stats:
                    result = {"success": True, **stats}
                else:
                    result = {
                        "success": False,
                        "error": f"Session not found: {session_id}"
                    }

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

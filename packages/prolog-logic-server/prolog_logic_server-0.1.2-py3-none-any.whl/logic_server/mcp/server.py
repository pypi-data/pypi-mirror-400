#!/usr/bin/env python3
"""
MCP Server for Logical Reasoning

This provides a standardized tool interface for constraint satisfaction
and logical reasoning that works across any MCP-compatible client.

Usage:
    python -m logic_server.mcp.server

Configuration for Claude Desktop (~/.config/claude/claude_desktop_config.json):
    {
      "mcpServers": {
        "logic-reasoning": {
          "command": "python",
          "args": ["-m", "logic_server.mcp.server"]
        }
      }
    }

Installation:
    pip install mcp

Documentation: https://modelcontextprotocol.io
"""

from __future__ import annotations

import json
import sys
from typing import Any

# NOTE: Install with: pip install mcp
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
except ImportError:
    print("ERROR: MCP SDK not installed. Run: pip install mcp", file=sys.stderr)
    sys.exit(1)

from logic_server.core.solver import execute_query


# Initialize MCP server
server = Server("logic-reasoning")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """Register available tools with the MCP client."""
    return [
        Tool(
            name="logic_query",
            description="""
Query facts using logical reasoning. Stateless - all facts and rules provided per call.

FACT FORMAT:
{"predicate": "name", "args": [arg1, arg2, ...]}

RULE FORMAT:
"head(Vars) :- condition1(Vars), condition2(Vars)"

QUERY FORMAT:
"predicate(Constant, Variable)" - Variables are capitalized

COMPLETE EXAMPLE:
logic_query(
  facts=[
    {"predicate": "person", "args": ["alice"]},
    {"predicate": "person", "args": ["bob"]},
    {"predicate": "age", "args": ["alice", 30]},
    {"predicate": "age", "args": ["bob", 17]}
  ],
  rules_program="adult(X) :- person(X), age(X, A), A >= 18",
  query="adult(P)"
) → returns [{"P": "alice"}] (only alice is >=18)

COMMON QUERIES:
- Find all: person(X) → returns all people
- Find specific: age(alice, A) → returns alice's age
- With conditions: age(X, A), A > 25 → people over 25
- Using rules: adult(X) → uses rules to derive answers
            """.strip(),
            inputSchema={
                "type": "object",
                "properties": {
                    "facts": {
                        "type": "array",
                        "description": "List of logical facts as {predicate: string, args: array}",
                        "items": {
                            "type": "object",
                            "properties": {
                                "predicate": {
                                    "type": "string",
                                    "description": "Predicate name (e.g., 'person', 'pet', 'forbidden')"
                                },
                                "args": {
                                    "type": "array",
                                    "description": "Arguments to the predicate (strings, numbers, or booleans)",
                                    "items": {}
                                }
                            },
                            "required": ["predicate", "args"]
                        }
                    },
                    "base_knowledge": {
                        "type": "array",
                        "description": "Optional: Base knowledge statements (reserved for future use)",
                        "items": {"type": "string"},
                        "default": []
                    },
                    "rules_program": {
                        "type": "string",
                        "description": "Optional: Logic rules (can be provided with or without trailing periods)",
                        "default": None
                    },
                    "query": {
                        "type": "string",
                        "description": "Query to execute in predicate(arg1, arg2) form"
                    },
                    "max_solutions": {
                        "type": "integer",
                        "description": "Maximum number of solutions to return",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 100
                    }
                },
                "required": ["facts", "query"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Execute a tool call from the MCP client."""

    if name != "logic_query":
        raise ValueError(f"Unknown tool: {name}")

    # Extract arguments with defaults
    facts = arguments.get("facts", [])
    base_knowledge = arguments.get("base_knowledge")
    rules_program = arguments.get("rules_program")
    query = arguments.get("query")
    max_solutions = arguments.get("max_solutions", 5)

    if not query:
        return [TextContent(type="text", text=json.dumps({
            "success": False,
            "error": "Query required"
        }))]

    # Execute the logic query
    result = execute_query(
        facts=facts,
        base_knowledge=base_knowledge,
        rules_program=rules_program,
        query=query,
        max_solutions=max_solutions
    )

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

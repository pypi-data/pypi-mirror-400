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

import difflib
import json
import sys
from typing import Any, Iterable, Optional

# NOTE: Install with: pip install mcp
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
except ImportError:
    print("ERROR: MCP SDK not installed. Run: pip install mcp", file=sys.stderr)
    sys.exit(1)

from jsonschema import Draft202012Validator

from logic_server.core.solver import execute_query, list_predicates, extract_query_predicate
from logic_server.core import formatting, schema


# Initialize MCP server
server = Server("logic-reasoning")

LOGIC_QUERY_INPUT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "facts": {
            "type": "array",
            "description": "List of logical facts in Prolog syntax",
            "items": {"type": "string"}
        },
        "base_knowledge": {
            "type": "array",
            "description": "Optional: Base knowledge statements (reserved for future use)",
            "items": {"type": "string"},
            "default": []
        },
        "rules_program": {
            "type": ["string", "array", "object"],
            "description": "Optional: Logic rules (string or structured rule objects, with or without trailing periods)",
            "default": None
        },
        "query": {
            "type": "string",
            "description": "Query to execute in Prolog syntax: predicate(arg1, arg2)"
        },
        "max_solutions": {
            "type": "integer",
            "description": "Maximum number of solutions to return",
            "default": 5,
            "minimum": 1,
            "maximum": 1000
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
        }
    },
    "required": ["facts", "query"],
    "additionalProperties": False
}

VALIDATE_QUERY_INPUT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "facts": {
            "type": "array",
            "description": "List of Prolog fact strings",
            "items": {"type": "string"}
        },
        "rules_program": {
            "type": ["string", "array", "object"],
            "description": "Optional: Logic rules (string or structured rule objects, with or without trailing periods)",
            "default": None
        },
        "query": {
            "type": "string",
            "description": "Query to validate in Prolog syntax: predicate(arg1, arg2)"
        }
    },
    "required": ["facts", "query"],
    "additionalProperties": False
}

LIST_PREDICATES_INPUT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "facts": {
            "type": "array",
            "description": "List of Prolog fact strings",
            "items": {"type": "string"}
        },
        "rules_program": {
            "type": ["string", "array", "object"],
            "description": "Optional: Logic rules (string or structured rule objects, with or without trailing periods)",
            "default": None
        }
    },
    "required": ["facts"],
    "additionalProperties": False
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


def _apply_pagination(result: dict, offset: int, limit: Optional[int]) -> dict:
    if not result.get("success"):
        return result
    if limit is None:
        return result
    solutions = result.get("solutions")
    if solutions is None:
        return result
    total_count = len(solutions)
    sliced = solutions[offset:offset + limit]
    result["solutions"] = sliced
    result["total_count"] = total_count
    result["count"] = len(sliced)
    result["offset"] = offset
    result["limit"] = limit
    return result


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


def _validate_query_payload(
    facts: list[str],
    rules_program: Any,
    query: Any
) -> dict:
    errors = schema.validate_query(query)
    if errors:
        return {
            "success": False,
            "error": "Schema validation failed",
            "details": errors,
            "query": query,
        }
    predicates = list_predicates(facts, rules_program)
    predicate = extract_query_predicate(query)
    warnings: list[str] = []
    if predicate and predicates and predicate not in predicates:
        close = difflib.get_close_matches(predicate, predicates, n=3)
        if close:
            warnings.append(
                f"Predicate '{predicate}' not found. Did you mean: {', '.join(close)}?"
            )
        else:
            warnings.append(
                f"Predicate '{predicate}' not found in facts/rules."
            )
    return {
        "success": True,
        "query": query,
        "predicate": predicate,
        "warnings": warnings,
    }


@server.list_tools()
async def list_tools() -> list[Tool]:
    """Register available tools with the MCP client."""
    return [
        Tool(
            name="logic_query",
            description="""
Query facts using logical reasoning. Stateless - all facts and rules provided per call.

IMPORTANT:
- Always use this tool for logic reasoning; do not solve in Python or outside MCP.
- When editing code, assert relevant facts/rules and query for risks before making changes.
- Facts and queries must be valid Prolog syntax.

FACT FORMAT:
Facts are Prolog terms ending with a period: "predicate(arg1, arg2, ...)."

EXAMPLES:
- Simple: "person(alice)."
- With numbers: "age(alice, 30)."
- With lists: "likes(alice, [cat, dog])."
- With strings: "name(alice, \"Alice Smith\")."

RULE FORMAT:
"head(Vars) :- condition1(Vars), condition2(Vars)"

QUERY FORMAT:
"predicate(Constant, Variable)" in Prolog syntax

COMPLETE EXAMPLE:
logic_query(
  facts=[
    "person(alice).",
    "person(bob).",
    "age(alice, 30).",
    "age(bob, 17)."
  ],
  rules_program="adult(X) :- person(X), age(X, A), A >= 18",
  query="adult(P)"
) → returns [{"P": "alice"}] (only alice is >=18)

COMMON QUERIES:
- Find all: person(X) → returns all people
- Find specific: age(alice, A) → returns alice's age
- With conditions: age(X, A), A > 25 → people over 25
- Using rules: adult(X) → uses rules to derive answers

OUTPUT OPTIONS:
- format: "raw" | "table" | "grouped"
- group_by: variable name for grouped output
- offset/limit: pagination over solutions
- return_csv: include CSV when using table format
            """.strip(),
            inputSchema=LOGIC_QUERY_INPUT_SCHEMA
        ),
        Tool(
            name="validate_query",
            description="""
Validate a query against provided facts/rules without executing it.

Returns schema errors and warnings (like unknown predicates).
            """.strip(),
            inputSchema=VALIDATE_QUERY_INPUT_SCHEMA
        ),
        Tool(
            name="list_predicates",
            description="""
List predicates present in the provided facts and rules.
            """.strip(),
            inputSchema=LIST_PREDICATES_INPUT_SCHEMA
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Execute a tool call from the MCP client."""

    arguments = arguments or {}

    if name == "logic_query":
        # Extract arguments with defaults
        facts = arguments.get("facts", [])
        base_knowledge = arguments.get("base_knowledge")
        rules_program = arguments.get("rules_program")
        query = arguments.get("query")
        max_solutions = arguments.get("max_solutions", 5)
        offset = arguments.get("offset", 0)
        limit = arguments.get("limit")

        validation_errors = _validate_arguments(LOGIC_QUERY_INPUT_SCHEMA, arguments)
        if validation_errors:
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "Invalid tool arguments",
                "details": validation_errors,
                "expected_schema": LOGIC_QUERY_INPUT_SCHEMA
            }, indent=2))]

        # Execute the logic query
        effective_max = max_solutions
        if limit is not None:
            effective_max = max(effective_max, offset + limit)
        result = execute_query(
            facts=facts,
            rules_program=rules_program,
            query=query,
            max_solutions=effective_max
        )
        result = _apply_pagination(result, offset, limit)
        result = _apply_formatting(result, arguments)

    elif name == "validate_query":
        validation_errors = _validate_arguments(VALIDATE_QUERY_INPUT_SCHEMA, arguments)
        if validation_errors:
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "Invalid tool arguments",
                "details": validation_errors,
                "expected_schema": VALIDATE_QUERY_INPUT_SCHEMA
            }, indent=2))]
        result = _validate_query_payload(
            arguments.get("facts", []),
            arguments.get("rules_program"),
            arguments.get("query"),
        )

    elif name == "list_predicates":
        validation_errors = _validate_arguments(LIST_PREDICATES_INPUT_SCHEMA, arguments)
        if validation_errors:
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "Invalid tool arguments",
                "details": validation_errors,
                "expected_schema": LIST_PREDICATES_INPUT_SCHEMA
            }, indent=2))]
        predicates = list_predicates(
            arguments.get("facts", []),
            arguments.get("rules_program"),
        )
        result = {
            "success": True,
            "predicates": predicates,
            "count": len(predicates),
        }

    else:
        raise ValueError(f"Unknown tool: {name}")

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

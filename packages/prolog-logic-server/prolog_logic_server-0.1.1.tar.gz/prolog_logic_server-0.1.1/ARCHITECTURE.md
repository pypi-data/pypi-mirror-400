# Architecture

## Vision

Provide a universal, provider-agnostic logic reasoning tool that LLMs can call for verifiable constraint solving. MCP is the preferred integration path because it is client-agnostic and local-first.

## Core Components

- `logic_server.core.solver` executes fact queries via SWI-Prolog.
- `logic_server.core.session` provides stateful sessions with fact accumulation.
- `logic_server.mcp.server` exposes stateless reasoning over MCP.
- `logic_server.mcp.stateful` exposes session-based tools over MCP.
- `logic_server.cli.main` runs queries over JSON fact files.
- `logic_server.cli.main` provides a CLI entry point for querying JSON facts.

## Predicates Supported

The solver accepts any predicate names present in the asserted facts and evaluates a Prolog query against them.

## Stateless vs Stateful

**Stateless**: Each `prolog_query` call is independent and must include all facts.

**Stateful**: Sessions store accumulated facts; callers can add, retract, query_facts, and query as they go.

## Tooling Approaches

- **Manual JSON tool calls**: Works with any LLM API, but depends on prompt adherence.
- **MCP**: Preferred universal tool interface for local tools and shared clients.
- **Native tool APIs**: Possible adapters for specific providers if needed.

## Status and Roadmap

Current implementation delivers:
- MCP stateless and stateful servers.
- CLI solver and LLM integration demo.
- Session management with query and retraction.

Potential next steps:
- Extend predicate library for temporal, spatial, and relational constraints.
- Add persistent session storage (SQLite or Redis).
- Broaden test coverage with more puzzle fixtures.

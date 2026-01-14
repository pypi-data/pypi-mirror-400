"""
Logic Server - A constraint-based logic solver with LLM integration

This package provides:
- Prolog-like constraint satisfaction solving
- LLM integration for natural language puzzle solving
- MCP server implementation for universal tool access
- Session management for stateful reasoning
"""

__version__ = "0.1.0"

# Re-export main APIs for convenience
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
    get_session_stats,
)
from logic_server.llm.clients import LLM, OllamaLLM, OpenAILLM, Message

__all__ = [
    # Core solver
    "prolog_query",
    # Session management
    "create_session",
    "destroy_session",
    "list_sessions",
    "assert_facts",
    "assert_rules",
    "retract_facts",
    "retract_rules",
    "query_facts",
    "query",
    "get_session_stats",
    # LLM clients
    "LLM",
    "OllamaLLM",
    "OpenAILLM",
    "Message",
]

"""Core logic reasoning components"""

from logic_server.core.solver import execute_query, prolog_query  # prolog_query for backward compat
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
    Session,
)

__all__ = [
    "execute_query",  # Primary API
    "prolog_query",   # Backward compatibility
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
    "Session",
]

# Optional: MQI-based solver (requires janus-swi)
try:
    from logic_server.core.mqi_solver import MQISolver, get_mqi_solver
    __all__.extend(["MQISolver", "get_mqi_solver"])
    HAS_MQI = True
except ImportError:
    HAS_MQI = False

# Optional: Process pool (for advanced use cases)
try:
    from logic_server.core.prolog_pool import PrologPool, get_prolog_pool
    __all__.extend(["PrologPool", "get_prolog_pool"])
    HAS_POOL = True
except ImportError:
    HAS_POOL = False

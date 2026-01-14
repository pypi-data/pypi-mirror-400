#!/usr/bin/env python3
"""
MQI-based Prolog solver using persistent processes.

This uses SWI-Prolog's MQI (Machine Query Interface) for efficient
query execution without subprocess overhead.

Installation:
    pip install janus-swi  # Official SWI-Prolog Python library

Usage:
    from logic_server.core.mqi_solver import MQISolver

    solver = MQISolver()
    result = solver.query(facts, rules_program, query, max_solutions=5)
    solver.close()
"""

from __future__ import annotations

import json
import threading
from typing import Any, Dict, List, Optional

try:
    # SWI-Prolog's official Python interface
    # Install with: pip install janus-swi
    from janus_swi import query_once, query, consult  # type: ignore
    HAS_JANUS = True
except ImportError:
    HAS_JANUS = False


class MQISolver:
    """
    Prolog solver using MQI for persistent process communication.

    This is much faster than spawning subprocesses for each query.
    """

    def __init__(self):
        if not HAS_JANUS:
            raise ImportError(
                "janus-swi not installed. Install with: pip install janus-swi\n"
                "See: https://www.swi-prolog.org/pldoc/doc_for?object=section(%27packages/janus.html%27)"
            )

        self._lock = threading.Lock()
        self._initialized = False

    def _ensure_initialized(self) -> None:
        """Ensure the Prolog engine is initialized."""
        if not self._initialized:
            # Load required libraries
            try:
                query_once("use_module(library(http/json))")
                query_once("use_module(library(solution_sequences))")
                self._initialized = True
            except Exception as e:
                raise RuntimeError(f"Failed to initialize Prolog: {e}")

    def _format_atom(self, value: Any) -> str:
        """Format a Python value as a Prolog atom."""
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (int, float)):
            return str(value)
        if value is None:
            return "null"
        # Escape strings
        text = str(value)
        if text.isalnum() and text[0].islower():
            return text
        return f"'{text.replace('\'', '\'\'')}'"

    def _facts_to_prolog(self, facts: List[Dict[str, Any]]) -> str:
        """Convert JSON facts to Prolog clauses."""
        lines: List[str] = []
        for fact in facts:
            predicate = fact.get("predicate", "unknown")
            args = fact.get("args", [])

            if args:
                rendered_args = ", ".join(self._format_atom(arg) for arg in args)
                lines.append(f"{predicate}({rendered_args}).")
            else:
                lines.append(f"{predicate}.")

        return "\n".join(lines)

    def query_prolog(
        self,
        facts: List[Dict[str, Any]],
        rules_program: Optional[str] = None,
        query_text: str = "",
        max_solutions: int = 5
    ) -> Dict[str, Any]:
        """
        Execute a Prolog query using MQI.

        Args:
            facts: List of facts to assert
            rules_program: Optional Prolog rules
            query_text: Query to execute (e.g., "person(P).")
            max_solutions: Maximum number of solutions

        Returns:
            Dict with success, solutions, and metadata
        """
        if not query_text.strip():
            return {
                "success": False,
                "error": "Query required",
                "query": query_text
            }

        with self._lock:
            self._ensure_initialized()

            try:
                # Build Prolog program
                program = self._facts_to_prolog(facts)
                if rules_program:
                    program += "\n\n"
                    # Ensure each rule ends with a period
                    for line in rules_program.strip().split('\n'):
                        line = line.strip()
                        if line and not line.endswith('.'):
                            line += '.'
                        if line:
                            program += line + '\n'

                # Write to temp file and consult it
                import tempfile
                import os

                with tempfile.NamedTemporaryFile(mode='w', suffix='.pl', delete=False) as f:
                    f.write(program)
                    temp_path = f.name

                try:
                    # Consult the file
                    consult(temp_path)

                    # Clean up query
                    query_clean = query_text.strip()
                    if query_clean.endswith("."):
                        query_clean = query_clean[:-1]

                    # Execute query and collect solutions
                    solutions: List[Dict[str, Any]] = []

                    try:
                        # Use janus query to get solutions
                        count = 0
                        for solution in query(query_clean):
                            # Filter out janus_swi's internal 'truth' field
                            bindings = {k: v for k, v in solution.items() if k != 'truth'}
                            solutions.append({"Bindings": bindings})
                            count += 1
                            if count >= max_solutions:
                                break
                    except Exception as e:
                        # Query failed (no solutions or error)
                        error_msg = str(e)
                        if "Unknown procedure" in error_msg or "Undefined procedure" in error_msg or "undefined" in error_msg.lower():
                            return {
                                "success": False,
                                "error": error_msg,
                                "query": query_text
                            }
                        # If just no solutions, return empty
                        pass

                    return {
                        "success": True,
                        "solutions": solutions,
                        "query": query_text,
                        "count": len(solutions)
                    }
                finally:
                    # Clean up temp file
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)

            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "query": query_text
                }

    def close(self) -> None:
        """Close the Prolog engine."""
        # Janus handles cleanup automatically
        pass


class MQIPooledSolver:
    """
    Pooled MQI solver for concurrent access.

    Maintains multiple MQI solver instances for thread-safe concurrent queries.
    """

    def __init__(self, pool_size: int = 4):
        """
        Initialize pooled solver.

        Args:
            pool_size: Number of solver instances to maintain
        """
        # Note: janus-swi has limitations on concurrent access
        # For true pooling, we'd need process-based pools
        # For now, use a single solver with locking
        self.solver = MQISolver() if HAS_JANUS else None
        self.pool_size = pool_size

    def query(
        self,
        facts: List[Dict[str, Any]],
        rules_program: Optional[str] = None,
        query_text: str = "",
        max_solutions: int = 5
    ) -> Dict[str, Any]:
        """Execute a query (thread-safe)."""
        if not self.solver:
            # Fall back to subprocess-based solver
            from logic_server.core.solver import prolog_query
            return prolog_query(facts, None, rules_program, query_text, max_solutions)

        return self.solver.query_prolog(facts, rules_program, query_text, max_solutions)

    def close(self) -> None:
        """Shutdown the pool."""
        if self.solver:
            self.solver.close()


# Global pooled solver
_global_solver: Optional[MQIPooledSolver] = None
_solver_lock = threading.Lock()


def get_mqi_solver(pool_size: int = 4) -> MQIPooledSolver:
    """Get or create the global MQI solver."""
    global _global_solver
    if _global_solver is None:
        with _solver_lock:
            if _global_solver is None:
                _global_solver = MQIPooledSolver(pool_size=pool_size)
    return _global_solver

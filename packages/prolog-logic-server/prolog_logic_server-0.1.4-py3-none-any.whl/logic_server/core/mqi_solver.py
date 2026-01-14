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

Architecture:
    Each query is isolated in a unique Prolog module. This ensures:
    - Complete isolation between queries (no predicate leakage)
    - Reliable cleanup via unload_file() which removes the entire module
    - No reliance on retractall() which only works for dynamic predicates
"""

from __future__ import annotations

import threading
import uuid
from typing import Any, Dict, List, Optional

from logic_server.core import schema, solver

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

    Each query runs in an isolated Prolog module to ensure clean separation
    and reliable cleanup between queries.
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
                query_once("use_module(library(clpfd))")
                # Note: all_different/1 and all_distinct/1 are provided by clpfd
                # No additional helper predicates needed
                self._initialized = True
            except Exception as e:
                raise RuntimeError(f"Failed to initialize Prolog: {e}")

    def _extract_predicates(self, lines: List[str]) -> set[tuple[str, int]]:
        """
        Extract predicate name/arity pairs from Prolog fact and rule lines.

        This is used to generate dynamic declarations for the module.
        Note: Arity detection uses parenthesis depth tracking to handle
        nested terms correctly (e.g., foo(bar(a,b), c) has arity 2, not 3).
        """
        predicates: set[tuple[str, int]] = set()
        for raw_line in lines:
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith("%"):
                continue
            if "%" in line:
                line = line.split("%", 1)[0].strip()
            if not line:
                continue

            if ":-" in line:
                head = line.split(":-", 1)[0].strip()
            else:
                head = line.strip()

            if not head or head.startswith(":-"):
                continue

            if "(" in head:
                paren_idx = head.find("(")
                pred_name = head[:paren_idx].strip()
                # Count arity using parenthesis depth tracking
                # This correctly handles nested terms like foo(bar(a,b), c)
                arity = self._count_arity(head[paren_idx:])
            else:
                pred_name = head.strip().rstrip(".")
                arity = 0

            if pred_name and pred_name[0].islower():
                predicates.add((pred_name, arity))

        return predicates

    def _count_arity(self, args_with_parens: str) -> int:
        """
        Count the arity of a predicate by tracking parenthesis depth.

        Args:
            args_with_parens: String starting with '(' e.g. "(bar(a,b), c)"

        Returns:
            Number of top-level arguments (arity)
        """
        if not args_with_parens or args_with_parens[0] != "(":
            return 0

        depth = 0
        arity = 0
        in_string = False
        string_char = None

        for i, char in enumerate(args_with_parens):
            # Handle string literals
            if char in ('"', "'") and (i == 0 or args_with_parens[i - 1] != "\\"):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
                    string_char = None
                continue

            if in_string:
                continue

            if char == "(":
                if depth == 0:
                    # Starting the argument list
                    arity = 1  # At least one argument if we have parens
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    # End of argument list
                    break
            elif char == "," and depth == 1:
                # Top-level comma separating arguments
                arity += 1

        # Handle empty argument list: foo()
        content = args_with_parens[1:].strip()
        if content.startswith(")"):
            return 0

        return arity

    def _generate_module_name(self) -> str:
        """Generate a unique module name for query isolation."""
        return f"mqi_session_{uuid.uuid4().hex[:12]}"

    def _build_module_program(
        self,
        module_name: str,
        facts: List[str],
        rules_text: Optional[str],
        predicates: set[tuple[str, int]],
    ) -> str:
        """
        Build a Prolog program with module declaration and dynamic predicates.

        Args:
            module_name: Unique module name for isolation
            facts: List of fact strings
            rules_text: Optional rendered rules
            predicates: Set of (name, arity) pairs to declare as dynamic

        Returns:
            Complete Prolog program as string
        """
        lines = []

        # Module declaration - empty export list since we query within module
        lines.append(f":- module({module_name}, []).")
        lines.append("")

        # Declare all predicates as dynamic for proper cleanup
        for pred_name, arity in sorted(predicates):
            lines.append(f":- dynamic {pred_name}/{arity}.")
        lines.append("")

        # Add facts
        lines.extend(facts)

        # Add rules if present
        if rules_text:
            lines.append("")
            lines.extend(rules_text.splitlines())

        return "\n".join(lines)

    def query_prolog(
        self,
        facts: List[str],
        rules_program: Any = None,
        query_text: str = "",
        max_solutions: int = 5
    ) -> Dict[str, Any]:
        """
        Execute a Prolog query using MQI with module isolation.

        Each query runs in a unique Prolog module, ensuring complete isolation
        between queries. The module is automatically unloaded after the query
        completes, guaranteeing clean state.

        Args:
            facts: List of Prolog fact strings like "person(alice)."
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

            import os
            import tempfile

            temp_path: Optional[str] = None
            module_name: Optional[str] = None

            try:
                # Generate unique module name for this query
                module_name = self._generate_module_name()

                # Render rules if present
                rules_text = solver._render_rules_program(rules_program)

                # Extract all predicates for dynamic declaration
                predicates = self._extract_predicates(facts)
                if rules_text:
                    predicates.update(
                        self._extract_predicates(rules_text.splitlines())
                    )

                # Build module-isolated program
                program = self._build_module_program(
                    module_name, facts, rules_text, predicates
                )

                # Write to temp file
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".pl", delete=False
                ) as f:
                    f.write(program)
                    temp_path = f.name

                # Consult the module file
                consult(temp_path)

                # Clean up query text
                query_clean = query_text.strip()
                if query_clean.endswith("."):
                    query_clean = query_clean[:-1]

                # Execute query within the module context
                # Use module:query syntax to ensure we query the right module
                module_query = f"{module_name}:({query_clean})"

                # Collect solutions
                solutions: List[Dict[str, Any]] = []

                try:
                    count = 0
                    for solution in query(module_query):
                        # Filter out janus_swi's internal 'truth' field
                        bindings = {
                            k: v for k, v in solution.items() if k != "truth"
                        }
                        solutions.append({"Bindings": bindings})
                        count += 1
                        if count >= max_solutions:
                            break
                except Exception as e:
                    error_msg = str(e)
                    return {
                        "success": False,
                        "error": error_msg,
                        "query": query_text,
                        "module": module_name,
                    }

                return {
                    "success": True,
                    "solutions": solutions,
                    "query": query_text,
                    "count": len(solutions),
                }

            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "query": query_text,
                }

            finally:
                # Clean up: unload the module file
                # This removes the entire module and all its predicates
                if temp_path:
                    try:
                        escaped_path = temp_path.replace("\\", "\\\\").replace(
                            "'", "\\'"
                        )
                        query_once(f"unload_file('{escaped_path}')")
                    except Exception:
                        pass
                    # Remove temp file from filesystem
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)

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
        facts: List[str],
        rules_program: Optional[str] = None,
        query_text: str = "",
        max_solutions: int = 5
    ) -> Dict[str, Any]:
        """Execute a query (thread-safe)."""
        if not self.solver:
            # Fall back to subprocess-based solver
            from logic_server.core.solver import execute_query
            result = execute_query(facts, rules_program, query_text, max_solutions)
            warnings = result.setdefault("warnings", [])
            warnings.append("janus-swi not installed; used subprocess backend")
            return result

        result = self.solver.query_prolog(facts, rules_program, query_text, max_solutions)
        result.setdefault("backend", "mqi")
        return result

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

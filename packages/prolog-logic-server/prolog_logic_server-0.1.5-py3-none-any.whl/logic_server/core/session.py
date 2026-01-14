#!/usr/bin/env python3
"""
Session Management for Stateful Prolog Reasoning

Enables accumulation of facts across multiple reasoning operations,
supporting complex multi-turn logical tasks.

Architecture:
- Sessions store accumulated facts in memory (or persistent storage)
- Multiple operations: assert, retract, query_facts, query
- Thread-safe for concurrent access
- Optional session expiry for cleanup

Example Use Case:
    # Turn 1: Setup entities
    session_id = create_session()
    assert_facts(session_id, [
        {"predicate": "person", "args": ["alice"]},
        {"predicate": "person", "args": ["bob"]}
    ])

    # Turn 2: Add constraints
    assert_facts(session_id, [
        {"predicate": "forbidden", "args": ["alice", "cat"]}
    ])

    # Turn 3: Add pets and query
    assert_facts(session_id, [
        {"predicate": "pet", "args": ["cat"]},
        {"predicate": "pet", "args": ["dog"]}
    ])
    result = query(session_id, query="pet(P).")
"""

from __future__ import annotations

import difflib
import json
import re
import uuid
import time
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from logic_server.core import schema, solver
from logic_server.core.solver import execute_query


_PATTERN_RE = re.compile(r"^\s*([a-z][A-Za-z0-9_]*)\s*(?:\((.*)\))?\s*$")


def _stable_key(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _rule_key(rule: Any) -> str:
    if isinstance(rule, str):
        return rule.strip()
    return _stable_key(rule)


def _parse_simple_term(token: str) -> Any:
    if token == "_" or token.startswith("_"):
        return token
    if token.isdigit():
        return int(token)
    try:
        return float(token)
    except ValueError:
        return token


def _parse_pattern(pattern: Any) -> Dict[str, Any]:
    if isinstance(pattern, dict):
        predicate = pattern.get("predicate")
        args = pattern.get("args", [])
        if not isinstance(args, list):
            raise ValueError("Pattern args must be a list")
        return {"predicate": predicate, "args": args}
    if not isinstance(pattern, str):
        raise ValueError("Pattern must be a string or {predicate, args} object")
    match = _PATTERN_RE.match(pattern)
    if not match:
        raise ValueError("Pattern must look like predicate(arg1, arg2)")
    predicate, arg_text = match.groups()
    if not arg_text:
        return {"predicate": predicate, "args": []}
    parts = [part.strip() for part in arg_text.split(",") if part.strip()]
    args = [_parse_simple_term(part) for part in parts]
    return {"predicate": predicate, "args": args}


@dataclass
class Session:
    """Represents a reasoning session with accumulated facts."""
    session_id: str
    facts: List[str] = field(default_factory=list)
    rules: List[Any] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)
    checkpoints: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    default_max_solutions: int = 5
    default_page_size: int = 50

    def add_facts(self, new_facts: List[str]) -> int:
        """Add facts to the session. Returns number of facts added."""
        before = len(self.facts)
        self.facts.extend(new_facts)
        self.last_accessed = time.time()
        if new_facts:
            self.history.append({"type": "facts", "items": new_facts})
        return len(self.facts) - before

    def remove_facts(self, facts_to_remove: List[str]) -> int:
        """Remove all matching facts from session. Returns number removed."""
        before = len(self.facts)
        # Remove ALL occurrences of each fact
        for fact in facts_to_remove:
            self.facts = [f for f in self.facts if f != fact]
        self.last_accessed = time.time()
        return before - len(self.facts)

    def add_rules(self, new_rules: List[Any]) -> int:
        """Add Prolog rules to the session. Returns number of rules added."""
        before = len(self.rules)
        self.rules.extend(new_rules)
        self.last_accessed = time.time()
        if new_rules:
            self.history.append({"type": "rules", "items": new_rules})
        return len(self.rules) - before

    def remove_rules(self, rules_to_remove: List[Any]) -> int:
        """Remove all matching rules from session. Returns number removed."""
        before = len(self.rules)
        # Remove ALL occurrences of each rule
        for rule in rules_to_remove:
            self.rules = [r for r in self.rules if r != rule]
        self.last_accessed = time.time()
        return before - len(self.rules)

    def undo_last(self) -> Optional[Dict[str, Any]]:
        """Undo the last assertion (facts or rules)."""
        if not self.history:
            return None
        entry = self.history.pop()
        if entry["type"] == "facts":
            removed = self.remove_facts(entry["items"])
            entry["removed"] = removed
        elif entry["type"] == "rules":
            removed = self.remove_rules(entry["items"])
            entry["removed"] = removed
        return entry

    def save_checkpoint(self, name: str) -> None:
        """Save a named checkpoint of the current session state."""
        self.checkpoints[name] = {
            "facts": list(self.facts),
            "rules": list(self.rules),
            "saved_at": datetime.fromtimestamp(time.time()).isoformat(),
        }

    def restore_checkpoint(self, name: str) -> bool:
        """Restore a named checkpoint. Returns False if not found."""
        checkpoint = self.checkpoints.get(name)
        if not checkpoint:
            return False
        self.facts = list(checkpoint["facts"])
        self.rules = list(checkpoint["rules"])
        self.last_accessed = time.time()
        return True

    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """List checkpoint metadata."""
        return [
            {
                "name": name,
                "fact_count": len(payload.get("facts", [])),
                "rule_count": len(payload.get("rules", [])),
                "saved_at": payload.get("saved_at"),
            }
            for name, payload in self.checkpoints.items()
        ]
    def query_facts(self, predicate: Optional[str] = None) -> List[str]:
        """Query accumulated facts, optionally filtered by predicate."""
        self.last_accessed = time.time()
        if predicate is None:
            return self.facts.copy()
        # Filter facts by predicate (simple regex match)
        import re
        pattern = re.compile(rf"^\s*{re.escape(predicate)}\s*\(")
        return [f for f in self.facts if pattern.match(f)]

    def get_statistics(self) -> Dict[str, Any]:
        """Get session statistics."""
        # Count facts by predicate
        predicate_counts: Dict[str, int] = {}
        for fact in self.facts:
            # Extract predicate from Prolog fact string
            match = re.match(r"^\s*([a-z][A-Za-z0-9_]*)\s*(?:\(|$)", fact)
            if match:
                pred = match.group(1)
                predicate_counts[pred] = predicate_counts.get(pred, 0) + 1

        return {
            "session_id": self.session_id,
            "total_facts": len(self.facts),
            "total_rules": len(self.rules),
            "predicates": predicate_counts,
            "created_at": datetime.fromtimestamp(self.created_at).isoformat(),
            "last_accessed": datetime.fromtimestamp(self.last_accessed).isoformat(),
            "age_seconds": time.time() - self.created_at,
            "metadata": self.metadata,
            "checkpoints": list(self.checkpoints.keys()),
            "default_max_solutions": self.default_max_solutions,
            "default_page_size": self.default_page_size,
        }


class SessionManager:
    """
    Thread-safe manager for reasoning sessions.

    Supports:
    - Creating and destroying sessions
    - Accumulating facts across operations
    - Querying accumulated knowledge
    - Session expiry and cleanup
    """

    def __init__(self, default_ttl_seconds: int = 3600):
        """
        Initialize session manager.

        Args:
            default_ttl_seconds: Time-to-live for sessions (default: 1 hour)
        """
        self.sessions: Dict[str, Session] = {}
        self.lock = threading.Lock()
        self.default_ttl = default_ttl_seconds

    def create_session(self, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new reasoning session.

        Args:
            metadata: Optional metadata to attach to session

        Returns:
            session_id: Unique identifier for the session
        """
        session_id = str(uuid.uuid4())
        with self.lock:
            session = Session(
                session_id=session_id,
                metadata=metadata or {}
            )
            self.sessions[session_id] = session

        return session_id

    def destroy_session(self, session_id: str) -> bool:
        """
        Destroy a session and free its resources.

        Args:
            session_id: Session to destroy

        Returns:
            True if session was destroyed, False if not found
        """
        with self.lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
                return True
            return False

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID, or None if not found."""
        with self.lock:
            return self.sessions.get(session_id)

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions with statistics."""
        with self.lock:
            return [s.get_statistics() for s in self.sessions.values()]

    def assert_facts(self, session_id: str, facts: List[str]) -> Dict[str, Any]:
        """
        Add facts to a session.

        Args:
            session_id: Target session
            facts: List of Prolog fact strings or dict facts to add

        Returns:
            Result with count of facts added
        """
        # Normalize facts (ensure they end with a period, strip whitespace)
        normalized_facts: List[str] = []
        for fact in facts:
            # Normalize Prolog string facts
            fact = fact.strip()
            if not fact.endswith("."):
                fact += "."
            normalized_facts.append(fact)

        with self.lock:
            session = self.sessions.get(session_id)
            if not session:
                return {
                    "success": False,
                    "error": f"Session not found: {session_id}"
                }
            existing = set(session.facts)
            deduped: List[str] = []
            duplicates: List[str] = []
            for fact in normalized_facts:
                if fact in existing:
                    duplicates.append(fact)
                else:
                    existing.add(fact)
                    deduped.append(fact)
            count = session.add_facts(deduped)
            total = len(session.facts)

        result = {
            "success": True,
            "session_id": session_id,
            "facts_added": count,
            "total_facts": total
        }
        if duplicates:
            result["warnings"] = [
                f"{len(duplicates)} duplicate facts were ignored."
            ]
            result["duplicates"] = duplicates
        return result

    def assert_rules(self, session_id: str, rules: List[str]) -> Dict[str, Any]:
        """
        Add rules to a session.

        Args:
            session_id: Target session
            rules: List of Prolog rule strings

        Returns:
            Result with count of rules added
        """
        errors = schema.validate_rules(rules)
        if errors:
            return {
                "success": False,
                "error": "Schema validation failed",
                "details": errors,
            }

        with self.lock:
            session = self.sessions.get(session_id)
            if not session:
                return {
                    "success": False,
                    "error": f"Session not found: {session_id}"
                }
            existing = {_rule_key(rule) for rule in session.rules}
            deduped: List[Any] = []
            duplicates: List[Any] = []
            for rule in rules:
                key = _rule_key(rule)
                if key in existing:
                    duplicates.append(rule)
                else:
                    existing.add(key)
                    deduped.append(rule)
            count = session.add_rules(deduped)
            total = len(session.rules)

        result = {
            "success": True,
            "session_id": session_id,
            "rules_added": count,
            "total_rules": total
        }
        if duplicates:
            result["warnings"] = [
                f"{len(duplicates)} duplicate rules were ignored."
            ]
            result["duplicates"] = duplicates
        return result

    def retract_rules(self, session_id: str, rules: List[str]) -> Dict[str, Any]:
        """
        Remove rules from a session.

        Args:
            session_id: Target session
            rules: List of Prolog rule strings to remove

        Returns:
            Result with count of rules removed
        """
        errors = schema.validate_rules(rules)
        if errors:
            return {
                "success": False,
                "error": "Schema validation failed",
                "details": errors,
            }

        with self.lock:
            session = self.sessions.get(session_id)
            if not session:
                return {
                    "success": False,
                    "error": f"Session not found: {session_id}"
                }
            count = session.remove_rules(rules)
            total = len(session.rules)

        return {
            "success": True,
            "session_id": session_id,
            "rules_removed": count,
            "total_rules": total
        }

    def retract_facts(self, session_id: str, facts: List[str]) -> Dict[str, Any]:
        """
        Remove facts from a session.

        Args:
            session_id: Target session
            facts: List of Prolog fact strings or dict facts to remove

        Returns:
            Result with count of facts removed
        """
        # Normalize facts (ensure they end with a period, strip whitespace)
        normalized_facts: List[str] = []
        for fact in facts:
            # Normalize Prolog string facts
            fact = fact.strip()
            if not fact.endswith("."):
                fact += "."
            normalized_facts.append(fact)

        with self.lock:
            session = self.sessions.get(session_id)
            if not session:
                return {
                    "success": False,
                    "error": f"Session not found: {session_id}"
                }
            count = session.remove_facts(normalized_facts)
            total = len(session.facts)

        return {
            "success": True,
            "session_id": session_id,
            "facts_removed": count,
            "total_facts": total
        }

    def query_facts(self, session_id: str, predicate: Optional[str] = None) -> Dict[str, Any]:
        """
        Query accumulated facts in a session.

        Args:
            session_id: Target session
            predicate: Optional predicate filter

        Returns:
            Matching facts
        """
        with self.lock:
            session = self.sessions.get(session_id)
            if not session:
                return {
                    "success": False,
                    "error": f"Session not found: {session_id}"
                }
            facts = session.query_facts(predicate)

        return {
            "success": True,
            "session_id": session_id,
            "predicate_filter": predicate,
            "facts": facts,
            "count": len(facts)
        }

    def list_predicates(self, session_id: str) -> Dict[str, Any]:
        """List predicates present in facts and rules for a session."""
        with self.lock:
            session = self.sessions.get(session_id)
            if not session:
                return {
                    "success": False,
                    "error": f"Session not found: {session_id}"
                }
            facts = list(session.facts)
            rules = list(session.rules)

        # Extract predicates from Prolog facts and rules
        predicates_set = set()
        for fact in facts:
            match = re.match(r"^\s*([a-z][A-Za-z0-9_]*)\s*(?:\(|$)", fact)
            if match:
                predicates_set.add(match.group(1))

        # Extract from rules
        if isinstance(rules, list):
            for rule in rules:
                if isinstance(rule, str):
                    match = re.match(r"^\s*([a-z][A-Za-z0-9_]*)\s*\(", rule)
                    if match:
                        predicates_set.add(match.group(1))

        predicates = sorted(predicates_set)
        return {
            "success": True,
            "session_id": session_id,
            "predicates": predicates,
            "count": len(predicates),
        }

    def validate_query(self, session_id: str, query: Any) -> Dict[str, Any]:
        """Validate a query against the session without executing it."""
        if query is None:
            return {
                "success": False,
                "error": "Query required",
                "session_id": session_id,
            }
        errors = schema.validate_query(query)
        if errors:
            return {
                "success": False,
                "error": "Schema validation failed",
                "details": errors,
                "session_id": session_id,
            }
        with self.lock:
            session = self.sessions.get(session_id)
            if not session:
                return {
                    "success": False,
                    "error": f"Session not found: {session_id}"
                }
            facts = list(session.facts)
            rules = list(session.rules)
        predicates = solver.list_predicates(facts, rules)
        predicate = solver.extract_query_predicate(query)
        warnings: List[str] = []
        if predicate and predicates and predicate not in predicates:
            close = difflib.get_close_matches(predicate, predicates, n=3)
            if close:
                warnings.append(
                    f"Predicate '{predicate}' not found. Did you mean: {', '.join(close)}?"
                )
            else:
                warnings.append(
                    f"Predicate '{predicate}' not found in session."
                )
        return {
            "success": True,
            "session_id": session_id,
            "query": query,
            "predicate": predicate,
            "warnings": warnings,
        }

    def assert_pattern(
        self,
        session_id: str,
        pattern: Any,
        bindings: List[Any],
    ) -> Dict[str, Any]:
        """Assert facts generated from a template pattern."""
        parsed = _parse_pattern(pattern)
        args = parsed.get("args", [])
        placeholders = [
            idx
            for idx, arg in enumerate(args)
            if arg == "_" or (isinstance(arg, dict) and arg.get("var") == "_")
        ]
        if not placeholders:
            return {
                "success": False,
                "error": "Pattern must contain '_' placeholders to fill.",
            }

        generated: List[str] = []
        for binding in bindings:
            if isinstance(binding, dict):
                values = []
                for key, value in binding.items():
                    values.append(key)
                    values.append(value)
            elif isinstance(binding, list):
                values = binding
            else:
                return {
                    "success": False,
                    "error": "Each binding must be an object or list.",
                }
            if len(values) != len(placeholders):
                return {
                    "success": False,
                    "error": (
                        f"Binding value count ({len(values)}) does not match "
                        f"placeholders ({len(placeholders)})."
                    ),
                }
            filled_args = list(args)
            for idx, value in zip(placeholders, values):
                filled_args[idx] = value

            # Generate Prolog fact string
            predicate = parsed["predicate"]
            args_str = ", ".join(str(arg) for arg in filled_args)
            fact = f"{predicate}({args_str})." if filled_args else f"{predicate}."
            generated.append(fact)

        return self.assert_facts(session_id, generated)

    def undo_last(self, session_id: str) -> Dict[str, Any]:
        """Undo the last assertion for a session."""
        with self.lock:
            session = self.sessions.get(session_id)
            if not session:
                return {
                    "success": False,
                    "error": f"Session not found: {session_id}"
                }
            entry = session.undo_last()
            if not entry:
                return {
                    "success": False,
                    "error": "No history entries to undo."
                }
        return {
            "success": True,
            "session_id": session_id,
            "undone": entry,
        }

    def create_checkpoint(self, session_id: str, name: str) -> Dict[str, Any]:
        """Create a named checkpoint for a session."""
        with self.lock:
            session = self.sessions.get(session_id)
            if not session:
                return {
                    "success": False,
                    "error": f"Session not found: {session_id}"
                }
            session.save_checkpoint(name)
        return {
            "success": True,
            "session_id": session_id,
            "checkpoint": name,
        }

    def restore_checkpoint(self, session_id: str, name: str) -> Dict[str, Any]:
        """Restore a named checkpoint for a session."""
        with self.lock:
            session = self.sessions.get(session_id)
            if not session:
                return {
                    "success": False,
                    "error": f"Session not found: {session_id}"
                }
            restored = session.restore_checkpoint(name)
            if not restored:
                return {
                    "success": False,
                    "error": f"Checkpoint not found: {name}",
                }
        return {
            "success": True,
            "session_id": session_id,
            "checkpoint": name,
        }

    def list_checkpoints(self, session_id: str) -> Dict[str, Any]:
        """List checkpoints for a session."""
        with self.lock:
            session = self.sessions.get(session_id)
            if not session:
                return {
                    "success": False,
                    "error": f"Session not found: {session_id}"
                }
            checkpoints = session.list_checkpoints()
        return {
            "success": True,
            "session_id": session_id,
            "checkpoints": checkpoints,
            "count": len(checkpoints),
        }

    def set_session_options(
        self,
        session_id: str,
        max_solutions: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Set defaults for a session."""
        with self.lock:
            session = self.sessions.get(session_id)
            if not session:
                return {
                    "success": False,
                    "error": f"Session not found: {session_id}"
                }
            if max_solutions is not None:
                session.default_max_solutions = max(1, min(1000, int(max_solutions)))
            if page_size is not None:
                session.default_page_size = max(1, min(1000, int(page_size)))
        return {
            "success": True,
            "session_id": session_id,
            "default_max_solutions": session.default_max_solutions,
            "default_page_size": session.default_page_size,
        }

    def diff_sessions(self, session_id_a: str, session_id_b: str) -> Dict[str, Any]:
        """Diff facts and rules between two sessions."""
        with self.lock:
            session_a = self.sessions.get(session_id_a)
            session_b = self.sessions.get(session_id_b)
            if not session_a or not session_b:
                return {
                    "success": False,
                    "error": "One or both sessions not found.",
                }
            facts_a_set = set(session_a.facts)
            facts_b_set = set(session_b.facts)
            rules_a = { _rule_key(rule): rule for rule in session_a.rules }
            rules_b = { _rule_key(rule): rule for rule in session_b.rules }

        added_facts = list(facts_b_set - facts_a_set)
        removed_facts = list(facts_a_set - facts_b_set)
        added_rules = [rules_b[key] for key in rules_b.keys() - rules_a.keys()]
        removed_rules = [rules_a[key] for key in rules_a.keys() - rules_b.keys()]

        return {
            "success": True,
            "session_id_a": session_id_a,
            "session_id_b": session_id_b,
            "added_facts": added_facts,
            "removed_facts": removed_facts,
            "added_rules": added_rules,
            "removed_rules": removed_rules,
        }

    def export_session(self, session_id: str) -> Dict[str, Any]:
        """Export session facts and rules as a Prolog program."""
        with self.lock:
            session = self.sessions.get(session_id)
            if not session:
                return {
                    "success": False,
                    "error": f"Session not found: {session_id}"
                }
            facts = list(session.facts)
            rules = list(session.rules)

        lines = []
        # Facts are already in Prolog format
        lines.extend(facts)
        rules_text = solver._render_rules_program(rules)
        if rules_text:
            lines.append("")
            lines.extend(rules_text.splitlines())
        program = "\n".join(lines) + "\n"
        return {
            "success": True,
            "session_id": session_id,
            "prolog": program,
        }

    def query(
        self,
        session_id: str,
        max_solutions: Optional[int] = None,
        offset: int = 0,
        limit: Optional[int] = None,
        query: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Query all accumulated facts in the session.

        Args:
            session_id: Target session
            max_solutions: Maximum solutions to return
            query: Query in predicate(arg1, arg2) form
        Returns:
            Query results from prolog_query
        """
        # Validate query early
        if not query:
            return {
                "success": False,
                "error": "Query required",
                "session_id": session_id,
            }

        # Get a snapshot of facts and rules while holding the lock
        with self.lock:
            session = self.sessions.get(session_id)
            if not session:
                return {
                    "success": False,
                    "error": f"Session not found: {session_id}"
                }

            # Get copies of facts and rules for thread-safe query execution
            facts = session.query_facts()  # Returns a copy
            rules_program = solver._render_rules_program(session.rules) if session.rules else None

            if not facts and not rules_program:
                return {
                    "success": False,
                    "error": "No facts or rules in session to query",
                    "session_id": session_id
                }

            # Update last accessed time
            session.last_accessed = time.time()
            if max_solutions is None:
                max_solutions = session.default_max_solutions
            if limit is None and offset > 0:
                limit = session.default_page_size

        # Execute query outside the lock (query execution may take time)
        effective_max = max_solutions if max_solutions is not None else 5
        if limit is not None:
            effective_max = max(effective_max, offset + limit)
        result = solver.execute_query(
            facts=facts,
            rules_program=rules_program,
            query=query,
            max_solutions=effective_max
        )

        # Add session info to result
        result["session_id"] = session_id
        result["facts_used"] = len(facts)
        if result.get("success") and result.get("solutions") is not None and limit is not None:
            solutions = result.get("solutions", [])
            total_count = len(solutions)
            sliced = solutions[offset:offset + limit]
            result["solutions"] = sliced
            result["total_count"] = total_count
            result["count"] = len(sliced)
            result["offset"] = offset
            result["limit"] = limit

        return result

    def cleanup_expired_sessions(self, max_age_seconds: Optional[int] = None) -> int:
        """
        Remove sessions older than max_age_seconds.

        Args:
            max_age_seconds: Age threshold (default: use default_ttl)

        Returns:
            Number of sessions removed
        """
        max_age = max_age_seconds or self.default_ttl
        cutoff_time = time.time() - max_age

        with self.lock:
            expired = [
                sid for sid, session in self.sessions.items()
                if session.last_accessed < cutoff_time
            ]

            for sid in expired:
                del self.sessions[sid]

        return len(expired)


# Global session manager instance with thread-safe initialization
_global_manager: Optional[SessionManager] = None
_global_manager_lock = threading.Lock()


def get_session_manager() -> SessionManager:
    """Get or create the global session manager (thread-safe)."""
    global _global_manager
    if _global_manager is None:
        with _global_manager_lock:
            # Double-check after acquiring lock
            if _global_manager is None:
                _global_manager = SessionManager()
    return _global_manager


# Convenience functions that use the global manager

def create_session(metadata: Optional[Dict[str, Any]] = None) -> str:
    """Create a new reasoning session."""
    return get_session_manager().create_session(metadata)


def destroy_session(session_id: str) -> bool:
    """Destroy a session."""
    return get_session_manager().destroy_session(session_id)


def list_sessions() -> List[Dict[str, Any]]:
    """List all active sessions."""
    return get_session_manager().list_sessions()


def assert_facts(session_id: str, facts: List[str]) -> Dict[str, Any]:
    """Add facts to a session."""
    return get_session_manager().assert_facts(session_id, facts)

def assert_rules(session_id: str, rules: List[Any]) -> Dict[str, Any]:
    """Add rules to a session."""
    return get_session_manager().assert_rules(session_id, rules)


def retract_facts(session_id: str, facts: List[str]) -> Dict[str, Any]:
    """Remove facts from a session."""
    return get_session_manager().retract_facts(session_id, facts)

def retract_rules(session_id: str, rules: List[Any]) -> Dict[str, Any]:
    """Remove rules from a session."""
    return get_session_manager().retract_rules(session_id, rules)


def query_facts(session_id: str, predicate: Optional[str] = None) -> Dict[str, Any]:
    """Query facts in a session."""
    return get_session_manager().query_facts(session_id, predicate)

def list_predicates(session_id: str) -> Dict[str, Any]:
    """List predicates for a session."""
    return get_session_manager().list_predicates(session_id)

def validate_query(session_id: str, query: Any) -> Dict[str, Any]:
    """Validate a query against a session without executing."""
    return get_session_manager().validate_query(session_id, query)


def query(
    session_id: str,
    max_solutions: Optional[int] = None,
    offset: int = 0,
    limit: Optional[int] = None,
    query: Optional[str] = None,
) -> Dict[str, Any]:
    """Query using accumulated facts and a query."""
    return get_session_manager().query(
        session_id,
        max_solutions,
        offset=offset,
        limit=limit,
        query=query
    )

def assert_pattern(session_id: str, pattern: Any, bindings: List[Any]) -> Dict[str, Any]:
    """Assert facts generated from a pattern template."""
    return get_session_manager().assert_pattern(session_id, pattern, bindings)

def undo_last(session_id: str) -> Dict[str, Any]:
    """Undo the last assertion in a session."""
    return get_session_manager().undo_last(session_id)

def create_checkpoint(session_id: str, name: str) -> Dict[str, Any]:
    """Create a named checkpoint."""
    return get_session_manager().create_checkpoint(session_id, name)

def restore_checkpoint(session_id: str, name: str) -> Dict[str, Any]:
    """Restore a named checkpoint."""
    return get_session_manager().restore_checkpoint(session_id, name)

def list_checkpoints(session_id: str) -> Dict[str, Any]:
    """List checkpoints for a session."""
    return get_session_manager().list_checkpoints(session_id)

def set_session_options(
    session_id: str,
    max_solutions: Optional[int] = None,
    page_size: Optional[int] = None,
) -> Dict[str, Any]:
    """Set default options for a session."""
    return get_session_manager().set_session_options(
        session_id,
        max_solutions=max_solutions,
        page_size=page_size
    )

def diff_sessions(session_id_a: str, session_id_b: str) -> Dict[str, Any]:
    """Diff two sessions."""
    return get_session_manager().diff_sessions(session_id_a, session_id_b)

def export_session(session_id: str) -> Dict[str, Any]:
    """Export a session to Prolog."""
    return get_session_manager().export_session(session_id)




def get_session_stats(session_id: str) -> Optional[Dict[str, Any]]:
    """Get statistics for a session."""
    session = get_session_manager().get_session(session_id)
    return session.get_statistics() if session else None

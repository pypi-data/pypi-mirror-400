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

import uuid
import time
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from logic_server.core.solver import execute_query


@dataclass
class Session:
    """Represents a reasoning session with accumulated facts."""
    session_id: str
    facts: List[Dict[str, Any]] = field(default_factory=list)
    rules: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_facts(self, new_facts: List[Dict[str, Any]]) -> int:
        """Add facts to the session. Returns number of facts added."""
        before = len(self.facts)
        self.facts.extend(new_facts)
        self.last_accessed = time.time()
        return len(self.facts) - before

    def remove_facts(self, facts_to_remove: List[Dict[str, Any]]) -> int:
        """Remove all matching facts from session. Returns number removed."""
        before = len(self.facts)
        # Remove ALL occurrences of each fact
        for fact in facts_to_remove:
            self.facts = [f for f in self.facts if f != fact]
        self.last_accessed = time.time()
        return before - len(self.facts)

    def add_rules(self, new_rules: List[str]) -> int:
        """Add Prolog rules to the session. Returns number of rules added."""
        before = len(self.rules)
        self.rules.extend(new_rules)
        self.last_accessed = time.time()
        return len(self.rules) - before

    def remove_rules(self, rules_to_remove: List[str]) -> int:
        """Remove all matching rules from session. Returns number removed."""
        before = len(self.rules)
        # Remove ALL occurrences of each rule
        for rule in rules_to_remove:
            self.rules = [r for r in self.rules if r != rule]
        self.last_accessed = time.time()
        return before - len(self.rules)
    def query_facts(self, predicate: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query accumulated facts, optionally filtered by predicate."""
        self.last_accessed = time.time()
        if predicate is None:
            return self.facts.copy()
        return [f for f in self.facts if f.get("predicate") == predicate]

    def get_statistics(self) -> Dict[str, Any]:
        """Get session statistics."""
        # Count facts by predicate
        predicate_counts: Dict[str, int] = {}
        for fact in self.facts:
            pred = fact.get("predicate", "unknown")
            predicate_counts[pred] = predicate_counts.get(pred, 0) + 1

        return {
            "session_id": self.session_id,
            "total_facts": len(self.facts),
            "total_rules": len(self.rules),
            "predicates": predicate_counts,
            "created_at": datetime.fromtimestamp(self.created_at).isoformat(),
            "last_accessed": datetime.fromtimestamp(self.last_accessed).isoformat(),
            "age_seconds": time.time() - self.created_at,
            "metadata": self.metadata
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

    def assert_facts(self, session_id: str, facts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Add facts to a session.

        Args:
            session_id: Target session
            facts: List of facts to add

        Returns:
            Result with count of facts added
        """
        with self.lock:
            session = self.sessions.get(session_id)
            if not session:
                return {
                    "success": False,
                    "error": f"Session not found: {session_id}"
                }
            count = session.add_facts(facts)
            total = len(session.facts)

        return {
            "success": True,
            "session_id": session_id,
            "facts_added": count,
            "total_facts": total
        }

    def assert_rules(self, session_id: str, rules: List[str]) -> Dict[str, Any]:
        """
        Add rules to a session.

        Args:
            session_id: Target session
            rules: List of Prolog rule strings

        Returns:
            Result with count of rules added
        """
        with self.lock:
            session = self.sessions.get(session_id)
            if not session:
                return {
                    "success": False,
                    "error": f"Session not found: {session_id}"
                }
            count = session.add_rules(rules)
            total = len(session.rules)

        return {
            "success": True,
            "session_id": session_id,
            "rules_added": count,
            "total_rules": total
        }

    def retract_rules(self, session_id: str, rules: List[str]) -> Dict[str, Any]:
        """
        Remove rules from a session.

        Args:
            session_id: Target session
            rules: List of Prolog rule strings to remove

        Returns:
            Result with count of rules removed
        """
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

    def retract_facts(self, session_id: str, facts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Remove facts from a session.

        Args:
            session_id: Target session
            facts: List of facts to remove

        Returns:
            Result with count of facts removed
        """
        with self.lock:
            session = self.sessions.get(session_id)
            if not session:
                return {
                    "success": False,
                    "error": f"Session not found: {session_id}"
                }
            count = session.remove_facts(facts)
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

    def query(
        self,
        session_id: str,
        max_solutions: int = 5,
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
            rules_program = "\n".join(session.rules) if session.rules else None

            if not facts:
                return {
                    "success": False,
                    "error": "No facts in session to query",
                    "session_id": session_id
                }

            # Update last accessed time
            session.last_accessed = time.time()

        # Execute query outside the lock (query execution may take time)
        result = execute_query(
            facts=facts,
            base_knowledge=None,
            rules_program=rules_program,
            query=query,
            max_solutions=max_solutions
        )

        # Add session info to result
        result["session_id"] = session_id
        result["facts_used"] = len(facts)

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


def assert_facts(session_id: str, facts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Add facts to a session."""
    return get_session_manager().assert_facts(session_id, facts)

def assert_rules(session_id: str, rules: List[str]) -> Dict[str, Any]:
    """Add rules to a session."""
    return get_session_manager().assert_rules(session_id, rules)


def retract_facts(session_id: str, facts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Remove facts from a session."""
    return get_session_manager().retract_facts(session_id, facts)

def retract_rules(session_id: str, rules: List[str]) -> Dict[str, Any]:
    """Remove rules from a session."""
    return get_session_manager().retract_rules(session_id, rules)


def query_facts(session_id: str, predicate: Optional[str] = None) -> Dict[str, Any]:
    """Query facts in a session."""
    return get_session_manager().query_facts(session_id, predicate)


def query(
    session_id: str,
    max_solutions: int = 5,
    query: Optional[str] = None,
) -> Dict[str, Any]:
    """Query using accumulated facts and a query."""
    return get_session_manager().query(session_id, max_solutions, query=query)




def get_session_stats(session_id: str) -> Optional[Dict[str, Any]]:
    """Get statistics for a session."""
    session = get_session_manager().get_session(session_id)
    return session.get_statistics() if session else None

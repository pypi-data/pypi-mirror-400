#!/usr/bin/env python3
"""
Example: Using MQI-based solver with session management.

This demonstrates how to use the MQI solver for fast, persistent
Prolog queries with stateful sessions.

Requirements:
    pip install janus-swi

Usage:
    python examples/mqi_session_example.py
"""

from logic_server.core.session import create_session, destroy_session
from logic_server.core.session import assert_facts, assert_rules, query

try:
    from logic_server.core.mqi_solver import get_mqi_solver
    HAS_MQI = True
except ImportError:
    HAS_MQI = False
    print("⚠️  MQI not available. Install with: pip install janus-swi")
    print("   Falling back to subprocess mode...\n")


def demo_standard_mode():
    """Standard session mode (uses subprocess)."""
    print("=" * 60)
    print("Standard Session Mode (subprocess)")
    print("=" * 60)

    session_id = create_session(metadata={"mode": "standard"})
    try:
        # Add facts
        result = assert_facts(session_id, [
            {"predicate": "person", "args": ["alice"]},
            {"predicate": "person", "args": ["bob"]},
            {"predicate": "person", "args": ["carol"]},
            {"predicate": "owns", "args": ["alice", "cat"]},
            {"predicate": "owns", "args": ["bob", "dog"]},
        ])
        print(f"✓ Asserted {result['facts_added']} facts")

        # Query
        result = query(session_id, query="person(P).")
        print(f"✓ Found {result['count']} people:")
        for sol in result['solutions']:
            print(f"  - {sol['Bindings']['P']}")

    finally:
        destroy_session(session_id)


def demo_mqi_mode():
    """MQI-enhanced mode (uses persistent Prolog process)."""
    if not HAS_MQI:
        print("\nSkipping MQI demo (janus-swi not installed)")
        return

    print("\n" + "=" * 60)
    print("MQI-Enhanced Mode (persistent process)")
    print("=" * 60)

    # Get the global MQI solver
    solver = get_mqi_solver()

    # Use it directly (bypassing sessions)
    facts = [
        {"predicate": "person", "args": ["alice"]},
        {"predicate": "person", "args": ["bob"]},
        {"predicate": "person", "args": ["carol"]},
        {"predicate": "owns", "args": ["alice", "cat"]},
        {"predicate": "owns", "args": ["bob", "dog"]},
    ]

    # Run multiple queries (all on same persistent process)
    print("\nRunning 5 queries on persistent Prolog process:")

    import time
    start = time.time()

    for i in range(5):
        result = solver.query(facts, query_text="person(P).", max_solutions=10)
        print(f"  Query {i+1}: {result['count']} results in {(time.time()-start)*1000:.1f}ms total")

    elapsed = time.time() - start
    print(f"\n✓ Total time: {elapsed*1000:.1f}ms ({elapsed/5*1000:.1f}ms avg per query)")


def demo_mqi_with_rules():
    """MQI with Prolog rules."""
    if not HAS_MQI:
        return

    print("\n" + "=" * 60)
    print("MQI with Rules")
    print("=" * 60)

    solver = get_mqi_solver()

    facts = [
        {"predicate": "parent", "args": ["alice", "bob"]},
        {"predicate": "parent", "args": ["bob", "carol"]},
        {"predicate": "parent", "args": ["carol", "dave"]},
    ]

    rules = """
    grandparent(X, Z) :- parent(X, Y), parent(Y, Z).
    ancestor(X, Y) :- parent(X, Y).
    ancestor(X, Z) :- parent(X, Y), ancestor(Y, Z).
    """

    # Query with rules
    result = solver.query(
        facts=facts,
        rules_program=rules,
        query_text="grandparent(X, Z).",
        max_solutions=10
    )

    print(f"✓ Grandparent relationships:")
    for sol in result['solutions']:
        print(f"  - {sol['Bindings']['X']} is grandparent of {sol['Bindings']['Z']}")

    # Query ancestors
    result = solver.query(
        facts=facts,
        rules_program=rules,
        query_text="ancestor(alice, X).",
        max_solutions=10
    )

    print(f"\n✓ Alice's descendants:")
    for sol in result['solutions']:
        print(f"  - {sol['Bindings']['X']}")


def demo_performance_comparison():
    """Compare subprocess vs MQI performance."""
    if not HAS_MQI:
        return

    print("\n" + "=" * 60)
    print("Performance Comparison")
    print("=" * 60)

    facts = [{"predicate": "person", "args": [f"person_{i}"]} for i in range(10)]
    query_text = "person(P)."
    num_queries = 20

    # Subprocess mode
    from logic_server.core.solver import prolog_query
    import time

    print(f"\nSubprocess mode ({num_queries} queries):")
    start = time.time()
    for _ in range(num_queries):
        prolog_query(facts, query=query_text, max_solutions=10)
    subprocess_time = time.time() - start
    print(f"  Time: {subprocess_time:.3f}s ({subprocess_time/num_queries*1000:.1f}ms avg)")

    # MQI mode
    solver = get_mqi_solver()
    print(f"\nMQI mode ({num_queries} queries):")
    start = time.time()
    for _ in range(num_queries):
        solver.query(facts, query_text=query_text, max_solutions=10)
    mqi_time = time.time() - start
    print(f"  Time: {mqi_time:.3f}s ({mqi_time/num_queries*1000:.1f}ms avg)")

    # Speedup
    speedup = subprocess_time / mqi_time if mqi_time > 0 else 0
    print(f"\n✓ Speedup: {speedup:.1f}x faster with MQI!")


def main():
    print("\n🚀 MQI Prolog Session Examples\n")

    demo_standard_mode()
    demo_mqi_mode()
    demo_mqi_with_rules()
    demo_performance_comparison()

    print("\n" + "=" * 60)
    print("✓ All demos completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

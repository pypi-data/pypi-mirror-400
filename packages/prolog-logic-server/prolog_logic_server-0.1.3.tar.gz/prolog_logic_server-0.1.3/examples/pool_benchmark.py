#!/usr/bin/env python3
"""
Benchmark comparing subprocess-based vs MQI-based Prolog execution.

This demonstrates the performance benefits of using a persistent
Prolog process pool vs spawning subprocesses for each query.

Usage:
    # Standard subprocess mode
    python examples/pool_benchmark.py --mode subprocess

    # MQI mode (requires: pip install janus-swi)
    python examples/pool_benchmark.py --mode mqi

    # Both for comparison
    python examples/pool_benchmark.py --mode both
"""

import argparse
import time
from typing import List, Dict, Any

from logic_server.core.solver import prolog_query

# Sample facts for testing
TEST_FACTS = [
    {"predicate": "person", "args": ["alice"]},
    {"predicate": "person", "args": ["bob"]},
    {"predicate": "person", "args": ["carol"]},
    {"predicate": "person", "args": ["dave"]},
    {"predicate": "owns", "args": ["alice", "cat"]},
    {"predicate": "owns", "args": ["bob", "dog"]},
    {"predicate": "owns", "args": ["carol", "fish"]},
    {"predicate": "forbidden", "args": ["dave", "cat"]},
]

TEST_QUERIES = [
    "person(P).",
    "owns(P, Pet).",
    "owns(alice, X).",
    "forbidden(P, Pet).",
]


def benchmark_subprocess(num_queries: int) -> float:
    """Benchmark subprocess-based execution."""
    print(f"\n📊 Subprocess mode: {num_queries} queries")

    start = time.time()
    for i in range(num_queries):
        query = TEST_QUERIES[i % len(TEST_QUERIES)]
        result = prolog_query(
            facts=TEST_FACTS,
            query=query,
            max_solutions=10
        )
        if not result.get("success"):
            print(f"Query failed: {result.get('error')}")

    elapsed = time.time() - start
    qps = num_queries / elapsed

    print(f"  Time: {elapsed:.2f}s")
    print(f"  Queries/sec: {qps:.1f}")
    print(f"  Avg latency: {(elapsed/num_queries)*1000:.1f}ms")

    return elapsed


def benchmark_mqi(num_queries: int) -> float:
    """Benchmark MQI-based execution."""
    try:
        from logic_server.core.mqi_solver import MQISolver
    except ImportError:
        print("\n⚠️  MQI mode requires: pip install janus-swi")
        print("   Skipping MQI benchmark")
        return 0.0

    print(f"\n📊 MQI mode: {num_queries} queries")

    solver = MQISolver()
    try:
        start = time.time()
        for i in range(num_queries):
            query = TEST_QUERIES[i % len(TEST_QUERIES)]
            result = solver.query_prolog(
                facts=TEST_FACTS,
                query_text=query,
                max_solutions=10
            )
            if not result.get("success"):
                print(f"Query failed: {result.get('error')}")

        elapsed = time.time() - start
        qps = num_queries / elapsed

        print(f"  Time: {elapsed:.2f}s")
        print(f"  Queries/sec: {qps:.1f}")
        print(f"  Avg latency: {(elapsed/num_queries)*1000:.1f}ms")

        return elapsed
    finally:
        solver.close()


def benchmark_pool(num_queries: int) -> float:
    """Benchmark pooled execution."""
    try:
        from logic_server.core.prolog_pool import PrologPool
    except ImportError:
        print("\n⚠️  Pool mode not available")
        return 0.0

    print(f"\n📊 Pool mode: {num_queries} queries (pool size=4)")

    pool = PrologPool(size=4)
    try:
        start = time.time()
        for i in range(num_queries):
            query = TEST_QUERIES[i % len(TEST_QUERIES)]
            with pool.acquire() as prolog:
                result = prolog.execute_query(
                    facts=TEST_FACTS,
                    rules_program=None,
                    query=query,
                    max_solutions=10
                )
                if not result.get("success"):
                    print(f"Query failed: {result.get('error')}")

        elapsed = time.time() - start
        qps = num_queries / elapsed

        print(f"  Time: {elapsed:.2f}s")
        print(f"  Queries/sec: {qps:.1f}")
        print(f"  Avg latency: {(elapsed/num_queries)*1000:.1f}ms")

        stats = pool.get_stats()
        print(f"  Pool stats: {stats}")

        return elapsed
    finally:
        pool.shutdown()


def main():
    parser = argparse.ArgumentParser(description="Benchmark Prolog execution modes")
    parser.add_argument(
        "--mode",
        choices=["subprocess", "mqi", "pool", "both"],
        default="both",
        help="Execution mode to benchmark"
    )
    parser.add_argument(
        "--queries",
        type=int,
        default=100,
        help="Number of queries to run"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Prolog Execution Mode Benchmark")
    print("=" * 60)

    results = {}

    if args.mode in ["subprocess", "both"]:
        results["subprocess"] = benchmark_subprocess(args.queries)

    if args.mode in ["mqi", "both"]:
        results["mqi"] = benchmark_mqi(args.queries)

    if args.mode in ["pool", "both"]:
        results["pool"] = benchmark_pool(args.queries)

    # Summary
    if len(results) > 1:
        print("\n" + "=" * 60)
        print("Summary")
        print("=" * 60)

        baseline = results.get("subprocess", 0)
        for mode, elapsed in results.items():
            if elapsed > 0:
                speedup = baseline / elapsed if elapsed > 0 else 0
                print(f"{mode:12s}: {elapsed:6.2f}s  (speedup: {speedup:.1f}x)")


if __name__ == "__main__":
    main()

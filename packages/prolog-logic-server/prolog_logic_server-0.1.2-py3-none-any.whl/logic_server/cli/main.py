from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List

from logic_server.core.solver import prolog_query


def load_facts(path: str) -> List[Dict[str, Any]]:
    try:
        with open(path, "r") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        raise SystemExit(f"❌ File not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"❌ Invalid JSON in {path}: {exc}")

    if not isinstance(data, list):
        raise SystemExit("❌ Facts file must contain a JSON array of fact objects.")
    return data


def format_solution(result: Dict[str, Any]) -> str:
    if not result.get("success"):
        return f"❌ Failed: {result.get('error', 'Unknown error')}"

    solutions = result.get("solutions", [])
    if not solutions:
        return "❌ No solutions found"

    output: List[str] = []
    output.append(f"✅ Found {len(solutions)} solution(s):\n")
    for i, solution in enumerate(solutions, 1):
        output.append(f"Solution {i}:")
        bindings = solution.get("Bindings", {})
        for name, value in sorted(bindings.items()):
            output.append(f"  • {name} = {value}")
        output.append("")
    return "\n".join(output)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Prolog queries over JSON facts.")
    parser.add_argument(
        "facts_file",
        help="Path to JSON facts file"
    )
    parser.add_argument(
        "--query",
        required=True,
        help="Query in predicate(arg1, arg2) form (e.g., 'person(P).')"
    )
    parser.add_argument(
        "--max-solutions",
        type=int,
        default=5,
        help="Maximum number of solutions to return (default: 5)"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    facts = load_facts(args.facts_file)
    result = prolog_query(
        facts=facts,
        base_knowledge=None,
        rules_program=None,
        query=args.query,
        max_solutions=args.max_solutions,
    )

    print("🔍 Result:")
    print(format_solution(result))
    print("\n📊 Raw Result:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

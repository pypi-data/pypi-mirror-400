from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List

from logic_server.core.solver import execute_query


def load_facts(path: str) -> List[str]:
    """Load facts from a Prolog file (.pl) or JSON file (.json)."""
    try:
        with open(path, "r") as handle:
            # Try to determine format based on extension
            if path.endswith(".pl"):
                # Prolog format - read lines and filter out comments/empty lines
                facts = []
                for line in handle:
                    line = line.strip()
                    if line and not line.startswith("%") and not line.startswith(":-"):
                        facts.append(line)
                return facts
            elif path.endswith(".json"):
                # Legacy JSON format - still supported
                data = json.load(handle)
                if not isinstance(data, list):
                    raise SystemExit("❌ JSON file must contain an array.")
                # Check if it's Prolog strings or JSON objects
                if data and isinstance(data[0], str):
                    return data
                else:
                    raise SystemExit("❌ JSON format with objects is no longer supported. Use Prolog syntax instead.")
            else:
                # Try to auto-detect
                content = handle.read()
                handle.seek(0)
                try:
                    data = json.loads(content)
                    if isinstance(data, list) and data and isinstance(data[0], str):
                        return data
                except:
                    pass
                # Treat as Prolog
                facts = []
                for line in content.splitlines():
                    line = line.strip()
                    if line and not line.startswith("%") and not line.startswith(":-"):
                        facts.append(line)
                return facts
    except FileNotFoundError:
        raise SystemExit(f"❌ File not found: {path}")


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
    parser = argparse.ArgumentParser(description="Run Prolog queries over fact files.")
    parser.add_argument(
        "facts_file",
        help="Path to facts file (.pl for Prolog, .json for Prolog strings)"
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
    result = execute_query(
        facts=facts,
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

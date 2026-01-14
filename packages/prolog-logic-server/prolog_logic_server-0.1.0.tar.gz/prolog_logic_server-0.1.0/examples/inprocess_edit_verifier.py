"""
In-process edit verifier: LLM extracts facts, logic server checks invariants.

Example:
  python examples/inprocess_edit_verifier.py --ollama-model gpt-oss:20b \
    --input-file examples/program_sample.py
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from logic_server.core.session import (
    assert_facts,
    assert_rules,
    create_session,
    destroy_session,
    query,
)
from logic_server.llm.clients import OllamaLLM


FACT_SPEC = [
    "function(load_config)",
    "function(transform_values)",
    "function(write_report)",
    "function(run_pipeline)",
    "has_docstring(load_config, true)",
    "has_docstring(transform_values, true)",
    "has_docstring(write_report, true)",
    "has_docstring(run_pipeline, true)",
    "is_public(load_config, true)",
    "is_public(transform_values, true)",
    "is_public(write_report, true)",
    "is_public(run_pipeline, true)",
    "writes_global(load_config)",
    "calls(write_report, print)",
]

RULES_PROGRAM = """
undocumented_public_function(Func) :-
    is_public(Func, true),
    has_docstring(Func, false).

has_side_effect(Func) :-
    calls(Func, print).

violates_no_globals(Func) :-
    writes_global(Func).

passes_docstring_policy :-
    \\+ undocumented_public_function(_).

passes_no_global_writes :-
    \\+ violates_no_globals(_).
""".strip()

ASSERTION_QUERIES = [
    ("passes_docstring_policy.", "Public functions are documented."),
    ("passes_no_global_writes.", "No function writes global state."),
    ("has_side_effect(Func).", "Some function has side effects."),
]


def parse_json_array(text: str) -> List[Dict[str, Any]]:
    raw = text.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("[")
        end = raw.rfind("]")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(raw[start : end + 1])


def load_source(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def extract_facts(llm: OllamaLLM, source: str) -> List[Dict[str, Any]]:
    system_prompt = (
        "Extract facts from the provided code excerpt. "
        "Output ONLY a JSON array of objects with keys 'predicate' and 'args'. "
        "Use the fact spec exactly as provided; do not add extra facts."
    )
    user_prompt = (
        "Code excerpt:\n"
        f"{source}\n\n"
        "Fact spec (return exactly these facts if supported by the code):\n"
        + "\n".join(f"- {line}" for line in FACT_SPEC)
    )
    response = llm.chat(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )
    return parse_json_array(response)


def run_assertions(session_id: str) -> None:
    print("\nInvariant checks:")
    for query_text, description in ASSERTION_QUERIES:
        result = query(session_id=session_id, query=query_text, max_solutions=3)
        if not result.get("success"):
            print(f"- {description} false [error: {result.get('error')}]")
            continue
        if result.get("count", 0) == 0:
            print(f"- {description} false")
            continue
        bindings = [sol.get("Bindings", {}) for sol in result.get("solutions", [])]
        if not bindings or all(not binding for binding in bindings):
            print(f"- {description} true")
        else:
            print(f"- {description} true {bindings}")


def main() -> None:
    parser = argparse.ArgumentParser(description="In-process edit verifier sample.")
    parser.add_argument("--ollama-model", default="gpt-oss:20b")
    parser.add_argument("--ollama-base-url", default="http://localhost:11434")
    parser.add_argument(
        "--input-file",
        default="examples/program_sample.py",
        help="Path to a source code file to analyze.",
    )
    args = parser.parse_args()

    llm = OllamaLLM(model=args.ollama_model, base_url=args.ollama_base_url, temperature=0)
    source = load_source(Path(args.input_file))
    facts = extract_facts(llm, source)

    session_id = create_session(metadata={"task": "edit verification"})
    try:
        result = assert_facts(session_id, facts)
        if not result["success"]:
            raise SystemExit(f"assert_facts failed: {result}")
        rules_result = assert_rules(session_id, [RULES_PROGRAM])
        if not rules_result["success"]:
            raise SystemExit(f"assert_rules failed: {rules_result}")
        print(f"Asserted {result['facts_added']} facts.")
        print(json.dumps(facts, indent=2))
        run_assertions(session_id)
    finally:
        destroy_session(session_id)


if __name__ == "__main__":
    main()

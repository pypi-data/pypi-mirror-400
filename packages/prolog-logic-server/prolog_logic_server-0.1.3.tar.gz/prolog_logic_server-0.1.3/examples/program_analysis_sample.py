"""
Program analysis sample using Ollama + Prolog rules.

Example:
  python examples/program_analysis_sample.py --ollama-model gpt-oss:20b \
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
    "module(program_sample)",
    "function(load_config)",
    "function(transform_values)",
    "function(write_report)",
    "function(run_pipeline)",
    "has_docstring(load_config, true)",
    "has_docstring(transform_values, true)",
    "has_docstring(write_report, true)",
    "has_docstring(run_pipeline, true)",
    "uses_global(load_config, config)",
    "calls(run_pipeline, load_config)",
    "calls(run_pipeline, transform_values)",
    "calls(run_pipeline, write_report)",
    "calls(write_report, print)",
    "has_side_effect(write_report)",
]

RULES_PROGRAM = """
undocumented_function(Func) :-
    function(Func),
    has_docstring(Func, false).

uses_global_state(Func) :-
    uses_global(Func, _).

has_side_effect(Func) :-
    calls(Func, print).

pipeline_has_side_effect :-
    calls(run_pipeline, Fn),
    has_side_effect(Fn).

module_pure :-
    module(program_sample),
    \\+ has_side_effect(_).
""".strip()


ASSERTION_QUERIES = [
    ("undocumented_function(Func).", "Every function has a docstring."),
    ("uses_global_state(Func).", "Some functions rely on global state."),
    ("pipeline_has_side_effect.", "The pipeline triggers side effects."),
    ("module_pure.", "The module is side-effect free."),
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
    print("\nProgram assertions:")
    for query_text, description in ASSERTION_QUERIES:
        result = query(
            session_id=session_id,
            query=query_text,
            max_solutions=3,
        )
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
    parser = argparse.ArgumentParser(description="Program analysis sample.")
    parser.add_argument("--ollama-model", default="gpt-oss:20b")
    parser.add_argument("--ollama-base-url", default="http://localhost:11434")
    parser.add_argument(
        "--input-file",
        default="examples/program_sample.py",
        help="Path to a source code file to analyze.",
    )
    args = parser.parse_args()

    llm = OllamaLLM(model=args.ollama_model, base_url=args.ollama_base_url, temperature=0)
    source_path = Path(args.input_file)
    source = load_source(source_path)
    facts = extract_facts(llm, source)

    session_id = create_session(metadata={"task": "program analysis"})
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

"""
End-to-end demo: simulate LLM edits and validate with logic rules.

Example:
  python examples/edit_guardrails_demo.py --input-file examples/program_sample.py
"""

import argparse
import ast
import json
from pathlib import Path
from typing import Any, Dict, List, Set

from logic_server.core.session import (
    assert_facts,
    assert_rules,
    create_session,
    destroy_session,
    query,
)
from logic_server.llm.clients import OllamaLLM


RULES_PROGRAM = """
undocumented_public_function(Func) :-
    function(Func),
    is_public(Func, true),
    has_docstring(Func, false).

violates_no_global_writes(Func) :-
    writes_global(Func).

has_side_effect(Func) :-
    calls(Func, print).

passes_docstring_policy :-
    \\+ undocumented_public_function(_).

passes_no_global_writes :-
    \\+ violates_no_global_writes(_).

passes_no_print :-
    \\+ has_side_effect(_).
""".strip()

ASSERTION_QUERIES = [
    ("passes_docstring_policy.", "All public functions have docstrings."),
    ("passes_no_global_writes.", "No function writes global state."),
    ("passes_no_print.", "No function uses print IO."),
    ("undocumented_public_function(Func).", "Undocumented public functions exist."),
    ("violates_no_global_writes(Func).", "Functions write global state."),
    ("has_side_effect(Func).", "Functions have IO side effects."),
]


def load_source(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def _module_globals(tree: ast.Module) -> Set[str]:
    globals_found: Set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    globals_found.add(target.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            globals_found.add(node.target.id)
    return globals_found


def _function_calls(func: ast.FunctionDef) -> Set[str]:
    calls: Set[str] = set()
    for node in ast.walk(func):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            calls.add(node.func.id)
    return calls


def _writes_global(func: ast.FunctionDef, globals_found: Set[str]) -> bool:
    for node in ast.walk(func):
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            targets: List[ast.AST] = []
            if isinstance(node, ast.Assign):
                targets = list(node.targets)
            elif isinstance(node, ast.AnnAssign):
                targets = [node.target]
            elif isinstance(node, ast.AugAssign):
                targets = [node.target]
            for target in targets:
                if isinstance(target, ast.Name) and target.id in globals_found:
                    return True
                if isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name):
                    if target.value.id in globals_found:
                        return True
    return False


def extract_facts_from_ast(source: str) -> List[Dict[str, Any]]:
    tree = ast.parse(source)
    globals_found = _module_globals(tree)
    facts: List[Dict[str, Any]] = []

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            func_name = node.name
            facts.append({"predicate": "function", "args": [func_name]})
            is_public = not func_name.startswith("_")
            facts.append({"predicate": "is_public", "args": [func_name, is_public]})
            has_doc = ast.get_docstring(node) is not None
            facts.append({"predicate": "has_docstring", "args": [func_name, has_doc]})
            if _writes_global(node, globals_found):
                facts.append({"predicate": "writes_global", "args": [func_name]})
            for call_name in sorted(_function_calls(node)):
                facts.append({"predicate": "calls", "args": [func_name, call_name]})
    return facts


FACT_SPEC = [
    "function(load_config)",
    "function(transform_values)",
    "function(write_report)",
    "function(run_pipeline)",
    "function(enable_fast_mode)",
    "has_docstring(load_config, true)",
    "has_docstring(transform_values, true)",
    "has_docstring(write_report, true)",
    "has_docstring(run_pipeline, true)",
    "has_docstring(enable_fast_mode, true)",
    "is_public(load_config, true)",
    "is_public(transform_values, true)",
    "is_public(write_report, true)",
    "is_public(run_pipeline, true)",
    "is_public(enable_fast_mode, true)",
    "writes_global(enable_fast_mode)",
    "calls(write_report, print)",
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


def extract_facts_with_llm(llm: OllamaLLM, source: str) -> List[Dict[str, Any]]:
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
    for query_text, description in ASSERTION_QUERIES:
        result = query(session_id=session_id, query=query_text, max_solutions=5)
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


def _insert_after(source: str, marker: str, insert_block: str) -> str:
    idx = source.find(marker)
    if idx == -1:
        raise ValueError(f"Marker not found: {marker}")
    insert_at = idx + len(marker)
    return source[:insert_at] + insert_block + source[insert_at:]


def make_bad_edit(source: str) -> str:
    insert_block = """

def enable_fast_mode() -> None:
    CONFIG["mode"] = "fast"
"""
    return _insert_after(source, 'def run_pipeline(values: list[int]) -> None:', insert_block)


def make_fixed_edit(source: str) -> str:
    insert_block = """

def enable_fast_mode(config: dict) -> dict:
    \"\"\"Return a copy of the config with fast mode enabled.\"\"\"
    updated = dict(config)
    updated["mode"] = "fast"
    return updated
"""
    return _insert_after(source, 'def run_pipeline(values: list[int]) -> None:', insert_block)


def run_version(label: str, source: str, use_llm: bool, llm: OllamaLLM | None) -> None:
    if use_llm:
        if llm is None:
            raise RuntimeError("LLM client required for --use-llm")
        facts = extract_facts_with_llm(llm, source)
    else:
        facts = extract_facts_from_ast(source)
    session_id = create_session(metadata={"task": f"edit_guardrails:{label}"})
    try:
        result = assert_facts(session_id, facts)
        if not result["success"]:
            raise SystemExit(f"assert_facts failed: {result}")
        rules_result = assert_rules(session_id, [RULES_PROGRAM])
        if not rules_result["success"]:
            raise SystemExit(f"assert_rules failed: {rules_result}")
        print(f"\n{label}")
        print(f"Asserted {result['facts_added']} facts.")
        run_assertions(session_id)
    finally:
        destroy_session(session_id)


def main() -> None:
    parser = argparse.ArgumentParser(description="Edit guardrails demo.")
    parser.add_argument("--use-llm", action="store_true", help="Extract facts via LLM.")
    parser.add_argument("--ollama-model", default="gpt-oss:20b")
    parser.add_argument("--ollama-base-url", default="http://localhost:11434")
    parser.add_argument(
        "--input-file",
        default="examples/program_sample.py",
        help="Path to a source code file to analyze.",
    )
    args = parser.parse_args()

    source = load_source(Path(args.input_file))
    llm = None
    if args.use_llm:
        llm = OllamaLLM(
            model=args.ollama_model,
            base_url=args.ollama_base_url,
            temperature=0,
        )

    run_version("Base version", source, args.use_llm, llm)
    run_version(
        "Bad edit (global write, missing docstring)",
        make_bad_edit(source),
        args.use_llm,
        llm,
    )
    run_version(
        "Fixed edit (no global write, documented)",
        make_fixed_edit(source),
        args.use_llm,
        llm,
    )


if __name__ == "__main__":
    main()

from __future__ import annotations

from typing import List, Dict, Any
import json
import os
import re
import shutil
import subprocess
import tempfile


_VAR_TOKEN = re.compile(r"\?[A-Za-z_][A-Za-z0-9_]*|\b[A-Z][A-Za-z0-9_]*\b")
_ATOM_PATTERN = re.compile(r"^[a-z][a-zA-Z0-9_]*$")


def _normalize_query(query: str) -> str:
    cleaned = query.strip()
    if cleaned.endswith("."):
        cleaned = cleaned[:-1].strip()
    cleaned = re.sub(r"\?([A-Za-z_][A-Za-z0-9_]*)", r"\1", cleaned)
    return cleaned


def _extract_variables(query: str) -> List[str]:
    vars_found: List[str] = []
    for token in _VAR_TOKEN.findall(query):
        name = token[1:] if token.startswith("?") else token
        if name == "_" or name.startswith("_"):
            continue
        if name not in vars_found:
            vars_found.append(name)
    return vars_found


def _escape_atom(text: str) -> str:
    return "'" + text.replace("'", "''") + "'"


def _format_atom(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if value is None:
        return "null"
    text = str(value)
    if _ATOM_PATTERN.match(text):
        return text
    return _escape_atom(text)


def _format_predicate(name: Any) -> str:
    text = str(name)
    if _ATOM_PATTERN.match(text):
        return text
    return _escape_atom(text)


def _facts_to_prolog(facts: List[Dict[str, Any]]) -> List[str]:
    lines: List[str] = []
    for fact in facts:
        predicate = _format_predicate(fact.get("predicate"))
        args = fact.get("args", [])
        if args:
            rendered_args = ",".join(_format_atom(arg) for arg in args)
            lines.append(f"{predicate}({rendered_args}).")
        else:
            lines.append(f"{predicate}.")
    return lines


def _build_program(
    facts: List[Dict[str, Any]],
    rules_program: str | None,
    query: str,
    max_solutions: int,
) -> str:
    variables = _extract_variables(query)
    dict_entries = ", ".join(f"'{name}':{name}" for name in variables)
    dict_expr = "_{" + dict_entries + "}"
    prolog_lines = [
        ":- use_module(library(http/json)).",
        ":- use_module(library(solution_sequences)).",
        "",
    ]
    prolog_lines.extend(_facts_to_prolog(facts))
    if rules_program:
        prolog_lines.append("")
        # Ensure each rule ends with a period
        for line in rules_program.strip().split('\n'):
            line = line.strip()
            if line and not line.endswith('.'):
                line += '.'
            if line:
                prolog_lines.append(line)
        prolog_lines.append("")
    query_goal = _normalize_query(query)
    prolog_lines.extend(
        [
            "run_query :-",
            f"  ( call_nth(({query_goal}), N),",
            f"    N =< {max_solutions},",
            f"    Dict = {dict_expr},",
            "    json_write_dict(current_output, Dict),",
            "    nl,",
            f"    ( N =:= {max_solutions} -> ! ; fail )",
            "  ; true ).",
        ]
    )
    return "\n".join(prolog_lines) + "\n"


def execute_query(
    facts: List[Dict[str, Any]],
    base_knowledge: List[str] | None = None,
    rules_program: str | None = None,
    query: str = "",
    max_solutions: int = 5,
) -> Dict[str, Any]:
    """
    Execute a logic query over facts and rules.

    Args:
        facts: List of fact dictionaries with 'predicate' and 'args'
        base_knowledge: Currently ignored (reserved for future use)
        rules_program: Optional logic rules as string
        query: Query to execute
        max_solutions: Maximum number of solutions to return

    Returns:
        Dict with 'success', 'solutions', 'count', and optional 'error'
    """
    cleaned = query.strip()
    if not cleaned:
        return {
            "success": False,
            "error": "Query required",
            "query": query,
        }

    swipl = shutil.which("swipl")
    if not swipl:
        return {
            "success": False,
            "error": "Logic solver runtime not found on PATH. Install SWI-Prolog (swipl).",
            "query": query,
        }

    # Validate and clamp max_solutions
    try:
        max_solutions = max(1, min(1000, int(max_solutions)))
    except (ValueError, TypeError):
        max_solutions = 5  # Default if conversion fails
    program = _build_program(facts, rules_program, cleaned, max_solutions)

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".pl", delete=False) as temp_file:
            temp_file.write(program)
            temp_path = temp_file.name

        result = subprocess.run(
            [swipl, "-q", "-s", temp_path, "-g", "run_query", "-t", "halt"],
            check=False,
            capture_output=True,
            text=True,
        )
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)

    if result.returncode != 0:
        return {
            "success": False,
            "error": result.stderr.strip() or "SWI-Prolog execution failed",
            "query": query,
        }

    solutions: List[Dict[str, Any]] = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            bindings = json.loads(line)
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": f"Failed to parse SWI-Prolog output: {line}",
                "query": query,
            }
        solutions.append({"Bindings": bindings})

    return {
        "success": True,
        "solutions": solutions,
        "query": query,
        "count": len(solutions),
    }


# Backward compatibility alias
prolog_query = execute_query

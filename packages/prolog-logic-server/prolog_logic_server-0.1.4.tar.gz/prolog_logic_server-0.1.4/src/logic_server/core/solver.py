from __future__ import annotations

from typing import List, Dict, Any
import difflib
import json
import time
import os
import re
import shutil
import subprocess
import tempfile

from logic_server.core import schema


_VAR_TOKEN = re.compile(r"\?[A-Za-z_][A-Za-z0-9_]*|\b[A-Z][A-Za-z0-9_]*\b")
_ATOM_PATTERN = re.compile(r"^[a-z][a-zA-Z0-9_]*$")
_VAR_PATTERN = re.compile(r"^[A-Z_][A-Za-z0-9_]*$")
_QUOTED_PATTERN = re.compile(r"'(?:''|[^'])*'|\"(?:\\\\.|[^\"])*\"")


def _normalize_query(query: str) -> str:
    cleaned = query.strip()
    if cleaned.endswith("."):
        cleaned = cleaned[:-1].strip()
    cleaned = re.sub(r"\?([A-Za-z_][A-Za-z0-9_]*)", r"\1", cleaned)
    return cleaned


def _extract_variables(query: str) -> List[str]:
    vars_found: List[str] = []
    scrubbed = _QUOTED_PATTERN.sub(" ", query)
    for token in _VAR_TOKEN.findall(scrubbed):
        name = token[1:] if token.startswith("?") else token
        if name == "_" or name.startswith("_"):
            continue
        if name not in vars_found:
            vars_found.append(name)
    return vars_found


def _extract_query_predicate(query: str) -> str | None:
    cleaned = query.strip()
    if not cleaned:
        return None
    match = re.match(r"^([a-z][A-Za-z0-9_]*)\b", cleaned)
    return match.group(1) if match else None


def _collect_predicates(facts: List[Dict[str, Any]], rules_program: Any) -> List[str]:
    predicates: List[str] = []
    for fact in facts:
        pred = fact.get("predicate")
        if isinstance(pred, str) and pred not in predicates:
            predicates.append(pred)

    if not rules_program:
        return predicates

    if isinstance(rules_program, str):
        lines = rules_program.splitlines()
        for line in lines:
            match = re.match(r"^\s*([a-z][A-Za-z0-9_]*)\s*\(", line)
            if match:
                name = match.group(1)
                if name not in predicates:
                    predicates.append(name)
    elif isinstance(rules_program, list):
        for rule in rules_program:
            if isinstance(rule, dict):
                head = rule.get("head", {})
                name = head.get("predicate")
                if isinstance(name, str) and name not in predicates:
                    predicates.append(name)
            elif isinstance(rule, str):
                match = re.match(r"^\s*([a-z][A-Za-z0-9_]*)\s*\(", rule)
                if match:
                    name = match.group(1)
                    if name not in predicates:
                        predicates.append(name)
    elif isinstance(rules_program, dict):
        head = rules_program.get("head", {})
        name = head.get("predicate")
        if isinstance(name, str) and name not in predicates:
            predicates.append(name)
    return predicates


def list_predicates(facts: List[Dict[str, Any]], rules_program: Any = None) -> List[str]:
    return sorted(_collect_predicates(facts, rules_program))


def extract_query_predicate(query: Any) -> str | None:
    if isinstance(query, str):
        return _extract_query_predicate(query)
    if isinstance(query, dict):
        name = query.get("predicate")
        return name if isinstance(name, str) else None
    return None


def _build_no_solution_hints(query: Any, facts: List[Dict[str, Any]], rules_program: Any) -> List[str]:
    hints = [
        "Looking for relationships? Try queries like owns(Person, Pet).",
        "Need aggregation? Consider findall/3, bagof/3, or setof/3 in rules.",
        "For CSPs, try all_different/1 or exactly_one/2 in constraints.",
        "If you need a capitalized atom, wrap it as {\"atom\": \"Alice\"}.",
    ]
    if isinstance(query, str):
        predicate = _extract_query_predicate(query)
        if predicate:
            available = _collect_predicates(facts, rules_program)
            if predicate not in available and available:
                close = difflib.get_close_matches(predicate, available, n=3)
                if close:
                    hints.insert(0, f"Predicate '{predicate}' not found. Did you mean: {', '.join(close)}?")
                else:
                    hints.insert(0, f"Predicate '{predicate}' not found. Available: {', '.join(available[:8])}.")
    return hints


def _build_query_stats(facts: List[Dict[str, Any]], rules_program: Any, max_solutions: int) -> Dict[str, Any]:
    rule_count = 0
    if isinstance(rules_program, list):
        rule_count = len(rules_program)
    elif isinstance(rules_program, str):
        rule_count = len([line for line in rules_program.splitlines() if line.strip()])
    elif isinstance(rules_program, dict):
        rule_count = 1
    warnings: List[str] = []
    if max_solutions >= 500:
        warnings.append("High max_solutions may be slow; consider a smaller limit or pagination.")
    if len(facts) >= 5000:
        warnings.append("Large fact base; queries may be slow. Consider indexing predicates.")
    return {
        "fact_count": len(facts),
        "rule_count": rule_count,
        "max_solutions": max_solutions,
        "warnings": warnings,
    }


def _escape_atom(text: str) -> str:
    return "'" + text.replace("'", "''") + "'"

def _format_atom_text(text: str) -> str:
    if _ATOM_PATTERN.match(text):
        return text
    return _escape_atom(text)

def _format_atom(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if value is None:
        return "null"
    text = str(value)
    return _format_atom_text(text)

def _format_string(value: str) -> str:
    return _escape_string(value)

def _format_term(value: Any) -> str:
    if isinstance(value, str):
        text = value.strip()
        if text == "_" or text.startswith("_"):
            return text
        if text.startswith("?"):
            name = text[1:]
            if not _VAR_PATTERN.match(name):
                raise ValueError(f"Invalid variable name: {name}")
            return name
        if _VAR_PATTERN.match(text):
            return text
        return _format_atom_text(text)
    if isinstance(value, list):
        return "[" + ", ".join(_format_term(item) for item in value) + "]"
    return _format_atom(value)


def _format_predicate(name: Any) -> str:
    text = str(name)
    return _format_atom_text(text)

def _render_predicate_call(predicate: Any, args: List[Any]) -> str:
    functor = _format_predicate(predicate)
    if not args:
        return functor
    rendered_args = ",".join(_format_term(arg) for arg in args)
    return f"{functor}({rendered_args})"



def _render_rules_program(rules_program: Any) -> str | None:
    if not rules_program:
        return None
    if isinstance(rules_program, str):
        lines: List[str] = []
        for line in rules_program.strip().split("\n"):
            line = line.strip()
            if line and not line.endswith("."):
                line += "."
            if line:
                lines.append(line)
        return "\n".join(lines)
    if isinstance(rules_program, list):
        rules: List[str] = []
        for rule in rules_program:
            if isinstance(rule, str):
                line = rule.strip()
                if line and not line.endswith("."):
                    line += "."
                if line:
                    rules.append(line)
            else:
                raise ValueError(f"Invalid rule format: {rule}")
        return "\n".join(rules)
    raise ValueError(f"Rules must be a string or list of strings, not {type(rules_program).__name__}")


def execute_query(
    facts: List[str],
    rules_program: Any = None,
    query: Any = "",
    max_solutions: int = 5,
) -> Dict[str, Any]:
    """
    Execute a logic query over Prolog fact strings and rules.

    Args:
        facts: List of Prolog fact strings like "person(alice)."
        rules_program: Optional logic rules as string or list
        query: Query to execute
        max_solutions: Maximum number of solutions to return

    Returns:
        Dict with 'success', 'solutions', 'count', and optional 'error'
    """
    if query is None:
        return {
            "success": False,
            "error": "Query required",
            "query": query,
        }

    start_time = time.monotonic()
    if not isinstance(query, str):
        return {
            "success": False,
            "error": "Query must be a Prolog string",
            "query": query,
        }
    cleaned = query.strip()
    if not cleaned:
        return {
            "success": False,
            "error": "Query required",
            "query": query,
        }
    query_goal = _normalize_query(cleaned)
    variables = _extract_variables(query_goal)

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

    # Build Prolog program directly from string facts
    dict_entries = ", ".join(f"'{name}':{name}" for name in variables)
    dict_expr = "_{" + dict_entries + "}"
    prolog_lines = [
        ":- use_module(library(http/json)).",
        ":- use_module(library(solution_sequences)).",
        ":- use_module(library(clpfd)).",
        "",
        "all_different(List) :- all_distinct(List).",
        "exactly_one(Item, List) :- include(=(Item), List, Matches), length(Matches, 1).",
        "json_value(Term, Json) :-",
        "  ( var(Term) -> Json = null",
        "  ; is_dict(Term) -> Json = Term",
        "  ; is_list(Term) -> maplist(json_value, Term, Json)",
        "  ; atomic(Term) -> Json = Term",
        "  ; term_to_atom(Term, Json)",
        "  ).",
        "json_pair(Key-Value, Key-JsonValue) :- json_value(Value, JsonValue).",
        "json_bindings(Dict, JsonDict) :-",
        "  dict_pairs(Dict, Tag, Pairs),",
        "  maplist(json_pair, Pairs, JsonPairs),",
        "  dict_pairs(JsonDict, Tag, JsonPairs).",
        "",
    ]

    # Add facts directly (they're already in Prolog format)
    for fact in facts:
        fact = fact.strip()
        if not fact.endswith("."):
            fact += "."
        prolog_lines.append(fact)

    # Add rules
    rules_text = _render_rules_program(rules_program)
    if rules_text:
        prolog_lines.append("")
        prolog_lines.extend(rules_text.split("\n"))
        prolog_lines.append("")

    prolog_lines.extend(
        [
            "run_query :-",
            f"  ( call_nth(({query_goal}), N),",
            f"    N =< {max_solutions},",
            f"    Dict = {dict_expr},",
            "    json_bindings(Dict, JsonDict),",
            "    json_write_dict(current_output, JsonDict),",
            "    nl,",
            f"    ( N =:= {max_solutions} -> ! ; fail )",
            "  ; true ).",
        ]
    )
    program = "\n".join(prolog_lines) + "\n"

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

    duration_ms = int((time.monotonic() - start_time) * 1000)

    if not solutions:
        return {
            "success": True,
            "solutions": [],
            "query": query,
            "count": 0,
            "duration_ms": duration_ms,
        }

    return {
        "success": True,
        "solutions": solutions,
        "query": query,
        "count": len(solutions),
        "duration_ms": duration_ms,
    }

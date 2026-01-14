from __future__ import annotations

from typing import Any, List

from jsonschema import Draft202012Validator


_SCHEMA_BASE = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$defs": {
        "term": {
            "oneOf": [
                {"type": "string"},
                {"type": "number"},
                {"type": "boolean"},
                {
                    "type": "array",
                    "items": {"$ref": "#/$defs/term"},
                },
                {
                    "type": "object",
                    "properties": {
                        "atom": {"type": "string"},
                        "quoted": {"type": "boolean"},
                    },
                    "required": ["atom"],
                    "additionalProperties": False,
                },
                {
                    "type": "object",
                    "properties": {"string": {"type": "string"}},
                    "required": ["string"],
                    "additionalProperties": False,
                },
                {
                    "type": "object",
                    "properties": {"var": {"type": "string"}},
                    "required": ["var"],
                    "additionalProperties": False,
                },
                {
                    "type": "object",
                    "properties": {"number": {"type": "number"}},
                    "required": ["number"],
                    "additionalProperties": False,
                },
                {
                    "type": "object",
                    "properties": {"bool": {"type": "boolean"}},
                    "required": ["bool"],
                    "additionalProperties": False,
                },
                {
                    "type": "object",
                    "properties": {
                        "list": {
                            "type": "array",
                            "items": {"$ref": "#/$defs/term"},
                        }
                    },
                    "required": ["list"],
                    "additionalProperties": False,
                },
            ]
        },
        "predicate_call": {
            "type": "object",
            "properties": {
                "predicate": {"type": "string"},
                "args": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/term"},
                },
            },
            "required": ["predicate", "args"],
            "additionalProperties": False,
        },
        "goal": {
            "oneOf": [
                {"$ref": "#/$defs/predicate_call"},
                {
                    "type": "object",
                    "properties": {
                        "op": {"type": "string"},
                        "left": {"$ref": "#/$defs/term"},
                        "right": {"$ref": "#/$defs/term"},
                    },
                    "required": ["op", "left", "right"],
                    "additionalProperties": False,
                },
            ]
        },
        "rule": {
            "type": "object",
            "properties": {
                "head": {"$ref": "#/$defs/predicate_call"},
                "body": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/goal"},
                },
            },
            "required": ["head"],
            "additionalProperties": False,
        },
    },
}


_RULES_SCHEMA = {
    **_SCHEMA_BASE,
    "oneOf": [
        {"type": "string"},
        {
            "type": "array",
            "items": {"type": "string"},
        },
    ],
}

_QUERY_SCHEMA = {
    **_SCHEMA_BASE,
    "type": "string",
}


def _format_error(error, label: str) -> str:
    path = label
    for part in error.absolute_path:
        if isinstance(part, int):
            path += f"[{part}]"
        else:
            path += f".{part}"
    return f"{path}: {error.message}"


def _validate(schema: dict, payload: Any, label: str) -> List[str]:
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda err: err.path)
    return [_format_error(err, label) for err in errors]


def validate_facts(facts: Any) -> List[str]:
    """Validate facts (deprecated - facts are now Prolog strings)."""
    # No validation needed for Prolog string facts
    return []


def validate_rules(rules_program: Any) -> List[str]:
    if rules_program is None:
        return []
    return _validate(_RULES_SCHEMA, rules_program, "rules_program")


def validate_query(query: Any) -> List[str]:
    return _validate(_QUERY_SCHEMA, query, "query")

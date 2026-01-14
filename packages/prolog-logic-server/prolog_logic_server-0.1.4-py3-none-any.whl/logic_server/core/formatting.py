from __future__ import annotations

import csv
import io
from typing import Any, Dict, List, Optional


def format_solutions(
    solutions: List[Dict[str, Any]],
    output_format: str,
    group_by: Optional[str] = None,
    return_csv: bool = False,
) -> Dict[str, Any]:
    if output_format == "raw":
        return {}

    bindings_list = [solution.get("Bindings", {}) for solution in solutions]

    if output_format == "table":
        columns: List[str] = []
        for bindings in bindings_list:
            for key in bindings.keys():
                if key not in columns:
                    columns.append(key)
        rows = [[bindings.get(col) for col in columns] for bindings in bindings_list]
        formatted: Dict[str, Any] = {
            "format": "table",
            "columns": columns,
            "rows": rows,
        }
        if return_csv:
            buffer = io.StringIO()
            writer = csv.writer(buffer)
            writer.writerow(columns)
            writer.writerows(rows)
            formatted["csv"] = buffer.getvalue()
        return formatted

    if output_format == "grouped":
        if not group_by:
            raise ValueError("group_by is required when format is 'grouped'")
        groups: Dict[str, List[Dict[str, Any]]] = {}
        for bindings in bindings_list:
            key_value = bindings.get(group_by)
            group_key = str(key_value)
            entry = {key: value for key, value in bindings.items() if key != group_by}
            groups.setdefault(group_key, []).append(entry)
        return {
            "format": "grouped",
            "group_by": group_by,
            "groups": groups,
        }

    raise ValueError(f"Unknown format: {output_format}")

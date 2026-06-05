from __future__ import annotations

import re
from collections.abc import Mapping
from typing import cast


def escape_latex(text: str) -> str:
    if not text:
        return text

    escaped: list[str] = []
    for char in text:
        if char == "\\":
            escaped.append("\\textbackslash{}")
        elif char == "&":
            escaped.append("\\&")
        elif char == "%":
            escaped.append("\\%")
        elif char == "$":
            escaped.append("\\$")
        elif char == "#":
            escaped.append("\\#")
        elif char == "_":
            escaped.append("\\_")
        elif char == "{":
            escaped.append("\\{")
        elif char == "}":
            escaped.append("\\}")
        elif char == "~":
            escaped.append("\\textasciitilde{}")
        elif char == "^":
            escaped.append("\\textasciicircum{}")
        else:
            escaped.append(char)
    return "".join(escaped)


def escape_field(entry: object, field_name: str) -> str:
    formatted = getattr(entry, "formatted", None)
    if isinstance(formatted, Mapping):
        field_override = formatted.get(field_name)
        if isinstance(field_override, Mapping):
            override_mapping = cast(Mapping[str, object], field_override)
            latex_val = override_mapping.get("latex")
            if isinstance(latex_val, str):
                return latex_val

    value = getattr(entry, field_name, "") or ""
    return escape_latex(str(value))


def is_raw_latex(text: str) -> bool:
    return bool(re.search(r"\\[a-zA-Z]", text))

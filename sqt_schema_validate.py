"""JSON Schema validation for SQT holidays and themes data files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    import jsonschema
    from jsonschema import Draft7Validator
except ImportError:  # pragma: no cover
    jsonschema = None  # type: ignore
    Draft7Validator = None  # type: ignore

SchemaSource = Union[str, Path, Dict[str, Any]]


class SchemaValidationError(Exception):
    """Raised when holidays or themes JSON fails schema validation."""

    def __init__(self, label: str, errors: List[str]):
        self.label = label
        self.errors = errors
        super().__init__(f"{label} schema validation failed:\n  - " + "\n  - ".join(errors))


def _load_schema(source: SchemaSource) -> Dict[str, Any]:
    if isinstance(source, dict):
        return source
    path = Path(source)
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _format_errors(validator: Draft7Validator, instance: Any) -> List[str]:
    messages: List[str] = []
    for error in sorted(validator.iter_errors(instance), key=lambda e: list(e.path)):
        path = ".".join(str(p) for p in error.path) or "(root)"
        messages.append(f"{path}: {error.message}")
    return messages


def validate_json(
    data: Dict[str, Any],
    schema: SchemaSource,
    label: str = "document",
) -> None:
    if Draft7Validator is None:
        raise RuntimeError(
            "jsonschema is required for validation. Install: pip install jsonschema"
        )
    schema_obj = _load_schema(schema)
    validator = Draft7Validator(schema_obj)
    errors = _format_errors(validator, data)
    if errors:
        raise SchemaValidationError(label, errors)


def validate_holidays_file(
    data_path: Union[str, Path],
    schema_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    path = Path(data_path)
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    schema = schema_path or path.with_suffix(".schema.json")
    if not Path(schema).exists():
        schema = path.parent / "sqt-holidays.schema.json"
    validate_json(data, schema, label=f"holidays ({path.name})")
    return data


def validate_themes_file(
    data_path: Union[str, Path],
    schema_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    path = Path(data_path)
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    schema = schema_path or path.with_suffix(".schema.json")
    if not Path(schema).exists():
        schema = path.parent / "sqt-themes.schema.json"
    validate_json(data, schema, label=f"themes ({path.name})")
    return data
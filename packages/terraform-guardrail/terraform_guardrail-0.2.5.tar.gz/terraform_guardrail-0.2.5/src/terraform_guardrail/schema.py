from __future__ import annotations

import json
import subprocess
from collections.abc import Iterable
from pathlib import Path
from typing import Any


class SchemaError(RuntimeError):
    pass


def load_provider_schema(workdir: Path) -> dict[str, Any] | None:
    """Return Terraform provider schema JSON if terraform is available."""
    try:
        result = subprocess.run(
            ["terraform", "providers", "schema", "-json"],
            cwd=str(workdir),
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return None
    except subprocess.CalledProcessError as exc:
        raise SchemaError(exc.stderr.strip() or "terraform schema command failed") from exc

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise SchemaError("Invalid schema JSON output") from exc


def iter_resource_blocks(hcl_data: dict[str, Any]) -> Iterable[tuple[str, dict[str, Any]]]:
    for block in hcl_data.get("resource", []) or []:
        for resource_type, instances in block.items():
            for _, attributes in instances.items():
                if isinstance(attributes, dict):
                    yield resource_type, attributes


def allowed_keys(schema: dict[str, Any], resource_type: str) -> set[str] | None:
    provider_schemas = schema.get("provider_schemas", {})
    for provider_schema in provider_schemas.values():
        resource_schemas = provider_schema.get("resource_schemas", {})
        resource_schema = resource_schemas.get(resource_type)
        if not resource_schema:
            continue
        block = resource_schema.get("block", {})
        attributes = set(block.get("attributes", {}).keys())
        block_types = set(block.get("block_types", {}).keys())
        return attributes | block_types
    return None

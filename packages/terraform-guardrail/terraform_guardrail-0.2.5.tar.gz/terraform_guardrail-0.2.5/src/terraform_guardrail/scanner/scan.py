from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

import hcl2

from terraform_guardrail.scanner.models import Finding, ScanReport, ScanSummary
from terraform_guardrail.scanner.rules import RULES, SENSITIVE_ASSIGN_RE, SENSITIVE_NAME_RE
from terraform_guardrail.schema import (
    SchemaError,
    allowed_keys,
    iter_resource_blocks,
    load_provider_schema,
)

TERRAFORM_EXTS = {".tf", ".tfvars", ".hcl"}


def scan_path(
    path: Path | str,
    state_path: Path | str | None = None,
    use_schema: bool = False,
) -> ScanReport:
    path = Path(path)
    state_path = Path(state_path) if state_path else None
    if not path.exists():
        raise FileNotFoundError(f"Path not found: {path}")
    schema = None
    if use_schema:
        workdir = path if path.is_dir() else path.parent
        try:
            schema = load_provider_schema(workdir)
        except SchemaError as exc:
            raise RuntimeError(f"Schema load failed: {exc}") from exc
    report = ScanReport.empty(path)
    findings: list[Finding] = []
    scanned_files = 0

    paths = _expand_paths(path)
    for file_path in paths:
        if file_path.suffix not in TERRAFORM_EXTS:
            continue
        scanned_files += 1
        findings.extend(_scan_hcl_file(file_path, schema))

    if state_path:
        if not state_path.exists():
            raise FileNotFoundError(f"State file not found: {state_path}")
        findings.extend(_scan_state_file(state_path))

    report.findings = findings
    report.summary = _build_summary(scanned_files, findings)
    return report


def _expand_paths(path: Path) -> Iterable[Path]:
    if path.is_dir():
        return path.rglob("*")
    return [path]


def _scan_hcl_file(path: Path, schema: dict | None) -> list[Finding]:
    findings: list[Finding] = []
    content = path.read_text(encoding="utf-8")

    for match in SENSITIVE_ASSIGN_RE.finditer(content):
        findings.append(
            Finding(
                rule_id="TG002",
                severity="high",
                message=RULES["TG002"],
                path=str(path),
                detail={
                    "key": match.group(1),
                    "recommendation": "Move secrets to variables or secret managers.",
                },
            )
        )

    try:
        with path.open("r", encoding="utf-8") as handle:
            data = hcl2.load(handle)
    except Exception as exc:  # noqa: BLE001
        findings.append(
            Finding(
                rule_id="TG004",
                severity="low",
                message=f"{RULES['TG004']}: {exc}",
                path=str(path),
            )
        )
        return findings

    variables = data.get("variable", [])
    for block in variables:
        for name, attrs in block.items():
            if not isinstance(attrs, dict):
                continue
            if attrs.get("sensitive") is True and attrs.get("ephemeral") is not True:
                findings.append(
                    Finding(
                        rule_id="TG001",
                        severity="medium",
                        message=f"{RULES['TG001']}: {name}",
                        path=str(path),
                        detail={"recommendation": "Add ephemeral = true to this variable."},
                    )
                )

    if path.suffix == ".tfvars":
        for key in data.keys():
            if SENSITIVE_NAME_RE.search(key):
                findings.append(
                    Finding(
                        rule_id="TG002",
                        severity="high",
                        message=f"{RULES['TG002']}: {key}",
                        path=str(path),
                        detail={"recommendation": "Avoid hardcoding secrets in tfvars."},
                    )
                )

    if schema:
        findings.extend(_schema_findings(data, schema, path))

    return findings


def _scan_state_file(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        findings.append(
            Finding(
                rule_id="TG003",
                severity="low",
                message=f"Invalid state JSON: {exc}",
                path=str(path),
            )
        )
        return findings

    for resource in data.get("resources", []):
        for instance in resource.get("instances", []) or []:
            attrs = instance.get("attributes", {}) or {}
            for key, value in attrs.items():
                if value is None:
                    continue
                if SENSITIVE_NAME_RE.search(key):
                    findings.append(
                        Finding(
                            rule_id="TG003",
                            severity="high",
                            message=f"{RULES['TG003']}: {key}",
                            path=str(path),
                            detail={
                                "resource": resource.get("name"),
                                "recommendation": (
                                    "Use ephemeral or write-only values to keep secrets out of "
                                    "state."
                                ),
                            },
                        )
                    )

    return findings


def _schema_findings(hcl_data: dict, schema: dict, path: Path) -> list[Finding]:
    findings: list[Finding] = []
    for resource_type, attributes in iter_resource_blocks(hcl_data):
        allowed = allowed_keys(schema, resource_type)
        if not allowed:
            continue
        for key in attributes.keys():
            if key in allowed:
                continue
            findings.append(
                Finding(
                    rule_id="TG005",
                    severity="medium",
                    message=f"{RULES['TG005']}: {resource_type}.{key}",
                    path=str(path),
                    detail={
                        "recommendation": "Verify the attribute name against provider schema.",
                    },
                )
            )
    return findings


def _build_summary(scanned_files: int, findings: list[Finding]) -> ScanSummary:
    summary = ScanSummary(scanned_files=scanned_files, findings=len(findings))
    for finding in findings:
        if finding.severity == "high":
            summary.high += 1
        elif finding.severity == "medium":
            summary.medium += 1
        else:
            summary.low += 1
    return summary

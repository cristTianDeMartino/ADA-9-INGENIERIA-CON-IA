#!/usr/bin/env python3
"""Deterministic contract and security verification for ADA-09 Agentic Code Review."""
from __future__ import annotations
import json
from pathlib import Path
import sys

REQUIRED_FILES = [
    "AGENTS.md",
    "README.md",
    "REQUIREMENTS.md",
    "SPEC.md",
    "ARCHITECTURE.md",
    "TASKS.md",
    "CHANGE_REQUEST.md",
    "docs/REPO_MAP.md",
    "scripts/verify_repo.sh",
    ".github/workflows/verify.yml",
]

FORBIDDEN_PATTERNS = [
    ".env",
    ".pem",
    ".key",
    "id_rsa",
    "credentials.json",
]


def check_required_files() -> list[str]:
    errors = []
    for rel_path in REQUIRED_FILES:
        path = Path(rel_path)
        if not path.exists():
            errors.append(f"Missing required file: {rel_path}")
    return errors


def check_directories() -> list[str]:
    errors = []
    for d in ["results", "src", "tests", "docs", "scripts"]:
        if not Path(d).is_dir():
            errors.append(f"Missing required directory: {d}")
    return errors


def check_spec_references() -> list[str]:
    spec_path = Path("SPEC.md")
    if not spec_path.exists():
        return []
    content = spec_path.read_text(encoding="utf-8")
    errors = []
    if "FR-" not in content:
        errors.append("SPEC.md does not reference any functional requirements (FR-*)")
    if "AC-" not in content:
        errors.append("SPEC.md does not reference any acceptance criteria (AC-*)")
    return errors


def check_change_request_contract() -> list[str]:
    cr_path = Path("CHANGE_REQUEST.md")
    if not cr_path.exists():
        return []
    content = cr_path.read_text(encoding="utf-8")
    errors = []
    for required_token in ["Change ID:", "## Goal", "## Requirements Covered", "FR-", "AC-", "Approved to implement: YES"]:
        if required_token not in content:
            errors.append(f"CHANGE_REQUEST.md is missing required element: '{required_token}'")
    return errors


def check_agents_contract() -> list[str]:
    agents_path = Path("AGENTS.md")
    if not agents_path.exists():
        return []
    content = agents_path.read_text(encoding="utf-8")
    errors = []
    required_sections = [
        "Read First",
        "Sources of Truth",
        "Repository Map",
        "Standard Commands",
        "Change Rules",
        "Stop Conditions",
        "Definition of Done",
    ]
    for section in required_sections:
        if section not in content:
            errors.append(f"AGENTS.md is missing required section: '{section}'")
    return errors


def check_forbidden_files() -> list[str]:
    errors = []
    for pattern in FORBIDDEN_PATTERNS:
        for p in Path(".").glob(f"**/{pattern}"):
            if not any(part.startswith(".git") for part in p.parts):
                errors.append(f"Found forbidden sensitive file: {p}")
    return errors


def check_protected_fixtures() -> list[str]:
    errors = []
    cust_data = Path("data/customers.json")
    if not cust_data.exists():
        errors.append("Protected dataset missing: data/customers.json")
    else:
        try:
            parsed = json.loads(cust_data.read_text(encoding="utf-8"))
            if not isinstance(parsed, list) or len(parsed) == 0:
                errors.append("data/customers.json must be a non-empty list of records")
        except json.JSONDecodeError as exc:
            errors.append(f"data/customers.json is invalid JSON: {exc}")
    return errors


def main() -> int:
    contract_errors = []
    contract_errors.extend(check_required_files())
    contract_errors.extend(check_directories())
    contract_errors.extend(check_spec_references())
    contract_errors.extend(check_change_request_contract())
    contract_errors.extend(check_agents_contract())
    contract_errors.extend(check_protected_fixtures())

    security_errors = check_forbidden_files()

    if contract_errors:
        print("Repository Contract: FAIL")
        for err in contract_errors:
            print(f"  - {err}")
    else:
        print("Repository Contract: PASS")

    if security_errors:
        print("Security Check: FAIL")
        for err in security_errors:
            print(f"  - {err}")
    else:
        print("Security Check: PASS")

    if contract_errors or security_errors:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env bash
set -euo pipefail

echo "[1/4] Running tests"
pytest -q
echo "Tests: PASS"

echo "[2/4] Checking syntax and compilation"
python3 -m compileall -q src tests
echo "Lint: PASS"

echo "[3/4] Checking repository contract and security"
python3 scripts/check_repo_contract.py

echo ""
echo "VERIFY_REPO: PASS"

# AGENTS.md

## Read First
1. `REQUIREMENTS.md`
2. `SPEC.md`
3. `ARCHITECTURE.md`
4. `TASKS.md`
5. `CHANGE_REQUEST.md`
6. `docs/REPO_MAP.md`

## Sources of Truth
- System requirements live in `REQUIREMENTS.md`.
- Verifiable behavior specifications live in `SPEC.md`.
- Architectural design boundaries live in `ARCHITECTURE.md`.
- Bounded change authorization lives in `CHANGE_REQUEST.md`.
- Never modify requirements or specs to make a failing test pass.

## Repository Map
- `src/`: Application source code and CLI entrypoints.
- `tests/`: Automated unit and integration test suites.
- `docs/`: Architecture documentation and repository map.
- `scripts/`: Deterministic checks and verification runners.
- `results/`: Evidence logs, review contracts, review reports, and PR evidence.

## Standard Commands
- Install: `pip install -r requirements.txt`
- Run: `python3 -m src.customer_search.cli "query"`
- Test: `pytest -q`
- Lint: `python3 -m compileall -q src tests`
- Verify: `./scripts/verify_repo.sh`

## Change Rules
- Scope changes strictly to the approved `CHANGE_REQUEST.md`.
- Respect architectural boundaries (`CLI -> Service -> Validator / Repository -> Models`).
- Maintain existing tests; never weaken assertions.
- Do not add new dependencies or invent undocumented APIs without explicit human approval.
- Do not edit files listed in `docs/REPO_MAP.md` under protected paths (`data/customers.json`).

## Role Separation & Review Rules
- **Coder Agent**: Plans and implements only the approved change in `CHANGE_REQUEST.md`, runs verification, and produces `results/coder-report.md`. Cannot approve its own change or close review findings.
- **Verification Gate**: Runs deterministic checks (`./scripts/verify_repo.sh`: tests, lint, repository contract, security check) before independent review.
- **Reviewer Agent**: Operates in an independent read-only session. Inspects diff, requirements, architecture, APIs, and tests to produce evidence-backed findings (`MUST FIX`, `SHOULD FIX`, `OPTIONAL`) in `results/review-report.md` and `results/re-review-report.md`.
- **Human Reviewer**: Accepts, modifies, rejects, or defers findings in `results/human-review-decisions.md` and makes the final merge readiness decision.

## Stop Conditions
Stop and ask for human input when:
- Requirements or specifications conflict.
- A destructive file modification or deletion is requested.
- An architectural layer boundary must change.
- A required test dependency or external service is unavailable.

## Definition of Done
A change is done only when:
- All items in `CHANGE_REQUEST.md` are implemented.
- New unit and integration tests cover the added behavior and edge cases.
- `./scripts/verify_repo.sh` exits with code 0 (`VERIFY_REPO: PASS`).
- Independent review, human review decisions, fix cycle (if needed), re-review, and `results/PR_EVIDENCE.md` are complete with zero unresolved accepted `MUST FIX` findings.

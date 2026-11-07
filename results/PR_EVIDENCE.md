# PR Evidence

## Change
Change ID: `CR-02`
PR / Branch: `ada09/cr-02` (PR candidate against `main`)
Base commit: `24374dc` (`baseline: initialize ADA-09 agent-ready repository with approved CR-02`)
Candidate commit (Phase 1): `e2f8999` (`feat: implement CR-02`)
Final commit (Phase 6 Fix Cycle): `5722e2a` (`fix: address ADA-09 review findings`)

## Requirements / Acceptance Criteria
- **FR-01 / AC-01**: Partial case-insensitive search by customer `name`.
- **FR-02 / AC-02**: Partial case-insensitive search by customer `email`.
- **FR-03 / AC-03**: Unified search across `name` and `email` (`field="all"`) without duplicate records.
- **FR-04 / AC-04**: Strict input validation rejecting empty/short queries and invalid `limit` parameters (`limit < 1`, booleans, or non-integers) via `ValidationError`.
- **FR-05 / AC-05**: Output reports total match count (`total_matches` prior to slicing) and displays all customer attributes (`id`, `name`, `email`, `phone`, `is_active`).
- **FR-06 / AC-06**: Controlled handling of invalid inputs or errors via descriptive messages to `stderr` with exit code `1` and no unhandled tracebacks.
- **NFR-02 / AC-08**: Complete decoupling of `CustomerSearchService` and `SearchQueryValidator` from the CLI (`cli.py`).
- **NFR-03 / AC-09**: 100% automated test execution via `pytest`.

## Implementation
- **Coder report**: `results/coder-report.md` (Coder Agent session `02e1e837-b5f5-4752-b9d5-73aaa0622837`)
- **Files changed**:
  - `src/customer_search/validator.py` (added `limit: int | None = None` validation to `SearchQueryValidator.validate`)
  - `src/customer_search/service.py` (added `limit: int | None = None` to `CustomerSearchService.search`, delegated validation to `self._validator.validate`, and preserved pre-slice `total_matches`)
  - `src/customer_search/cli.py` (added `PHONE` column to `format_text_output` and `--limit` flag to `build_parser()` / `main()`)
  - `tests/test_validator.py` (added `test_validator_valid_limit` and `test_validator_invalid_limit`)
  - `tests/test_service.py` (added `test_service_search_with_limit` and `test_service_search_invalid_limit`)
  - `tests/test_cli.py` (added `test_cli_limit_flag`, `test_cli_limit_text_output`, `test_cli_invalid_limit_zero`, `test_cli_invalid_limit_negative`, and `test_cli_text_output_includes_phone`)
- **Commits**:
  - `e2f8999 feat: implement CR-02`
  - `5722e2a fix: address ADA-09 review findings`

## Verification
- **Verification command**: `./scripts/verify_repo.sh`
- **Final result**: `VERIFY_REPO: PASS`
- **Tests**: `PASS` (`66 passed in 0.12s` via `pytest -q`)
- **Lint**: `PASS` (`python3 -m compileall -q src tests`)
- **Security / repo checks**: `PASS` (`Repository Contract: PASS`, `Security Check: PASS` via `python3 scripts/check_repo_contract.py`)

## Independent Review
- **Review report**: `results/review-report.md` (Independent Reviewer Agent session `87d3351d-0769-4ec1-8378-9a83215d2f97`, read-only permissions)
- **MUST FIX found**: `2` (`RF-01`: `total_matches` overwritten by post-slice length; `RF-02`: `limit` validation placed in `cli.py` instead of `validator.py` / `service.py`)
- **SHOULD FIX found**: `2` (`RF-03`: missing validator/service tests and missing `total_matches` assertions creating false confidence; `RF-04`: duplicated validation check in `cli.py` and outdated docstrings)
- **OPTIONAL found**: `2` (`RF-05`: fixed-width table separator padding in `cli.py`; `RF-06`: suggestion to add `"limit"` key to `SearchResult.to_dict()`)

## Human Decisions
- **Decision record**: `results/human-review-decisions.md`
- **Accepted**: `3` (`RF-01`, `RF-02`, `RF-04`)
- **Modified**: `1` (`RF-03` — upgraded from `SHOULD FIX` to `MUST FIX` because incomplete tests masked `RF-01` and `RF-02` and violated `CHANGE_REQUEST.md` Verification criteria)
- **Rejected**: `1` (`RF-06` — rejected because adding `"limit"` to `SearchResult.to_dict()` violates `SPEC.md` Domain Model and breaks backward compatibility)
- **Deferred**: `1` (`RF-05` — deferred as cosmetic technical debt outside the bounded scope of `CR-02`)

## Re-review
- **Re-review report**: `results/re-review-report.md`
- **Resolved**: `4` (`RF-01`, `RF-02`, `RF-03`, `RF-04`)
- **Partially resolved**: `0`
- **Not resolved**: `0`
- **New MUST FIX**: `0`

## Traceability

| Requirement / AC | Task / Change | Code | Test | Review Finding |
|---|---|---|---|---|
| `FR-01` / `AC-01` | `T-03`, `CR-02` | `src/customer_search/service.py`, `src/customer_search/cli.py` | `tests/test_service.py::test_search_by_name_partial_and_case_insensitive`, `tests/test_cli.py::test_cli_search_by_name` | None (No regression) |
| `FR-02` / `AC-02` | `T-03`, `CR-02` | `src/customer_search/service.py`, `src/customer_search/cli.py` | `tests/test_service.py::test_search_by_email_partial_and_case_insensitive`, `tests/test_cli.py::test_cli_search_by_email` | None (No regression) |
| `FR-03` / `AC-03` | `T-03`, `CR-02` | `src/customer_search/service.py`, `src/customer_search/cli.py` | `tests/test_service.py::test_unified_search_all_fields`, `tests/test_cli.py::test_cli_search_unified_all` | None (No regression) |
| `FR-04` / `AC-04` | `T-04`, `CR-02` | `src/customer_search/validator.py`, `src/customer_search/service.py` | `tests/test_validator.py::test_validator_valid_limit`, `tests/test_validator.py::test_validator_invalid_limit`, `tests/test_service.py::test_service_search_invalid_limit` | `RF-02` (`RESOLVED`), `RF-03` (`RESOLVED`) |
| `FR-05` / `AC-05` | `T-05`, `CR-02` | `src/customer_search/service.py`, `src/customer_search/cli.py`, `src/customer_search/models.py` | `tests/test_service.py::test_service_search_with_limit`, `tests/test_cli.py::test_cli_limit_flag`, `tests/test_cli.py::test_cli_limit_text_output`, `tests/test_cli.py::test_cli_text_output_includes_phone` | `RF-01` (`RESOLVED`), `RF-05` (`DEFERRED`), `RF-06` (`REJECTED`) |
| `FR-06` / `AC-06` | `T-04`, `T-05`, `CR-02` | `src/customer_search/cli.py`, `src/customer_search/exceptions.py` | `tests/test_cli.py::test_cli_invalid_limit_zero`, `tests/test_cli.py::test_cli_invalid_limit_negative` | `RF-02` (`RESOLVED`), `RF-04` (`RESOLVED`) |
| `NFR-02` / `AC-08` | `T-03`, `CR-02` | `src/customer_search/validator.py`, `src/customer_search/service.py` | `tests/test_service.py::test_service_decoupling_with_custom_repo`, `tests/test_service.py::test_service_search_invalid_limit` | `RF-02` (`RESOLVED`), `RF-04` (`RESOLVED`) |
| `NFR-03` / `AC-09` | `T-05`, `CR-02` | `tests/` | `pytest -q` (`66 passed in 0.12s`) | `RF-03` (`RESOLVED`) |

## Remaining Risks / Technical Debt
- **Deferred Cosmetic Debt (`RF-05`)**: `format_text_output` in `src/customer_search/cli.py` uses fixed column widths (`12`, `28`, `30`, `16`, `8`) and a 98-character separator line. If future datasets contain significantly longer names or email addresses, dynamic column width calculation can be introduced in a dedicated UI formatting task without affecting service or domain contracts.

## PR Description (GitHub Pull Request Template — Section 24)

### Change
CR-02 — Add optional result limit (`limit` / `--limit`) and display customer `phone` in CLI text output

### Requirements Covered
- FR-01, FR-02, FR-03, FR-04, FR-05, FR-06, NFR-02, NFR-03
- AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-08, AC-09

### Verification
- [x] Tests pass (`66 passed in 0.12s`)
- [x] Lint/checks pass (`VERIFY_REPO: PASS`)
- [x] Independent reviewer completed (`results/review-report.md`)
- [x] Human review decisions recorded (`results/human-review-decisions.md`)
- [x] Re-review completed (`results/re-review-report.md`)
- [x] No unresolved accepted MUST FIX

### Evidence
- `results/coder-report.md`
- `results/verification-report.md`
- `results/review-report.md`
- `results/human-review-decisions.md`
- `results/re-review-report.md`
- `results/PR_EVIDENCE.md`

## Final Human Decision
- [ ] NOT READY
- [x] READY FOR HUMAN MERGE

Approved by: Cristian David Mena (Human Reviewer)
Date: 2026-11-06

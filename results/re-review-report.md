# Independent Re-Review Report

## Review Context
- **Change ID**: `CR-02`
- **Branch / PR**: `ada09/cr-02`
- **Initial Commit Reviewed**: `e2f8999` (`feat: implement CR-02`)
- **Post-Fix Commit Reviewed**: `5722e2a` (`fix: address ADA-09 review findings`)
- **Reviewer agent**: Independent Reviewer Agent (`reviewer-agent`, session `87d3351d-0769-4ec1-8378-9a83215d2f97`)
- **Model**: Gemini 4 Argon (High) / Independent Read-Only Subagent Context
- **Tools / permissions**: Read-only (`read_file` only; `EnableWriteTools: false` — no code modification or shell write access)

## Inputs Reviewed
- `results/review-report.md` (Phase 4 Independent Review Report)
- `results/human-review-decisions.md` (Phase 5 Human Review Decisions)
- `results/pr.diff` (Updated branch diff `main...HEAD` at `5722e2a`)
- `results/verification-report.md` (`66 passed in 0.12s`, `VERIFY_REPO: PASS`)
- Production files: `src/customer_search/validator.py`, `src/customer_search/service.py`, `src/customer_search/cli.py`, `src/customer_search/models.py`
- Test files: `tests/test_validator.py`, `tests/test_service.py`, `tests/test_cli.py`

## Finding Resolution Status

| Finding | Human Decision | Re-review Status | Evidence |
|---|---|---|---|
| `RF-01` (`MUST FIX`) | `ACCEPTED` | `RESOLVED` | `src/customer_search/service.py:73-82` computes `total_matches = len(matched)` at line 73 before slicing `matched = matched[:limit]` at lines 75-76, and passes `total_matches=total_matches` to `SearchResult` at line 81. |
| `RF-02` (`MUST FIX`) | `ACCEPTED` | `RESOLVED` | `src/customer_search/validator.py:14-50` adds `limit: int | None = None` to `SearchQueryValidator.validate` and rejects `isinstance(limit, bool) or not isinstance(limit, int) or limit < 1` with `ValidationError("Result limit must be a positive integer greater than or equal to 1.")` (lines 46-50). `src/customer_search/service.py:44` invokes `self._validator.validate(query, field=field, limit=limit)`. |
| `RF-03` (`MODIFIED` -> `MUST FIX`) | `MODIFIED` (Upgraded from `SHOULD FIX` to `MUST FIX`) | `RESOLVED` | `tests/test_validator.py:29-40` tests valid (`None, 1, 5, 100`) and invalid (`0, -1, -10, True, False, "2", 1.5`) limits. `tests/test_service.py:110-125` asserts `res.total_matches == 3` with `len(res.customers) == 2` and tests invalid limits (`0, -1, True, False, "2"`). `tests/test_cli.py:96-136` asserts `data["total_matches"] == 3` in JSON mode, tests `--limit 1` in text mode (`test_cli_limit_text_output`), and tests `--limit -2` (`test_cli_invalid_limit_negative`). |
| `RF-04` (`SHOULD FIX`) | `ACCEPTED` | `RESOLVED` | `src/customer_search/cli.py:94-103` removes the duplicate inline `args.limit < 1` check and delegates validation to `service.search`. `src/customer_search/validator.py:15-28` and `src/customer_search/service.py:29-42` update docstrings to document `limit` validation. |
| `RF-05` (`OPTIONAL`) | `DEFERRED` | `DEFERRED (Verified Unchanged)` | Per human decision in `results/human-review-decisions.md`, fixed-width table formatting in `src/customer_search/cli.py:21-30` is deferred outside `CR-02` scope; `phone` column is present and verified (`AC-05`). |
| `RF-06` (`OPTIONAL`) | `REJECTED` | `REJECTED (Verified Unchanged)` | Per human decision in `results/human-review-decisions.md`, `src/customer_search/models.py:48-65` (`SearchResult.to_dict()`) remains unchanged, preserving canonical `SPEC.md` domain schema and backward compatibility. |

## Detailed Verification of Accepted / Modified Findings

### RF-01 — Pre-slice `total_matches` Preservation (`MUST FIX` — `ACCEPTED`)
- **Status**: `RESOLVED`
- **File / Line**: `src/customer_search/service.py:72-83`
- **Verification**: `matched.sort(...)` is followed immediately by `total_matches = len(matched)` on line 73, prior to `if limit is not None: matched = matched[:limit]` on lines 75-76. `SearchResult` receives `total_matches=total_matches` (line 81) and `customers=matched` (line 82), satisfying `FR-05`, `AC-05`, and `CHANGE_REQUEST.md` Goal 2.

### RF-02 — Validator & Service Layer `limit` Validation (`MUST FIX` — `ACCEPTED`)
- **Status**: `RESOLVED`
- **File / Line**: `src/customer_search/validator.py:14, 46-50` and `src/customer_search/service.py:44`
- **Verification**: `SearchQueryValidator.validate` now accepts `limit: int | None = None` (preserving default `None` for backward compatibility) and checks `if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:` when `limit is not None`, raising `ValidationError("Result limit must be a positive integer greater than or equal to 1.")`. `CustomerSearchService.search` forwards `limit=limit` to `self._validator.validate`, ensuring programmatic service callers (`NFR-02` / `AC-08`) are protected identically to CLI callers.

### RF-03 — Unit & Integration Test Coverage for `limit` and `total_matches` (`MUST FIX` — `MODIFIED`)
- **Status**: `RESOLVED`
- **File / Line**: `tests/test_validator.py:29-40`, `tests/test_service.py:110-125`, `tests/test_cli.py:96-136`
- **Verification**: All test gaps identified in the initial review and human review decisions are now covered. Total test count increased from 48 to 66 (`66 passed in 0.12s`), with explicit assertions on pre-slice `total_matches` (`3`) vs post-slice `len(customers)` (`2` or `1`) and negative/zero/boolean/non-int `limit` rejection across validator, service, and CLI layers.

### RF-04 — Removal of Duplicate CLI Validation & Docstring Updates (`SHOULD FIX` — `ACCEPTED`)
- **Status**: `RESOLVED`
- **File / Line**: `src/customer_search/cli.py:94-103`, `src/customer_search/validator.py:15-28`, `src/customer_search/service.py:29-42`
- **Verification**: The redundant `if args.limit is not None and args.limit < 1:` check in `cli.py` was removed. Invalid `--limit` values passed on the CLI now flow through `service.search` -> `validator.validate`, which raises `ValidationError` caught by `cli.py:101-103` (`Error: Result limit must be a positive integer greater than or equal to 1.` to `stderr`, exit code `1`).

## Regression & Architecture Check
- **New `MUST FIX` Issues**: `0` (None introduced).
- **Architecture Boundaries**: `CLI -> Service -> Validator / Repository -> Models` is strictly preserved (`src/customer_search/models.py` has zero diff against `main`; `data/customers.json`, `REQUIREMENTS.md`, and `SPEC.md` are untouched).
- **Verification Gate**: All checks in `results/verification-report.md` pass (`Tests: PASS` with `66 passed`, `Lint: PASS`, `Repository Contract: PASS`, `Security Check: PASS`, `VERIFY_REPO: PASS`).

## Summary
- **Unresolved `MUST FIX`**: 0
- **Unresolved Accepted `SHOULD FIX`**: 0
- **Deferred `OPTIONAL`**: 1 (`RF-05`)
- **Rejected `OPTIONAL`**: 1 (`RF-06`)

## Reviewer Recommendation
- [ ] NOT READY
- [ ] READY AFTER MUST FIX
- [x] READY FOR HUMAN REVIEW

This recommendation is not a merge approval.

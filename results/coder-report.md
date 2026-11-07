# Coder Agent Report

## Change
- Change ID: CR-02
- Branch: ada09/cr-02
- Base commit: 24374dc

## Requirements Covered
- FR-01
- FR-02
- FR-03
- FR-04
- FR-05
- FR-06
- NFR-02
- NFR-03
- AC-01
- AC-02
- AC-03
- AC-04
- AC-05
- AC-06
- AC-08
- AC-09

## Implementation Plan
1. Inspect `CHANGE_REQUEST.md`, `REQUIREMENTS.md`, `SPEC.md`, and `ARCHITECTURE.md` to confirm the scope of CR-02.
2. Add optional parameter `limit: int | None = None` to `SearchQueryValidator.validate` in `src/customer_search/validator.py` and `CustomerSearchService.search` in `src/customer_search/service.py`, validating `limit >= 1` (rejecting booleans, zero, negative integers, and non-integers) and preserving pre-slice `total_matches` when slicing `matched = matched[:limit]`.
3. Update `format_text_output` in `src/customer_search/cli.py` to display the `PHONE` column (`c.phone`) alongside `ID`, `NAME`, `EMAIL`, and `STATUS` (`FR-05` / `AC-05`).
4. Add `--limit` option to `build_parser()` in `src/customer_search/cli.py` and forward `limit=args.limit` to `service.search(...)`.
5. Add unit/integration tests in `tests/test_validator.py`, `tests/test_service.py`, and `tests/test_cli.py` covering `limit` validation, pre-slice `total_matches` preservation, and `phone` text formatting, then run `./scripts/verify_repo.sh`.

## Files Changed
- `src/customer_search/validator.py`: Added `limit: int | None = None` parameter and strict positive integer validation (`isinstance(limit, bool) or not isinstance(limit, int) or limit < 1`) to `SearchQueryValidator.validate`.
- `src/customer_search/service.py`: Added `limit: int | None = None` parameter to `CustomerSearchService.search`, passed `limit=limit` to `self._validator.validate`, captured `total_matches = len(matched)` prior to slicing `matched = matched[:limit]`, and updated docstrings.
- `src/customer_search/cli.py`: Added `PHONE` column to `format_text_output`, added `--limit` argument to `build_parser()`, delegated `limit` validation to `service.search(..., limit=args.limit)` without duplicate inline CLI checks.
- `tests/test_validator.py`: Added `test_validator_valid_limit` and `test_validator_invalid_limit`.
- `tests/test_service.py`: Added `test_service_search_with_limit` (asserting `res.total_matches == 3` and `len(res.customers) == 2`) and `test_service_search_invalid_limit`.
- `tests/test_cli.py`: Added `test_cli_limit_flag`, `test_cli_limit_text_output`, `test_cli_invalid_limit_zero`, `test_cli_invalid_limit_negative`, and `test_cli_text_output_includes_phone`.

## Tests Added / Updated
- `tests/test_validator.py::test_validator_valid_limit`: Verifies `SearchQueryValidator.validate` accepts `None`, `1`, `5`, `100`.
- `tests/test_validator.py::test_validator_invalid_limit`: Verifies `SearchQueryValidator.validate` raises `ValidationError` for `0`, `-1`, `-10`, `True`, `False`, `"2"`, `1.5`.
- `tests/test_service.py::test_service_search_with_limit`: Verifies `service.search("garcia", field="all", limit=2)` returns `total_matches == 3` and `len(customers) == 2` in sorted order.
- `tests/test_service.py::test_service_search_invalid_limit`: Verifies `service.search` raises `ValidationError` when called programmatically with `0`, `-1`, `True`, `False`, or `"2"`.
- `tests/test_cli.py::test_cli_limit_flag`: Verifies `--limit 2 --json` returns `total_matches == 3` and 2 customer records.
- `tests/test_cli.py::test_cli_limit_text_output`: Verifies `--limit 1` in text mode reports `"Found 3 customer(s) matching 'garcia'"` and renders only the first matching customer row.
- `tests/test_cli.py::test_cli_invalid_limit_zero`: Verifies `--limit 0` returns exit code 1 with `ValidationError` message on `stderr` and no traceback.
- `tests/test_cli.py::test_cli_invalid_limit_negative`: Verifies `--limit -2` returns exit code 1 with `ValidationError` message on `stderr` and no traceback.
- `tests/test_cli.py::test_cli_text_output_includes_phone`: Verifies customer phone number and `PHONE` header are included in CLI standard text output.

## Commands Executed
- `pytest -q`
- `python3 -m compileall -q src tests`
- `./scripts/verify_repo.sh`

## Verification Result
- Tests: PASS (`66 passed in 0.12s`)
- Lint / Typecheck / Build: PASS (`python3 -m compileall -q src tests`)
- Repository Contract: PASS
- Security Check: PASS
- Overall (`./scripts/verify_repo.sh`): `VERIFY_REPO: PASS`

## Fix Cycle (Phase 6)
- **Findings Addressed (`results/human-review-decisions.md`)**:
  - **RF-01 (`ACCEPTED`, MUST FIX)**: Computed `total_matches = len(matched)` in `src/customer_search/service.py` before applying `if limit is not None: matched = matched[:limit]`, preserving the full pre-slice match count in `SearchResult.total_matches`.
  - **RF-02 (`ACCEPTED`, MUST FIX)**: Added `limit: int | None = None` validation to `SearchQueryValidator.validate` in `src/customer_search/validator.py` (rejecting `isinstance(limit, bool) or not isinstance(limit, int) or limit < 1` with `ValidationError("Result limit must be a positive integer greater than or equal to 1.")`) and passed `limit=limit` from `CustomerSearchService.search` to `self._validator.validate`.
  - **RF-03 (`MODIFIED` -> MUST FIX)**: Added unit tests in `tests/test_validator.py` (`test_validator_valid_limit`, `test_validator_invalid_limit`), service tests in `tests/test_service.py` (`test_service_search_with_limit` asserting `res.total_matches == 3`, `test_service_search_invalid_limit`), and CLI tests in `tests/test_cli.py` (`test_cli_limit_flag` asserting `data["total_matches"] == 3`, `test_cli_limit_text_output`, `test_cli_invalid_limit_negative`).
  - **RF-04 (`ACCEPTED`, SHOULD FIX)**: Removed the duplicate inline `if args.limit is not None and args.limit < 1:` check from `src/customer_search/cli.py` so validation is enforced strictly by the validation/service layers, and updated docstrings in `validator.py` and `service.py`.
- **Findings Not Implemented per Human Decision**:
  - **RF-05 (`DEFERRED`)**: Left CLI fixed-width table padding untouched as deferred cosmetic debt.
  - **RF-06 (`REJECTED`)**: Preserved `SearchResult` and `SearchResult.to_dict()` schema without adding a `"limit"` key per `SPEC.md`.

## Assumptions
- Calling `--limit` with non-integer strings on the CLI continues to be handled by `argparse` (`type=int`) with exit code `2`.
- Default behavior when `limit` is `None` remains unchanged and returns all matching records.

## Known Limitations
- Pagination offsets or cursor-based pagination remain out of scope per `SPEC.md`.

## Self-Check
- [x] Scope matches CHANGE_REQUEST.md
- [x] Existing tests still pass
- [x] New behavior has tests
- [x] No secrets or debug artifacts were added

This report is NOT an approval.

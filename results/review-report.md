# Independent Review Report

## Review Context
- **Change ID**: `CR-02`
- **Branch / PR**: `ada09/cr-02`
- **Commit reviewed**: `e2f8999` (`feat: implement CR-02`)
- **Reviewer agent**: Independent Reviewer Agent (`reviewer-agent`, session `87d3351d-0769-4ec1-8378-9a83215d2f97`)
- **Model**: Gemini 4 Argon (High) / Independent Read-Only Subagent Context
- **Tools / permissions**: Read-only (`read_file` only; `EnableWriteTools: false` — no code modification or shell write access)

## Requirements Reviewed
- **CHANGE_REQUEST.md (`CR-02`)**:
  - Goal 1: `SearchQueryValidator.validate` in `src/customer_search/validator.py` must validate `limit` when provided (`limit >= 1`, strictly positive integer, rejecting booleans, zero, negative integers, and non-integer types) and raise `ValidationError("Result limit must be a positive integer greater than or equal to 1.")`.
  - Goal 2: `CustomerSearchService.search` in `src/customer_search/service.py` must accept `limit: int | None = None`, slice `SearchResult.customers` to at most `limit` sorted matches, and preserve `SearchResult.total_matches` as the full pre-slice match count.
  - Goal 3: `src/customer_search/cli.py` must support `--limit`, display each customer's `phone` column in `format_text_output`, and handle invalid `--limit` values cleanly as `ValidationError` on `stderr` with exit code `1` and no traceback.
- **Functional & Non-Functional Requirements (`REQUIREMENTS.md` / `SPEC.md` / `results/review-contract.md`)**:
  - `FR-01` / `AC-01`, `FR-02` / `AC-02`, `FR-03` / `AC-03`: Partial case-insensitive search across `name`, `email`, and unified `all` without duplicates.
  - `FR-04` / `AC-04`: Strict input validation in the validation layer rejecting invalid query terms and invalid `limit` parameters with `ValidationError`.
  - `FR-05` / `AC-05`: Output must report the total number of matches (`total_matches` before result slicing) and include all customer attributes (`id`, `name`, `email`, `phone`, `is_active`).
  - `FR-06` / `AC-06`: Clean error handling in CLI to `stderr` with exit code `1` and no unhandled tracebacks.
  - `NFR-02` / `AC-08`: Complete decoupling of business and validation logic (`CustomerSearchService` and `SearchQueryValidator`) from the CLI (`cli.py`).
  - `NFR-03` / `AC-09`: Automated `pytest` suite covering all functional behaviors and validation rules.

## Verification Evidence Reviewed
- `results/verification-report.md`:
  - `pytest -q`: `48 passed in 0.09s` (`Tests: PASS`)
  - `python3 -m compileall -q src tests`: `PASS` (`Lint: PASS`)
  - `python3 scripts/check_repo_contract.py`: `PASS` (`Repository Contract: PASS`, `Security Check: PASS`)
  - Overall Gate: `PASS (VERIFY_REPO: PASS)`
- `results/pr.diff` and source/test files (`src/customer_search/validator.py`, `src/customer_search/service.py`, `src/customer_search/cli.py`, `src/customer_search/models.py`, `tests/test_validator.py`, `tests/test_service.py`, `tests/test_cli.py`).
- **Assessment of Verification Evidence**: Although `./scripts/verify_repo.sh` passed all 48 tests, inspection of the diff and test assertions reveals that the new tests omit assertions on `total_matches` when `limit` is applied and omit direct validator/service tests for invalid `limit` values, masking two `MUST FIX` defects.

## Findings

### RF-01 — MUST FIX
- **Category**: Requirement Violation / Functional Defect
- **Requirement / AC**: `FR-05`, `AC-05`, `CHANGE_REQUEST.md` (Goal 2)
- **File / Line**: `src/customer_search/service.py:74-82`
- **Evidence**:
  ```python
        if limit is not None:
            matched = matched[:limit]

        return SearchResult(
            query=normalized_query,
            field=field_target,
            total_matches=len(matched),
            customers=matched,
        )
  ```
- **Problem**: `CustomerSearchService.search` slices `matched = matched[:limit]` before computing `total_matches=len(matched)`. When `limit` is smaller than the number of matching records (e.g., searching `"garcia"` with `limit=2` where 3 records match), `SearchResult.total_matches` is overwritten with the post-slice length (`2`) instead of preserving the true pre-slice match count (`3`).
- **Risk**: Callers and CLI users (in both text header `"Found X customer(s)..."` and `--json` output `"total_matches"`) receive an inaccurate total match count whenever `limit` truncates results, violating `FR-05`, `AC-05`, and `CHANGE_REQUEST.md` Goal 2.
- **Recommended next step**: Capture `total_matches = len(matched)` prior to applying `if limit is not None: matched = matched[:limit]`, and pass the pre-slice `total_matches` into `SearchResult`.

### RF-02 — MUST FIX
- **Category**: Architecture Boundary Violation / Missing Validation in Validator & Service Layers
- **Requirement / AC**: `FR-04`, `NFR-02`, `AC-04`, `AC-08`, `ARCHITECTURE.md`, `CHANGE_REQUEST.md` (Goal 1 & Goal 2)
- **File / Line**: `src/customer_search/validator.py:13-44`, `src/customer_search/service.py:44-45`, `src/customer_search/cli.py:95-96`
- **Evidence**:
  - `src/customer_search/validator.py:14`:
    ```python
    def validate(query: str, field: str = "all") -> str:
    ```
    (`validator.py` has no `limit` parameter or `limit` validation logic.)
  - `src/customer_search/service.py:44`:
    ```python
    normalized_query = self._validator.validate(query, field=field)
    ```
  - `src/customer_search/cli.py:95-96`:
    ```python
    if args.limit is not None and args.limit < 1:
        raise ValidationError("Result limit must be a positive integer greater than or equal to 1.")
    ```
- **Problem**: `limit` validation was implemented exclusively in `src/customer_search/cli.py` instead of `SearchQueryValidator.validate` in `src/customer_search/validator.py` and `CustomerSearchService.search` in `src/customer_search/service.py`. Furthermore, Python's `bool` is a subclass of `int` (`isinstance(True, int) == True`), so programmatic calls such as `service.search("garcia", limit=0)`, `service.search("garcia", limit=-1)`, `service.search("garcia", limit=True)`, or `service.search("garcia", limit="2")` bypass validation completely.
- **Risk**: Programmatic callers of `CustomerSearchService.search` (`NFR-02` / `AC-08`) receive silent data corruption (e.g., `limit=-1` slices `matched[:-1]`, silently dropping the last customer; `limit=0` returns 0 customers; `limit=True` returns 1 customer; `limit="2"` raises an unhandled `TypeError` on slice) instead of raising `ValidationError`.
- **Recommended next step**: Add `limit: int | None = None` to `SearchQueryValidator.validate(query: str, field: str = "all", limit: int | None = None) -> str` (rejecting `isinstance(limit, bool) or not isinstance(limit, int) or limit < 1` when `limit is not None` with `ValidationError("Result limit must be a positive integer greater than or equal to 1.")`), pass `limit=limit` from `CustomerSearchService.search` to `self._validator.validate`, and remove the ad-hoc validation from `cli.py`.

### RF-03 — SHOULD FIX
- **Category**: Test Coverage / False Confidence (Test Masking)
- **Requirement / AC**: `NFR-03`, `AC-05`, `AC-08`, `AC-09`, `CHANGE_REQUEST.md` (Verification items 1, 2, 3)
- **File / Line**: `tests/test_validator.py:1-26`, `tests/test_service.py:110-115`, `tests/test_cli.py:96-112`
- **Evidence**:
  - `tests/test_service.py:110-115`:
    ```python
    def test_service_search_with_limit(search_service):
        # CR-02: limit parameter restricts returned customers
        res = search_service.search("garcia", field="all", limit=2)
        assert len(res.customers) == 2
        assert [c.name for c in res.customers] == ["Ana Garcia", "Beatriz Mendez"]
    ```
  - `tests/test_cli.py:96-102`:
    ```python
    def test_cli_limit_flag(capsys):
        # CR-02: --limit restricts the number of returned customers
        ret = main(["garcia", "--limit", "2", "--json"])
        assert ret == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert len(data["customers"]) == 2
    ```
- **Problem**:
  1. `tests/test_validator.py` was not updated with any unit tests for `limit` validation (`None`, `1`, `5`, `0`, `-1`, `True`, `False`, `"2"`).
  2. `test_service_search_with_limit` in `tests/test_service.py` and `test_cli_limit_flag` in `tests/test_cli.py` only assert `len(customers) == 2` and omit asserting `total_matches == 3`, which masked `RF-01`.
  3. `tests/test_service.py` has no tests verifying that calling `service.search` directly with an invalid `limit` raises `ValidationError`, which masked `RF-02`.
  4. `tests/test_cli.py` lacks coverage for `--limit` in text output mode and negative `--limit` values (e.g., `--limit -2`).
- **Risk**: Automated verification (`pytest -q`) passes with 100% green status while core requirements in `CHANGE_REQUEST.md` are unimplemented or broken.
- **Recommended next step**: Add unit tests in `tests/test_validator.py` for valid/invalid `limit` values (including booleans `True`/`False`), update `tests/test_service.py` to assert `res.total_matches == 3` when `limit=2` and test invalid `limit` values via `service.search`, and update `tests/test_cli.py` to assert `data["total_matches"] == 3`, test `--limit` in text mode, and test negative `--limit`.

### RF-04 — SHOULD FIX
- **Category**: Technical Debt / Layer Coupling & Documentation Drift
- **Requirement / AC**: `NFR-02`, `ARCHITECTURE.md`
- **File / Line**: `src/customer_search/cli.py:95-96`, `src/customer_search/service.py:40-41`, `src/customer_search/validator.py:14-26`
- **Evidence**:
  - `src/customer_search/cli.py:95-96`:
    ```python
    if args.limit is not None and args.limit < 1:
        raise ValidationError("Result limit must be a positive integer greater than or equal to 1.")
    ```
  - `src/customer_search/service.py:40-41`:
    ```python
    Raises:
        ValidationError: If query violates VR-01, VR-02, or VR-03.
    ```
- **Problem**: Hardcoding domain validation rules and error messages in `cli.py` couples the CLI presentation layer to domain validation logic. In addition, docstrings in `validator.py` and `service.py` do not document the `limit` validation contract.
- **Risk**: Duplicated validation checks across layers increase maintenance overhead and risk inconsistent error messages if validation rules evolve.
- **Recommended next step**: Remove the inline `args.limit < 1` check from `src/customer_search/cli.py` once `SearchQueryValidator.validate` and `CustomerSearchService.search` enforce `limit` validation, and update the docstrings in `validator.py` and `service.py`.

### RF-05 — OPTIONAL
- **Category**: Presentation / CLI Formatting Polish
- **Requirement / AC**: `FR-05`, `AC-05`
- **File / Line**: `src/customer_search/cli.py:21-30`
- **Evidence**:
  ```python
    lines = [
        f"Found {result.total_matches} customer(s) matching '{result.query}' [field: {result.field}]:",
        "-" * 98,
        f"{'ID':<12} | {'NAME':<28} | {'EMAIL':<30} | {'PHONE':<16} | {'STATUS':<8}",
        "-" * 98,
    ]
  ```
- **Problem**: The formatted row width is `12 + 3 + 28 + 3 + 30 + 3 + 16 + 3 + 8 = 106` characters, whereas the horizontal divider uses `"-" * 98` (8 characters shorter than the header/rows). Additionally, some records in `data/customers.json` have names of 29 characters (`"Carlos Alberto Ramirez Garcia"`) or emails of 33 characters (`"isabel.vargas@creative-agency.com"`), slightly shifting column pipes on those rows.
- **Risk**: Cosmetic misalignment in terminal text output; does not affect functional correctness or data presence (`AC-05`).
- **Recommended next step**: Optionally compute dynamic column widths or adjust fixed padding in a future CLI formatting improvement.

### RF-06 — OPTIONAL
- **Category**: Domain Model / API Enhancement Proposal
- **Requirement / AC**: `FR-05`, `SPEC.md` (Domain Model `SearchResult`)
- **File / Line**: `src/customer_search/models.py:48-65`
- **Evidence**:
  ```python
    def to_dict(self) -> dict[str, Any]:
        """Convert search result to dictionary."""
        return {
            "query": self.query,
            "field": self.field,
            "total_matches": self.total_matches,
            "customers": [c.to_dict() for c in self.customers],
        }
  ```
- **Problem**: `SearchResult` does not expose a `limit: int | None = None` attribute in `to_dict()` to indicate whether the returned `customers` list was truncated by a limit parameter.
- **Risk**: JSON consumers have to compare `total_matches > len(customers)` to infer whether a limit was applied.
- **Recommended next step**: Consider adding `limit: int | None = None` to `SearchResult` and `SearchResult.to_dict()` if schema changes are authorized.

## API / Dependency Verification
- **Production APIs & Standard Library Imports**:
  - `src/customer_search/models.py`: Uses standard library `dataclasses` (`dataclass`, `asdict`) and `typing.Any`. `SearchResult.to_dict()` preserves backward compatibility (`query`, `field`, `total_matches`, `customers`).
  - `src/customer_search/validator.py`: Imports `ValidationError` from `src.customer_search.exceptions`. Missing the `limit: int | None = None` parameter on `SearchQueryValidator.validate` required by `CHANGE_REQUEST.md` Goal 1 (flagged in `RF-02`).
  - `src/customer_search/service.py`: Imports `Customer`, `SearchResult`, `SearchQueryValidator`, and `CustomerRepository`. All referenced methods (`self._validator.validate`, `self._repository.get_all`) exist in production code.
  - `src/customer_search/cli.py`: Uses standard library `argparse`, `json`, `sys`, `pathlib.Path`, `typing.Sequence`, and internal modules (`exceptions`, `repository`, `service`, `models`). All called APIs exist.
- **External Dependencies**: Zero new third-party dependencies added (`requirements.txt` remains `pytest>=8.0.0` only, satisfying `C-01`).

## Missing Evidence / Open Questions
- **Missing Test Evidence**: Unit test evidence for `SearchQueryValidator.validate` with `limit` (`None`, `1`, `5`, `0`, `-1`, `True`, `False`, `"2"`) and service-level tests asserting `total_matches` preservation and `ValidationError` on invalid `limit` values are missing from `tests/test_validator.py`, `tests/test_service.py`, and `tests/test_cli.py` (covered by `RF-03`).
- **Open Questions**: None. The requirements in `CHANGE_REQUEST.md`, `REQUIREMENTS.md`, `SPEC.md`, and `ARCHITECTURE.md` are unambiguous.

## Summary
- **MUST FIX**: 2 (`RF-01`, `RF-02`)
- **SHOULD FIX**: 2 (`RF-03`, `RF-04`)
- **OPTIONAL**: 2 (`RF-05`, `RF-06`)

## Reviewer Recommendation
- [ ] NOT READY
- [x] READY AFTER MUST FIX
- [ ] READY FOR HUMAN REVIEW

This recommendation is not a merge approval.

# Change Request

Change ID: CR-02

## Goal
Add an optional result limit capability (`limit: int | None = None` in `CustomerSearchService.search` and `--limit` in `src/customer_search/cli.py`) and complete customer attribute presentation in CLI text output by including the customer `phone` column (`FR-05` / `AC-05`):
1. `SearchQueryValidator.validate` in `src/customer_search/validator.py` (or a dedicated validation method called by `validate`) must validate `limit` when provided: `limit` must be a strictly positive integer (`limit >= 1`, rejecting booleans, zero, negative integers, or non-integer types) and raise `ValidationError("Result limit must be a positive integer greater than or equal to 1.")` on invalid values.
2. `CustomerSearchService.search` in `src/customer_search/service.py` must accept `limit: int | None = None`. When `limit` is provided, `SearchResult.customers` must contain at most `limit` sorted matching customers, while `SearchResult.total_matches` must continue to report the total number of matching customers before slicing so callers know the true match count (`FR-05`, `AC-05`, `AC-08`).
3. `src/customer_search/cli.py` must support an optional `--limit` argument forwarded to `service.search`, and `format_text_output` must include each customer's `phone` field alongside `id`, `name`, `email`, and `is_active` status (`FR-05`, `AC-05`). Invalid `--limit` values (such as `0` or `-5`) must be handled cleanly as `ValidationError` printing to `stderr` with exit code `1` and no traceback (`FR-06`, `AC-06`).

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

## Constraints
- Follow AGENTS.md.
- Use REQUIREMENTS.md and SPEC.md as the source of truth.
- Preserve architecture boundaries (`CLI -> Service -> Validator / Repository -> Models`).
- Do not weaken existing tests.
- Preserve backward compatibility for existing callers of `CustomerSearchService.search`, `SearchQueryValidator.validate`, and `SearchResult.to_dict()`.

## Verification
1. Validator unit tests in `tests/test_validator.py` verify that valid `limit` values (`None`, `1`, `5`) pass and invalid values (`0`, `-1`, `True`, `False`, `"2"`) raise `ValidationError`.
2. Service tests in `tests/test_service.py` verify that `limit` caps `result.customers` while preserving `result.total_matches` as the full match count, and that calling `service.search` directly with an invalid `limit` raises `ValidationError`.
3. CLI tests in `tests/test_cli.py` verify `--limit` in both text and `--json` modes, verify that `phone` is displayed in CLI text output (`AC-05`), and verify that `--limit 0` or `--limit -2` exits with code `1` and writes a clean error to `stderr` (`AC-06`).
4. `./scripts/verify_repo.sh` passes all checks (`Tests: PASS`, `Lint: PASS`, `Repository Contract: PASS`, `Security Check: PASS`, `VERIFY_REPO: PASS`).

## Human Approval
Approved to implement: YES
Approved by: Cristian David Mena (Human Reviewer)
Date: 2026-11-06

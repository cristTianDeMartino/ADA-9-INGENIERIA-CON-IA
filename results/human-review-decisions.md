# Human Review Decisions

## Change
CR-02 — Optional result limit (`limit` / `--limit`) and complete customer attribute presentation (`phone` in CLI text output)

### RF-01
Reviewer severity: MUST FIX
Human decision: ACCEPTED
Reason: `src/customer_search/service.py:74-82` slices `matched = matched[:limit]` before computing `total_matches=len(matched)`, which overwrites the true match count with the truncated list length. This directly violates `FR-05`, `AC-05`, and `CHANGE_REQUEST.md` Goal 2.
Required action: Compute `total_matches = len(matched)` prior to applying `if limit is not None: matched = matched[:limit]` in `src/customer_search/service.py` and pass `total_matches=total_matches` to `SearchResult`.

### RF-02
Reviewer severity: MUST FIX
Human decision: ACCEPTED
Reason: `limit` validation was placed in `src/customer_search/cli.py:95-96` instead of `SearchQueryValidator.validate` (`src/customer_search/validator.py`), leaving `CustomerSearchService.search` unprotected when invoked programmatically (`NFR-02` / `AC-08` and `ARCHITECTURE.md` layered flow `CLI -> Service -> Validator`). Calling `service.search("garcia", limit=-1)` or `limit=True` silently returns wrong results instead of raising `ValidationError`.
Required action: Add `limit: int | None = None` validation to `SearchQueryValidator.validate` in `src/customer_search/validator.py` (rejecting `isinstance(limit, bool) or not isinstance(limit, int) or limit < 1` when `limit is not None` with `ValidationError("Result limit must be a positive integer greater than or equal to 1.")`), invoke `self._validator.validate(query, field=field, limit=limit)` in `CustomerSearchService.search`.

### RF-03
Reviewer severity: SHOULD FIX
Human decision: MODIFIED
Reason: The reviewer classified the missing validator/service tests and missing `total_matches` assertions as `SHOULD FIX`. However, `CHANGE_REQUEST.md` (Verification items 1, 2, and 3) and `NFR-03` / `AC-09` explicitly mandate unit and integration tests for `limit` validation (`None`, `1`, `5`, `0`, `-1`, `True`, `False`, `"2"`), pre-slice `total_matches` preservation, and negative CLI limits. Because the incomplete tests in Commit `e2f8999` produced false confidence (green test suite masking `RF-01` and `RF-02`), this finding blocks merge readiness and is upgraded to `MUST FIX`.
Final severity: MUST FIX
Required action: Add unit tests for `limit` validation in `tests/test_validator.py`, update `tests/test_service.py` to assert `res.total_matches == 3` when `limit=2` and verify `ValidationError` on invalid `limit` values (`0`, `-1`, `True`, `"2"`), and update `tests/test_cli.py` to assert `data["total_matches"] == 3` and test negative `--limit -2` and text mode `--limit`.

### RF-04
Reviewer severity: SHOULD FIX
Human decision: ACCEPTED
Reason: Keeping a duplicate `if args.limit is not None and args.limit < 1:` check in `src/customer_search/cli.py:95-96` violates layer decoupling (`NFR-02`) once `SearchQueryValidator.validate` and `CustomerSearchService.search` enforce the rule.
Required action: Remove the inline `args.limit` validation from `src/customer_search/cli.py` so `cli.py` relies on `CustomerSearchService.search` raising `ValidationError`, and update the docstrings in `validator.py` and `service.py`.

### RF-05
Reviewer severity: OPTIONAL
Human decision: DEFERRED
Reason: Fixed-width column padding and the `"-" * 98` separator in `format_text_output` (`src/customer_search/cli.py:21-30`) are purely cosmetic. All required customer attributes (`id`, `name`, `email`, `phone`, `is_active`) are present and readable (`FR-05` / `AC-05`). Refactoring the CLI table formatter to dynamically calculate column widths is outside the bounded scope of `CR-02` and is recorded as deferred technical debt.

### RF-06
Reviewer severity: OPTIONAL
Human decision: REJECTED
Reason: Adding a `"limit"` field to `SearchResult` and `SearchResult.to_dict()` in `src/customer_search/models.py:48-65` conflicts with the canonical Domain Model in `SPEC.md` (lines 39-44, which define strictly `query`, `field`, `total_matches`, and `customers`) and violates the backward-compatibility constraint in `CHANGE_REQUEST.md`. Callers can already determine truncation from `total_matches > len(customers)` without breaking existing schema contracts.

## Human Gate
- [x] Return to coder-agent
- [ ] Ready for final re-review
- [ ] Stop / escalate

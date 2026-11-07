# Review Contract

## Change
CR-02 — Optional result limit (`limit` / `--limit`) and complete customer attribute presentation (`phone` in CLI text output)

## Requirements / Acceptance Criteria
- **FR-01 / AC-01**: Partial case-insensitive search by customer `name`.
- **FR-02 / AC-02**: Partial case-insensitive search by customer `email`.
- **FR-03 / AC-03**: Unified search across `name` and `email` (`field="all"`) without duplicate records.
- **FR-04 / AC-04**: Strict input validation rejecting empty/short queries and invalid search parameters (`limit < 1`, non-integer, or boolean values) by raising `ValidationError`.
- **FR-05 / AC-05**: Output must report the total number of matches (`total_matches` before result slicing) and present all customer attributes (`id`, `name`, `email`, `phone`, `is_active`) in both CLI text and JSON modes.
- **FR-06 / AC-06**: Controlled handling of invalid inputs or errors via descriptive messages to `stderr` and exit code `1` without unhandled tracebacks.
- **NFR-02 / AC-08**: Complete decoupling of `CustomerSearchService` and `SearchQueryValidator` from the CLI (`cli.py`), ensuring programmatic callers receive identical validation and search behavior without relying on `argparse` or `cli.py`.
- **NFR-03 / AC-09**: 100% automated test pass rate via `pytest`.

## Architecture Constraints
- **Expected dependency flow**:
  - `cli.py` -> `service.py` (`CustomerSearchService`), `repository.py` (`InMemoryCustomerRepository`), `models.py` (`SearchResult`), `exceptions.py`
  - `service.py` -> `validator.py` (`SearchQueryValidator`), `repository.py` (`CustomerRepository`), `models.py` (`Customer`, `SearchResult`)
  - `validator.py` -> `exceptions.py` (`ValidationError`)
  - `models.py` -> Standard library `dataclasses` only (zero upward dependencies)
- **Business-rule location**:
  - Query and parameter validation rules (`VR-01`, `VR-02`, `VR-03`, and `limit` validation) must reside in `src/customer_search/validator.py` (`SearchQueryValidator`) and be enforced by `CustomerSearchService.search` in `src/customer_search/service.py` — never exclusively in `src/customer_search/cli.py`.
  - Filtering, sorting (`SR-05`), and result limiting while preserving pre-slice `total_matches` must reside in `src/customer_search/service.py`.
- **Protected boundaries**:
  - `data/customers.json` (protected reference dataset — must not be modified).
  - `REQUIREMENTS.md` and `SPEC.md` (sources of truth — must not be weakened or altered to fit buggy code).
  - `SearchResult` domain schema (`query`, `field`, `total_matches`, `customers`) must preserve backward compatibility.

## Review Rules
- Verify requirement coverage across all listed `FR-*`, `NFR-*`, and `AC-*` items in `CHANGE_REQUEST.md`.
- Verify every called API/dependency exists in production code (`models.py`, `validator.py`, `repository.py`, `service.py`, `cli.py`, `exceptions.py`).
- Check architecture boundaries (`CLI -> Service -> Validator / Repository -> Models`) and verify no validation or business rule leaks exclusively into `cli.py`.
- Inspect tests for masking / false confidence (e.g., testing only happy paths, asserting post-slice counts instead of total matches, or testing validation only via CLI while programmatic service calls bypass validation).
- Check regression behavior and backward compatibility for existing callers.
- Identify unnecessary technical debt or coupling introduced by the diff.
- Cite concrete file and line evidence for every finding.

## Severity
MUST FIX:
Requirement violation, regression, security/integrity risk,
hallucinated API/dependency, broken architecture constraint,
or defect that makes the change unsafe to approve.

SHOULD FIX:
Significant maintainability, coverage, design, or clarity issue
that does not block the requested behavior.

OPTIONAL:
Non-blocking improvement outside the minimum acceptance threshold.

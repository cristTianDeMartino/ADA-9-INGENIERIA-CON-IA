# Repository Map

## Entry Points
- `src/customer_search/cli.py`: CLI entrypoint and argument parser.
- `src/customer_search/service.py`: Core search logic (`CustomerSearchService`).
- `src/customer_search/models.py`: Domain models (`Customer`, `SearchResult`).
- `src/customer_search/repository.py`: In-memory and JSON data persistence.
- `src/customer_search/validator.py`: Query normalization and validation rules.

## Tests
- `tests/test_service.py`: Service-layer business logic and filtering tests.
- `tests/test_cli.py`: CLI interface execution and argument parsing tests.
- `tests/test_models.py`: Domain entity immutability and schema tests.
- `tests/test_repository.py`: Data loading and error handling tests.
- `tests/test_validator.py`: Query validation rule tests.
- `tests/test_performance.py`: Response latency tests on 1,000 synthetic records.

## Change Guide
If adding or modifying search behavior:
1. Review `REQUIREMENTS.md` and `SPEC.md` for existing constraints.
2. Implement domain or service changes in `src/customer_search/service.py`.
3. Update argument flags and handlers in `src/customer_search/cli.py` if needed.
4. Add corresponding tests in `tests/test_service.py` and `tests/test_cli.py`.
5. Execute `./scripts/verify_repo.sh` to confirm syntax, tests, and repository contracts.

## Do Not Edit Directly
- `data/customers.json`: Protected reference dataset used by regression tests.
- `docs/traceability.md`: Requirement matrix; updated through formal requirement reviews.
- `.github/workflows/verify.yml`: CI pipeline definitions; requires human review.

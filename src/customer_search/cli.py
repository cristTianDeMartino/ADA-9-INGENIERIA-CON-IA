"""Command-line interface (CLI) for Customer Search feature."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from typing import Sequence
from src.customer_search.exceptions import CustomerSearchError, ValidationError, DataLoadError
from src.customer_search.repository import InMemoryCustomerRepository
from src.customer_search.service import CustomerSearchService
from src.customer_search.models import SearchResult

DEFAULT_DATA_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "customers.json"


def format_text_output(result: SearchResult) -> str:
    """Format a SearchResult into human-readable text output."""
    if result.total_matches == 0:
        return f"No customers found matching '{result.query}'."

    lines = [
        f"Found {result.total_matches} customer(s) matching '{result.query}' [field: {result.field}]:",
        "-" * 80,
        f"{'ID':<12} | {'NAME':<28} | {'EMAIL':<30} | {'STATUS':<8}",
        "-" * 80,
    ]
    for c in result.customers:
        status = "Active" if c.is_active else "Inactive"
        lines.append(f"{c.id:<12} | {c.name:<28} | {c.email:<30} | {status:<8}")
    lines.append("-" * 80)
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    """Construct the command line argument parser."""
    parser = argparse.ArgumentParser(
        prog="customer-search",
        description="Search customers by name or email with partial match support.",
    )
    parser.add_argument(
        "query",
        type=str,
        help="Search term (minimum 2 non-whitespace characters).",
    )
    parser.add_argument(
        "-f",
        "--field",
        choices=["all", "name", "email"],
        default="all",
        help="Field to search within (default: all).",
    )
    parser.add_argument(
        "-d",
        "--data-file",
        type=str,
        default=str(DEFAULT_DATA_FILE),
        help=f"Path to JSON customer data file (default: {DEFAULT_DATA_FILE}).",
    )
    parser.add_argument(
        "--active-only",
        action="store_true",
        dest="active_only",
        help="Filter search results to active customers only.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Output results in JSON format.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Main CLI entrypoint.

    Returns:
        0 on success (including zero matches),
        1 on business/validation or data loading errors,
        2 on CLI syntax/argument errors.
    """
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2

    try:
        data_path = Path(args.data_file)
        repository = InMemoryCustomerRepository.from_json_file(data_path)
        service = CustomerSearchService(repository=repository)
        result = service.search(
            query=args.query,
            field=args.field,
            active_only=args.active_only,
        )

        if args.as_json:
            print(json.dumps(result.to_dict(), indent=2))
        else:
            print(format_text_output(result))
        return 0

    except (ValidationError, DataLoadError, CustomerSearchError) as err:
        sys.stderr.write(f"Error: {err}\n")
        return 1
    except Exception as err:
        sys.stderr.write(f"Unexpected error: {err}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())

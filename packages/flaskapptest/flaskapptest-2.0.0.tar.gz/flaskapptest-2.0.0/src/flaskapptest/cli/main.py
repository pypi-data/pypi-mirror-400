import argparse
import sys

from flaskapptest.cli.manual_runner import ManualRunner
from flaskapptest.cli.batch_runner import BatchRunner
from flaskapptest.cli.ci_runner import CIRunner

# Default Flask URL if none is provided
DEFAULT_FLASK_BASE_URL = "http://127.0.0.1:5000"


def main():
    parser = argparse.ArgumentParser(
        prog="flaskapptest",
        description="Production-grade Flask API testing CLI (AST-based, offline scanning supported)",
    )

    subparsers = parser.add_subparsers(dest="mode", required=True)

    # -------- Manual mode --------
    manual = subparsers.add_parser(
        "manual",
        help="Run interactive manual testing",
    )
    manual.add_argument(
        "--project",
        required=True,
        help="Path to Flask project root",
    )
    manual.add_argument(
        "--base-url",
        required=False,
        help=f"Base URL of running Flask app (default: {DEFAULT_FLASK_BASE_URL})",
    )

    # -------- Batch mode --------
    batch = subparsers.add_parser(
        "batch",
        help="Run batch testing for all detected endpoints",
    )
    batch.add_argument(
        "--project",
        required=True,
        help="Path to Flask project root",
    )
    batch.add_argument(
        "--base-url",
        required=False,
        help=f"Base URL of running Flask app (default: {DEFAULT_FLASK_BASE_URL})",
    )
    batch.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop execution on first failure",
    )

    # -------- CI mode --------
    ci = subparsers.add_parser(
        "ci",
        help="Run CI/CD validation (non-interactive)",
    )
    ci.add_argument(
        "--project",
        required=True,
        help="Path to Flask project root",
    )
    ci.add_argument(
        "--base-url",
        required=False,
        help=f"Base URL of running Flask app (default: {DEFAULT_FLASK_BASE_URL})",
    )

    args = parser.parse_args()

    # Resolve base URL fallback
    base_url = args.base_url or DEFAULT_FLASK_BASE_URL

    # -------- Dispatch --------
    if args.mode == "manual":
        runner = ManualRunner(
            project_path=args.project,
            base_url=base_url,
        )
        runner.run()

    elif args.mode == "batch":
        runner = BatchRunner(
            project_path=args.project,
            base_url=base_url,
            fail_fast=args.fail_fast,
        )
        runner.run()

    elif args.mode == "ci":
        runner = CIRunner(
            project_path=args.project,
            base_url=base_url,
        )
        runner.run()

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

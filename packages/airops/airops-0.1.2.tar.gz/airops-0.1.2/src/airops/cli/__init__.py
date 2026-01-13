"""AirOps CLI entry point."""

from __future__ import annotations

import argparse
import sys

from airops._version import __version__


def main(argv: list[str] | None = None) -> int:
    """Main CLI entry point.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:]).

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    parser = argparse.ArgumentParser(
        prog="airops",
        description="AirOps Python SDK CLI",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    init_parser = subparsers.add_parser(
        "init",
        help="Initialize a new AirOps tool project",
        description="Create a new AirOps tool project with example files.",
    )
    init_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Directory to initialize (default: current directory)",
    )
    init_parser.add_argument(
        "--name",
        default=None,
        help="Tool name (default: derived from directory name)",
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files",
    )

    run_parser = subparsers.add_parser(
        "run",
        help="Build and run the tool with hot reload",
        description="Build the Docker image and run with hot reload enabled.",
    )
    run_parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to expose (default: 8080)",
    )

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "init":
        from airops.cli.init import run_init

        return run_init(args.path, args.name, args.force)

    if args.command == "run":
        from airops.cli.run import run_dev

        return run_dev(args.port)

    return 0


if __name__ == "__main__":
    sys.exit(main())

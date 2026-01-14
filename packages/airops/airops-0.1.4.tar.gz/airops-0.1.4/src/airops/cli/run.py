"""Implementation of the 'airops run' command."""

from __future__ import annotations

import subprocess
from pathlib import Path

from airops.cli.init import sanitize_name


def run_dev(port: int) -> int:
    """Run the tool in development mode with hot reload.

    Args:
        port: Port to expose.

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    cwd = Path.cwd()

    if not (cwd / "Dockerfile").exists():
        print("Error: No Dockerfile found. Run 'airops init' first.")
        return 1

    if not (cwd / "tool.py").exists():
        print("Error: No tool.py found. Run 'airops init' first.")
        return 1

    if not (cwd / ".env").exists():
        print("Error: No .env file found.")
        print("Copy .env.example to .env and add your AIROPS_API_TOKEN:")
        print("  cp .env.example .env")
        return 1

    name = sanitize_name(cwd.name)

    print(f"Building {name}...")
    build_result = subprocess.run(
        ["docker", "build", "-t", name, "."],
        cwd=cwd,
    )

    if build_result.returncode != 0:
        print("Error: Docker build failed.")
        return build_result.returncode

    print(f"\nStarting {name} with hot reload...")
    print(f"  API: http://localhost:{port}/runs")
    print(f"  UI:  http://localhost:{port}/")
    print("\nPress Ctrl+C to stop.\n")

    tool_py = cwd / "tool.py"
    env_file = cwd / ".env"

    run_cmd = [
        "docker",
        "run",
        "--rm",
        "-p",
        f"{port}:8080",
        "-e",
        "HOT_RELOAD=true",
        "-e",
        "WATCHFILES_FORCE_POLLING=true",
        "-v",
        f"{tool_py}:/app/tool.py",
        "-v",
        f"{env_file}:/app/.env",
        name,
    ]

    try:
        run_result = subprocess.run(run_cmd, cwd=cwd)
        return run_result.returncode
    except KeyboardInterrupt:
        print("\nStopping...")
        return 0

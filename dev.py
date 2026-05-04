#!/usr/bin/env python3
"""
Development script for GitHub Analytics Dashboard
Provides common development tasks and utilities.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], cwd: Path = None) -> int:
    """Run a command and return exit code."""
    try:
        result = subprocess.run(cmd, cwd=cwd or Path.cwd())
        return result.returncode
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 1


def run_tests(args):
    """Run tests with various options."""
    cmd = ["python", "-m", "pytest"]

    if args.verbose:
        cmd.append("-v")
    if args.coverage:
        cmd.extend(["--cov=.", "--cov-report=html"])
    if args.pattern:
        cmd.extend(["-k", args.pattern])

    cmd.append("tests/")

    return run_command(cmd)


def run_linting(args):
    """Run linting tools."""
    tools = []

    if args.black or args.all:
        tools.append(["black", "--check", "--diff", "."])

    if args.isort or args.all:
        tools.append(["isort", "--check-only", "--diff", "."])

    if args.flake8 or args.all:
        tools.append(["flake8", "."])

    if args.mypy or args.all:
        tools.append(["mypy", "."])

    success = True
    for tool in tools:
        print(f"Running: {' '.join(tool)}")
        if run_command(tool) != 0:
            success = False

    return 0 if success else 1


def format_code(args):
    """Format code with black and isort."""
    tools = [
        ["black", "."],
        ["isort", "."],
    ]

    success = True
    for tool in tools:
        print(f"Running: {' '.join(tool)}")
        if run_command(tool) != 0:
            success = False

    return 0 if success else 1


def run_app(args):
    """Run the Streamlit app."""
    cmd = ["streamlit", "run", "app.py"]
    if args.port:
        cmd.extend(["--server.port", str(args.port)])
    if args.address:
        cmd.extend(["--server.address", args.address])

    return run_command(cmd)


def install_deps(args):
    """Install dependencies."""
    cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
    return run_command(cmd)


def setup_dev(args):
    """Setup development environment."""
    print("Setting up development environment...")

    # Install dependencies
    if run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]) != 0:
        return 1

    # Install development dependencies
    dev_deps = [
        "black",
        "isort",
        "flake8",
        "mypy",
        "pytest",
        "pytest-cov",
        "pre-commit",
    ]

    if run_command([sys.executable, "-m", "pip", "install"] + dev_deps) != 0:
        return 1

    # Setup pre-commit
    if run_command(["pre-commit", "install"]) != 0:
        return 1

    print("Development environment setup complete!")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Development script for GitHub Analytics Dashboard")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    test_parser.add_argument("-c", "--coverage", action="store_true", help="Run with coverage")
    test_parser.add_argument("-k", "--pattern", help="Test pattern to run")
    test_parser.set_defaults(func=run_tests)

    # Lint command
    lint_parser = subparsers.add_parser("lint", help="Run linting tools")
    lint_parser.add_argument("--black", action="store_true", help="Run black")
    lint_parser.add_argument("--isort", action="store_true", help="Run isort")
    lint_parser.add_argument("--flake8", action="store_true", help="Run flake8")
    lint_parser.add_argument("--mypy", action="store_true", help="Run mypy")
    lint_parser.add_argument("-a", "--all", action="store_true", help="Run all linting tools")
    lint_parser.set_defaults(func=run_linting)

    # Format command
    format_parser = subparsers.add_parser("format", help="Format code")
    format_parser.set_defaults(func=format_code)

    # Run command
    run_parser = subparsers.add_parser("run", help="Run the Streamlit app")
    run_parser.add_argument("-p", "--port", type=int, help="Port to run on")
    run_parser.add_argument("-a", "--address", help="Address to bind to")
    run_parser.set_defaults(func=run_app)

    # Install command
    install_parser = subparsers.add_parser("install", help="Install dependencies")
    install_parser.set_defaults(func=install_deps)

    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Setup development environment")
    setup_parser.set_defaults(func=setup_dev)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
"""CLI wrapper to launch the Streamlit dashboard."""

import subprocess
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    script_path = Path(__file__).parent / "app.py"
    cmd = [sys.executable, "-m", "streamlit", "run", str(script_path)]
    cmd.extend(argv)
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())

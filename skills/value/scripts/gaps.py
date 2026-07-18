#!/usr/bin/env python3
"""List blocking hard gaps and optional soft gaps by section."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _session import hard_gaps_by_section, load_atoms, load_session, soft_gaps_by_section


def main() -> int:
    parser = argparse.ArgumentParser(description="Show value session gaps.")
    parser.add_argument("session", type=Path, help="Path to session.json")
    parser.add_argument(
        "--module",
        default="",
        help="Module slug to inspect (defaults to active module)",
    )
    args = parser.parse_args()

    if not args.session.is_file():
        print(f"Missing session: {args.session}", file=sys.stderr)
        return 1

    session = load_session(args.session)
    atoms = load_atoms()
    module = args.module or None
    print(
        json.dumps(
            {
                "hard_gaps": hard_gaps_by_section(session, atoms, module),
                "soft_gaps": soft_gaps_by_section(session, atoms, module),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

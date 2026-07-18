#!/usr/bin/env python3
"""Print one-line session ledger and position."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _session import format_status_line, load_session, recompute_ledger, save_session


def main() -> int:
    parser = argparse.ArgumentParser(description="Show value session status.")
    parser.add_argument("session", type=Path, help="Path to session.json")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Recompute ledger fields and write session.json",
    )
    args = parser.parse_args()

    if not args.session.is_file():
        print(f"Missing session: {args.session}", file=sys.stderr)
        return 1

    session = load_session(args.session)
    session["ledger"] = recompute_ledger(session)
    if args.refresh:
        save_session(args.session, session)
    print(format_status_line(session))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

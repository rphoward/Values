#!/usr/bin/env python3
"""Write IDE export pack from a value session (glossary, boundaries, UI, ADRs)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _session import (
    all_modules_ready,
    load_session,
    plan_build_pack,
    recompute_ledger,
    save_session,
    utc_now_iso,
    write_planned_files,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Write IDE export files from session.json."
    )
    parser.add_argument("session", type=Path, help="Path to session.json")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Write even when module gates are not all complete or bypassed",
    )
    args = parser.parse_args()

    if not args.session.is_file():
        print(f"Missing session: {args.session}", file=sys.stderr)
        return 1

    session = load_session(args.session)
    if not args.force and not all_modules_ready(session):
        print(
            "Not all modules are completed or bypassed; use --force to override.",
            file=sys.stderr,
        )
        return 1

    planned = plan_build_pack(session, args.session.parent)
    session["project"]["updated_at"] = utc_now_iso()
    session["ledger"] = recompute_ledger(session)
    save_session(args.session, session)
    written = write_planned_files(planned)
    for path in written:
        print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

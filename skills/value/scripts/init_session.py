#!/usr/bin/env python3
"""Create a new value-proposition session.json."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from _session import default_session, save_session

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PACING_CHOICES = ("standard", "express")


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a value proposition session.")
    parser.add_argument("--slug", required=True, help="Path-safe project slug")
    parser.add_argument("--name", required=True, help="Display name")
    parser.add_argument(
        "--root",
        default="workproduct/value-proposition",
        help="Workproduct root relative to cwd (default: workproduct/value-proposition)",
    )
    parser.add_argument(
        "--pacing-mode",
        default="standard",
        choices=PACING_CHOICES,
        help="Interview pacing (default: standard)",
    )
    args = parser.parse_args()

    if not SLUG_RE.fullmatch(args.slug):
        print(f"Invalid slug: {args.slug!r}", file=sys.stderr)
        return 1

    session_dir = Path(args.root) / args.slug
    session_path = session_dir / "session.json"
    if session_path.exists():
        print(f"Session already exists: {session_path}", file=sys.stderr)
        return 1

    session = default_session(args.slug, args.name, pacing_mode=args.pacing_mode)
    save_session(session_path, session)
    print(f"Created {session_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

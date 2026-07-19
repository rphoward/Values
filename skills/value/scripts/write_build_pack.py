#!/usr/bin/env python3
"""Write IDE export pack from a value session (glossary, boundaries, UI, ADRs)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _session import (
    BUILD_PACK_FILES,
    all_modules_ready,
    fill_build_pack_file,
    load_session,
    recompute_ledger,
    save_session,
    upsert_artifact,
    utc_now_iso,
    write_hard_decision_adrs,
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

    session_dir = args.session.parent
    written: list[str] = []
    for template_name, output_name in BUILD_PACK_FILES:
        output_path = session_dir / output_name
        content = fill_build_pack_file(session, template_name)
        output_path.write_text(content, encoding="utf-8")
        upsert_artifact(session, output_name, "final")
        written.append(str(output_path))

    for adr_path in write_hard_decision_adrs(session, session_dir):
        rel = adr_path.relative_to(session_dir).as_posix()
        upsert_artifact(session, rel, "final")
        written.append(str(adr_path))

    session["project"]["updated_at"] = utc_now_iso()
    session["ledger"] = recompute_ledger(session)
    save_session(args.session, session)
    for path in written:
        print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

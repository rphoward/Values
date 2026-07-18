#!/usr/bin/env python3
"""Write a module milestone artifact from accepted answers."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _session import (
    GATE_ARTIFACTS,
    fill_milestone_template,
    load_session,
    module_outcome,
    recompute_ledger,
    save_session,
    upsert_artifact,
    utc_now_iso,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Write module milestone artifact.")
    parser.add_argument("session", type=Path, help="Path to session.json")
    parser.add_argument(
        "--module",
        required=True,
        choices=["profile", "value-map", "business-model", "experiments"],
        help="Module whose milestone to write",
    )
    args = parser.parse_args()

    if not args.session.is_file():
        print(f"Missing session: {args.session}", file=sys.stderr)
        return 1

    session = load_session(args.session)
    artifact_name = GATE_ARTIFACTS[args.module]
    output_path = args.session.parent / artifact_name
    content = fill_milestone_template(session, args.module)
    output_path.write_text(content, encoding="utf-8")
    upsert_artifact(session, artifact_name, "final")
    session["project"]["updated_at"] = utc_now_iso()

    if session["position"]["module"] == args.module:
        session["position"]["status"] = "completed"

    session["ledger"] = recompute_ledger(session)
    save_session(args.session, session)
    print(f"Wrote {output_path} (module outcome={module_outcome(session, args.module)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

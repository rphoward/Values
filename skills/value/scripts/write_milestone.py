#!/usr/bin/env python3
"""Write a module milestone artifact from accepted answers."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _session import (
    GATE_ARTIFACTS,
    advance_after_gate_milestone,
    fill_milestone_template,
    load_session,
    module_gate_passed,
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
    parser.add_argument(
        "--force",
        action="store_true",
        help="Write milestone even when gate_pending or pass decision is missing",
    )
    args = parser.parse_args()

    if not args.session.is_file():
        print(f"Missing session: {args.session}", file=sys.stderr)
        return 1

    session = load_session(args.session)
    position = session["position"]
    if not args.force:
        if position["module"] != args.module or position["status"] != "gate_pending":
            print(
                f"Module {args.module!r} is not gate_pending "
                f"(position={position}); use --force to override.",
                file=sys.stderr,
            )
            return 1
        if not module_gate_passed(session, args.module):
            print(
                f"Module {args.module!r} has no canonical pass decision; "
                "use --force to override.",
                file=sys.stderr,
            )
            return 1

    artifact_name = GATE_ARTIFACTS[args.module]
    output_path = args.session.parent / artifact_name
    content = fill_milestone_template(session, args.module)
    output_path.write_text(content, encoding="utf-8")
    upsert_artifact(session, artifact_name, "final")
    session["project"]["updated_at"] = utc_now_iso()
    advance_after_gate_milestone(session, args.module)
    session["ledger"] = recompute_ledger(session)
    save_session(args.session, session)
    print(f"Wrote {output_path} (module outcome={module_outcome(session, args.module)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

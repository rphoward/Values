#!/usr/bin/env python3
"""Write a module milestone artifact from accepted answers."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _session import (
    GATE_ARTIFACTS,
    advance_after_gate_milestone,
    artifact_status,
    fill_milestone_template,
    load_session,
    module_gate_passed,
    module_outcome,
    plan_build_pack,
    recompute_ledger,
    save_session,
    upsert_artifact,
    utc_now_iso,
    write_planned_files,
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
    artifact_name = GATE_ARTIFACTS[args.module]
    output_path = args.session.parent / artifact_name
    recovering_missing_file = (
        module_gate_passed(session, args.module)
        and artifact_status(session, artifact_name) == "final"
        and not output_path.is_file()
    )
    if not args.force and not recovering_missing_file:
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

    content = fill_milestone_template(session, args.module)
    upsert_artifact(session, artifact_name, "final")
    session["project"]["updated_at"] = utc_now_iso()
    if not recovering_missing_file:
        advance_after_gate_milestone(session, args.module)
    # Commit session before disk exports so a crash cannot leave
    # gate_pending with "final" files already written.
    planned = [(output_path, content), *plan_build_pack(session, args.session.parent)]
    session["ledger"] = recompute_ledger(session)
    save_session(args.session, session)
    for path in write_planned_files(planned):
        print(f"Wrote {path}")
    print(f"Wrote {output_path} (module outcome={module_outcome(session, args.module)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

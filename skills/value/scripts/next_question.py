#!/usr/bin/env python3
"""Emit the next focus atom question from the DAG scheduler."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _session import (
    GATE_ATOMS,
    all_modules_ready,
    load_atoms,
    load_session,
    match_board_for_atom,
    module_outcome,
    pacing_mode,
    schedule_next_atom,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Next value session question.")
    parser.add_argument("session", type=Path, help="Path to session.json")
    parser.add_argument(
        "--gaps",
        action="store_true",
        help="Emit hard gaps by section instead of the next question",
    )
    args = parser.parse_args()

    if not args.session.is_file():
        print(f"Missing session: {args.session}", file=sys.stderr)
        return 1

    session = load_session(args.session)
    atoms = load_atoms()
    if args.gaps:
        from _session import hard_gaps_by_section, soft_gaps_by_section

        print(
            json.dumps(
                {
                    "hard_gaps": hard_gaps_by_section(session, atoms),
                    "soft_gaps": soft_gaps_by_section(session, atoms),
                },
                indent=2,
            )
        )
        return 0

    if all_modules_ready(session):
        print(json.dumps({"done": True, "message": "All modules completed or bypassed."}))
        return 0

    atom = schedule_next_atom(session, atoms)
    if atom is None:
        print(
            json.dumps(
                {
                    "done": True,
                    "message": "No unsatisfied atoms remain, but module gates are not all complete or bypassed.",
                }
            )
        )
        return 0

    gate_due = atom["id"] in GATE_ATOMS and module_outcome(
        session, GATE_ATOMS[atom["id"]]
    ) == "pending"
    position = session["position"]
    payload = {
        "atom_id": atom["id"],
        "module": atom["module"],
        "section": atom.get("section"),
        "asks": atom["asks"],
        "accepts_summary": atom["accepts_summary"],
        "soft": atom.get("soft", False),
        "gate": atom.get("gate", False),
        "gate_due": gate_due,
        "pacing_mode": pacing_mode(session),
        "position_status": position["status"],
    }
    board = match_board_for_atom(session, atom["id"])
    if board is not None:
        payload["match_board"] = {
            "parts": board["parts"],
            "targets": board["targets"],
            "part_labels": board["part_labels"],
            "target_labels": board["target_labels"],
            "target_atom": board["target_atom"],
            "target_name": board["target_name"],
        }
        payload["match_prompt"] = board["match_prompt"]
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

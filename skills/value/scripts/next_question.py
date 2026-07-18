#!/usr/bin/env python3
"""Emit the next unsatisfied atom question."""

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
    module_outcome,
    next_unsatisfied_atom,
    recompute_ledger,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Next value session question.")
    parser.add_argument("session", type=Path, help="Path to session.json")
    args = parser.parse_args()

    if not args.session.is_file():
        print(f"Missing session: {args.session}", file=sys.stderr)
        return 1

    session = load_session(args.session)
    atoms = load_atoms()
    if all_modules_ready(session):
        print(json.dumps({"done": True, "message": "All modules completed or bypassed."}))
        return 0

    atom = next_unsatisfied_atom(session, atoms)
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
        "asks": atom["asks"],
        "accepts_summary": atom["accepts_summary"],
        "gate": atom.get("gate", False),
        "gate_due": gate_due,
        "position_atom_id": position["atom_id"],
        "position_status": position["status"],
        "ledger": recompute_ledger(session),
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

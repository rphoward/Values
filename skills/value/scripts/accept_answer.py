#!/usr/bin/env python3
"""Append an accepted answer and advance session position."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _session import (
    GATE_ARTIFACTS,
    GATE_ATOMS,
    append_session_records,
    atom_by_id,
    atom_module,
    load_atoms,
    load_session,
    recompute_ledger,
    save_session,
    upsert_artifact,
    utc_now_iso,
)


def load_records(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("--records file must contain a JSON object")
    return payload


def position_from_records(payload: dict) -> dict | None:
    decisions = payload.get("decisions", [])
    if not decisions:
        return None
    last = decisions[-1]
    required = ("resulting_module", "resulting_atom", "resulting_status")
    if all(field in last for field in required):
        return last
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Accept a value session answer.")
    parser.add_argument("session", type=Path, help="Path to session.json")
    parser.add_argument("--atom-id", required=True, help="Atom identifier")
    parser.add_argument("--answer", required=True, help="Accepted answer text")
    parser.add_argument(
        "--kind",
        required=True,
        choices=["fact", "inference", "hypothesis", "decision", "unknown"],
        help="Evidence kind",
    )
    parser.add_argument(
        "--records",
        type=Path,
        default=None,
        help="Optional JSON sidecar with evidence, assumptions, decisions, unknowns, artifacts arrays",
    )
    parser.add_argument(
        "--reopen",
        action="store_true",
        help="Supersede an existing answer for this atom",
    )
    parser.add_argument(
        "--conflict-note",
        default="",
        help="Reason for reopening a prior answer",
    )
    parser.add_argument(
        "--stay",
        action="store_true",
        help="Keep current atom active (blocking unknown)",
    )
    parser.add_argument(
        "--gate-pending",
        action="store_true",
        help="Set position status gate_pending after gate atom pass",
    )
    parser.add_argument(
        "--next-atom",
        default="",
        help="Override next atom id (reopen target or conditional unlock)",
    )
    args = parser.parse_args()

    if not args.session.is_file():
        print(f"Missing session: {args.session}", file=sys.stderr)
        return 1

    session = load_session(args.session)
    atoms = load_atoms()
    index = atom_by_id(atoms)
    atom = index.get(args.atom_id)
    if atom is None:
        print(f"Unknown atom: {args.atom_id}", file=sys.stderr)
        return 1

    existing = [
        record
        for record in session.get("answers", [])
        if record["atom_id"] == args.atom_id
    ]
    if existing and not args.reopen:
        print(
            f"Atom {args.atom_id} already answered; use --reopen to supersede.",
            file=sys.stderr,
        )
        return 1
    if args.reopen and not args.conflict_note:
        print("--conflict-note is required with --reopen", file=sys.stderr)
        return 1

    accepted_at = utc_now_iso()
    record = {
        "atom_id": args.atom_id,
        "answer": args.answer,
        "kind": args.kind,
        "accepted_at": accepted_at,
    }
    if args.reopen:
        record["reopen"] = True
        record["conflict_note"] = args.conflict_note
    session["answers"].append(record)
    session["project"]["updated_at"] = accepted_at

    records_payload: dict | None = None
    if args.records is not None:
        if not args.records.is_file():
            print(f"Missing records file: {args.records}", file=sys.stderr)
            return 1
        try:
            records_payload = load_records(args.records)
            append_session_records(
                session,
                records_payload,
                default_source_atom=args.atom_id,
            )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1

    if args.stay:
        session["position"]["module"] = atom["module"]
        session["position"]["atom_id"] = args.atom_id
        session["position"]["status"] = "in_progress"
    else:
        next_atom = args.next_atom or atom.get("unlocks")
        position_override = (
            position_from_records(records_payload) if records_payload else None
        )
        if args.gate_pending and args.atom_id in GATE_ATOMS:
            session["position"]["module"] = atom["module"]
            session["position"]["atom_id"] = args.atom_id
            session["position"]["status"] = "gate_pending"
            upsert_artifact(session, GATE_ARTIFACTS[atom["module"]], "pending")
        elif args.next_atom:
            session["position"]["module"] = atom_module(next_atom)
            session["position"]["atom_id"] = next_atom
            session["position"]["status"] = "in_progress"
        elif position_override is not None:
            session["position"]["module"] = position_override["resulting_module"]
            session["position"]["atom_id"] = position_override["resulting_atom"]
            session["position"]["status"] = position_override["resulting_status"]
        elif next_atom:
            session["position"]["module"] = atom_module(next_atom)
            session["position"]["atom_id"] = next_atom
            session["position"]["status"] = "in_progress"
        else:
            session["position"]["status"] = "completed"

    session["ledger"] = recompute_ledger(session)
    save_session(args.session, session)
    print(f"Accepted {args.atom_id}; position={session['position']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

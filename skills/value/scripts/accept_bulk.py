#!/usr/bin/env python3
"""Accept multiple mapped answers from a draft map JSON file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _session import (
    append_session_records,
    load_atoms,
    load_session,
    ready_atoms,
    recompute_ledger,
    save_session,
    set_position_to_focus,
    utc_now_iso,
)
from map_gaps import validate_draft_map


def main() -> int:
    parser = argparse.ArgumentParser(description="Bulk accept mapped answers.")
    parser.add_argument("session", type=Path, help="Path to session.json")
    parser.add_argument(
        "--map",
        type=Path,
        required=True,
        help="Draft map JSON file",
    )
    args = parser.parse_args()

    if not args.session.is_file():
        print(f"Missing session: {args.session}", file=sys.stderr)
        return 1
    if not args.map.is_file():
        print(f"Missing draft map: {args.map}", file=sys.stderr)
        return 1

    session = load_session(args.session)
    atoms = load_atoms()
    try:
        payload = json.loads(args.map.read_text(encoding="utf-8"))
        mappings = validate_draft_map(payload)
    except (json.JSONDecodeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    ready = set(ready_atoms(session, atoms))
    accepted: list[str] = []
    skipped: list[str] = []
    for item in mappings:
        atom_id = str(item["atom_id"])
        if not item.get("satisfied", True):
            skipped.append(atom_id)
            continue
        ready = set(ready_atoms(session, atoms))
        if atom_id not in ready:
            print(f"Atom {atom_id} is not ready; refusing bulk accept.", file=sys.stderr)
            return 1
        if any(record["atom_id"] == atom_id for record in session.get("answers", [])):
            skipped.append(atom_id)
            continue
        answer = str(item.get("answer", "")).strip()
        if not answer:
            print(f"Mapping for {atom_id} missing answer text.", file=sys.stderr)
            return 1
        kind = str(item.get("kind", "inference"))
        accepted_at = utc_now_iso()
        session["answers"].append(
            {
                "atom_id": atom_id,
                "answer": answer,
                "kind": kind,
                "accepted_at": accepted_at,
            }
        )
        sidecar: dict[str, list] = {}
        if item.get("gaps"):
            sidecar["unknowns"] = [
                {
                    "question": gap,
                    "blocking": False,
                }
                for gap in item["gaps"]
            ]
        if sidecar:
            append_session_records(
                session,
                sidecar,
                default_source_atom=atom_id,
            )
        accepted.append(atom_id)

    session["project"]["updated_at"] = utc_now_iso()
    set_position_to_focus(session, atoms)
    session["ledger"] = recompute_ledger(session)
    save_session(args.session, session)
    print(
        json.dumps(
            {
                "accepted": accepted,
                "skipped": skipped,
                "position": session["position"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

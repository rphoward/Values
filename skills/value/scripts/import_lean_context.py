#!/usr/bin/env python3
"""Import accepted answers from a lean-mvp session into value-proposition."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _session import (
    answered_atom_ids,
    atom_by_id,
    atom_requires,
    default_lean_mvp_workproduct_root,
    load_atoms,
    load_json,
    load_session,
    recompute_ledger,
    save_session,
    schedule_next_atom,
    utc_now_iso,
)

SKILL_ROOT = Path(__file__).resolve().parent.parent
BRIDGE_PATH = SKILL_ROOT / "assets" / "lean-bridge-map.json"


def latest_answer_by_atom(session: dict) -> dict[str, dict]:
    latest: dict[str, dict] = {}
    for record in session.get("answers", []):
        atom_id = record["atom_id"]
        prior = latest.get(atom_id)
        if prior is None or record["accepted_at"] >= prior["accepted_at"]:
            latest[atom_id] = record
    return latest


def value_answer_exists(session: dict, atom_id: str) -> bool:
    return any(record["atom_id"] == atom_id for record in session.get("answers", []))


def import_from_lean(
    value_session: dict,
    lean_session: dict,
    bridge: dict,
    atoms: list[dict],
) -> tuple[dict, list[str]]:
    atom_map: dict[str, str] = bridge.get("atom_map", {})
    lean_answers = latest_answer_by_atom(lean_session)
    imported: list[str] = []
    timestamp = utc_now_iso()
    index = atom_by_id(atoms)
    pending: list[tuple[str, str, dict]] = []

    for lean_atom_id, value_atom_id in atom_map.items():
        if value_atom_id not in index:
            continue
        if value_answer_exists(value_session, value_atom_id):
            continue
        source = lean_answers.get(lean_atom_id)
        if source is None:
            continue
        pending.append((lean_atom_id, value_atom_id, source))

    changed = True
    while changed and pending:
        changed = False
        answered = answered_atom_ids(value_session)
        still_pending: list[tuple[str, str, dict]] = []
        for lean_atom_id, value_atom_id, source in pending:
            atom = index[value_atom_id]
            if not all(req in answered for req in atom_requires(atom)):
                still_pending.append((lean_atom_id, value_atom_id, source))
                continue
            value_session["answers"].append(
                {
                    "atom_id": value_atom_id,
                    "answer": source["answer"],
                    "kind": source.get("kind", "fact"),
                    "accepted_at": timestamp,
                    "provenance": "lean-import",
                    "source_atom": lean_atom_id,
                }
            )
            imported.append(value_atom_id)
            answered.add(value_atom_id)
            changed = True
        pending = still_pending

    if imported:
        value_session["project"]["updated_at"] = timestamp
        value_session["lean_import"] = {
            "source_session": bridge.get("_resolved_lean_session", ""),
            "imported_at": timestamp,
            "mapped_atoms": sorted(set(imported)),
        }
        next_atom = schedule_next_atom(value_session, atoms)
        if next_atom is not None:
            value_session["position"] = {
                "module": next_atom["module"],
                "atom_id": next_atom["id"],
                "status": "in_progress",
            }
        value_session["ledger"] = recompute_ledger(value_session)

    return value_session, imported


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import lean-mvp session answers into value-proposition."
    )
    parser.add_argument("session", type=Path, help="Path to value session.json")
    parser.add_argument(
        "--lean-root",
        default=None,
        help=(
            "Lean workproduct root (default: <repo>/workproduct/lean-mvp when detectable)"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print import plan without writing session.json",
    )
    args = parser.parse_args()

    if not args.session.is_file():
        print(f"Missing session: {args.session}", file=sys.stderr)
        return 1
    if not BRIDGE_PATH.is_file():
        print(f"Missing bridge map: {BRIDGE_PATH}", file=sys.stderr)
        return 1

    bridge = load_json(BRIDGE_PATH)
    value_session = load_session(args.session)
    slug = value_session["project"]["slug"]
    lean_root = (
        Path(args.lean_root)
        if args.lean_root
        else default_lean_mvp_workproduct_root()
    )
    lean_path = lean_root / slug / "session.json"
    bridge["_resolved_lean_session"] = str(lean_path).replace("\\", "/")

    if not lean_path.is_file():
        print(json.dumps({"imported": [], "reason": "no lean session"}))
        return 0

    lean_session = load_session(lean_path)
    atoms = load_atoms()
    updated, imported = import_from_lean(value_session, lean_session, bridge, atoms)

    payload = {"imported": imported, "path": str(lean_path)}
    if args.dry_run:
        print(json.dumps(payload))
        return 0

    if imported:
        save_session(args.session, updated)
    print(json.dumps(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

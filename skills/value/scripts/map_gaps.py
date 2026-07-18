#!/usr/bin/env python3
"""Dry-run a draft map against session readiness (no writes)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _session import atom_by_id, load_atoms, load_session, ready_atoms


def validate_draft_map(payload: dict) -> list[dict[str, object]]:
    if not isinstance(payload, dict):
        raise ValueError("Draft map must be a JSON object")
    mappings = payload.get("mappings")
    if not isinstance(mappings, list):
        raise ValueError("Draft map requires a mappings array")

    atoms = load_atoms()
    index = atom_by_id(atoms)
    results: list[dict[str, object]] = []
    for item in mappings:
        if not isinstance(item, dict):
            raise ValueError("Each mapping must be an object")
        atom_id = item.get("atom_id")
        if atom_id not in index:
            raise ValueError(f"Unknown atom_id: {atom_id!r}")
        kind = item.get("kind", "inference")
        if kind not in {"fact", "inference", "hypothesis", "decision", "unknown"}:
            raise ValueError(f"Invalid kind for {atom_id}: {kind!r}")
        satisfied = bool(item.get("satisfied", True))
        results.append(
            {
                "atom_id": atom_id,
                "answer": item.get("answer", ""),
                "section": index[atom_id].get("section"),
                "soft": index[atom_id].get("soft", False),
                "kind": kind,
                "satisfied": satisfied,
                "gaps": item.get("gaps", []),
            }
        )
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a draft map without writing.")
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
    report = []
    for item in mappings:
        atom_id = str(item["atom_id"])
        report.append(
            {
                **item,
                "ready": atom_id in ready,
                "would_accept": atom_id in ready and item["satisfied"],
            }
        )
    print(json.dumps({"source": payload.get("source"), "mappings": report}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Set session pacing_mode to standard or express."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _session import PACING_MODES, load_session, recompute_ledger, save_session, set_position_to_focus, load_atoms, utc_now_iso


def main() -> int:
    parser = argparse.ArgumentParser(description="Set value session pacing mode.")
    parser.add_argument("session", type=Path, help="Path to session.json")
    parser.add_argument(
        "--mode",
        required=True,
        choices=PACING_MODES,
        help="Pacing mode",
    )
    args = parser.parse_args()

    if not args.session.is_file():
        print(f"Missing session: {args.session}", file=sys.stderr)
        return 1

    session = load_session(args.session)
    if args.mode == "standard":
        session.pop("pacing_mode", None)
    else:
        session["pacing_mode"] = args.mode
    session["project"]["updated_at"] = utc_now_iso()
    atoms = load_atoms()
    set_position_to_focus(session, atoms)
    session["ledger"] = recompute_ledger(session)
    save_session(args.session, session)
    print(f"Set pacing_mode={args.mode}; position={session['position']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

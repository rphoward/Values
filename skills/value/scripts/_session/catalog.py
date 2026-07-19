"""Asset paths, atom indexes, and atomic session I/O."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .constants import MODULE_ORDER, SLUG_RE

SKILL_ROOT = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = SKILL_ROOT / "assets"

_atom_indexes_built = False
GATE_ATOMS: dict[str, str] = {}
MODULE_ATOMS: dict[str, tuple[str, ...]] = {}
ATOM_MODULE_BY_ID: dict[str, str] = {}
REVERSE_UNLOCKS: dict[str, list[str]] = {}


def reset_atom_indexes() -> None:
    """Clear cached atom indexes (tests reload between cases)."""
    global _atom_indexes_built
    _atom_indexes_built = False
    GATE_ATOMS.clear()
    MODULE_ATOMS.clear()
    ATOM_MODULE_BY_ID.clear()
    REVERSE_UNLOCKS.clear()


def utc_now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_atoms() -> list[dict[str, Any]]:
    payload = load_json(ASSETS_DIR / "atoms.json")
    return payload["atoms"]


def load_section_map() -> dict[str, Any]:
    return load_json(ASSETS_DIR / "section-map.json")


def _build_atom_indexes() -> None:
    global _atom_indexes_built
    if _atom_indexes_built:
        return
    module_atoms: dict[str, list[str]] = {module: [] for module in MODULE_ORDER}
    gate_atoms: dict[str, str] = {}
    atom_module_by_id: dict[str, str] = {}
    reverse_unlocks: dict[str, list[str]] = {}
    for atom in load_atoms():
        atom_id = atom["id"]
        module = atom["module"]
        module_atoms[module].append(atom_id)
        atom_module_by_id[atom_id] = module
        unlocks = atom.get("unlocks")
        if unlocks:
            reverse_unlocks.setdefault(unlocks, []).append(atom_id)
        if atom.get("gate"):
            gate_atoms[atom_id] = module
    GATE_ATOMS.clear()
    GATE_ATOMS.update(gate_atoms)
    MODULE_ATOMS.clear()
    MODULE_ATOMS.update({module: tuple(ids) for module, ids in module_atoms.items()})
    ATOM_MODULE_BY_ID.clear()
    ATOM_MODULE_BY_ID.update(atom_module_by_id)
    REVERSE_UNLOCKS.clear()
    REVERSE_UNLOCKS.update(reverse_unlocks)
    _atom_indexes_built = True


def atom_by_id(atoms: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {atom["id"]: atom for atom in atoms}


def atom_module(atom_id: str) -> str:
    _build_atom_indexes()
    if atom_id not in ATOM_MODULE_BY_ID:
        raise KeyError(f"Unknown atom id: {atom_id!r}")
    return ATOM_MODULE_BY_ID[atom_id]


def migrate_session_if_needed(session: dict[str, Any]) -> None:
    if session.get("schema_version") == "1.0":
        session["schema_version"] = "1.1"


def load_session(path: Path) -> dict[str, Any]:
    session = load_json(path)
    migrate_session_if_needed(session)
    return session


def save_session(path: Path, session: dict[str, Any]) -> None:
    """Atomically write session.json via temp file + replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(session, indent=2) + "\n"
    tmp_path = path.with_name(path.name + ".tmp")
    tmp_path.write_text(payload, encoding="utf-8")
    tmp_path.replace(path)


def derive_slug_from_name(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    slug = re.sub(r"-+", "-", slug)
    if not slug or not SLUG_RE.fullmatch(slug):
        raise ValueError(f"Cannot derive path-safe slug from name: {name!r}")
    return slug

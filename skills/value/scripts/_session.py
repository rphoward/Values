"""Shared session helpers for the value skill scripts (stdlib only)."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = SKILL_ROOT / "assets"

MODULE_ORDER = ("profile", "value-map", "business-model", "experiments")
MODULE_PHASE = {
    "profile": "Canvas",
    "value-map": "Design",
    "business-model": "Evolve",
    "experiments": "Test",
}
GATE_ARTIFACTS = {
    "profile": "customer-profile.md",
    "value-map": "value-map.md",
    "business-model": "business-model.md",
    "experiments": "experiment-plan.md",
}
MILESTONE_TEMPLATES = {
    "profile": "customer-profile.template.md",
    "value-map": "value-map.template.md",
    "business-model": "business-model.template.md",
    "experiments": "experiment-plan.template.md",
}
DESIGN_BRIEFS = (
    ("product-design-brief.template.md", "product-design-brief.md"),
    ("ux-brief.template.md", "ux-brief.md"),
    ("app-design-brief.template.md", "app-design-brief.md"),
)
CANONICAL_GATE_PASS = {
    "profile": "pass profile gate",
    "value-map": "pass value-map gate",
    "business-model": "pass business-model gate",
    "experiments": "pass experiments gate",
}
EXPRESS_SPINE: dict[str, tuple[str, ...]] = {
    "profile": ("P01", "P03", "P11", "P12"),
    "value-map": ("V01", "V08"),
    "business-model": ("B01", "B08"),
    "experiments": ("E01", "E03", "E10"),
}
EXPRESS_REQUIRES: dict[str, tuple[str, ...]] = {
    "P03": ("P01",),
    "P11": ("P03",),
    "P12": ("P11",),
    "V08": ("V01",),
    "B08": ("B01",),
    "E03": ("E01",),
    "E10": ("E01", "E03"),
}
PACING_MODES = ("standard", "express")

_atom_indexes_built = False
GATE_ATOMS: dict[str, str] = {}
MODULE_ATOMS: dict[str, tuple[str, ...]] = {}
ATOM_MODULE_BY_ID: dict[str, str] = {}
REVERSE_UNLOCKS: dict[str, list[str]] = {}
SECTION_STRIP_SYMBOLS = {
    "empty": "·",
    "partial": "◐",
    "satisfied": "✓",
    "unknown_ok": "✓?",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_atoms() -> list[dict[str, Any]]:
    payload = load_json(ASSETS_DIR / "atoms.json")
    return payload["atoms"]


def load_section_map() -> dict[str, Any]:
    return load_json(ASSETS_DIR / "section-map.json")


def _build_atom_indexes() -> None:
    global _atom_indexes_built, GATE_ATOMS, MODULE_ATOMS, ATOM_MODULE_BY_ID, REVERSE_UNLOCKS
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
    GATE_ATOMS = gate_atoms
    MODULE_ATOMS = {module: tuple(ids) for module, ids in module_atoms.items()}
    ATOM_MODULE_BY_ID = atom_module_by_id
    REVERSE_UNLOCKS = reverse_unlocks
    _atom_indexes_built = True


def atom_by_id(atoms: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {atom["id"]: atom for atom in atoms}


def migrate_session_if_needed(session: dict[str, Any]) -> None:
    if session.get("schema_version") == "1.0":
        session["schema_version"] = "1.1"


def load_session(path: Path) -> dict[str, Any]:
    session = load_json(path)
    migrate_session_if_needed(session)
    return session


def save_session(path: Path, session: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(session, indent=2) + "\n", encoding="utf-8")


def default_session(slug: str, name: str, *, pacing_mode: str = "standard") -> dict[str, Any]:
    _build_atom_indexes()
    if pacing_mode not in PACING_MODES:
        raise ValueError(f"Invalid pacing_mode: {pacing_mode!r}")
    timestamp = utc_now_iso()
    session = {
        "schema_version": "1.1",
        "project": {
            "slug": slug,
            "name": name,
            "created_at": timestamp,
            "updated_at": timestamp,
        },
        "position": {
            "module": "profile",
            "atom_id": "P01",
            "status": "in_progress",
        },
        "answers": [],
        "evidence": [],
        "assumptions": [],
        "decisions": [],
        "unknowns": [],
        "artifacts": [],
    }
    if pacing_mode != "standard":
        session["pacing_mode"] = pacing_mode
    session["ledger"] = recompute_ledger(session)
    return session


def pacing_mode(session: dict[str, Any]) -> str:
    mode = session.get("pacing_mode", "standard")
    if mode not in PACING_MODES:
        return "standard"
    return mode


def express_spine_for_module(module: str) -> tuple[str, ...]:
    return EXPRESS_SPINE.get(module, ())


def atom_in_express_spine(atom_id: str) -> bool:
    module = atom_module(atom_id)
    return atom_id in express_spine_for_module(module)


def effective_requires(session: dict[str, Any], atom: dict[str, Any]) -> list[str]:
    if pacing_mode(session) != "express":
        return atom_requires(atom)
    express = EXPRESS_REQUIRES.get(atom["id"])
    if express is not None:
        return list(express)
    return atom_requires(atom)


def schedulable_atom_ids(session: dict[str, Any], atoms: list[dict[str, Any]]) -> set[str]:
    if pacing_mode(session) != "express":
        return {atom["id"] for atom in atoms}
    schedulable: set[str] = set()
    for module in MODULE_ORDER:
        if module_bypassed(session, module):
            continue
        schedulable.update(express_spine_for_module(module))
    return schedulable


def current_answer(session: dict[str, Any], atom_id: str) -> dict[str, Any] | None:
    latest: dict[str, Any] | None = None
    for record in session.get("answers", []):
        if record["atom_id"] != atom_id:
            continue
        if latest is None or record["accepted_at"] >= latest["accepted_at"]:
            latest = record
    return latest


def answered_atom_ids(session: dict[str, Any]) -> set[str]:
    return {record["atom_id"] for record in session.get("answers", [])}


def latest_decision(session: dict[str, Any]) -> dict[str, Any] | None:
    decisions = session.get("decisions", [])
    if not decisions:
        return None
    return decisions[-1]


def gate_atom_for_module(module: str) -> str:
    _build_atom_indexes()
    for atom_id, atom_module in GATE_ATOMS.items():
        if atom_module == module:
            return atom_id
    raise KeyError(f"No gate atom for module {module!r}")


def canonical_gate_pass_text(module: str) -> str:
    return CANONICAL_GATE_PASS[module]


def is_canonical_bypass_decision(text: str) -> bool:
    lowered = text.lower().strip()
    return "bypass" in lowered and " gate" in lowered


def records_allow_off_position(records_payload: dict[str, Any] | None) -> bool:
    if not records_payload:
        return False
    for decision in records_payload.get("decisions", []):
        if is_canonical_bypass_decision(decision.get("decision", "")):
            return True
    return False


def off_position_accept_hint(active_atom_id: str) -> str:
    return (
        f"Atom is not in the ready set (focus={active_atom_id}). "
        "Accept only ready atoms, or use --reopen --conflict-note, --stay, "
        "or --records with a bypass gate decision."
    )


def can_accept_atom(
    session: dict[str, Any],
    atom_id: str,
    *,
    reopen: bool,
    stay: bool,
    records_payload: dict[str, Any] | None,
) -> tuple[bool, str | None]:
    if reopen or stay:
        return True, None
    if atom_id == session["position"]["atom_id"]:
        return True, None
    if records_allow_off_position(records_payload):
        return True, None
    atoms = load_atoms()
    if atom_id in ready_atoms(session, atoms):
        return True, None
    return False, off_position_accept_hint(session["position"]["atom_id"])


def module_bypassed(session: dict[str, Any], module: str) -> bool:
    needle = f"bypass {module} gate"
    for decision in reversed(session.get("decisions", [])):
        if needle in decision.get("decision", "").lower():
            return True
    return False


def module_gate_passed(session: dict[str, Any], module: str) -> bool:
    _build_atom_indexes()
    gate_atom = gate_atom_for_module(module)
    canonical = canonical_gate_pass_text(module)
    for decision in reversed(session.get("decisions", [])):
        text = decision.get("decision", "").lower().strip()
        if f"bypass {module} gate" in text:
            return False
        if decision.get("source_atom") == gate_atom and text == canonical:
            return True
    return False


def artifact_status(session: dict[str, Any], path: str) -> str | None:
    latest: dict[str, Any] | None = None
    for record in session.get("artifacts", []):
        if record["path"] != path:
            continue
        latest = record
    return latest["status"] if latest else None


def module_outcome(session: dict[str, Any], module: str) -> str:
    if module_bypassed(session, module):
        return "bypassed"
    artifact = GATE_ARTIFACTS[module]
    if module_gate_passed(session, module) and artifact_status(session, artifact) == "final":
        return "completed"
    return "pending"


def effective_answered_atoms(session: dict[str, Any], atoms: list[dict[str, Any]]) -> set[str]:
    _build_atom_indexes()
    answered = answered_atom_ids(session)
    for module in MODULE_ORDER:
        if module_outcome(session, module) != "bypassed":
            continue
        answered.update(MODULE_ATOMS[module])
    return answered


def completion_pct(session: dict[str, Any], atoms: list[dict[str, Any]]) -> int:
    answered = effective_answered_atoms(session, atoms)
    if pacing_mode(session) == "express":
        spine = schedulable_atom_ids(session, atoms)
        total = len(spine)
        if total == 0:
            return 0
        return int(round(len(answered & spine) / total * 100))
    total = len(atoms)
    if total == 0:
        return 0
    return int(round(len(answered) / total * 100))


def unvalidated_bombs(session: dict[str, Any]) -> list[str]:
    bombs: list[str] = []
    for assumption in session.get("assumptions", []):
        if assumption.get("criticality") != "high":
            continue
        if assumption.get("evidence_status") in {"supported", "partial"}:
            continue
        claim = assumption.get("claim", "").strip()
        if claim:
            bombs.append(claim)
    return bombs


def validation_milestone(session: dict[str, Any]) -> str:
    outcomes = {module: module_outcome(session, module) for module in MODULE_ORDER}
    if all(outcomes[module] in {"completed", "bypassed"} for module in MODULE_ORDER):
        return "Validation Complete"
    if outcomes["business-model"] in {"completed", "bypassed"}:
        return "Business Model Fit"
    if outcomes["value-map"] in {"completed", "bypassed"}:
        return "Product-Market Fit"
    if outcomes["profile"] in {"completed", "bypassed"}:
        return "Problem-Solution Fit"
    return "None"


def active_phase(session: dict[str, Any]) -> str:
    position = session["position"]
    if position.get("module") == "experiments" and module_outcome(session, "experiments") in {
        "completed",
        "bypassed",
    }:
        return "Complete"
    return MODULE_PHASE.get(position["module"], "Canvas")


def recompute_ledger(session: dict[str, Any]) -> dict[str, Any]:
    atoms = load_atoms()
    position = session["position"]
    active_module = position["module"]
    if module_outcome(session, "experiments") in {"completed", "bypassed"}:
        active_module = "none"
    return {
        "phase": active_phase(session),
        "active_module": active_module,
        "completion_pct": completion_pct(session, atoms),
        "validation_milestone": validation_milestone(session),
        "unvalidated_bombs": unvalidated_bombs(session),
    }


def format_status_line(session: dict[str, Any]) -> str:
    ledger = session.get("ledger") or recompute_ledger(session)
    position = session["position"]
    answered = sorted(effective_answered_atoms(session, load_atoms()))
    bombs = ledger["unvalidated_bombs"]
    bomb_text = "; ".join(bombs[:3]) if bombs else "none"
    if len(bombs) > 3:
        bomb_text += f" (+{len(bombs) - 3} more)"
    return (
        f"Ledger: phase={ledger['phase']} module={ledger['active_module']} "
        f"atom={position['atom_id']} status={position['status']} "
        f"pacing={pacing_mode(session)} "
        f"completion={ledger['completion_pct']}% "
        f"milestone={ledger['validation_milestone']} "
        f"answered={','.join(answered) or 'none'} "
        f"bombs={bomb_text}"
    )


def atom_requires(atom: dict[str, Any]) -> list[str]:
    if "requires" in atom:
        return list(atom["requires"])
    _build_atom_indexes()
    return list(REVERSE_UNLOCKS.get(atom["id"], []))


def build_dag(atoms: list[dict[str, Any]]) -> dict[str, list[str]]:
    return {atom["id"]: atom_requires(atom) for atom in atoms}


def detect_dag_cycles(atoms: list[dict[str, Any]]) -> list[str]:
    graph = build_dag(atoms)
    visiting: set[str] = set()
    visited: set[str] = set()
    cycles: list[str] = []

    def visit(node: str, stack: list[str]) -> None:
        if node in visiting:
            cycles.append(" -> ".join(stack + [node]))
            return
        if node in visited:
            return
        visiting.add(node)
        for neighbor in graph.get(node, []):
            visit(neighbor, stack + [node])
        visiting.remove(node)
        visited.add(node)

    for atom_id in graph:
        visit(atom_id, [])
    return cycles


def module_entry_ready(session: dict[str, Any], module: str) -> bool:
    if module == MODULE_ORDER[0]:
        return True
    prior = MODULE_ORDER[MODULE_ORDER.index(module) - 1]
    return module_outcome(session, prior) in {"completed", "bypassed"}


def gate_pending_atom(session: dict[str, Any]) -> dict[str, Any] | None:
    position = session["position"]
    if position.get("status") != "gate_pending":
        return None
    gate_atom_id = position["atom_id"]
    module = atom_module(gate_atom_id)
    artifact = GATE_ARTIFACTS[module]
    if artifact_status(session, artifact) == "final":
        return None
    atoms = load_atoms()
    index = atom_by_id(atoms)
    return index.get(gate_atom_id)


def ready_atoms(session: dict[str, Any], atoms: list[dict[str, Any]]) -> list[str]:
    _build_atom_indexes()
    answered = effective_answered_atoms(session, atoms)
    schedulable = schedulable_atom_ids(session, atoms)
    ready: list[str] = []
    for atom in atoms:
        atom_id = atom["id"]
        module = atom["module"]
        if atom_id not in schedulable:
            continue
        if module_bypassed(session, module):
            continue
        if atom_id in answered:
            continue
        first_atom = MODULE_ATOMS[module][0]
        if atom_id == first_atom and not module_entry_ready(session, module):
            continue
        requires = effective_requires(session, atom)
        if all(req in answered for req in requires):
            ready.append(atom_id)
    return ready


def section_status(
    session: dict[str, Any], atoms: list[dict[str, Any]], module: str
) -> dict[str, str]:
    section_map = load_section_map()["milestones"].get(module, {})
    answered = effective_answered_atoms(session, atoms)
    index = atom_by_id(atoms)
    status: dict[str, str] = {}
    for section, atom_ids in section_map.items():
        answered_ids = [atom_id for atom_id in atom_ids if atom_id in answered]
        if not answered_ids:
            status[section] = "empty"
            continue
        if len(answered_ids) < len(atom_ids):
            status[section] = "partial"
            continue
        soft_ids = [atom_id for atom_id in atom_ids if index[atom_id].get("soft")]
        if soft_ids and all(
            (answer := current_answer(session, atom_id)) is not None
            and answer.get("kind") == "unknown"
            for atom_id in soft_ids
        ):
            status[section] = "unknown_ok"
        else:
            status[section] = "satisfied"
    return status


def pick_focus_atom(
    session: dict[str, Any], atoms: list[dict[str, Any]]
) -> dict[str, Any] | None:
    pending_gate = gate_pending_atom(session)
    if pending_gate is not None:
        return pending_gate

    ready_ids = ready_atoms(session, atoms)
    if not ready_ids:
        return None

    index = atom_by_id(atoms)
    answered = effective_answered_atoms(session, atoms)
    by_module: dict[str, list[str]] = {}
    for atom_id in ready_ids:
        by_module.setdefault(atom_module(atom_id), []).append(atom_id)

    for module in MODULE_ORDER:
        module_ready = by_module.get(module)
        if not module_ready:
            continue
        statuses = section_status(session, atoms, module)
        section_map = load_section_map()["milestones"].get(module, {})
        section_order = list(section_map.keys())
        ready_by_section: dict[str, list[str]] = {}
        for atom_id in module_ready:
            ready_by_section.setdefault(index[atom_id]["section"], []).append(atom_id)

        def section_rank(section_name: str) -> tuple[int, int]:
            atom_ids = section_map.get(section_name, [])
            answered_count = sum(1 for atom_id in atom_ids if atom_id in answered)
            try:
                order = section_order.index(section_name)
            except ValueError:
                order = len(section_order)
            return (answered_count, order)

        best_section = min(ready_by_section.keys(), key=section_rank)
        focus_id = min(ready_by_section[best_section])
        return index[focus_id]
    return None


def schedule_next_atom(
    session: dict[str, Any], atoms: list[dict[str, Any]]
) -> dict[str, Any] | None:
    return pick_focus_atom(session, atoms)


def format_section_strip(
    session: dict[str, Any], atoms: list[dict[str, Any]], module: str | None = None
) -> str:
    active_module = module or session["position"]["module"]
    statuses = section_status(session, atoms, active_module)
    if not statuses:
        return f"{active_module}: (no sections)"
    parts = [
        f"{name}{SECTION_STRIP_SYMBOLS.get(state, '?')}"
        for name, state in statuses.items()
    ]
    return f"{active_module}: {' '.join(parts)}"


def hard_gaps_by_section(
    session: dict[str, Any], atoms: list[dict[str, Any]], module: str | None = None
) -> dict[str, list[str]]:
    active_module = module or session["position"]["module"]
    answered = effective_answered_atoms(session, atoms)
    index = atom_by_id(atoms)
    ready = set(ready_atoms(session, atoms))
    gaps: dict[str, list[str]] = {}
    for atom_id in ready:
        atom = index[atom_id]
        if atom.get("soft"):
            continue
        if atom_id in answered:
            continue
        section = atom.get("section", "Other")
        gaps.setdefault(section, []).append(atom_id)
    return gaps


def soft_gaps_by_section(
    session: dict[str, Any], atoms: list[dict[str, Any]], module: str | None = None
) -> dict[str, list[str]]:
    active_module = module or session["position"]["module"]
    answered = effective_answered_atoms(session, atoms)
    index = atom_by_id(atoms)
    ready = set(ready_atoms(session, atoms))
    gaps: dict[str, list[str]] = {}
    for atom_id in ready:
        atom = index[atom_id]
        if not atom.get("soft"):
            continue
        if atom_id in answered:
            continue
        section = atom.get("section", "Other")
        gaps.setdefault(section, []).append(atom_id)
    return gaps


def set_position_to_focus(session: dict[str, Any], atoms: list[dict[str, Any]]) -> None:
    focus = pick_focus_atom(session, atoms)
    if focus is None:
        session["position"]["status"] = "completed"
        return
    session["position"] = {
        "module": focus["module"],
        "atom_id": focus["id"],
        "status": "in_progress",
    }


def next_unsatisfied_atom(
    session: dict[str, Any], atoms: list[dict[str, Any]]
) -> dict[str, Any] | None:
    return schedule_next_atom(session, atoms)


def atom_module(atom_id: str) -> str:
    _build_atom_indexes()
    if atom_id in ATOM_MODULE_BY_ID:
        return ATOM_MODULE_BY_ID[atom_id]
    if atom_id.startswith("P"):
        return "profile"
    if atom_id.startswith("V"):
        return "value-map"
    if atom_id.startswith("B"):
        return "business-model"
    return "experiments"


def upsert_artifact(session: dict[str, Any], path: str, status: str) -> None:
    session["artifacts"] = [
        record for record in session.get("artifacts", []) if record["path"] != path
    ]
    session["artifacts"].append({"path": path, "status": status})


RECORD_COLLECTIONS = ("evidence", "assumptions", "decisions", "unknowns")
EVIDENCE_FIELDS = ("claim", "kind", "source", "strength")
ASSUMPTION_FIELDS = ("claim", "criticality", "evidence_status", "source_atom")
DECISION_FIELDS = (
    "decision",
    "reason",
    "source_atom",
    "resulting_module",
    "resulting_atom",
    "resulting_status",
)
UNKNOWN_FIELDS = ("question", "blocking")
ARTIFACT_FIELDS = ("path", "status")


def _require_fields(record: dict[str, Any], fields: tuple[str, ...], label: str) -> None:
    missing = [field for field in fields if field not in record]
    if missing:
        raise ValueError(f"{label} record missing fields: {', '.join(missing)}")


def append_session_records(
    session: dict[str, Any],
    payload: dict[str, Any],
    *,
    default_source_atom: str,
) -> None:
    """Append validated evidence, assumptions, decisions, unknowns, and artifacts."""
    for record in payload.get("evidence", []):
        _require_fields(record, EVIDENCE_FIELDS, "evidence")
        session.setdefault("evidence", []).append(dict(record))

    for record in payload.get("assumptions", []):
        item = dict(record)
        item.setdefault("source_atom", default_source_atom)
        _require_fields(item, ASSUMPTION_FIELDS, "assumption")
        session.setdefault("assumptions", []).append(item)

    for record in payload.get("decisions", []):
        item = dict(record)
        item.setdefault("source_atom", default_source_atom)
        _require_fields(item, DECISION_FIELDS, "decision")
        session.setdefault("decisions", []).append(item)

    for record in payload.get("unknowns", []):
        _require_fields(record, UNKNOWN_FIELDS, "unknown")
        session.setdefault("unknowns", []).append(dict(record))

    for record in payload.get("artifacts", []):
        _require_fields(record, ARTIFACT_FIELDS, "artifact")
        upsert_artifact(session, record["path"], record["status"])


def answers_for_module(session: dict[str, Any], module: str) -> list[dict[str, Any]]:
    _build_atom_indexes()
    module_atoms = set(MODULE_ATOMS[module])
    latest: dict[str, dict[str, Any]] = {}
    for record in session.get("answers", []):
        if record["atom_id"] in module_atoms:
            latest[record["atom_id"]] = record
    return [latest[atom_id] for atom_id in sorted(latest)]


def format_answer_block(records: list[dict[str, Any]]) -> str:
    if not records:
        return "unknown"
    lines = []
    for record in records:
        lines.append(
            f"- **{record['atom_id']}** ({record['kind']}): {record['answer']}"
        )
    return "\n".join(lines)


def format_answer_block_for_atoms(session: dict[str, Any], atom_ids: list[str]) -> str:
    records = [
        current_answer(session, atom_id)
        for atom_id in atom_ids
        if current_answer(session, atom_id)
    ]
    return format_answer_block(records)


def fill_section(template: str, heading: str, body: str) -> str:
    pattern = rf"(## {re.escape(heading)}\n)(.*?)(?=\n## |\Z)"
    replacement = f"\\1\n{body.strip()}\n\n"
    if re.search(pattern, template, flags=re.DOTALL):
        return re.sub(pattern, replacement, template, count=1, flags=re.DOTALL)
    return template


def fill_milestone_template(session: dict[str, Any], module: str) -> str:
    template_name = MILESTONE_TEMPLATES[module]
    template = (ASSETS_DIR / template_name).read_text(encoding="utf-8")
    section_map = load_section_map()["milestones"].get(module, {})
    for heading, atom_ids in section_map.items():
        if heading == "Unknowns":
            body = format_unknowns(session)
        elif heading == "Decisions":
            body = format_decisions(session, module)
        else:
            body = format_answer_block_for_atoms(session, atom_ids)
        template = fill_section(template, heading, body)
    return template.rstrip() + "\n"


def format_unknowns(session: dict[str, Any]) -> str:
    unknowns = session.get("unknowns", [])
    if not unknowns:
        return "unknown"
    return "\n".join(
        f"- {item['question']} (blocking={item['blocking']})" for item in unknowns
    )


def format_decisions(session: dict[str, Any], module: str) -> str:
    decisions = [
        item
        for item in session.get("decisions", [])
        if item.get("resulting_module") == module
    ]
    if not decisions:
        return "unknown"
    return "\n".join(
        f"- {item['decision']}: {item['reason']}" for item in decisions[-5:]
    )


def fill_design_brief(session: dict[str, Any], template_name: str) -> str:
    template = (ASSETS_DIR / template_name).read_text(encoding="utf-8")
    section_map = load_section_map()["design_briefs"].get(template_name, {})
    assumptions = session.get("assumptions", [])
    assumption_block = (
        "\n".join(
            f"- ({item['criticality']}/{item['evidence_status']}) {item['claim']}"
            for item in assumptions
        )
        or "unknown"
    )
    title = template.splitlines()[0].lstrip("# ").strip()
    for heading, atom_ids in section_map.items():
        if heading == "Hypotheses and excluded/parked scope":
            body = assumption_block
        elif heading == "Non-goals from orphans and bypasses":
            body = assumption_block
        elif heading == "Open assumptions from bombs":
            body = (
                "\n".join(f"- {item}" for item in unvalidated_bombs(session)) or "unknown"
            )
        elif heading == "Evidence, assumptions, unknowns":
            body = assumption_block
        elif heading == "Accessibility and content implications":
            body = "unknown"
        else:
            body = format_answer_block_for_atoms(session, atom_ids)
        template = fill_section(template, heading, body)
        if heading == "Required states":
            for sub in ("Empty", "Loading", "Success", "Error", "Recovery"):
                template = fill_section(template, sub, "unknown")
    if title == "Product design brief":
        for heading in ("Moat and unknown scores", "Excluded scope"):
            if heading not in section_map:
                template = fill_section(template, heading, assumption_block)
    return template.rstrip() + "\n"


def all_modules_ready(session: dict[str, Any]) -> bool:
    return all(
        module_outcome(session, module) in {"completed", "bypassed"}
        for module in MODULE_ORDER
    )


def advance_after_gate_milestone(session: dict[str, Any], module: str) -> None:
    atoms = load_atoms()
    set_position_to_focus(session, atoms)


def position_from_records(payload: dict[str, Any]) -> dict[str, Any] | None:
    decisions = payload.get("decisions", [])
    if not decisions:
        return None
    last = decisions[-1]
    required = ("resulting_module", "resulting_atom", "resulting_status")
    if all(field in last for field in required):
        return last
    return None


def advance_position_after_accept(
    session: dict[str, Any],
    atom: dict[str, Any],
    atom_id: str,
    *,
    reopen: bool,
    stay: bool,
    gate_pending: bool,
    next_atom_override: str,
    records_payload: dict[str, Any] | None,
) -> None:
    _build_atom_indexes()
    if stay:
        session["position"]["module"] = atom["module"]
        session["position"]["atom_id"] = atom_id
        session["position"]["status"] = "in_progress"
        return

    position_override = position_from_records(records_payload) if records_payload else None
    if atom_id in GATE_ATOMS and not reopen:
        session["position"]["module"] = atom["module"]
        session["position"]["atom_id"] = atom_id
        session["position"]["status"] = "gate_pending"
        upsert_artifact(session, GATE_ARTIFACTS[atom["module"]], "pending")
        return

    if next_atom_override:
        session["position"]["module"] = atom_module(next_atom_override)
        session["position"]["atom_id"] = next_atom_override
        session["position"]["status"] = "in_progress"
        return

    if position_override is not None:
        session["position"]["module"] = position_override["resulting_module"]
        session["position"]["atom_id"] = position_override["resulting_atom"]
        session["position"]["status"] = position_override["resulting_status"]
        return

    atoms = load_atoms()
    set_position_to_focus(session, atoms)

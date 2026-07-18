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
GATE_ATOMS = {"P12": "profile", "V08": "value-map", "B08": "business-model", "E10": "experiments"}
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
PROFILE_ATOMS = tuple(f"P{n:02d}" for n in range(1, 13))
VALUE_MAP_ATOMS = tuple(f"V{n:02d}" for n in range(1, 9))
BUSINESS_MODEL_ATOMS = tuple(f"B{n:02d}" for n in range(1, 9))
EXPERIMENT_ATOMS = tuple(f"E{n:02d}" for n in range(1, 11))
MODULE_ATOMS = {
    "profile": PROFILE_ATOMS,
    "value-map": VALUE_MAP_ATOMS,
    "business-model": BUSINESS_MODEL_ATOMS,
    "experiments": EXPERIMENT_ATOMS,
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_atoms() -> list[dict[str, Any]]:
    payload = load_json(ASSETS_DIR / "atoms.json")
    return payload["atoms"]


def load_kb() -> dict[str, Any]:
    return load_json(ASSETS_DIR / "knowledge-base.json")


def atom_by_id(atoms: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {atom["id"]: atom for atom in atoms}


def load_session(path: Path) -> dict[str, Any]:
    return load_json(path)


def save_session(path: Path, session: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(session, indent=2) + "\n", encoding="utf-8")


def default_session(slug: str, name: str) -> dict[str, Any]:
    timestamp = utc_now_iso()
    session = {
        "schema_version": "1.0",
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
    session["ledger"] = recompute_ledger(session)
    return session


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


def module_bypassed(session: dict[str, Any], module: str) -> bool:
    needle = f"bypass {module} gate"
    for decision in reversed(session.get("decisions", [])):
        if needle in decision.get("decision", "").lower():
            return True
    return False


def module_gate_passed(session: dict[str, Any], module: str) -> bool:
    gate_atom = next(key for key, value in GATE_ATOMS.items() if value == module)
    for decision in reversed(session.get("decisions", [])):
        text = decision.get("decision", "").lower()
        if decision.get("source_atom") == gate_atom and "pass" in text and module in text:
            return True
        if f"bypass {module} gate" in text:
            return False
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
    answered = answered_atom_ids(session)
    for module in MODULE_ORDER:
        if module_outcome(session, module) != "bypassed":
            continue
        answered.update(MODULE_ATOMS[module])
    return answered


def completion_pct(session: dict[str, Any], atoms: list[dict[str, Any]]) -> int:
    total = len(atoms)
    if total == 0:
        return 0
    answered = effective_answered_atoms(session, atoms)
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
        f"completion={ledger['completion_pct']}% "
        f"milestone={ledger['validation_milestone']} "
        f"answered={','.join(answered) or 'none'} "
        f"bombs={bomb_text}"
    )


def next_unsatisfied_atom(
    session: dict[str, Any], atoms: list[dict[str, Any]]
) -> dict[str, Any] | None:
    answered = effective_answered_atoms(session, atoms)
    index = atom_by_id(atoms)
    position = session["position"]
    current = index.get(position["atom_id"])
    if current and position["atom_id"] not in answered:
        return current
    for atom in atoms:
        if atom["id"] not in answered:
            return atom
    return None


def atom_module(atom_id: str) -> str:
    if atom_id.startswith("P"):
        return "profile"
    if atom_id.startswith("V"):
        return "value-map"
    if atom_id.startswith("B"):
        return "business-model"
    return "experiments"


def upsert_artifact(session: dict[str, Any], path: str, status: str) -> None:
    for record in session["artifacts"]:
        if record["path"] == path:
            record["status"] = status
            return
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


def fill_section(template: str, heading: str, body: str) -> str:
    pattern = rf"(## {re.escape(heading)}\n)(.*?)(?=\n## |\Z)"
    replacement = f"\\1\n{body.strip()}\n\n"
    if re.search(pattern, template, flags=re.DOTALL):
        return re.sub(pattern, replacement, template, count=1, flags=re.DOTALL)
    return template


def fill_milestone_template(session: dict[str, Any], module: str) -> str:
    template_name = MILESTONE_TEMPLATES[module]
    template = (ASSETS_DIR / template_name).read_text(encoding="utf-8")
    records = answers_for_module(session, module)
    block = format_answer_block(records)
    section_map = {
        "profile": {
            "Segment": block,
            "Situation": block,
            "Jobs": block,
            "Pains": block,
            "Gains": block,
            "Alternatives": block,
            "Evidence": block,
            "Unknowns": format_unknowns(session),
        },
        "value-map": {
            "Offering": block,
            "Pain relievers": block,
            "Gain creators": block,
            "Fit links": block,
            "Orphan candidates": block,
            "Decisions": format_decisions(session, module),
        },
        "business-model": {
            "Delivery": block,
            "Relationships": block,
            "Revenue": block,
            "Activities": block,
            "Resources": block,
            "Partners": block,
            "Costs": block,
            "Scale": block,
            "Defensibility": block,
            "Unknowns": format_unknowns(session),
        },
        "experiments": {
            "Hypothesis": block,
            "Criticality": block,
            "Evidence status": block,
            "Method": block,
            "Metric": block,
            "Threshold": block,
            "Result": block,
            "Learning": block,
            "Decision": block,
        },
    }
    for heading, body in section_map.get(module, {}).items():
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
    all_answers = format_answer_block(
        [
            current_answer(session, atom_id)
            for atom_id in sorted(answered_atom_ids(session))
            if current_answer(session, atom_id)
        ]
    )
    assumptions = session.get("assumptions", [])
    assumption_block = (
        "\n".join(
            f"- ({item['criticality']}/{item['evidence_status']}) {item['claim']}"
            for item in assumptions
        )
        or "unknown"
    )
    section_defaults = {
        "Product design brief": {
            "Problem and target segment": all_answers,
            "Validated job and desired outcome": all_answers,
            "Evidence": all_answers,
            "Proposed value and fit": all_answers,
            "Capabilities implied by accepted state": all_answers,
            "Constraints and business-model dependencies": all_answers,
            "Hypotheses and excluded/parked scope": assumption_block,
            "Acceptance signals": all_answers,
        },
        "UX brief": {
            "User and situation": all_answers,
            "Primary job and journey start": all_answers,
            "Pains to reduce and gains to support": all_answers,
            "Key user decisions": all_answers,
            "Information and trust needs": all_answers,
            "Required states": all_answers,
            "Accessibility and content implications": "unknown",
            "Evidence, assumptions, unknowns": assumption_block,
            "Research and experiment hooks": all_answers,
        },
        "App design brief": {
            "Capabilities from value map": all_answers,
            "Primary flows from jobs and channels": all_answers,
            "Entities and data from offering": all_answers,
            "Non-goals from orphans and bypasses": assumption_block,
            "Open assumptions from bombs": "\n".join(
                f"- {item}" for item in unvalidated_bombs(session)
            )
            or "unknown",
        },
    }
    title = template.splitlines()[0].lstrip("# ").strip()
    for heading, body in section_defaults.get(title, {}).items():
        template = fill_section(template, heading, body)
        if heading == "Required states":
            for sub in ("Empty", "Loading", "Success", "Error", "Recovery"):
                template = fill_section(template, sub, "unknown")
    return template.rstrip() + "\n"


def all_modules_ready(session: dict[str, Any]) -> bool:
    return all(
        module_outcome(session, module) in {"completed", "bypassed"}
        for module in MODULE_ORDER
    )

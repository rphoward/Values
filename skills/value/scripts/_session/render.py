"""Template fills, ADRs, and build pack rendering."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .catalog import ASSETS_DIR, load_section_map
from .constants import BUILD_PACK_FILES, MILESTONE_TEMPLATES
from .runtime import (
    current_answer,
    is_ceremony_answer,
    is_hard_decision,
    unvalidated_bombs,
    upsert_artifact,
)
from .voice import (
    fill_north_star_blurb,
    fill_value_trail,
)


def format_atom_block(
    session: dict[str, Any],
    atom_ids: list[str],
    *,
    include_atom_ids: bool,
) -> str:
    lines: list[str] = []
    for atom_id in atom_ids:
        record = current_answer(session, atom_id)
        if record is None or is_ceremony_answer(record):
            continue
        if include_atom_ids:
            lines.append(
                f"- **{record['atom_id']}** ({record['kind']}): {record['answer']}"
            )
        else:
            lines.append(f"- ({record['kind']}) {record['answer']}")
    return "\n".join(lines) if lines else "unknown"


def format_answer_block_for_atoms(session: dict[str, Any], atom_ids: list[str]) -> str:
    return format_atom_block(session, atom_ids, include_atom_ids=True)


def format_content_block_for_atoms(session: dict[str, Any], atom_ids: list[str]) -> str:
    return format_atom_block(session, atom_ids, include_atom_ids=False)


def fill_section(
    template: str, heading: str, body: str, *, required: bool = True
) -> str:
    pattern = rf"(## {re.escape(heading)}\n)(.*?)(?=\n## |\Z)"
    if not re.search(pattern, template, flags=re.DOTALL):
        if required:
            raise ValueError(f"Missing section heading in template: {heading!r}")
        return template
    replacement = f"\\1\n{body.strip()}\n\n"
    return re.sub(pattern, replacement, template, count=1, flags=re.DOTALL)


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
                template = fill_section(template, sub, "unknown", required=False)
    if title == "Product design brief":
        for heading in ("Moat and unknown scores", "Excluded scope"):
            if heading not in section_map:
                template = fill_section(template, heading, assumption_block, required=False)
    return template.rstrip() + "\n"


def format_blocking_unknowns(session: dict[str, Any]) -> str:
    items = [
        item for item in session.get("unknowns", []) if item.get("blocking")
    ]
    if not items:
        return "none"
    return "\n".join(f"- {item['question']}" for item in items)


def format_bombs_block(session: dict[str, Any]) -> str:
    bombs = unvalidated_bombs(session)
    return "\n".join(f"- {item}" for item in bombs) if bombs else "none"


def format_orphan_non_goals(session: dict[str, Any]) -> str:
    body = format_content_block_for_atoms(session, ["V06"])
    if body != "unknown":
        return body
    parked = [
        f"- {item['decision']}: {item['reason']}"
        for item in session.get("decisions", [])
        if "orphan" in f"{item.get('decision', '')} {item.get('reason', '')}".lower()
        or "park" in f"{item.get('decision', '')} {item.get('reason', '')}".lower()
    ]
    return "\n".join(parked) if parked else "none"


def slugify_adr(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    slug = re.sub(r"-+", "-", slug)
    return (slug[:48].rstrip("-") if slug else "decision")


def _sync_adr_directory(adr_dir: Path, keep: set[Path]) -> None:
    """Delete ADR markdown files not in keep. No-op when keep is empty (leave dir alone)."""
    if not keep or not adr_dir.is_dir():
        return
    keep_resolved = {path.resolve() for path in keep}
    for path in adr_dir.glob("*.md"):
        if path.resolve() not in keep_resolved:
            path.unlink()


def plan_hard_decision_adrs(
    session: dict[str, Any], session_dir: Path
) -> list[tuple[Path, str]]:
    """Return planned ADR (path, content) pairs; orphan sync happens at write."""
    adr_dir = session_dir / "docs" / "adr"
    hard = [item for item in session.get("decisions", []) if is_hard_decision(item)]
    planned: list[tuple[Path, str]] = []
    for index, item in enumerate(hard, start=1):
        title = item.get("decision", "decision").strip() or "decision"
        path = adr_dir / f"{index:04d}-{slugify_adr(title)}.md"
        source = item.get("source_atom", "unknown")
        body = (
            f"# {title}\n\n"
            f"{item.get('reason', '').strip() or 'No reason recorded.'}\n\n"
            f"_Source atom: {source}_\n"
        )
        planned.append((path, body))
    return planned


def write_hard_decision_adrs(session: dict[str, Any], session_dir: Path) -> list[Path]:
    planned = plan_hard_decision_adrs(session, session_dir)
    return write_planned_files(planned)


def fill_build_pack_file(session: dict[str, Any], template_name: str) -> str:
    if template_name == "north-star-blurb.template.md":
        return fill_north_star_blurb(session)
    if template_name == "value-trail.template.md":
        return fill_value_trail(session)

    template = (ASSETS_DIR / template_name).read_text(encoding="utf-8")
    section_map = load_section_map().get("ide_exports", {}).get(template_name, {})
    project_name = session.get("project", {}).get("name", "Project")
    template = template.replace("PROJECT_NAME", project_name)

    ask_parts: list[str] = []
    bombs = unvalidated_bombs(session)
    if bombs:
        ask_parts.extend(f"- (bomb) {item}" for item in bombs)
    for item in session.get("unknowns", []):
        if item.get("blocking"):
            ask_parts.append(f"- (blocking unknown) {item['question']}")
    ask_first = "\n".join(ask_parts) if ask_parts else "- none recorded"

    never_parts = [
        "- Implement orphan / parked features without an explicit decision.",
        "- Invent facts past unknowns or upgrade unknown/inference to fact.",
        "- Expand past the segment exclusion without reopening the decision.",
    ]
    orphans = format_orphan_non_goals(session)
    if orphans != "none":
        never_parts.append(orphans)

    special_bodies = {
        "Always": (
            "- Respect the accepted segment boundary and exclusions.\n"
            "- Keep evidence labels (fact, inference, hypothesis, decision, unknown).\n"
            "- Prefer customer language from CONTEXT.product.md."
        ),
        "Ask first": ask_first,
        "Never": "\n".join(never_parts),
        "Bombs": format_bombs_block(session),
        "Blocking unknowns": format_blocking_unknowns(session),
        "Non-goals": format_orphan_non_goals(session),
        "Flagged unknowns": format_unknowns(session),
    }

    for heading, atom_ids in section_map.items():
        if heading in special_bodies:
            body = special_bodies[heading]
        else:
            body = format_content_block_for_atoms(session, atom_ids)
        template = fill_section(template, heading, body)

    for heading, body in special_bodies.items():
        if heading not in section_map:
            template = fill_section(template, heading, body, required=False)

    return template.rstrip() + "\n"


def plan_build_pack(
    session: dict[str, Any], session_dir: Path
) -> list[tuple[Path, str]]:
    planned: list[tuple[Path, str]] = []
    for template_name, output_name in BUILD_PACK_FILES:
        output_path = session_dir / output_name
        content = fill_build_pack_file(session, template_name)
        upsert_artifact(session, output_name, "final")
        planned.append((output_path, content))
    for path, content in plan_hard_decision_adrs(session, session_dir):
        rel = path.relative_to(session_dir).as_posix()
        upsert_artifact(session, rel, "final")
        planned.append((path, content))
    return planned


def write_planned_files(planned: list[tuple[Path, str]]) -> list[Path]:
    """Atomically write planned files (temp + replace), then drop ADR orphans not kept."""
    written: list[Path] = []
    for path, content in planned:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = path.with_name(path.name + ".tmp")
        tmp_path.write_text(content, encoding="utf-8")
        tmp_path.replace(path)
        written.append(path)
    adr_keep = {path for path in written if path.parent.name == "adr"}
    if adr_keep:
        _sync_adr_directory(next(iter(adr_keep)).parent, adr_keep)
    return written


def refresh_build_pack(session: dict[str, Any], session_dir: Path) -> list[Path]:
    """Write IDE export pack files (including north-star blurb and value trail) and hard-decision ADRs."""
    planned = plan_build_pack(session, session_dir)
    return write_planned_files(planned)

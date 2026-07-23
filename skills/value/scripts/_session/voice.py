"""Voice rendering helpers: sticky labels, match board, outward pitch, trail crumbs."""

from __future__ import annotations

import re
from typing import Any

from .catalog import ASSETS_DIR
from .constants import (
    MATCH_BOARD_ATOMS,
    VALUE_TRAIL_CRUMBS,
    _EXTREME_PAIN_RE,
    _LINE_ITEM_RE,
    _NUMBERED_ITEM_RE,
)
from .runtime import current_answer, is_ceremony_answer


_TAXONOMY_PREFIX_RE = re.compile(
    r"^(?:"
    r"priority\s+job(?:\s*\([^)]*\))?|"
    r"job|"
    r"extreme|severe|mild|"
    r"situation|trigger|audience|"
    r"buying|co-creating|transferring|"
    r"usual|sometimes|big temptation|"
    r"offering|gains?\s+for[^:]*|"
    r"excluded"
    r")\s*:\s*",
    flags=re.IGNORECASE,
)
_AUTONOMY_JOB_RE = re.compile(
    r"\b(autonomy|creativity|liberty|freedom)\b",
    flags=re.IGNORECASE,
)


def _strip_voice_prefixes(text: str) -> str:
    """Drop interview labels so paste copy stays customer language."""
    cleaned = re.sub(r"\s+", " ", text).strip()
    cleaned = re.sub(r"^[\(\[]?\d+[\)\].:]?\s*", "", cleaned)
    cleaned = re.sub(r"^[-*•]\s*", "", cleaned)
    cleaned = re.sub(
        r"^\((?:extreme|severe|expected|desired|unexpected)[^)]*\)\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    for _ in range(3):
        next_cleaned = _TAXONOMY_PREFIX_RE.sub("", cleaned).strip()
        if next_cleaned == cleaned:
            break
        cleaned = next_cleaned
    return cleaned


def sticky_label(text: str, max_words: int = 10) -> str:
    """Short sticky-note summary for voice rendering (aim ≤10 words)."""
    cleaned = _strip_voice_prefixes(text)
    words = cleaned.split()
    if len(words) <= max_words:
        return cleaned
    return " ".join(words[:max_words])


def pitch_clause(text: str, max_words: int = 18) -> str:
    """Paste-ready clause: strip labels, prefer first natural clause, soft trim."""
    cleaned = _strip_voice_prefixes(text)
    for splitter in (";", ". ", " — ", " - ", ": "):
        if splitter in cleaned:
            head = cleaned.split(splitter, 1)[0].strip(" ,")
            if len(head.split()) >= 4:
                cleaned = head
                break
    cleaned = re.sub(
        r"^(also named|also called)\b.*$",
        "",
        cleaned,
        flags=re.IGNORECASE,
    ).strip(" ,;—-:")
    words = cleaned.split()
    if len(words) <= max_words:
        return cleaned
    trimmed = " ".join(words[:max_words]).rstrip(" ,;—-:")
    return trimmed


def split_sticky_items(text: str) -> list[str]:
    """Split an answer into sticky items; fall back to one block."""
    raw = text.strip()
    if not raw:
        return []

    numbered = [part.strip(" ;.") for part in _NUMBERED_ITEM_RE.split(raw) if part.strip(" ;.")]
    numbered_items = [part for part in numbered if not part.isdigit()]
    if len(numbered_items) >= 2:
        if len(numbered_items[0].split()) <= 4 and not re.search(
            r"\b(pain|gain|product|service|include)\b",
            numbered_items[0],
            flags=re.IGNORECASE,
        ):
            numbered_items = numbered_items[1:] or numbered_items
        return numbered_items

    line_parts = [part.strip(" ;.") for part in _LINE_ITEM_RE.split(raw) if part.strip(" ;.")]
    if len(line_parts) >= 2:
        if len(line_parts[0].split()) <= 4:
            line_parts = line_parts[1:] or line_parts
        return line_parts

    semi = [part.strip() for part in raw.split(";") if part.strip()]
    if len(semi) >= 2:
        return semi
    return [raw]


def _prefer_extreme_first(items: list[str]) -> list[str]:
    extreme = [item for item in items if _EXTREME_PAIN_RE.search(item)]
    rest = [item for item in items if not _EXTREME_PAIN_RE.search(item)]
    return extreme + rest if extreme else items


def match_board_for_atom(session: dict[str, Any], atom_id: str) -> dict[str, Any] | None:
    """Agent-internal parts×pains/gains board for pain-reliever and gain-creator match steps."""
    if atom_id not in MATCH_BOARD_ATOMS:
        return None
    target_atom, target_name, link_question = MATCH_BOARD_ATOMS[atom_id]
    parts_record = current_answer(session, "V02")
    targets_record = current_answer(session, target_atom)
    parts = (
        split_sticky_items(parts_record["answer"])
        if parts_record and not is_ceremony_answer(parts_record)
        else []
    )
    targets = (
        split_sticky_items(targets_record["answer"])
        if targets_record and not is_ceremony_answer(targets_record)
        else []
    )
    if atom_id == "V03":
        targets = _prefer_extreme_first(targets)
    part_labels = [sticky_label(item) for item in parts]
    target_labels = [sticky_label(item) for item in targets]
    parts_list = "\n".join(f"- {label}" for label in part_labels) or "- (no offering parts yet)"
    targets_list = (
        "\n".join(f"- {label}" for label in target_labels)
        or f"- (no accepted {target_name} yet)"
    )
    match_prompt = (
        f"Offering parts:\n{parts_list}\n\n"
        f"Accepted {target_name}:\n{targets_list}\n\n"
        f"{link_question}"
    )
    return {
        "parts": parts,
        "targets": targets,
        "part_labels": part_labels,
        "target_labels": target_labels,
        "target_atom": target_atom,
        "target_name": target_name,
        "match_prompt": match_prompt,
    }


def answer_text(session: dict[str, Any], atom_id: str) -> str:
    record = current_answer(session, atom_id)
    if record is None or is_ceremony_answer(record):
        return ""
    return record["answer"].strip()


def _first_answered_record(
    session: dict[str, Any], atom_ids: tuple[str, ...]
) -> dict[str, Any] | None:
    for atom_id in atom_ids:
        record = current_answer(session, atom_id)
        if record is not None and not is_ceremony_answer(record):
            return record
    return None


def _de_sentence_case(text: str) -> str:
    """Lower the lead letter when the clause is a verb phrase, not a proper name."""
    if len(text) < 2 or not text[0].isupper() or text[1].isupper():
        return text
    return text[0].lower() + text[1:]


def compose_outward_pitch(session: dict[str, Any]) -> str:
    """Outward pitch paragraph shared by north-star blurb and value-trail.

    Peer Discord voice: short sentences — who, freeze, what you get. So-what
    features into daily relief; never a fourth Connection beat. Prefer
    Prefer stated job over priority-sequence when both exist. When the job is
    autonomy-coded, lean on the outward pain so the paste stays aimed outward.
    """
    segment = answer_text(session, "P01")
    job = answer_text(session, "P03") or answer_text(session, "P11")
    why_record = _first_answered_record(session, ("P07", "P08"))
    who_bit = pitch_clause(segment, max_words=20) if segment else "this customer"
    why_bit = ""
    if why_record is not None:
        why_text = why_record["answer"].strip()
        if why_record.get("atom_id") == "P07":
            items = _prefer_extreme_first(split_sticky_items(why_text))
            why_text = items[0] if items else why_text
        why_bit = pitch_clause(why_text, max_words=16)
    job_is_autonomy = bool(job and _AUTONOMY_JOB_RE.search(job))
    if why_bit and (job_is_autonomy or not job):
        return (
            f"For {who_bit}. They freeze on {why_bit}. "
            "You get a clear outward pitch — not only a clever build."
        )
    job_bit = (
        _de_sentence_case(pitch_clause(job, max_words=14))
        if job
        else "make progress that matters"
    )
    if why_bit:
        return (
            f"For {who_bit}. They freeze on {why_bit}. "
            f"North star: {job_bit}."
        )
    return f"For {who_bit}. North star: {job_bit}."


def value_trail_crumb_visible(session: dict[str, Any], crumb: dict[str, Any]) -> bool:
    crumb_id = crumb["id"]
    if crumb_id == "first_win":
        return any(answer_text(session, atom_id) for atom_id in ("P03", "P11", "P08"))
    return any(answer_text(session, atom_id) for atom_id in crumb["sources"])


def format_value_trail_crumb_body(
    session: dict[str, Any], crumb: dict[str, Any]
) -> str:
    crumb_id = crumb["id"]
    if crumb_id == "outward_pitch":
        return compose_outward_pitch(session)
    if crumb_id == "job":
        record = _first_answered_record(session, ("P11", "P03"))
        if record is None:
            return ""
        return f"({record['kind']}) {sticky_label(record['answer'])}"
    if crumb_id == "why_outward":
        record = _first_answered_record(session, ("P07", "P08"))
        if record is None:
            return ""
        text = record["answer"].strip()
        if record["atom_id"] == "P07":
            items = _prefer_extreme_first(split_sticky_items(text))
            sticky = sticky_label(items[0]) if items else sticky_label(text)
        else:
            sticky = sticky_label(text)
        return f"({record['kind']}) {sticky}"
    if crumb_id == "parts":
        record = _first_answered_record(session, ("V02",))
        if record is None:
            return ""
        items = split_sticky_items(record["answer"])
        kind = record["kind"]
        return "\n".join(f"- ({kind}) {sticky_label(item)}" for item in items)
    if crumb_id == "first_win":
        lines: list[str] = []
        win_record = _first_answered_record(session, ("P11", "P03", "P08"))
        if win_record is not None:
            lines.append(
                f"({win_record['kind']}) {sticky_label(win_record['answer'])}"
            )
        alt_record = _first_answered_record(session, ("P09",))
        if alt_record is not None:
            lines.append(
                f"({alt_record['kind']}) Beat: {sticky_label(alt_record['answer'])}"
            )
        return "\n".join(lines)
    record = _first_answered_record(session, crumb["sources"])
    if record is None:
        return ""
    return f"({record['kind']}) {sticky_label(record['answer'])}"


def fill_value_trail(session: dict[str, Any]) -> str:
    template = (ASSETS_DIR / "value-trail.template.md").read_text(encoding="utf-8")
    project_name = session.get("project", {}).get("name", "Project")
    sections: list[str] = []
    for crumb in VALUE_TRAIL_CRUMBS:
        if not value_trail_crumb_visible(session, crumb):
            continue
        body = format_value_trail_crumb_body(session, crumb).strip()
        if not body:
            continue
        sections.append(f"## {crumb['title']}\n\n{body}")
    body_text = "\n\n".join(sections)
    return (
        template.replace("PROJECT_NAME", project_name)
        .replace("VALUE_TRAIL_BODY", body_text)
        .rstrip()
        + "\n"
    )


def fill_north_star_blurb(session: dict[str, Any]) -> str:
    """One early paste-ready north-star paragraph (distinct from on-ask ad-lib variations)."""
    template = (ASSETS_DIR / "north-star-blurb.template.md").read_text(encoding="utf-8")
    project_name = session.get("project", {}).get("name", "Project")
    paragraph = compose_outward_pitch(session)
    install = "npx skills add rphoward/Values"
    return (
        template.replace("PROJECT_NAME", project_name)
        .replace("NORTH_STAR_PARAGRAPH", paragraph)
        .replace("NORTH_STAR_INSTALL", install)
    )

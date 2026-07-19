"""Constants and compiled patterns for the value session package."""

from __future__ import annotations

import re
from typing import Any

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
BUILD_PACK_FILES = (
    ("CONTEXT.product.template.md", "CONTEXT.product.md"),
    ("AGENTS.product.template.md", "AGENTS.product.md"),
    ("ui-copy.template.md", "ui-copy.md"),
    ("states-and-flows.template.md", "states-and-flows.md"),
    ("first-value.template.md", "first-value.md"),
    ("north-star-blurb.template.md", "north-star-blurb.md"),
    ("value-trail.template.md", "value-trail.md"),
)
VALUE_TRAIL_CRUMBS: tuple[dict[str, Any], ...] = (
    {"id": "segment", "title": "Who it is for", "sources": ("P01",)},
    {"id": "job", "title": "Progress they want", "sources": ("P11", "P03")},
    {
        "id": "why_outward",
        "title": "Why it matters to someone else",
        "sources": ("P07", "P08"),
    },
    {
        "id": "outward_pitch",
        "title": "Outward pitch",
        "sources": ("P01", "P03", "P11", "P07", "P08"),
    },
    {"id": "offering", "title": "Offering boundary", "sources": ("V01",)},
    {"id": "parts", "title": "What is in the box", "sources": ("V02",)},
    {"id": "relief", "title": "Pain relief claims", "sources": ("V03",)},
    {"id": "gains_created", "title": "Gain creation claims", "sources": ("V04",)},
    {
        "id": "difference",
        "title": "Difference vs alternatives",
        "sources": ("V07",),
    },
    {
        "id": "first_win",
        "title": "Smallest first win",
        "sources": ("P03", "P11", "P08", "P09"),
    },
)
MATCH_BOARD_ATOMS = {
    "V03": ("P07", "pains", "Which offering part reduces which pain, and how?"),
    "V04": ("P08", "gains", "Which offering part creates which gain, and how?"),
}
_NUMBERED_ITEM_RE = re.compile(r"\((\d+)\)\s*")
_LINE_ITEM_RE = re.compile(
    r"(?:^|\n)\s*(?:[-*•]|\(?\d+[\)\].:])\s+",
    flags=re.MULTILINE,
)
_EXTREME_PAIN_RE = re.compile(r"\b(extreme|severe)\b", flags=re.IGNORECASE)
HARD_DECISION_MARKERS = (
    "bypass",
    "orphan",
    "segment boundary",
    "excluded",
    "park",
    "non-goal",
    "out of scope",
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
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MODULE_BRIEF_LABEL = {
    "profile": "Customer profile",
    "value-map": "Value map",
    "business-model": "Business model",
    "experiments": "Experiments",
}
SECTION_STATE_BRIEF = {
    "partial": "in progress",
    "satisfied": "locked",
    "unknown_ok": "locked",
}
SECTION_STRIP_SYMBOLS = {
    "empty": "·",
    "partial": "◐",
    "satisfied": "✓",
    "unknown_ok": "✓?",
}
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

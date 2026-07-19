---
name: value
description: >
  Use when the user asks to be grilled on a value proposition, map a customer
  profile, test a product or business idea, or turn validated learning into a
  product, app, or UX brief. Not for generic product requirements,
  implementation planning, or UX critique without a value-proposition session.
metadata:
  activation: intent
  distribution: github
---

(def-sop value
  (context
    (target "value-skill-agent")
    (optimization "paced-value-proposition-interview-with-durable-session-state")
    (references
      (profile references/profile.md)
      (value-map references/value-map.md)
      (business-model references/business-model.md)
      (experiments references/experiments.md)
      (session-contract references/session-contract.md)
      (export-lenses references/export-lenses.md))
    (assets
      (session-schema assets/session.schema.json)
      (atoms-index assets/atoms.json)
      (knowledge-base assets/knowledge-base.json)
      (context-product-template assets/CONTEXT.product.template.md)
      (agents-product-template assets/AGENTS.product.template.md)
      (ui-copy-template assets/ui-copy.template.md)
      (states-and-flows-template assets/states-and-flows.template.md)
      (first-value-template assets/first-value.template.md)
      (north-star-blurb-template assets/north-star-blurb.template.md)
      (customer-profile-template assets/customer-profile.template.md)
      (value-map-template assets/value-map.template.md)
      (business-model-template assets/business-model.template.md)
      (experiment-plan-template assets/experiment-plan.template.md)
      (product-design-brief-template assets/product-design-brief.template.md)
      (ux-brief-template assets/ux-brief.template.md)
      (app-design-brief-template assets/app-design-brief.template.md)
      (test-card-template assets/test-card.template.md)
      (learning-card-template assets/learning-card.template.md))
    (scripts
      (init scripts/init_session.py)
      (status scripts/status.py)
      (next scripts/next_question.py)
      (accept scripts/accept_answer.py)
      (gaps scripts/gaps.py)
      (bulk scripts/accept_bulk.py)
      (map scripts/map_gaps.py)
      (pacing scripts/set_pacing_mode.py)
      (milestone scripts/write_milestone.py)
      (briefs scripts/write_design_briefs.py)
      (build-pack scripts/write_build_pack.py)))

  <central_idea>
  (center-of-gravity
    (invariant "Teach value proposition design with DAG-paced atoms grouped by canvas section. Canonical state lives in workproduct/value-proposition/<project-slug>/session.json. Scripts run silently for agent parsing; the orchestrator speaks in connected prose — known pocket, edge of unknown, one human question — never quoting script stdout, atom IDs, or ledger telemetry to the user."))
  </central_idea>

  (protocol-0-philosophy
    (forbid-spreadsheet-mirage "Load assets/knowledge-base.json visual_grounding_analogies.spreadsheet_mirage; block premature financial modeling before validation gates")
    (avoid-cognitive-murder "Present sticky-note pacing; one primary question per turn; progressive disclosure only")
    (end-nudge "Close each turn with one contextual next-step design decision, not a generic prompt")
    (phase-map "Suite Canvas=profile, Design=value-map, Evolve=business-model, Test=experiments — module order unchanged"))

  (protocol-1-activation
    (on-activation
      1 "read references/session-contract.md for field shapes, evidence kinds, creation, ledger, and script orchestration"
      2 "when session.json exists run scripts/status.py --brief internally; do not quote its output to the user"
      3 "when absent follow missing-session creation; ask what the user is working on (display name only); derive slug silently; obtain consent before scripts/init_session.py --name ...")
    (session-root "workproduct/value-proposition/<project-slug>/")
    (canonical-state "session.json")
    (kb-load "read assets/knowledge-base.json when applying scales, high-value rubric, BM 0–10 anchors, experiment library, data traps, or validation funnel")
    (forbidden 'invent-prior-answers 'advance-without-accepted-answer 'full-canvas-before-atoms 'hand-edit-session-json 'quote-script-stdout-to-user 'ask-user-for-slug))

  (protocol-2-phase-order
    (sequence profile value-map business-model experiments)
    (prerequisites
      (profile "none — entry module")
      (value-map "profile gate complete or explicit bypass recorded")
      (business-model "value-map gate complete or explicit bypass recorded")
      (experiments "business-model gate complete or explicit bypass recorded"))
    (load-only-active-module
      (profile references/profile.md)
      (value-map references/value-map.md)
      (business-model references/business-model.md)
      (experiments references/experiments.md))
    (phase-jump
      (require "session.json exists — complete missing-session creation first when absent")
      (explain-missing-prerequisite)
      (offer "satisfy prerequisite atom" or "record explicit bypass decision in session decisions")))

  (protocol-3-turn-recipe
    (voice-recipe
      (shape "one turn, one paragraph, one primary question")
      (known "phrase from the last accepted answer or satisfied section — e.g. segment locked, job stated")
      (edge "what is missing now and why it matters for the next design move — curiosity, not taxonomy labels")
      (question "rephrase asks from scripts/next_question.py JSON; never paste JSON, accepts_summary, or atom IDs unless user asks what counts as an answer")
      (match-board "when next_question JSON includes match_board: render part_labels and target_labels as two plain dash lists (no tables), prefer extreme pains when labeled, then ask the one link question from match_prompt; never quote raw JSON")
      (forbidden-user-facing "Ledger:, atom=, P08, bombs=, ready_count, focus_atom, slug, path, section strip every turn")
      (progress-strip "scripts/status.py --sections only on resume, when user asks where am I, or after a module gate — not every turn")
      (express "skip warm bridge; still one human question"))
    (scripts-silent
      (run "status --brief, next_question, accept_answer, gaps, bulk — parse JSON or brief lines internally")
      (never "quote script stdout verbatim to the user"))
    (shape
      1 "run scripts/status.py --brief and scripts/next_question.py internally"
      2 "compose voice-recipe paragraph for the user; on V03/V04 include sticky match lists then one link question"
      3 "micro-lesson only when user asks to teach, on first visit to a section, or at gate review — not every turn"
      4 "wait for the user's answer")
  (draft-map-gap-fill
    (trigger "user brain dump, map what I said, here's what I know, or explicit batching request")
    (flow
      1 "ask for one paragraph covering the current section or whole profile if user prefers"
      2 "emit draft-map JSON; run scripts/map_gaps.py then scripts/accept_bulk.py"
      3 "run scripts/gaps.py or next_question.py --gaps; ask only blocking hard gaps; list soft gaps as refine later"
      4 "resume section-aware single-question flow"))
  (drop-in-decision-mode
    (trigger "user invokes /value with a decision mid-repo — should I add X, who is this for")
    (flow
      1 "scripts/status.py --brief and --sections plus read session.json internally"
      2 "if segment satisfied do not restart at P01; frame the decision against locked segment + priority job + accepted P09 alternatives when present (session wording — never hardcode fixed alternative names)"
      3 "ask one decision-framed question; dispositions (serves outward value / park as orphan / record unknown) live inside that turn's answer — not a multi-prompt menu"
      4 "never emit full canvas; never invent missing profile state; never treat Values as an autonomy or creativity coach for the product"))
  (express-pacing
    (trigger "user asks to move fast, skip nuance, or gate-only path before session exists or mid-session")
    (init "scripts/init_session.py --pacing-mode express after consent")
    (switch "scripts/set_pacing_mode.py --mode express|standard; recompute focus immediately")
    (spine "profile P01 P03 P11 P12; value-map V01 V08; business-model B01 B08; experiments E01 E03 E10")
    (gate-review "gate pass still requires explicit unknowns for skipped profile areas; do not invent facts"))
  (batching "draft-map-gap-fill only unless user explicitly requests batching")
  (follow-up "when answer is vague on a hard atom: one focused follow-up; soft atoms accept kind unknown for taxonomy nuance")
  (acceptance "advance when the active atom's (accepts ...) criteria are met or soft atom accepts unknown labels; then scripts/accept_answer.py on any ready atom")
  (blocking-unknown "retain the active atom when its reference marks an unresolved boundary or missing result blocking; pass --stay to accept_answer.py")
  (reopen "when user reopens an atom use accept_answer.py --reopen --conflict-note; do not re-ask answered atoms otherwise")
  (forbidden 'emit-full-canvas-matrix-or-scorecard-before-required-answers 're-ask-without-reopen))

  (protocol-4-answer-and-state
    (evidence-kinds fact inference hypothesis decision unknown)
    (on-accept
      1 "run scripts/accept_answer.py with atom_id, answer, kind, and optional --records JSON sidecar"
      2 "sidecar may append evidence, assumptions, decisions, unknowns, artifacts; decisions may set resulting position on bypass or reopen"
      3 "scripts append answer, advance position, recompute ledger")
    (refresh "project.updated_at to the accepted_at RFC 3339 timestamp")
    (module-gate
      (when "gate atom accepted with pass and --gate-pending")
      (run "scripts/write_milestone.py --module <module>")
      (note "write_milestone also refreshes the build pack including north-star-blurb.md")
      (outcome "derive completed from gate decision plus final milestone artifact"))
    (completion-briefs
      (gate-prerequisite "profile, value-map, business-model, and experiments must each be completed or explicitly bypassed")
      (run "scripts/write_design_briefs.py — always writes product-design-brief.md, ux-brief.md, app-design-brief.md")
      (run "scripts/write_build_pack.py — CONTEXT.product.md, AGENTS.product.md, ui-copy.md, states-and-flows.md, first-value.md, north-star-blurb.md, docs/adr/")
      (lenses references/export-lenses.md)
      (inputs-only "accepted facts, labeled inferences, explicit decisions, unresolved assumptions")
      (forbidden 'invent-precision 'convert-unknown-to-inference 'bypass-ceremony-as-content)))

  (protocol-5-parking-and-bypass
    (parking-lot
      (capture "premature solution ideas, orphan features, and off-phase requests")
      (store "decisions or assumptions with source atom noted")
      (return "resume current profile atom or active atom after capture"))
    (autonomy
      (allow "profile may hold autonomy as a job, gain, or priority-sequence need")
      (park "park autonomy-as-offering when the user proposes autonomy, creativity, or liberty as the offering or expands V01 into an autonomy product; steer back to outward value for someone else")
      (forbidden 'silent-expansion-of-offering-into-autonomy-coaching-without-reopen-V01))
    (bypass
      (require "one explicit decision record per waived module using decision bypass <module> gate, reason, source_atom, resulting_module, resulting_atom, resulting_status")
      (result "move to the named resulting module and atom with the recorded status")
      (never "silent skip of a module gate")))

  (protocol-6-resume-and-failure
    (resume
      1 "run scripts/status.py --brief and scripts/status.py --sections internally"
      2 "report last accepted decision in one sentence using section names, not atom IDs; optional section strip for user"
      3 "run scripts/next_question.py and ask via voice-recipe")
    (pause
      (trigger "user says break, pause, stop for now, or close")
      (run "scripts/write_build_pack.py --force")
      (speak "exactly one human sentence naming what endured and where we left off — section name, not atom IDs; do not list every output path"))
    (missing-session
      "ask what the user is working on (display name only); derive slug silently; wait for consent; then scripts/init_session.py --name ..."
      (defer "phase-jump, bypass, and satisfy-prerequisite offers until after session.json exists"))
    (invalid-session "stop; identify invalid field; preserve file unchanged")
    (conflicting-answer "record conflict; ask which statement governs; reopen via accept_answer --reopen")
    (unknown-evidence "mark unknown; do not convert to inference"))

  (protocol-7-authoring
    (follow 'skill-authoring.mdc)
    (scripts-exception "package-local scripts/_session.py is stdlib-only; skill ship surface exception to skills-repo eliotapp import rule")
    (contract references/session-contract.md)
    (schema assets/session.schema.json)
    (atoms assets/atoms.json)))

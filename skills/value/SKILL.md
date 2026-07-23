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
      (lean-bridge references/lean-bridge.md)
      (export-lenses references/export-lenses.md))
    (assets
      (session-schema assets/session.schema.json)
      (atoms-index assets/atoms.json)
      (knowledge-base assets/knowledge-base.json)
      (lean-bridge-map assets/lean-bridge-map.json)
      (context-product-template assets/CONTEXT.product.template.md)
      (agents-product-template assets/AGENTS.product.template.md)
      (ui-copy-template assets/ui-copy.template.md)
      (states-and-flows-template assets/states-and-flows.template.md)
      (first-value-template assets/first-value.template.md)
      (north-star-blurb-template assets/north-star-blurb.template.md)
      (value-trail-template assets/value-trail.template.md)
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
      (import-lean scripts/import_lean_context.py)
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
      1 "read references/session-contract.md and references/lean-bridge.md for field shapes, evidence kinds, creation, ledger, and script orchestration"
      2 "when session.json exists run scripts/status.py --brief internally; then scripts/import_lean_context.py <session> internally when lean session exists"
      3 "when absent follow missing-session creation; ask what the user is working on (display name only); derive slug silently; obtain consent before scripts/init_session.py --name ...; then import_lean_context when lean session exists")
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
      (forbidden-user-facing "Ledger:, atom=, atom IDs (P01, V01, B01, E01, etc.), bombs=, ready_count, focus_atom, slug, path, section strip every turn")
      (progress-strip "on resume, when user asks where am I / progress, or after a module gate: run scripts/status.py --sections and show that one strip line to the user; never every turn; never quote --brief or --operator")
      (express "skip warm bridge; still one human question"))
    (scripts-silent
      (run "status --brief, next_question, accept_answer, gaps, bulk — parse JSON or brief lines internally")
      (never "quote script stdout verbatim to the user"))
    (shape
      1 "run scripts/status.py --brief and scripts/next_question.py internally"
      2 "compose voice-recipe paragraph for the user; when next_question includes match_board for pain relievers or gain creators, render sticky match lists then one link question"
      3 "micro-lesson only when user asks to teach, on first visit to a section, or at gate review — not every turn"
      4 "wait for the user's answer")
  (value-map-gate-review
    (trigger "value-map gate review is active or the user reopened the value-map gate — gate only, not every turn")
    (user-language "progress-strip section names only — Offering, Pain relievers, Gain creators, Fit links, Orphan candidates, Differentiation; never atom IDs, internal codes, or cryptic shorthands to the user")
    (turn-1-flow
      1 "run scripts/status.py --sections internally; show progress-strip using those section names"
      2 "Who sticky — segment + freeze in short peer sentences"
      3 "Box sticky — four offering parts as plain dash list, max ~10 words per line per cognitive_murder"
      4 "Honest read — thin gain creators, hypothesis labels, orphan status, one sentence on how this differs from what they do today"
      5 "offer optional depth in plain English: user may ask to walk through Fit links or Differentiation before answering; then ask Does this value map pass its gate now?")
    (expand-fit-links
      (trigger "user asks to walk through fit links, how offering pieces connect to pains and gains, or connection strengths")
      (emit "dash list from accepted fit-links state; label each chain indirect, conditional, or weak — never fake direct"))
    (expand-differentiation
      (trigger "user asks about differentiation, alternatives, or how this beats what they do today")
      (emit "plain comparison against accepted alternatives from session wording — no atom IDs"))
    (ad-lib-on-ask "KB ad-lib-pitch fires only when user asks ad-lib, pitch, or blank formula — never at gate open")
    (forbidden-at-gate
      'mermaid-diagrams
      'tables
      'full-canvas-matrix-or-scorecard
      'monolithic-ad-lib-paragraph
      'three-blank-ad-libs-at-gate-open
      'ad-lib-dump-before-pass-question
      'atom-ids-or-internal-codes-to-user
      'cryptic-drill-triggers))
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
      2 "if segment is satisfied do not restart at segment; frame the decision against locked segment + priority job + accepted alternatives when present (session wording — never hardcode fixed alternative names)"
      3 "ask one decision-framed question; dispositions (serves outward value / park as orphan / record unknown) live inside that turn's answer — not a multi-prompt menu"
      4 "never emit full canvas; never invent missing profile state; never treat Values as an autonomy or creativity coach for the product"))
  (express-pacing
    (trigger "user asks to move fast, skip nuance, or gate-only path before session exists or mid-session")
    (init "scripts/init_session.py --pacing-mode express after consent")
    (switch "scripts/set_pacing_mode.py --mode express|standard; recompute focus immediately")
    (spine "agent-internal schedulable atoms only — profile segment jobs priority-job profile-gate; value-map offering through value-map gate; business-model delivery through business-model gate; experiments hypothesis through experiments gate; never quote spine codes to the user")
    (gate-review "gate pass still requires explicit unknowns for skipped profile areas; do not invent facts; value-map gate uses value-map-gate-review stickies — no Mermaid, tables, ad-lib wall, atom IDs, or cryptic triggers at gate open"))
  (batching "draft-map-gap-fill only unless user explicitly requests batching")
  (follow-up "when answer is vague on a hard atom: one focused follow-up; soft atoms accept kind unknown for taxonomy nuance")
  (acceptance "advance when the active atom's (accepts ...) criteria are met or soft atom accepts unknown labels; then scripts/accept_answer.py on any ready atom")
  (blocking-unknown "retain the active atom when its reference marks an unresolved boundary or missing result blocking; pass --stay to accept_answer.py")
  (reopen
    (when "user asks to revise, change, or reopen a prior answer — e.g. revise segment, pains, job")
    (run "accept_answer.py --reopen --conflict-note; do not re-ask answered atoms otherwise")
    (post-fix "after the supersede lands: one short line that the change is locked and they can say revise <area> anytime — not a every-turn prefix or banner")
    (forbidden 're-ask-without-reopen 'prefix-notification-every-turn 'one-turn-only-edit-unless-explicitly-requested))
  (forbidden 'emit-full-canvas-matrix-or-scorecard-before-required-answers 're-ask-without-reopen 'mermaid-or-tables-at-value-map-gate 'ad-lib-wall-at-value-map-gate-open))

  (protocol-4-answer-and-state
    (human-artifacts "milestones, design briefs, build pack, and ADRs use section headings and customer language only — never atom IDs, source_atom codes, or curriculum numbers in bodies the user may open")
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
      (surface-north-star "after milestone refresh, quote ## Blurb and ## Install from north-star-blurb.md once in chat — paste-ready, not a path scavenger hunt; add one short line naming which value-trail section titles grew")
      (surface-strip "run scripts/status.py --sections and show that one strip line to the user")
      (outcome "derive completed from gate decision plus final milestone artifact"))
    (completion-briefs
      (gate-prerequisite "profile, value-map, business-model, and experiments must each be completed or explicitly bypassed")
      (run "scripts/write_design_briefs.py — always writes product-design-brief.md, ux-brief.md, app-design-brief.md")
      (run "scripts/write_build_pack.py — CONTEXT.product.md, AGENTS.product.md, ui-copy.md, states-and-flows.md, first-value.md, north-star-blurb.md, value-trail.md, docs/adr/")
      (surface-north-star "quote ## Blurb and ## Install from north-star-blurb.md once in chat when the pack is written; add one short line naming which value-trail section titles grew")
      (lenses references/export-lenses.md)
      (inputs-only "accepted facts, labeled inferences, explicit decisions, unresolved assumptions")
      (forbidden 'invent-precision 'convert-unknown-to-inference 'bypass-ceremony-as-content)))
    (north-star-blurb
      (file "north-star-blurb.md under the session root")
      (on-ask "when user asks for discord, blurb, pitch, north star, or paste — read the file and quote ## Blurb plus ## Install in chat")
      (voice "peer Discord: who + freeze + what you get; so-what each feature into daily relief; Connection stays private; follow export-lenses North_Star_Lens and Discord_Update_Blurb; docs/values-discord-intro.md for ship posts")
      (forbidden 'only-mentioning-file-path-without-quoting-body 'requiring-a-canvas-to-see-the-blurb 'ai-slop-pitch-voice 'feature-semicolon-laundry-list 'false-pitch-enthusiasm))
    (value-trail
      (file "value-trail.md under the session root")
      (on-ask "when user asks for trail, breadcrumbs, value record, marketing, or ads — read value-trail.md and quote the trail or newest crumbs in chat")
      (pause-milestone "do not paste the entire trail; quote Discord blurb as today, plus one short line naming which trail section titles grew")
      (forbidden 'path-only-without-quoting-trail 'requiring-a-canvas-to-see-the-trail))

  (protocol-5-parking-and-bypass
    (parking-lot
      (capture "premature solution ideas, orphan features, and off-phase requests")
      (store "decisions or assumptions with source atom noted")
      (return "resume current profile atom or active atom after capture"))
    (autonomy
      (allow "profile may hold autonomy as a job, gain, or priority-sequence need")
      (park "park autonomy-as-offering when the user proposes autonomy, creativity, or liberty as the offering or expands offering boundary into an autonomy product; steer back to outward value for someone else")
      (forbidden 'silent-expansion-of-offering-into-autonomy-coaching-without-reopen-offering-boundary))
    (bypass
      (require "one explicit decision record per waived module using decision bypass <module> gate, reason, source_atom, resulting_module, resulting_atom, resulting_status")
      (result "move to the named resulting module and atom with the recorded status")
      (never "silent skip of a module gate")))

  (protocol-6-resume-and-failure
    (resume
      1 "run scripts/status.py --brief and scripts/status.py --sections internally"
      2 "report last accepted decision in one sentence using section names, not atom IDs; then show the one --sections strip line to the user"
      3 "run scripts/next_question.py and ask via voice-recipe")
    (pause
      (trigger "user says break, pause, stop for now, or close")
      (run "scripts/status.py --sections then scripts/write_build_pack.py --force")
      (speak "one human sentence naming what endured and where we left off — section name, not atom IDs; show the one --sections strip line; do not list every output path")
      (then "quote ## Blurb and ## Install from the refreshed north-star-blurb.md in chat so paste does not require opening the file or a canvas; add one short line naming which value-trail section titles grew — do not paste the full trail"))
    (missing-session
      "ask what the user is working on (display name only); derive slug silently; wait for consent; then scripts/init_session.py --name ..."
      (defer "phase-jump, bypass, and satisfy-prerequisite offers until after session.json exists"))
    (invalid-session "stop; identify invalid field; preserve file unchanged")
    (conflicting-answer "record conflict; ask which statement governs; reopen via accept_answer --reopen")
    (unknown-evidence "mark unknown; do not convert to inference"))

  (protocol-7-authoring
    (follow 'skill-authoring.mdc)
    (scripts-exception "package-local scripts/_session/ is stdlib-only; skill ship surface exception to skills-repo eliotapp import rule")
    (contract references/session-contract.md)
    (schema assets/session.schema.json)
    (atoms assets/atoms.json)))

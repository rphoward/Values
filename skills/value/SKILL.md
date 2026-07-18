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
      (session-contract references/session-contract.md))
    (assets
      (session-schema assets/session.schema.json)
      (customer-profile-template assets/customer-profile.template.md)
      (value-map-template assets/value-map.template.md)
      (business-model-template assets/business-model.template.md)
      (experiment-plan-template assets/experiment-plan.template.md)
      (product-design-brief-template assets/product-design-brief.template.md)
      (ux-brief-template assets/ux-brief.template.md)))

  <central_idea>
  (center-of-gravity
    (invariant "Teach value proposition design one atom at a time. Canonical state lives in workproduct/value-proposition/<project-slug>/session.json. The orchestrator paces turns; module references supply atoms; milestone artifacts come from labeled state only."))
  </central_idea>

  (protocol-1-activation
    (on-activation
      1 "read references/session-contract.md for field shapes, evidence kinds, creation, and failure handling"
      2 "validate session.json against assets/session.schema.json when present"
      3 "when absent, follow the missing-session creation sequence and ask only its one project-identity question")
    (session-root "workproduct/value-proposition/<project-slug>/")
    (canonical-state "session.json")
    (forbidden 'invent-prior-answers 'advance-without-accepted-answer 'full-canvas-before-atoms))

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
    (shape
      1 "orientation — name current module and why this atom follows the last accepted answer"
      2 "micro-lesson or compact original visual analogy when useful — never reproduce book figures"
      3 "one primary question from the active atom"
      4 "wait for the user's answer")
  (batching "up to three tightly related questions only when the user explicitly requests batching")
  (follow-up "when answer is vague, inferred, or missing evidence: one focused follow-up; do not advance")
  (acceptance "advance only when the active atom's (accepts ...) criteria are met")
  (blocking-unknown "retain the active atom when its reference marks an unresolved boundary or missing result blocking")
  (forbidden 'emit-full-canvas-matrix-or-scorecard-before-required-answers))

  (protocol-4-answer-and-state
    (evidence-kinds fact inference hypothesis decision unknown)
    (on-accept
      1 "append answer record with atom_id, answer text, kind, accepted_at"
      2 "update position to the atom's (unlocks ...) target"
      3 "refresh project.updated_at and write session.json immediately")
    (refresh "project.updated_at to the accepted_at RFC 3339 timestamp")
    (module-gate
      (when "module final atom accepted")
      (outcome "derive completed from the gate decision plus final milestone artifact; position remains only the current active atom")
      (write-artifact-from-template
        (profile assets/customer-profile.template.md → customer-profile.md)
        (value-map assets/value-map.template.md → value-map.md)
        (business-model assets/business-model.template.md → business-model.md)
        (experiments assets/experiment-plan.template.md → experiment-plan.md)))
    (completion-briefs
      (gate-prerequisite "profile, value-map, business-model, and experiments must each be completed or explicitly bypassed")
      (inputs-only "accepted facts, labeled inferences, explicit decisions, unresolved assumptions")
      (product-design-brief assets/product-design-brief.template.md)
      (ux-brief assets/ux-brief.template.md)
      (forbidden 'invent-precision 'convert-unknown-to-inference)))

  (protocol-5-parking-and-bypass
    (parking-lot
      (capture "premature solution ideas, orphan features, and off-phase requests")
      (store "decisions or assumptions with source atom noted")
      (return "resume current profile atom or active atom after capture"))
    (bypass
      (require "one explicit decision record per waived module using decision bypass <module> gate, reason, source_atom, resulting_module, resulting_atom, resulting_status")
      (result "move to the named resulting module and atom with the recorded status")
      (never "silent skip of a module gate")))

  (protocol-6-resume-and-failure
    (resume
      1 "read session.json"
      2 "report last accepted decision in one sentence"
      3 "ask the current atom — do not repeat completed questions unless user reopens a decision")
    (missing-session
      "ask project identity only, wait for consent, then write the complete initial document from references/session-contract.md"
      (defer "phase-jump, bypass, and satisfy-prerequisite offers until after session.json exists"))
    (invalid-session "stop; identify invalid field; preserve file unchanged")
    (conflicting-answer "record conflict; ask which statement governs")
    (unknown-evidence "mark unknown; do not convert to inference"))

  (protocol-7-authoring
    (follow 'skill-authoring.mdc)
    (follow 'skills-repo.mdc)
    (contract references/session-contract.md)
    (schema assets/session.schema.json)))

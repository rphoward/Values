(def-ref session-contract
  (linked-from protocol-1 protocol-4 protocol-6 protocol-7)

  (section canonical-fields
    (session-root "workproduct/value-proposition/<project-slug>/")
    (canonical-file "session.json")
    (schema assets/session.schema.json)
    (atoms-index assets/atoms.json)
    (knowledge-base assets/knowledge-base.json)
    (required-top-level
      schema_version
      project
      position
      ledger
      answers
      evidence
      assumptions
      decisions
      unknowns
      artifacts)
    (optional-top-level pacing_mode)
    (schema-version "1.0 or 1.1 — lazy upgrade on read sets 1.1")
    (pacing-mode "standard default; express schedules gate spine only — profile P01 P03 P11 P12, value-map V01 V08, business-model B01 B08, experiments E01 E03 E10")
    (project-fields slug name created_at updated_at)
    (slug-format "lowercase ASCII letters, digits, and single hyphens only; must match ^[a-z0-9]+(?:-[a-z0-9]+)*$")
    (position-fields module atom_id status)
    (module-enum profile value-map business-model experiments)
    (status-enum in_progress gate_pending completed bypassed)
    (atom-pairing "position.module and position.atom_id, plus decision resulting_module and resulting_atom, must be a known pair from the module references")
    (record-atoms "answer atom_id and decision or assumption source_atom must be known atom identifiers"))

  (section missing-session-creation
    (ask-first "project slug and display name only")
    (wait "for the user's project identity answer")
    (ask-consent "one primary question: create workproduct/value-proposition/<project-slug>/session.json?")
    (wait-for "explicit consent before creating session.json")
    (initial-document
      (schema_version "1.1")
      (project
        (slug "confirmed project slug")
        (name "confirmed display name")
        (created_at "current RFC 3339 timestamp")
        (updated_at "same timestamp as created_at"))
      (initial-position profile P01 in_progress)
      (initial-ledger "scripts/init_session.py computes phase Canvas, active_module profile, completion_pct 0, validation_milestone None, unvalidated_bombs empty")
      (initial-arrays answers evidence assumptions decisions unknowns artifacts :empty t)
      (initial-timestamps created_at updated_at :rfc3339 t :same-value t))
    (write "complete schema-valid session.json immediately after consent")
    (forbidden
      'create-before-consent
      'ask-curriculum-question-with-project-identity
      'combine-phase-jump-with-project-identity
      'offer-bypass-or-satisfy-before-session-exists))

  (section evidence-kinds
    (fact "supplied by the user or observed in evidence")
    (inference "reasoned from facts; must be labeled as inference in answer or evidence")
    (hypothesis "unvalidated statement that requires a test")
    (decision "explicit choice with reason recorded")
    (unknown "required information not yet established — never convert to inference"))

  (section ledger
    (shape
      (phase "Canvas | Design | Evolve | Test | Complete — mapped from active module via phase_module_map in knowledge-base")
      (active_module "profile | value-map | business-model | experiments | none")
      (completion_pct "integer 0–100: count of atoms with a current accepted answer divided by total atoms in atoms.json; bypassed modules count all their atoms complete")
      (validation_milestone "None | Problem-Solution Fit | Product-Market Fit | Business Model Fit | Validation Complete")
      (unvalidated_bombs "list of high-criticality assumptions with unsupported or unknown evidence_status"))
    (recompute "scripts/_session.py recomputes ledger on init, accept, status --refresh, milestone, and brief writes")
    (surface "agent opens every turn with scripts/status.py one-line ledger output"))

  (section answer-record
    (shape
      (atom_id "stable atom identifier from active module reference")
      (answer "accepted text for this atom")
      (kind "one of fact inference hypothesis decision unknown")
      (accepted_at "RFC 3339 timestamp"))
    (sidecar "accept_answer.py --records path.json may append evidence assumptions decisions unknowns artifacts in one write")
    (sidecar-shape
      (evidence "array of claim kind source strength")
      (assumptions "array of claim criticality evidence_status source_atom")
      (decisions "array of decision reason source_atom resulting_module resulting_atom resulting_status")
      (unknowns "array of question blocking")
      (artifacts "array of path status upserts"))
    (project-write "set project.updated_at to accepted_at on every accepted answer")
    (append-only "new acceptance appends; reopening a decision adds a superseding record and notes conflict resolution")
    (reopen "only via accept_answer.py --reopen --conflict-note or explicit user reopen request; refuse duplicate accept without reopen")
    (current-answer "latest answers[] record for an atom_id is the current accepted answer"))

  (section position-shape
    (position-only "position is only the current active atom; it is not module history")
    (module "current curriculum module enum")
    (atom_id "active atom id from the loaded module reference")
    (status
      (in_progress "working the current atom")
      (gate_pending "final atom accepted; milestone artifact write due")
      (completed "module gate artifact written")
      (bypassed "module skipped by explicit bypass decision")))

  (section module-outcomes
    (derive "read decisions and artifacts in session.json; do not add a second position")
    (completed "latest gate decision for the module is pass and its milestone artifact status is final")
    (bypassed "latest applicable decision uses decision bypass <module> gate and names the waived module")
    (pending "neither completed nor bypassed by the durable records")
    (precedence "latest applicable gate or bypass decision governs; reopening a module makes it pending until its gate passes and artifact returns to final")
    (forbidden 'infer-completion-from-current-position 'store-parallel-position))

  (section evidence-records
    (shape claim kind source strength)
    (strength "behavioral commitment rank when applicable; spoken feedback remains weak evidence"))

  (section assumptions
    (shape claim criticality evidence_status source_atom)
    (criticality high medium low)
    (evidence_status supported partial unsupported unknown))

  (section decisions
    (shape decision reason source_atom resulting_module resulting_atom resulting_status)
    (resulting-position resulting_module resulting_atom resulting_status)
    (use "bypass records, conflict resolutions, and explicit tradeoffs"))

  (section unknowns
    (shape question blocking)
    (blocking "true when the unknown blocks the current atom or gate"))

  (section artifacts
    (shape path status)
    (status pending draft final)
    (milestones
      customer-profile.md
      value-map.md
      business-model.md
      experiment-plan.md
      product-design-brief.md
      ux-brief.md
      app-design-brief.md))

  (section conflict-handling
    (on-conflict "append a blocking unknown with the conflicting statements; preserve both accepted answers")
    (resolution "append a decision naming the governing statement, reason, source_atom, and resulting position; remove the blocking unknown")
    (forbidden 'silent-overwrite 'advance-without-resolution))

  (section resume-behavior
    (read "session.json and validate against schema")
    (report "last accepted decision in one sentence")
    (ask "current atom only")
    (forbidden 'repeat-completed-atoms 'invent-missing-state))

  (section scheduler
    (atoms-index "assets/atoms.json fields requires section soft per atom; unlocks retained for gate bridges only")
    (ready-set "all atoms whose requires subset is answered and module not bypassed; first atom of each module also requires prior module completed or bypassed")
    (focus-atom "scripts/next_question.py pick among ready set: gate_pending milestone first, then section with fewest satisfied atoms, then lowest atom id")
    (off-position-accept "accept_answer.py allows any ready atom; refuses when atom not in ready set")
    (soft-accept "soft true atoms accept kind unknown for taxonomy labels; orchestrator does not loop on nuance unless user asks to teach")
    (draft-map "agent JSON with mappings array; map_gaps.py dry-run; accept_bulk.py validates and writes")
    (gaps "gaps.py or next_question.py --gaps returns hard_gaps and soft_gaps by section")
    (express "pacing_mode express limits schedulable atoms to module spine; completion_pct counts spine only; set via init_session --pacing-mode or set_pacing_mode.py"))

  (section script-orchestration
    (init scripts/init_session.py — creates session after explicit user consent; agent must not call without consent)
    (status scripts/status.py — one-line ledger; --sections prints section strip; run on activation and open every turn)
    (next scripts/next_question.py — emit scheduler focus atom with section and ready_count; --gaps for gap lists)
    (accept scripts/accept_answer.py — append answer on any ready atom; optional --records sidecar; refuse duplicate without --reopen)
    (gaps scripts/gaps.py — hard and soft gaps by section)
    (bulk scripts/accept_bulk.py — validate draft-map JSON and append multiple answers)
    (map scripts/map_gaps.py — dry-run draft-map without writes)
    (pacing scripts/set_pacing_mode.py — set pacing_mode standard or express and recompute focus)
    (milestone scripts/write_milestone.py — fill module template at gate_pending)
    (briefs scripts/write_design_briefs.py — always writes product-design-brief.md, ux-brief.md, app-design-brief.md)
    (forbidden 'agent-hand-writes-session-json 're-ask-answered-atom-without-reopen))

  (section milestone-writes
    (trigger "module gate_pending after final atom accepted")
    (source "accepted answers and labeled evidence for that module only")
    (brief-prerequisite "derive all four module outcomes from decisions and artifact statuses; each must be completed or bypassed")
    (product-brief "only from accepted facts, labeled inferences, decisions, unresolved assumptions")
    (ux-brief "only from accepted facts, labeled inferences, decisions, unresolved assumptions")
    (app-brief "only from accepted facts, labeled inferences, decisions, unresolved assumptions")
    (forbidden 'score-without-evidence 'full-canvas-before-atoms))

  (section phase-bypass-record
    (prerequisite "session.json exists — if absent, complete missing-session creation first; do not offer bypass or satisfy in the project-identity turn")
    (when "user requests a later phase before prerequisites are met")
    (require
      (decision "exact canonical statement bypass <module> gate naming the waived module")
      (reason "why the prerequisite is waived")
      (source_atom "atom id active when bypass was requested")
      (resulting_module "requested target phase")
      (resulting_atom "first atom id in the target module")
      (resulting_status in_progress))
    (one-record-per-waived-module "record one decision for each skipped module so every bypass outcome is durable")
    (position-update "set position.module, position.atom_id, and position.status exactly to the decision's resulting_module, resulting_atom, and resulting_status")
    (forbidden 'silent-phase-jump))

  (section parking-lot
    (capture "premature solutions, orphan features, off-phase ideas")
    (store "assumptions or decisions with source_atom reference")
    (return "active atom after capture")))

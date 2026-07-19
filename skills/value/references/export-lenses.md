(def-ref export-lenses
  (linked-from protocol-4 protocol-7)

  (note "Sift lenses map session.json into IDE-standard files. Write these even when the user has no Pocock or pstack skills — those skills are readers of the same shapes.")

  (section files
    (CONTEXT.product.md "customer-domain glossary; Term/_Avoid_ when tightened")
    (docs/adr "one short ADR per hard Value decision")
    (ui-copy.md "microcopy for hero, empty, error, success, trust")
    (states-and-flows.md "critical paths + Empty/Loading/Success/Error/Recovery")
    (first-value.md "first-session win and what to hide")
    (AGENTS.product.md "Always / Ask first / Never product walls")
    (script scripts/write_build_pack.py))

  (section Glossary_Lens
    (principle "Emit CONTEXT.product.md as a customer-domain glossary only.")
    (trigger "Profile gate complete, or P01–P03 plus named pains/gains; or user asks for shared language.")
    (guiding_principle "One term per concept. Define what it IS in the customer's world. Never put stack or UI chrome here. Prefer customer words from accepted answers."))

  (section Decision_Lens
    (principle "Emit short ADRs under docs/adr/ for hard-to-reverse Value decisions.")
    (trigger "decisions[] with bypass, orphan, segment boundary, exclusion, park, or out of scope.")
    (guiding_principle "One paragraph: context, decision, why. Skip soft atom accepts. Cite source_atom for agents."))

  (section Agent_Boundary_Lens
    (principle "Emit AGENTS.product.md with Always / Ask first / Never.")
    (trigger "bombs, blocking unknowns, orphans, segment exclusion; or coding handoff.")
    (guiding_principle "Always = segment + evidence labels. Ask first = bombs and blocking unknowns. Never = orphans, inventing past unknown. No build commands."))

  (section UI_State_Lens
    (principle "Emit states-and-flows.md for 1–3 critical paths with required states.")
    (trigger "P02–P03 accepted and a pain reliever or gain creator exists; or UX handoff.")
    (guiding_principle "Follow job progress, not sitemap. Weight Empty and Error. Cap at critical paths."))

  (section UI_Copy_Lens
    (principle "Emit ui-copy.md keyed to those states.")
    (trigger "same as UI_State_Lens, or user asks for microcopy / hero / onboarding copy.")
    (guiding_principle "Steal phrasing from accepted answers. Label evidence kind. Leave unknown as unknown — do not invent charm."))

  (section First_Value_Lens
    (principle "Emit first-value.md for first-session win and what to hide.")
    (trigger "priority job or top pains/gains; or demo / sampling / activation talk.")
    (guiding_principle "Smallest observable win against current alternative. Hide orphans. Name bombs that block a honest first run."))

  (section inputs-only
    (allow "accepted facts, labeled inferences, explicit decisions, unresolved assumptions and unknowns")
    (forbidden 'bypass-ceremony-as-content 'invent-precision 'convert-unknown-to-inference 'quote-atom-ids-in-user-facing-copy)))

(def-ref export-lenses
  (linked-from protocol-4 protocol-7)

  (note "Sift lenses map session.json into IDE-standard files. Write these even when the user has no Pocock or pstack skills — those skills are readers of the same shapes.")

  (section files
    (CONTEXT.product.md "customer-domain glossary; Term/_Avoid_ when tightened")
    (docs/adr "one short ADR per hard Value decision")
    (ui-copy.md "microcopy for hero, empty, error, success, trust")
    (states-and-flows.md "critical paths + Empty/Loading/Success/Error/Recovery")
    (first-value.md "first-session win and what to hide")
    (north-star-blurb.md "Discord paste lens: one outward paragraph plus install CTA; body matches value-trail outward pitch")
    (value-trail.md "intentional-value spine: progressive sticky crumbs from accepted answers")
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
    (guiding_principle "Prefer customer language already on value-trail.md when present. Steal phrasing from accepted answers. Label evidence kind. Leave unknown as unknown — do not invent charm."))

  (section First_Value_Lens
    (principle "Emit first-value.md for first-session win and what to hide.")
    (trigger "priority job or top pains/gains; or demo / sampling / activation talk.")
    (guiding_principle "Prefer customer language already on value-trail.md when present. Smallest observable win against current alternative. Hide orphans. Name bombs that block a honest first run."))

  (section Value_Trail_Lens
    (principle "Emit value-trail.md as the intentional-value spine — sticky progressive crumbs, not a path dump.")
    (trigger "every build-pack refresh including --force on pause; grows as profile and value-map answers land.")
    (guiding_principle "One section per answered crumb in registry order. Sticky customer language with evidence kind. Outward pitch paragraph shared with north-star blurb body. Progressive disclosure like cognitive_murder; segment fit like pregnant_man_trap and fit_check_rules; no spreadsheet_mirage precision. Do not emit V08 three ad-libs, atom IDs, or Ledger lines.")
    (surface "on-ask for trail, breadcrumbs, value record, marketing, or ads — quote trail or newest crumbs in chat; on pause/milestone quote Discord blurb plus one short line naming which trail section titles grew — never paste the full trail")
    (forbidden 'claim-validated-demand 'path-only-without-quoting-trail 'requiring-a-canvas 'install-cta-in-trail))

  (section North_Star_Lens
    (principle "Emit north-star-blurb.md as Discord paste lens: outward pitch paragraph plus install CTA only here.")
    (trigger "every build-pack run including --force on pause; also after profile milestone so a blurb exists before value-map completes.")
    (guiding_principle "Body from value-trail outward_pitch crumb (who P01, job P03/P11, why P07/P08). Plain Discord text. Mark draft from accepted session state. Do not duplicate V08 three Blank ad-lib variations.")
    (surface "orchestrator quotes ## Blurb and ## Install in chat on milestone, pause, completion, and on-ask — file is backup, not the only door; add one short line naming which value-trail section titles grew since last refresh")
    (forbidden 'claim-validated-demand 'autonomy-as-offering-without-reopen 'path-only-without-quoting-blurb))

  (section inputs-only
    (allow "accepted facts, labeled inferences, explicit decisions, unresolved assumptions and unknowns")
    (forbidden 'bypass-ceremony-as-content 'invent-precision 'convert-unknown-to-inference 'quote-atom-ids-in-user-facing-copy 'autonomy-as-offering-without-reopen)))

(def-ref lean-bridge
  (linked-from protocol-1 protocol-2)

  (section shared-slug
    (rule "value and lean-mvp skills use the same project slug under workproduct/")
    (value-root "workproduct/value-proposition/<slug>/")
    (lean-root "workproduct/lean-mvp/<slug>/"))

  (section detection
    (on-activation-after-session-exists
      1 "resolve slug from value session.json project.slug"
      2 "if workproduct/lean-mvp/<slug>/session.json exists run scripts/import_lean_context.py <session-path> internally"
      3 "parse JSON stdout; never quote raw script output to the user unless user asks for import details")
    (on-activation-before-value-session
      1 "during missing-session creation derive slug silently from display name"
      2 "after init_session.py if lean session exists for same slug run import_lean_context.py before first grill question"))

  (section mapping
    (bridge-asset assets/lean-bridge-map.json)
    (atom_map
      (C01 P01 "segment")
      (MS01 P09 "alternatives as competitors column"))
    (import-behavior
      (skip "value atoms that already have accepted answers")
      (provenance "lean-import on imported answer records")
      (never "overwrite user-accepted value answers with lean imports")))

  (section artifacts
    (read "workproduct/lean-mvp/<slug>/customer-context.md for human-readable context only — do not treat as canonical over session.json")
    (never "write lean-mvp paths from the value skill"))

  (check lean-read-only "lean-mvp skill files are never modified by value activation"))

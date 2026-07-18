(def-ref value-map
  (linked-from protocol-2 protocol-3 protocol-4)
  (purpose "Define how one offering serves the accepted profile and park unmatched features for explicit decisions.")
  (evidence-policy "Use only accepted profile state as the fit baseline. Preserve every inference, hypothesis, decision, and unknown label.")

  (atom
    (id V01)
    (name "offering boundary")
    (teaches "A value map covers one offering for the accepted segment and priority job. Choosing that scope is a decision; a user-supported description keeps its original evidence kind rather than being upgraded to fact.")
    (asks "Which single offering are we mapping?")
    (accepts "Names one offering and at least one boundary exclusion; labels an explicit scope choice decision and preserves another user-supported kind, while an unresolved boundary creates a blocking unknown and keeps V01 active.")
    (writes "append answers record {atom_id V01, answer accepted text, kind decision for an explicit scope choice or the accepted supported kind, accepted_at current RFC 3339 timestamp}; when boundary is accepted append decisions record {decision accepted offering boundary, reason accepted scope reason, source_atom V01, resulting_module value-map, resulting_atom V02, resulting_status in_progress}; when boundary is unresolved append unknowns record {question offering boundary not established, blocking true}; set project.updated_at to accepted_at; when boundary is unresolved keep position.module value-map, position.atom_id V01, position.status in_progress; when boundary is accepted set position.module value-map, position.atom_id V02, position.status in_progress")
    (unlocks "when boundary is unresolved keep V01; when boundary is accepted unlock V02"))

  (atom
    (id V02)
    (name "products and services")
    (teaches "Products and services are the concrete things the customer can receive or use, whether physical, service-based, digital, or financial. Listing them now establishes the parts whose effects must be justified next.")
    (asks "What products or services are actually included in this offering?")
    (accepts "Lists concrete included items and distinguishes established scope from hypotheses; avoids claiming benefits in place of deliverables.")
    (writes "append answers record {atom_id V02, answer accepted text, kind accepted fact or hypothesis label, accepted_at current RFC 3339 timestamp}; when unconfirmed append assumptions record {claim proposed included product or service, criticality medium, evidence_status unknown, source_atom V02}; set project.updated_at to accepted_at; set position.module value-map, position.atom_id V03, position.status in_progress")
    (unlocks V03))

  (atom
    (id V03)
    (name "pain relievers")
    (teaches "A pain reliever states how an included item reduces a specific accepted pain. It follows the offering list so relief claims can be traced to something the offering actually does.")
    (asks "How does each relevant part of the offering reduce a specific accepted customer pain?")
    (accepts "Links each proposed relief to an included item and an accepted pain, states the expected reduction, and labels unsupported effects as hypotheses.")
    (writes "append answers record {atom_id V03, answer accepted text, kind hypothesis, accepted_at current RFC 3339 timestamp}; append assumptions record {claim proposed pain relief, criticality high, evidence_status unsupported or partial, source_atom V03}; set project.updated_at to accepted_at; set position.module value-map, position.atom_id V04, position.status in_progress")
    (unlocks V04))

  (atom
    (id V04)
    (name "gain creators")
    (teaches "A gain creator states how the offering produces an accepted essential, expected, desired, or unexpected outcome. Separating creation from pain relief prevents the same claim from doing double duty without evidence.")
    (asks "How does each relevant part of the offering create a specific accepted customer gain?")
    (accepts "Links each proposed effect to an included item and accepted gain, states the expected outcome, and labels unsupported effects as hypotheses.")
    (writes "append answers record {atom_id V04, answer accepted text, kind hypothesis, accepted_at current RFC 3339 timestamp}; append assumptions record {claim proposed gain creation, criticality medium, evidence_status unsupported or partial, source_atom V04}; set project.updated_at to accepted_at; set position.module value-map, position.atom_id V05, position.status in_progress")
    (unlocks V05))

  (atom
    (id V05)
    (name "job alignment")
    (teaches "Fit requires traceable links from offering items and effects to accepted jobs, pains, or gains. Checking alignment now reveals both supported value and claims that have no profile basis.")
    (asks "Which accepted job, pain, or gain does each offering item, pain reliever, and gain creator serve?")
    (accepts "Provides a traceable match for every listed item or marks it unmatched; does not invent a profile claim to manufacture fit.")
    (writes "append answers record {atom_id V05, answer accepted text, kind accepted inference or unknown label, accepted_at current RFC 3339 timestamp}; when unsupported append assumptions record {claim proposed profile alignment, criticality high, evidence_status unsupported, source_atom V05}; when missing append unknowns record {question required profile link not established, blocking false}; set project.updated_at to accepted_at; set position.module value-map, position.atom_id V06, position.status in_progress")
    (unlocks V06))

  (atom
    (id V06)
    (name "orphan candidates")
    (teaches "An unmatched item is an orphan candidate, not automatic waste. Parking it preserves the idea while forcing an explicit later decision to support, test, change, or remove it.")
    (asks "Which unmatched items are orphan candidates?")
    (accepts "Names every unmatched item and records a deferred support, test, change, or remove decision; an empty list is accepted only when V05 matched every item.")
    (writes "append answers record {atom_id V06, answer accepted text, kind decision, accepted_at current RFC 3339 timestamp}; for each parked candidate append assumptions record {claim orphan candidate needs a support, test, change, or remove decision, criticality medium, evidence_status unknown, source_atom V06}; append decisions record {decision park named orphan candidates, reason accepted deferred disposition reason, source_atom V06, resulting_module value-map, resulting_atom V07, resulting_status in_progress}; set project.updated_at to accepted_at; set position.module value-map, position.atom_id V07, position.status in_progress")
    (unlocks V07))

  (atom
    (id V07)
    (name "alternative distinction")
    (teaches "Value is relative to what the customer does today, including workarounds and inaction. Comparing against accepted alternatives now tests whether the mapped effects create a meaningful difference.")
    (asks "What meaningful difference does this offering provide over the accepted current alternatives for the priority job?")
    (accepts "States at least one specific difference tied to an accepted job, pain, or gain and labels its evidence; records no established difference as unknown.")
    (writes "append answers record {atom_id V07, answer accepted text, kind accepted fact, inference, hypothesis, or unknown label, accepted_at current RFC 3339 timestamp}; when supported append evidence record {claim accepted alternative distinction, kind accepted fact or inference label, source accepted source, strength accepted strength}; when unsupported append assumptions record {claim proposed alternative distinction, criticality high, evidence_status unsupported, source_atom V07}; when no distinction is established append unknowns record {question meaningful alternative distinction not established, blocking false}; set project.updated_at to accepted_at; set position.module value-map, position.atom_id V08, position.status in_progress")
    (unlocks V08))

  (atom
    (id V08)
    (name "value-map gate")
    (teaches "The value-map gate checks that the offering boundary, effects, fit links, alternatives, and orphan decisions are explicit. Passing confirms a coherent design hypothesis, not proven customer demand.")
    (asks "Does this value map pass its gate now?")
    (accepts "Records an explicit pass or reopen decision with a reason and target atom; pass requires offering scope, mapped effects, fit links, alternative distinction, and parked orphan candidates or an explicit empty set.")
    (writes "append answers record {atom_id V08, answer accepted text, kind decision, accepted_at current RFC 3339 timestamp}; append decisions record {decision pass or reopen value-map gate, reason accepted reason, source_atom V08, resulting_module value-map, resulting_atom V08 or chosen value-map atom, resulting_status gate_pending or in_progress}; on pass upsert artifacts record {path value-map.md, status pending}; set project.updated_at to accepted_at; set position.module value-map, position.atom_id V08 or chosen value-map atom, position.status gate_pending or in_progress exactly as the decision")
    (unlocks "value-map gate: write value-map.md from accepted value-map state, set its artifact status final so completion derives from the pass decision plus artifact, then set position to business-model/B01/in_progress")))

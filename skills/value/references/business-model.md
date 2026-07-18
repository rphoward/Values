(def-ref business-model
  (linked-from protocol-2 protocol-3 protocol-4)
  (purpose "Describe how the accepted value map is delivered, funded, operated, scaled, and defended.")
  (score-policy "A 0–10 score is only a discussion aid accompanied by reasons and evidence. Store unknown when evidence cannot support a score.")

  (atom
    (id B01)
    (name "delivery channel")
    (teaches "A channel is how the segment discovers, evaluates, buys, receives, and uses the offering. Delivery comes first because the accepted value map has no business effect unless it can reach the customer.")
    (asks "Through which concrete channel path will the accepted segment discover, buy, receive, and use this offering?")
    (accepts "Describes the applicable channel stages and labels untested stages as hypotheses or unknowns; does not infer customer behavior from the design alone.")
    (writes "append answers record {atom_id B01, answer accepted text, kind accepted fact, hypothesis, or unknown label, accepted_at current RFC 3339 timestamp}; when untested append assumptions record {claim proposed channel behavior, criticality high, evidence_status unknown, source_atom B01}; when missing append unknowns record {question required channel stage not established, blocking false}; set project.updated_at to accepted_at; set position.module business-model, position.atom_id B02, position.status in_progress")
    (unlocks B02))

  (atom
    (id B02)
    (name "customer relationship")
    (teaches "The customer relationship describes the human or automated support required before, during, and after delivery. It follows the channel so relationship work is tied to actual customer contact points.")
    (asks "What relationship must the business maintain with this segment across the accepted channel path?")
    (accepts "Names required acquisition, onboarding, service, retention, or exit interactions and who performs them; marks unestablished requirements unknown.")
    (writes "append answers record {atom_id B02, answer accepted text, kind accepted fact, hypothesis, or unknown label, accepted_at current RFC 3339 timestamp}; when unsupported append assumptions record {claim proposed customer relationship requirement, criticality medium, evidence_status unknown, source_atom B02}; when unresolved append unknowns record {question relationship ownership not established, blocking false}; set project.updated_at to accepted_at; set position.module business-model, position.atom_id B03, position.status in_progress")
    (unlocks B03))

  (atom
    (id B03)
    (name "revenue behavior")
    (teaches "Revenue behavior covers who pays, what they commit, whether payment repeats, and whether cash arrives before or after delivery costs. It comes after channels and relationships because those choices shape both willingness to pay and collection timing.")
    (asks "What payment behavior will fund this offering?")
    (accepts "States payer, exchange, recurrence, and cash timing with evidence labels; any 0–10 discussion score includes a reason and source, otherwise remains unknown.")
    (writes "append answers record {atom_id B03, answer accepted text, kind accepted fact, hypothesis, or unknown label, accepted_at current RFC 3339 timestamp}; when observed append evidence record {claim accepted payment behavior, kind fact, source accepted source, strength accepted strength}; when untested append assumptions record {claim proposed revenue behavior, criticality high, evidence_status unknown, source_atom B03}; when absent append unknowns record {question revenue or score evidence not established, blocking false}; set project.updated_at to accepted_at; set position.module business-model, position.atom_id B04, position.status in_progress")
    (unlocks B04))

  (atom
    (id B04)
    (name "key activities and resources")
    (teaches "Key activities are the work the model must perform, and key resources are the assets or capabilities that work consumes. Identifying them now translates the promised delivery and relationship into operational requirements.")
    (asks "Which activities and resources are indispensable to deliver the accepted value map through this model?")
    (accepts "Names indispensable work and assets, identifies whether the business, customers, or partners perform the work, and labels unverified capacity unknown.")
    (writes "append answers record {atom_id B04, answer accepted text, kind accepted fact, hypothesis, or unknown label, accepted_at current RFC 3339 timestamp}; when unsupported append assumptions record {claim proposed capacity or work ownership, criticality high, evidence_status unknown, source_atom B04}; when missing append unknowns record {question activity or resource ownership not established, blocking false}; set project.updated_at to accepted_at; set position.module business-model, position.atom_id B05, position.status in_progress")
    (unlocks B05))

  (atom
    (id B05)
    (name "partners and costs")
    (teaches "Partners supply work or resources the business does not provide alone, while costs reveal what those choices require. This follows internal operations so partner dependence and structural cost claims can be compared with the actual delivery model.")
    (asks "What external support and spending does this model require?")
    (accepts "Names required partners, dependencies, and principal costs; a claimed cost advantage or 0–10 discussion score includes reasons and evidence, otherwise remains unknown.")
    (writes "append answers record {atom_id B05, answer accepted text, kind accepted fact, hypothesis, or unknown label, accepted_at current RFC 3339 timestamp}; when observed append evidence record {claim accepted partner, cost, or cost advantage, kind fact, source accepted source, strength accepted strength}; when untested append assumptions record {claim proposed partner or cost requirement, criticality high, evidence_status unknown, source_atom B05}; when unsupported append unknowns record {question cost advantage evidence not established, blocking false}; set project.updated_at to accepted_at; set position.module business-model, position.atom_id B06, position.status in_progress")
    (unlocks B06))

  (atom
    (id B06)
    (name "scale constraints")
    (teaches "Scale depends on where demand increases scarce labor, capital, inventory, support, or partner capacity. Examining constraints after activities and costs shows what grows linearly and what can be reused.")
    (asks "What becomes the first binding constraint as demand grows?")
    (accepts "Advances only when a likely constraint, its growth behavior, and a labeled basis are supplied; an unknown records a blocking unknown and keeps B06 active without invention. Any scalability score is reasoned evidence-backed discussion, otherwise unknown.")
    (writes "append answers record {atom_id B06, answer accepted text, kind accepted fact, hypothesis, or unknown label, accepted_at current RFC 3339 timestamp}; when observed append evidence record {claim accepted scale constraint, kind fact, source accepted source, strength accepted strength}; when projected append assumptions record {claim proposed scale constraint, criticality high, evidence_status unknown, source_atom B06}; when constraint is unknown append unknowns record {question first binding scale constraint not established, blocking true}; set project.updated_at to accepted_at; when constraint is unknown keep position.module business-model, position.atom_id B06, position.status in_progress; when constraint is accepted set position.module business-model, position.atom_id B07, position.status in_progress")
    (unlocks "when constraint is unknown keep B06; when constraint is accepted unlock B07"))

  (atom
    (id B07)
    (name "switching and defensibility")
    (teaches "Switching behavior and defensibility describe why customers might stay and why competitors cannot quickly erase the model's advantage. They come last in the model analysis because credible protection must arise from accepted delivery, relationship, revenue, resource, or partner choices.")
    (asks "What evidenced switching behavior or hard-to-copy model advantage could protect this business?")
    (accepts "Names a concrete switching factor or defensibility mechanism and its evidence, or records none established; any 0–10 discussion score includes reasons and a source, otherwise unknown.")
    (writes "append answers record {atom_id B07, answer accepted text, kind accepted fact, hypothesis, or unknown label, accepted_at current RFC 3339 timestamp}; when observed append evidence record {claim accepted switching or defensibility behavior, kind fact, source accepted source, strength accepted strength}; when untested append assumptions record {claim proposed switching or defensibility mechanism, criticality medium, evidence_status unknown, source_atom B07}; when absent append unknowns record {question switching or defensibility evidence not established, blocking false}; set project.updated_at to accepted_at; set position.module business-model, position.atom_id B08, position.status in_progress")
    (unlocks B08))

  (atom
    (id B08)
    (name "business-model gate")
    (teaches "The business-model gate checks that delivery, relationships, revenue behavior, operations, partners, costs, constraints, and protection are explicit. Passing means the model is testable; unknown scores and assumptions remain visible rather than becoming invented precision.")
    (asks "Does this business model pass its gate now?")
    (accepts "Records an explicit pass or reopen decision with a reason and target atom; pass requires every model area to contain accepted content or an explicit unknown.")
    (writes "append answers record {atom_id B08, answer accepted text, kind decision, accepted_at current RFC 3339 timestamp}; append decisions record {decision pass or reopen business-model gate, reason accepted reason, source_atom B08, resulting_module business-model, resulting_atom B08 or chosen business-model atom, resulting_status gate_pending or in_progress}; on pass upsert artifacts record {path business-model.md, status pending}; set project.updated_at to accepted_at; set position.module business-model, position.atom_id B08 or chosen business-model atom, position.status gate_pending or in_progress exactly as the decision")
    (unlocks "business-model gate: write business-model.md from accepted business-model state, set its artifact status final so completion derives from the pass decision plus artifact, then set position to experiments/E01/in_progress")))

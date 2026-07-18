(def-ref experiments
  (linked-from protocol-2 protocol-3 protocol-4)
  (purpose "Turn the accepted profile, value map, and business model into one evidence-seeking experiment and a recorded next decision.")
  (evidence-policy "Behavior and commitment are stronger evidence than polite agreement. Keep unsupported claims and absent results labeled hypothesis or unknown.")
  (kb assets/knowledge-base.json)
  (lit-fuse-priority "Rank by criticality to survival vs evidence gap; load visual_grounding_analogies.business_killer_bomb")
  (experiment-library experiment_library)
  (data-traps data_traps)
  (validation-funnel validation_funnel)
  (card-templates
    (test-card assets/test-card.template.md)
    (learning-card assets/learning-card.template.md))
  (funnel-rule "Never test willingness to pay before interest and preference are validated")

  (atom
    (id E01)
    (name "assumption inventory")
    (teaches "An assumption states what must be true for the accepted design to work. Inventorying desirability, feasibility, and viability assumptions first prevents the easiest test from displacing the most important uncertainty.")
    (asks "Which assumptions must be true for this design to succeed?")
    (accepts "States at least one falsifiable assumption in each applicable category and labels any category not yet understood unknown.")
    (writes "append answers record {atom_id E01, answer accepted assumption inventory, kind hypothesis, accepted_at current RFC 3339 timestamp}; when missing append unknowns record {question required assumption category not established, blocking false}; set project.updated_at to accepted_at; set position.module experiments, position.atom_id E02, position.status in_progress")
    (unlocks E02))

  (atom
    (id E02)
    (name "criticality and evidence")
    (teaches "Criticality describes the harm if an assumption is false, while evidence status describes how well it is supported now. Comparing both makes high-impact, weakly supported claims visible without pretending that a rank is proof.")
    (kb lit-fuse-priority)
    (asks "How should the inventoried assumptions be ranked for testing?")
    (accepts "Assigns high, medium, or low criticality and supported, partial, unsupported, or unknown evidence status to each assumption, citing evidence records where available.")
    (writes "append answers record {atom_id E02, answer accepted text, kind inference, accepted_at current RFC 3339 timestamp}; for each ranked claim append assumptions record {claim accepted assumption, criticality accepted high, medium, or low value, evidence_status accepted supported, partial, unsupported, or unknown value, source_atom E02}; when cited append evidence record {claim evidence supporting ranked assumption, kind accepted fact or inference label, source accepted source, strength accepted strength}; when absent append unknowns record {question evidence for ranked assumption not established, blocking false}; set project.updated_at to accepted_at; set position.module experiments, position.atom_id E03, position.status in_progress")
    (unlocks E03))

  (atom
    (id E03)
    (name "highest-risk hypothesis")
    (teaches "The highest-risk hypothesis combines serious consequences with weak evidence. Choosing one now focuses the next experiment on learning that could change the design rather than confirming a comfortable detail.")
    (asks "Which assumption should be tested next?")
    (accepts "Selects one inventoried assumption, states the consequence of failure and current evidence gap, and records the choice as a decision.")
    (writes "append answers record {atom_id E03, answer accepted text, kind decision, accepted_at current RFC 3339 timestamp}; append decisions record {decision selected highest-risk hypothesis, reason accepted ranking reason, source_atom E03, resulting_module experiments, resulting_atom E04, resulting_status in_progress}; set project.updated_at to accepted_at; set position.module experiments, position.atom_id E04, position.status in_progress")
    (unlocks E04))

  (atom
    (id E04)
    (name "experiment choice")
    (teaches "An experiment creates an observable chance for the selected hypothesis to fail. The method follows the hypothesis so its action, participants, and setting measure the claim rather than general interest.")
    (kb experiment-library)
    (asks "What smallest ethical experiment could expose the selected hypothesis to observable customer behavior?")
    (accepts "Names participants, setup, action, and observation tied directly to the selected hypothesis; labels unverified access or feasibility as assumptions.")
    (writes "append answers record {atom_id E04, answer accepted text, kind hypothesis, accepted_at current RFC 3339 timestamp}; when unverified append assumptions record {claim proposed setup or participant access, criticality high, evidence_status unknown, source_atom E04}; set project.updated_at to accepted_at; set position.module experiments, position.atom_id E05, position.status in_progress")
    (unlocks E05))

  (atom
    (id E05)
    (name "metric and threshold")
    (teaches "A metric specifies what the experiment observes, and a threshold states the result that would support the hypothesis before data arrives. Defining both now prevents the team from moving the goal after seeing results.")
    (asks "What result would count as support for this hypothesis?")
    (accepts "Defines one observable metric, a numerical or unambiguous threshold, a time window, and the result classification; records unavailable baseline information as unknown.")
    (writes "append answers record {atom_id E05, answer accepted text, kind decision, accepted_at current RFC 3339 timestamp}; when unsupported append assumptions record {claim proposed metric threshold rationale, criticality high, evidence_status unknown, source_atom E05}; when missing append unknowns record {question metric baseline not established, blocking false}; set project.updated_at to accepted_at; set position.module experiments, position.atom_id E06, position.status in_progress")
    (unlocks E06))

  (atom
    (id E06)
    (name "evidence-quality defense")
    (teaches "Evidence quality depends on whether the observation could occur without the claimed demand and whether the test explores only one familiar direction. Reviewing those risks now strengthens interpretation before the experiment runs.")
    (visual "Use two checks: a signal filter rejects results explainable by politeness, while a wider-map check asks whether the test merely improves one small hill without comparing another route.")
    (kb data-traps visual_grounding_analogies.pregnant_man_trap visual_grounding_analogies.local_maximum_hill)
    (asks "How strong is the evidence this experiment is designed to produce?")
    (accepts "Names the required customer behavior or commitment, at least one alternative explanation, and one credible alternative direction or reason it is out of scope; spoken agreement alone is weak evidence.")
    (writes "append answers record {atom_id E06, answer accepted text, kind inference, accepted_at current RFC 3339 timestamp}; append evidence record {claim planned experiment signal, kind hypothesis, source planned experiment behavior or commitment, strength accepted expected strength}; when unresolved append unknowns record {question false-positive explanation or alternative direction not resolved, blocking false}; set project.updated_at to accepted_at; set position.module experiments, position.atom_id E07, position.status in_progress")
    (unlocks E07))

  (atom
    (id E07)
    (name "test card")
    (teaches "A test card turns prior choices into an executable agreement: hypothesis, method, metric, threshold, owner, and time window. Assembling it now makes responsibility and interpretation explicit before observations begin.")
    (kb test-card-template assets/test-card.template.md)
    (asks "Do you accept the assembled test card as written?")
    (accepts "Confirms or corrects a card containing title, owner, timing, criticality, hypothesis, method, metric, and threshold; acceptance is an explicit decision.")
    (writes "append answers record {atom_id E07, answer accepted text, kind decision, accepted_at current RFC 3339 timestamp}; append decisions record {decision accept assembled test card, reason accepted approval or correction reason, source_atom E07, resulting_module experiments, resulting_atom E08, resulting_status in_progress}; upsert artifacts record {path experiment-plan.md, status draft}; set project.updated_at to accepted_at; set position.module experiments, position.atom_id E08, position.status in_progress")
    (unlocks E08))

  (atom
    (id E08)
    (name "learning card")
    (teaches "A learning card separates what was believed, what was observed, and what may reasonably be learned. E08 waits until a test result exists; if it does not, record a blocking unknown rather than infer a result.")
    (kb learning-card-template assets/learning-card.template.md)
    (asks "What observable result did the test produce?")
    (accepts "Advances only with the prior hypothesis, raw observation, source, evidence strength, and labeled learning; a no-run or incomplete result creates a blocking unknown and keeps E08 active.")
    (writes "append answers record {atom_id E08, answer accepted result or missing-result text, kind accepted fact or unknown label, accepted_at current RFC 3339 timestamp}; when observed append evidence record {claim raw test result, kind fact, source accepted test source, strength accepted strength}; when interpreted append evidence record {claim labeled learning, kind inference, source accepted raw-result evidence, strength accepted strength}; when result is absent append unknowns record {question test result not yet available, blocking true}; set project.updated_at to accepted_at; when result is absent keep position.module experiments, position.atom_id E08, position.status in_progress; when result is accepted set position.module experiments, position.atom_id E09, position.status in_progress")
    (unlocks "when result is absent keep E08; when result is accepted unlock E09"))

  (atom
    (id E09)
    (name "next decision")
    (teaches "A result matters when it changes a decision. Choosing to proceed, revise, pivot, stop, or run another test now ties action to the threshold and evidence quality rather than enthusiasm.")
    (asks "What should change next because of this result?")
    (accepts "Chooses one concrete next action, cites the accepted result and threshold, and explains the reason. A new governing assumption is appended only with an accepted high, medium, or low criticality; otherwise its missing criticality remains an explicit nonblocking unknown.")
    (writes "append answers record {atom_id E09, answer accepted text, kind decision, accepted_at current RFC 3339 timestamp}; append decisions record {decision accepted next design action, reason accepted threshold and evidence reason, source_atom E09, resulting_module experiments, resulting_atom E10, resulting_status in_progress}; when criticality is accepted append assumptions record {claim accepted assumption governing further work, criticality accepted high, medium, or low value, evidence_status unknown, source_atom E09}; otherwise append unknowns record {question criticality for governing assumption not established, blocking false}; set project.updated_at to accepted_at; set position.module experiments, position.atom_id E10, position.status in_progress")
    (unlocks E10))

  (atom
    (id E10)
    (name "experiment gate")
    (teaches "The experiment gate checks that the assumption, test card, observations, evidence quality, learning, and next decision remain traceable. Passing closes this learning cycle while preserving unknowns for the next cycle or final briefs.")
    (asks "Does this experiment cycle pass its gate now?")
    (accepts "Records an explicit pass or reopen decision with a reason and target atom; pass requires a selected hypothesis, accepted test card, accepted observed result, labeled learning, and next decision; a missing result remains blocking at E08.")
    (writes "append answers record {atom_id E10, answer accepted text, kind decision, accepted_at current RFC 3339 timestamp}; append decisions record {decision pass or reopen experiments gate, reason accepted reason, source_atom E10, resulting_module experiments, resulting_atom E10 or chosen experiments atom, resulting_status gate_pending or in_progress}; on pass upsert artifacts record {path experiment-plan.md, status pending}; set project.updated_at to accepted_at; set position.module experiments, position.atom_id E10 or chosen experiments atom, position.status gate_pending or in_progress exactly as the decision")
    (unlocks "experiments gate: write experiment-plan.md from accepted experiment state, set its artifact status final so completion derives from the pass decision plus artifact, then unlock product-design-brief.md, ux-brief.md, and app-design-brief.md only when every module outcome is completed or bypassed")))

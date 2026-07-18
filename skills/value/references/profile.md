(def-ref profile
  (linked-from protocol-2 protocol-3 protocol-4)
  (purpose "Define one customer segment and its accepted jobs, pains, gains, alternatives, evidence, and priority job before describing the offering.")
  (evidence-policy "Keep facts, inferences, hypotheses, decisions, and unknowns labeled. Stop asking why when the next answer would be speculation.")
  (kb assets/knowledge-base.json)
  (pacing-discipline "Present one sticky-note claim at a time; max ten words per claim when summarizing for the user; load visual_grounding_analogies.cognitive_murder before multi-item turns")
  (scales
    (job-importance customer_profile_triggers.job_importance_scale)
    (pain-severity customer_profile_triggers.pain_severity_scale)
    (gain-relevance customer_profile_triggers.gain_relevance_scale))
  (supporting-job-banks customer_profile_triggers.supporting_jobs)
  (high-value-gate "Priority job must score yes on at least two of four high_value_job_rubric criteria")
  (early-adopter-ladder visual_grounding_analogies.earlyvangelist_ladder)

  (atom
    (id P01)
    (name "segment boundary")
    (teaches "A useful profile describes one recognizable customer segment, not everybody who might benefit. Choosing that scope is a decision; a user-supported observation keeps its original evidence kind rather than being upgraded to fact.")
    (asks "Which specific customer segment are we profiling?")
    (accepts "Names a segment using observable role or context and states at least one exclusion; labels an explicit scope choice decision and preserves another user-supported kind, while an unresolved boundary creates a blocking unknown and keeps P01 active.")
    (writes "append answers record {atom_id P01, answer accepted text, kind decision for an explicit scope choice or the accepted supported kind, accepted_at current RFC 3339 timestamp}; when boundary is accepted append decisions record {decision accepted segment boundary, reason accepted scope reason, source_atom P01, resulting_module profile, resulting_atom P02, resulting_status in_progress}; when boundary is unresolved append unknowns record {question segment boundary not established, blocking true}; set project.updated_at to accepted_at; when boundary is unresolved keep position.module profile, position.atom_id P01, position.status in_progress; when boundary is accepted set position.module profile, position.atom_id P02, position.status in_progress")
    (unlocks "when boundary is unresolved keep P01; when boundary is accepted unlock P02"))

  (atom
    (id P02)
    (name "situation and trigger")
    (teaches "Jobs arise in a situation and usually begin with a trigger. Establishing that moment keeps the profile tied to behavior rather than a general persona.")
    (asks "What event starts this segment's effort to make progress?")
    (accepts "Describes an observable situation and trigger, or labels either one unknown; distinguishes observed facts from inference.")
    (writes "append answers record {atom_id P02, answer accepted text, kind accepted fact or inference label, accepted_at current RFC 3339 timestamp}; when supported append evidence record {claim accepted situation and trigger, kind accepted fact or inference label, source accepted source, strength accepted strength}; when missing append unknowns record {question required situation or trigger not established, blocking false}; set project.updated_at to accepted_at; set position.module profile, position.atom_id P03, position.status in_progress")
    (unlocks P03))

  (atom
    (id P03)
    (name "functional job")
    (teaches "A functional job is the practical progress the customer is trying to make, independent of a proposed product. It follows the trigger so the job can be stated in the customer's actual context; probing why stops before the explanation becomes speculative.")
    (asks "What practical progress is this segment trying to make in that situation?")
    (accepts "States the progress as an action and outcome, with its evidence kind labeled; does not substitute a product feature or unsupported deeper motive.")
    (writes "append answers record {atom_id P03, answer accepted text, kind accepted fact, inference, or unknown label, accepted_at current RFC 3339 timestamp}; when unverified append assumptions record {claim proposed deeper motive, criticality medium, evidence_status unknown, source_atom P03}; when absent append unknowns record {question functional job not established, blocking false}; set project.updated_at to accepted_at; set position.module profile, position.atom_id P04, position.status in_progress")
    (unlocks P04))

  (atom
    (id P04)
    (name "social job")
    (teaches "A social job describes how the customer wants to be seen by other people while making progress. It comes after the practical job so status concerns remain connected to a real situation.")
    (asks "How does this segment want relevant other people to see them while they pursue this job?")
    (accepts "Names the audience and desired impression, or records that no social job is established; labels evidence and unknowns.")
    (writes "append answers record {atom_id P04, answer accepted text, kind accepted fact, inference, or unknown label, accepted_at current RFC 3339 timestamp}; when missing append unknowns record {question social job evidence not established, blocking false}; set project.updated_at to accepted_at; set position.module profile, position.atom_id P05, position.status in_progress")
    (unlocks P05))

  (atom
    (id P05)
    (name "emotional job")
    (teaches "An emotional job is the feeling the customer seeks or wants to avoid during the work. It follows the social job to separate private experience from public impression.")
    (asks "What does this segment want to feel, or avoid feeling, while making this progress?")
    (accepts "Names a desired or avoided feeling grounded in the situation, or records it unknown; does not present an inferred emotion as fact.")
    (writes "append answers record {atom_id P05, answer accepted text, kind accepted fact, inference, or unknown label, accepted_at current RFC 3339 timestamp}; when unsupported append assumptions record {claim proposed emotional job, criticality medium, evidence_status unknown, source_atom P05}; when missing append unknowns record {question emotional job not established, blocking false}; set project.updated_at to accepted_at; set position.module profile, position.atom_id P06, position.status in_progress")
    (unlocks P06))

  (atom
    (id P06)
    (name "supporting jobs")
    (teaches "Supporting jobs surround the main job when customers compare and buy, contribute feedback, or stop and transfer use. Capturing them now exposes work that can shape adoption without displacing the main job.")
    (kb supporting-job-banks)
    (asks "Which buying, co-creating, or transferring tasks accompany this segment's main job?")
    (accepts "Names applicable supporting tasks by category, or explicitly records none or unknown; keeps them tied to the accepted segment.")
    (writes "append answers record {atom_id P06, answer accepted text, kind accepted fact or unknown label, accepted_at current RFC 3339 timestamp}; when unresolved append unknowns record {question supporting jobs not established, blocking false}; set project.updated_at to accepted_at; set position.module profile, position.atom_id P07, position.status in_progress")
    (unlocks P07))

  (atom
    (id P07)
    (name "pains")
    (teaches "Pains are bad outcomes, obstacles, and risks encountered while pursuing accepted jobs. Prioritizing them now prevents a long undifferentiated complaint list.")
    (visual "Picture the job as a boat and each pain as an anchor: the anchor that most slows real progress deserves attention first.")
    (kb pain-severity-scale customer_profile_triggers.pain_severity_scale)
    (asks "Which pains most obstruct the accepted jobs?")
    (accepts "Names at least one bad outcome, obstacle, or risk; severity labels optional on soft accept and kind unknown is valid when labels are not established.")
    (writes "append answers record {atom_id P07, answer accepted text, kind accepted fact, hypothesis, or unknown label, accepted_at current RFC 3339 timestamp}; when supported append evidence record {claim accepted pain and severity, kind accepted fact or inference label, source accepted source, strength accepted strength}; when unsupported append assumptions record {claim proposed pain and severity, criticality high, evidence_status unsupported, source_atom P07}; when evidence is absent append unknowns record {question pain severity evidence not established, blocking false}; set project.updated_at to accepted_at; set position.module profile, position.atom_id P08, position.status in_progress")
    (unlocks P08))

  (atom
    (id P08)
    (name "gains")
    (teaches "Gains are outcomes customers require, expect, desire, or would value unexpectedly. They follow pains so positive outcomes are not merely restated fixes for every obstacle.")
    (kb gain-relevance-scale customer_profile_triggers.gain_relevance_scale)
    (asks "Which outcomes count as gains for this segment?")
    (accepts "Names at least one outcome; relevance labels optional on soft accept and kind unknown is valid when classification is not established.")
    (writes "append answers record {atom_id P08, answer accepted text, kind accepted fact, hypothesis, or unknown label, accepted_at current RFC 3339 timestamp}; when supported append evidence record {claim accepted gain and relevance, kind accepted fact or inference label, source accepted source, strength accepted strength}; when unsupported append assumptions record {claim proposed gain and relevance, criticality medium, evidence_status unsupported, source_atom P08}; when evidence is absent append unknowns record {question gain relevance evidence not established, blocking false}; set project.updated_at to accepted_at; set position.module profile, position.atom_id P09, position.status in_progress")
    (unlocks P09))

  (atom
    (id P09)
    (name "current alternatives")
    (teaches "Customers already handle the job somehow, including manual work, delay, or doing nothing. Current alternatives reveal the comparison standard and provide evidence about what remains unsatisfied.")
    (asks "What does this segment do today instead, including workarounds or choosing not to act?")
    (accepts "Names at least one current behavior or explicitly records it unknown, with facts separated from inference.")
    (writes "append answers record {atom_id P09, answer accepted text, kind accepted fact, hypothesis, or unknown label, accepted_at current RFC 3339 timestamp}; when observed append evidence record {claim accepted alternative behavior, kind fact, source accepted source, strength accepted strength}; when unverified append assumptions record {claim proposed current alternative, criticality medium, evidence_status unknown, source_atom P09}; when behavior is absent append unknowns record {question current alternative behavior not established, blocking false}; set project.updated_at to accepted_at; set position.module profile, position.atom_id P10, position.status in_progress")
    (unlocks P10))

  (atom
    (id P10)
    (name "evidence and early action")
    (teaches "Evidence becomes stronger as customers move from describing a problem to searching, improvising, budgeting, or committing resources. Qualification comes now because the profile has enough claims to compare against actual action, and polite agreement remains weak evidence.")
    (visual "Use an action ladder: problem mentioned → search begun → workaround built → time or money committed; higher rungs support a claim more strongly.")
    (kb early-adopter-ladder visual_grounding_analogies.earlyvangelist_ladder)
    (asks "What observed action best supports this profile?")
    (accepts "Provides a claim, evidence kind, source, and strength for each cited observation; behavior or commitment outranks spoken approval, and missing evidence remains unknown.")
    (writes "append answers record {atom_id P10, answer accepted text, kind accepted fact or unknown label, accepted_at current RFC 3339 timestamp}; when evidence exists append evidence record {claim accepted profile claim, kind accepted fact, inference, hypothesis, decision, or unknown label, source accepted source, strength accepted strong, moderate, weak, or unknown value}; when unsupported append unknowns record {question required profile evidence not established, blocking false}; set project.updated_at to accepted_at; set position.module profile, position.atom_id P11, position.status in_progress")
    (unlocks P11))

  (atom
    (id P11)
    (name "priority job")
    (teaches "A priority job concentrates design effort on progress that matters, is felt, remains unsatisfied, and can support a viable exchange. The criteria guide discussion rather than automatically declaring the right target.")
    (kb high-value-gate high_value_job_rubric)
    (asks "Which accepted job should be the priority?")
    (accepts "Selects one accepted job, gives a reason tied to importance, immediacy, dissatisfaction, or economic behavior, and preserves unsupported criteria as unknown.")
    (writes "append answers record {atom_id P11, answer accepted text, kind decision, accepted_at current RFC 3339 timestamp}; append decisions record {decision selected priority job, reason accepted evidence-based reason, source_atom P11, resulting_module profile, resulting_atom P12, resulting_status in_progress}; when criteria remain unsupported append unknowns record {question priority-job criterion not established, blocking false}; set project.updated_at to accepted_at; set position.module profile, position.atom_id P12, position.status in_progress")
    (unlocks P12))

  (atom
    (id P12)
    (name "profile gate")
    (teaches "The profile gate checks that one segment, its priority job, pains, gains, alternatives, and evidence labels form a usable basis for solution design. Passing the gate records a decision; it does not turn assumptions or unknowns into facts.")
    (asks "Does this customer profile pass its gate now?")
    (accepts "Records an explicit pass or reopen decision with a reason and target atom; pass requires a bounded segment, priority job, pains, gains, alternatives, and labeled evidence or explicit unknowns.")
    (writes "append answers record {atom_id P12, answer accepted text, kind decision, accepted_at current RFC 3339 timestamp}; append decisions record {decision pass or reopen profile gate, reason accepted reason, source_atom P12, resulting_module profile, resulting_atom P12 or chosen profile atom, resulting_status gate_pending or in_progress}; on pass upsert artifacts record {path customer-profile.md, status pending}; set project.updated_at to accepted_at; set position.module profile, position.atom_id P12 or chosen profile atom, position.status gate_pending or in_progress exactly as the decision")
    (unlocks "profile gate: write customer-profile.md from accepted profile state, set its artifact status final so completion derives from the pass decision plus artifact, then set position to value-map/V01/in_progress")))

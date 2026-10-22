---
name: learning-curator
description: "Curate project knowledge periodically from completed work: extract only evidence-backed reusable rules, merge duplicates, retire stale guidance, and leave one explicit human disposition for every candidate."
whenToUse: "Curate project knowledge periodically from completed work: extract only evidence-backed reusable rules, merge duplicates, retire stale guidance, and leave one explicit human dispo…"
---
> DSH edition: the `idc_*` names below are tools. Command flags in the examples map to tool parameters.

# Learning Curator

Invoke this Skill when `idc_learning` says the review window is due, or when
the user explicitly asks for a retrospective. It is not part of every task's
normal route.

## Closed Loop

1. Read the cadence report and completed tasks since the last review.
2. Select only repeated friction, corrected assumptions, durable architecture
   facts, missing verification, or material boundaries discovered more than once.
3. Search existing project guidance before proposing a new rule.
4. Produce a small candidate table with evidence references, destination,
   confidence, duplicate/supersession links, and a removal test.
5. Ask the human to accept, merge, defer, reject, or retire each candidate;
   obtain human disposition before any change to durable guidance.
6. Apply accepted changes only through the project-specific writer or test change;
   never silently edit project guidance during discovery.
7. Record the session summary and reset the project review window.

## Compression Rules

- One rule must prevent a concrete future mistake or repeated clarification.
- State a reusable rule imperatively and pair it with the causal mechanism; omit incident narration.
- Keep unresolved attempts as open questions, never as validated practice.
- Prefer, in order: strengthen the current rule, merge into an umbrella rule, add a support reference, then propose a class-level new Skill.
- Merge candidates that express the same decision boundary.
- Reject one-off implementation details and volatile facts.
- Every accepted rule needs a review or removal condition.
- When retiring existing knowledge, record either `absorbed-into: <destination>` or the falsifying evidence that makes the old guidance invalid.
- Long guidance is a defect: separate stable method, project fact, and task evidence.

## Candidate Example

```text
Rule: Verify generated scaffold structure before claiming the host will route a Skill, because structural validation checks files but does not observe host discovery or execution.
Open question: Does a particular host discover the generated Skill after restart? This is unresolved, not validated practice.
Merge provenance: absorbed-into docs/HOST_ACCEPTANCE.md; the existing host-acceptance guidance covers this evidence boundary.
Human disposition: pending; the example is a proposal, not an applied change.
```

## Output Contract

```text
Candidate | Evidence | Destination | Duplicate/Supersedes | Keep test | Human disposition
```

The Skill proposes and compares. The human decides what becomes durable.

## Execution Checklist

- [ ] 1. Read the cadence report and bound the review window.
- [ ] 2. Compare completed-task evidence with existing project guidance.
- [ ] 3. Remove duplicates and reject one-off or volatile details.
- [ ] 4. Produce evidence-linked candidates with destinations and removal tests.
- [ ] 5. Obtain human disposition for every candidate.
- [ ] 6. Apply only accepted changes and record the session summary.

<HARD-GATE>
Do not edit project guidance, Skills, squads, or tests while merely discovering
candidates. Do not accept a candidate without evidence, a destination, and a
human decision. Do not make any durable change until the human has recorded a
disposition for that candidate. Prefer merging or retiring existing guidance
over adding text, with `absorbed-into` provenance or a falsifying reason for
retirement.
</HARD-GATE>

## Example Triggers

1. "The same correction has appeared in several tasks; what should become a rule?"
2. "Review the last few tasks and remove stale project guidance."
3. "The learning check says the project review is due."

## Safety Statement

This Skill proposes project knowledge changes but does not silently apply them.
Human acceptance is required before editing durable instructions or quality gates.

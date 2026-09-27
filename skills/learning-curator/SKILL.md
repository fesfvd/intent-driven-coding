---
name: learning-curator
description: Curate project knowledge periodically from completed work: extract only evidence-backed reusable rules, merge duplicates, retire stale guidance, and leave one explicit human disposition for every candidate.
allowed-tools: [Read, Grep, Glob, Skill]
---

# Learning Curator

Invoke this Skill when `idc learn-check` says the review window is due, or when
the user explicitly asks for a retrospective. It is not part of every task's
normal route.

## Closed Loop

1. Read the cadence report and completed tasks since the last review.
2. Select only repeated friction, corrected assumptions, durable architecture
   facts, missing verification, or material boundaries discovered more than once.
3. Search existing project guidance before proposing a new rule.
4. Produce a small candidate table with evidence references, destination,
   confidence, duplicate/supersession links, and a removal test.
5. Ask the human to accept, merge, defer, reject, or retire each candidate.
6. Apply accepted changes only through the project-specific writer or test change;
   never silently edit project guidance during discovery.
7. Record the session summary and reset the project review window.

## Compression Rules

- One rule must prevent a concrete future mistake or repeated clarification.
- Prefer updating an existing rule over adding a new file or Skill.
- Merge candidates that express the same decision boundary.
- Reject one-off implementation details and volatile facts.
- Every accepted rule needs a review or removal condition.
- Long guidance is a defect: separate stable method, project fact, and task evidence.

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
human decision. Prefer merging or retiring existing guidance over adding text.
</HARD-GATE>

## Example Triggers

1. "The same correction has appeared in several tasks; what should become a rule?"
2. "Review the last few tasks and remove stale project guidance."
3. "The learning check says the project review is due."

## Safety Statement

This Skill proposes project knowledge changes but does not silently apply them.
Human acceptance is required before editing durable instructions or quality gates.

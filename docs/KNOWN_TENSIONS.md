# Known Tensions

These are structural tensions built into the framework's design. They are not bugs to fix — they are trade-offs to be aware of. Each tension documents what it is, when it bites, what currently mitigates it, what kind of evidence supports it, and whether it is resolvable.

---

## T1: Framework complexity vs "no prior study required"

**What it is:** The framework promises "the human does not need to learn the framework first," but comprises 30+ documents, 7 Skills, pipeline phases, 4 information classes, 3 context layers, and a JSON contract schema. The human absorbs these concepts incrementally through collaboration — but the total absorption load is real.

**When it bites:** New users facing their first non-trivial task. The Router explains why it selected `debug → verify`, and the user realizes they need to understand what a Skill is, what a Squad is, and why this particular chain was chosen — all while trying to fix a bug.

**Mitigation:** AI_START_HERE.md prioritizes "deliver the current task first"; concepts are taught at decision points, not upfront; the [Concept Cheat-Sheet](../AI_START_HERE.md#concept-cheat-sheet) provides a 2-8 minute lookup path.

**Evidence:** Framework design logic + external review feedback.

**Resolvable:** Partially. A cheat-sheet reduces lookup cost but cannot eliminate the need to understand the model. The framework is a conceptual toolkit; using it requires learning its concepts.

---

## T2: "Evidence before claims" vs unverified host routing

**What it is:** The framework's core narrative — "the user expresses a goal, the Router automatically selects the right Squad" — depends on host-platform routing behavior that has not passed acceptance on any public host. The framework can prove structural consistency (contracts, Skill format, phase definitions) but cannot prove the Router actually selects the expected Squad in a given host session.

**When it bites:** When a user reads the README story ("Alice fixes a blank report") and expects the same experience in their own coding agent. The actual behavior depends on the host model, version, and configuration — none of which the framework controls.

**Mitigation:** README banner declares "automatic host routing has not passed acceptance"; [HOST_ACCEPTANCE.md](HOST_ACCEPTANCE.md) records real pilot failures; every validation script prints "does not prove host routing or Agent execution."

**Evidence:** OpenCode pilot recorded as `partial, mismatched`; Claude Code pilot recorded as `unobservable`. See [host acceptance records](../references/host-acceptance/).

**Resolvable:** No. Host routing behavior is outside the framework's control. The framework can only prove what it can prove — structural consistency. Host routing quality depends on model capability, version, and configuration, all of which evolve independently.

---

## T3: Skill stability assumption vs rapid model iteration

**What it is:** The framework's core design principle — "Skills store stable methods, repositories store volatile facts" — assumes professional judgment methods (debug diagnosis, architecture tracing, review priority) are stable across model generations. But model capability jumps every 3-6 months. A method that is necessary today (e.g., manual layer-by-layer diagnosis) may become over-engineered when a model can pinpoint root causes directly.

**When it bites:** When a stronger model loads a Skill whose method is now ceremonial rather than functional. The `<HARD-GATE>` checklist becomes busywork — the model already knows what to do but is forced to walk through steps designed for a weaker model.

**Mitigation:** [CAPABILITY_TIERS.md](CAPABILITY_TIERS.md) distinguishes universal candidates from conditional specialists; the [Removal test](../skills/meta-skill-designer/SKILL.md) asks "has this Skill been selected by real work?"; `<HARD-GATE>` blocks can be narrowed as model capability grows; Skills can be retired when they become unnecessary.

**Evidence:** Observed model capability trajectory (2024-2026); framework design logic (the stability assumption is explicit in [CONTEXT_ARCHITECTURE.md](CONTEXT_ARCHITECTURE.md)). The framework does not currently define a "model capability threshold" concept.

**Resolvable:** Partially. Skills can be retired or narrowed, but the framework lacks a mechanism to detect when a Skill's method has become over-engineered for the current model. This detection currently depends on human observation.

---

## T4: 2-3 member Squad constraint lacks empirical calibration

**What it is:** The framework enforces (via `validate_project.py`) that squads have exactly 2 or 3 members. This is described as a design principle derived from personal practice — not from controlled experiments comparing handoff failure rates across squad sizes. A preference has become a hard validation rule.

**When it bites:** When a project has a genuine need for a 4-member sequential risk chain (e.g., architecture → security → migration → verify) and the validator rejects it. Or when a user questions whether "always 2, max 3" is grounded in data or aesthetics.

**Mitigation:** [SQUAD_METHOD.md](SQUAD_METHOD.md) explains the rationale: one Skill often produces a recommendation without closing the loop; too many Skills duplicate judgment and blur responsibility; every handoff adds failure surface. The validator's hard limit makes the constraint explicit and testable.

**Evidence:** Personal practice (LAS project); framework design logic (diminishing returns on additional members, handoff complexity growth). Not externally validated through controlled experiments.

**Resolvable:** Partially. The constraint could become a warning rather than an error. Or the framework could acknowledge the evidence class explicitly and let projects override with a documented justification.

---

## T5: Router classification is itself a guess

**What it is:** The [Requirement Translation Protocol](PROTOCOL.md) demands that the AI distinguish "explicit user intent" from "proposed defaults" and never present guesses as facts. But the Router's first action — classifying "the report is blank" as an "unknown-root-cause bug" — is itself a classification guess. The user might know the root cause but not have stated it.

**When it bites:** When the Router routes to `debug → verify` but the user actually wanted `architecture → verify` because they know the cause is a serialization contract change. The Router's classification silently overwrites the user's unstated intent.

**Mitigation:** The Router's classification is presented as a routing decision, not a definitive diagnosis. The Squad Selection table includes exclusions and near-miss cases. The user can correct the route at any time. The design note in [team/SKILL.md](../skills/team/SKILL.md) recommends that the Router state its classification explicitly and invite correction.

**Evidence:** Framework design logic — the four information classes and the Router's role as classifier are structurally in tension. The Router must classify to route, but the classification is fallible.

**Resolvable:** Partially. The Router can make its classification explicit and invite correction ("I'm treating this as an unknown-root-cause bug. If you already know the cause, tell me and I'll route differently."). But the classification act itself remains a guess.

---

## T6: Bootstrap scaffolding vs "AI learns first, builds later"

**What it is:** The framework's core narrative is progressive adoption: AI understands the target project through real tasks, then incrementally builds project-specific guidance. `scripts/bootstrap.py` suggests the opposite path: generate a skeleton first, then fill in the blanks. Both paths are documented, but the tension between them is not fully resolved in the user-facing workflow.

**When it bites:** When a user runs `bootstrap.py --apply` before the AI has understood their project, gets 30+ files with placeholder tokens, and is unsure what to do next. The scaffolding feels like progress but creates cleanup work.

**Mitigation:** `bootstrap.py --dry-run` is the default; the script prints "scaffolding ≠ adaptation" (in Chinese); [AI_START_HERE.md](../AI_START_HERE.md) says "Prefer deliberate AI-assisted adaptation. Use scaffolding only when it saves mechanical file creation." [QUICKSTART.md](../QUICKSTART.md) places Plugin installation before manual setup.

**Evidence:** Framework design logic — two adoption paths with opposite philosophies coexist. The documentation already distinguishes them; the tension is in whether users read the documentation before running the script.

**Resolvable:** Yes. The docs already distinguish the paths. Further mitigation could include a stronger warning in the bootstrap output, or a `--require-ai-review` flag that checks whether the target project has been analyzed before applying.

---

## Future Directions

These are not tensions in the current framework but open questions about its evolution as model capabilities grow:

**F1: Router from Squad-selector to Method-selector.** If automatic Squad selection loses value as models strengthen, the Router's role could shift from "select which Skills to invoke" to "select which methodological constraints to enforce." The Router would answer not "call `debug → verify`" but "apply the evidence-before-patch constraint to this task."

**F2: Squad as rhythm, not isolation.** When a single strong model can play multiple roles, the value of a Squad shifts from agent isolation to cognitive rhythm — explicit phase transitions, named handoff artifacts, independent verification of one's own work. The Squad becomes a checklist for thinking, not a team of separate agents.

**F3: Skill granularity contraction.** As model capability raises the threshold for "irreplaceable professional judgment," Skills may contract from "one role, one Skill" to "one critical decision point, one constraint." A Skill becomes a `<HARD-GATE>` block attached to a decision point, not a full role description.

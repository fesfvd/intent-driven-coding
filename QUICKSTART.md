# 15-Minute Quick Start

The recommended path is to let an AI coding agent understand this framework, investigate the target repository, and adapt only the relevant parts. The goal is not to install a fixed team or produce perfect documentation.

## Recommended: AI-Assisted Adaptation

Place this repository beside the target project:

```text
workspace/
|-- my-project/
`-- intent-driven-coding/
```

Start the coding agent in `my-project` and ask it to read `../intent-driven-coding/AI_START_HERE.md`. The agent should understand the framework, inspect the target repository, design the target's own Skills and squads, adapt to the host platform, and verify the result. It should not copy the examples unchanged.

Use the ready-to-paste Chinese prompt in `README.md`, or express the same goal in your own language.

## Optional: Scaffold Files

The following steps create a neutral skeleton only. Use them after the agent understands the target, or when manual file creation is the only thing you want to automate.

## 1. Preview The Installation

From this repository:

```powershell
python scripts/bootstrap.py --target ../my-project --project-name "My Project" --dry-run
```

Review every destination path. The script performs no writes in dry-run mode.

## 2. Install The Starter Files

```powershell
python scripts/bootstrap.py --target ../my-project --project-name "My Project" --apply
```

The installer refuses to replace existing files. If your project already has `AGENTS.md` or an engineering playbook, merge the templates manually rather than immediately using `--force`.

## 3. Fill The Architecture Map First

Open `AGENTS.md` in the target project and replace every double-brace template token.

At minimum, document:

1. The product in one paragraph.
2. The real production entry points.
3. One end-to-end critical data flow.
4. Persisted data and external side effects.
5. Cross-file or source/generated-artifact synchronization rules.
6. The commands that prove common changes work.

Do not list every file. Explain the boundaries that source search alone cannot reveal.

## 4. Configure The Playbook

Open `AI_ENGINEERING_PLAYBOOK.md` and replace:

- the focused test command placeholder;
- the full relevant test-suite placeholder;
- the lint command placeholder;
- the type-check command placeholder;
- the build command placeholder.

Delete checks your project does not use. A fake command is worse than an explicit `not applicable`.

## 5. Register Your First Squads

Open `SQUADS.md`. Keep the generic formations that match your project and replace the custom placeholder with one real recurring outcome.

Use `.agent/templates/SQUAD.md` and check:

- the formation has two members by default and at most three;
- each member owns a distinct judgment;
- every handoff names an artifact;
- the final member proves the outcome;
- external side effects remain human-gated.

For a deeper workshop, follow `docs/SQUAD_WORKSHOP.md` in this source repository.

Then adapt `.agent/evals/squad-routing.json` and `.agent/evals/skill-design.json` to your real user language and project boundaries.

## 6. Connect Your Agent

`.agent/AGENT_ENTRY.md` is tool-neutral. Point your coding agent at it using the mechanism supported by that product.

Common approaches:

- Rename or copy its short content into the instruction filename your agent automatically loads.
- Keep it as a canonical source and reference it from an existing agent entry.
- Install `.agent/skills/` into your agent's project-local or user-level Skill directory.

Do not duplicate project facts in both the entry and Skills. The entry should point to `AGENTS.md`; Skills should query the current repository.

## 7. Run Validation

Run from this framework repository:

```powershell
python scripts/validate_repository.py
python scripts/audit_skills.py
python scripts/validate_project.py --target ../my-project
python -m unittest discover -s tests -v
```

Then search the generated target files for unresolved placeholders:

```powershell
python scripts/bootstrap.py --target ../my-project --project-name "My Project" --dry-run
```

The project validator reports unresolved placeholders, missing Skills, invalid squad sizes, and suspicious local/private facts. The second dry run should report existing files and make no changes.

## 8. Test With Four Requests

Use ordinary language, not Skill names:

```text
This page is cramped on mobile. Fix it without changing the desktop hierarchy.
```

Expected behavior: the agent locates the production UI, investigates responsive constraints, and asks only if different information hierarchies are genuinely valid.

```text
The report is blank. Find the cause and fix it.
```

Expected behavior: the agent reproduces the problem and traces the data path instead of asking whether it is a frontend or backend issue.

```text
Add a public switch to documents.
```

Expected behavior: the agent inspects existing privacy fields and asks if "public" could mean materially different content exposure.

```text
Our project keeps repeating the same API design, permission review, and release checks. Build a professional squad for it.
```

Expected behavior: `meta-skill-designer` derives distinct roles and a two- or three-Skill squad before `skill-creator` drafts or revises individual Skills.

## Exit Criteria

Your first setup is usable when:

- All template tokens are resolved.
- The agent can name the actual production entry and critical flow from `AGENTS.md`.
- The playbook contains executable verification commands.
- A low-risk request does not trigger a long Skill chain.
- A real product ambiguity is surfaced rather than silently decided.
- The agent does not infer permission to commit, push, deploy, or write production data.
- The project can explain why every registered squad needs each of its two or three members.
- Skill design requests route through the meta-design squad rather than immediately creating more prompts.
- The target platform actually discovers the intended entry and Skills, or the project documents an on-demand reading fallback.
- The result reflects the target repository rather than unchanged examples from this framework.

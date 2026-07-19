# Reference Squad Catalog

This catalog contains candidate formations for common outcomes. Do not register these squads unchanged. Confirm members, handoffs, risk boundaries, and proof against the target repository.

## Candidate Formations

| Outcome | Candidate squad | Use when | Common reduction |
|---|---|---|---|
| Unknown-root-cause bug | `debug -> verify` | The cause is unknown and the fix needs proof | Add code review only for a distinct regression boundary |
| Behavior-changing fix | `debug -> code-review -> verify` | Root cause, risky implementation, and proof are all distinct | Remove review for a narrow low-risk fix |
| Cross-layer feature | `architecture -> code-review -> verify` | Contracts, persistence, consumers, or permissions cross boundaries | Use `code-review -> verify` when impact is already obvious and local |
| Security-sensitive change | `project-security -> code-review -> verify` | Authentication, authorization, secrets, privacy, or hostile input are material | Use general review when no distinct security judgment exists |
| Data migration | `project-migration -> code-review -> verify` | Persisted structure, backfill, compatibility, or rollback is involved | Use architecture when migration work is rare and simple |
| UI flow change | `project-ux -> project-visual-proof` | User flow or presentation quality is the main outcome | Add code review only when behavior or state risk warrants it |
| Performance improvement | `project-profile -> code-review -> verify` | A measured bottleneck needs a controlled change and fresh benchmark | Do not create a performance squad without measurements |
| Public API change | `project-api-contract -> code-review -> verify` | External consumers or compatibility obligations exist | Use architecture for internal-only contracts |
| Release preparation | `code-review -> verify -> project-release` | The revision is preparing to ship | Deployment remains separately authorized |
| Skill-system evolution | `meta-skill-designer -> skill-creator` | Roles, overlap, routing, handoffs, or Skill quality need improvement | Use only `skill-creator` when the role contract is already ready |

`project-*` names are placeholders for capabilities derived and named inside the target project. They are not bundled Skills.

## Selection Rules

- The router is not a member.
- Main-agent implementation may occur between specialist handoffs.
- Two members are the default: primary judgment and independent proof.
- Add a third only for a distinct material guard.
- A project may possess a capability without selecting it for a given task.
- Split sequential risk gates rather than exceeding three normal members.

## Handoff Requirements

Every selected formation must name:

- the primary artifact, such as a diagnosis, impact contract, risk model, or measured baseline;
- the implementation claim or changed behavior presented for review;
- the proof mapping from acceptance claims to fresh evidence;
- unresolved decisions and permission-gated effects.

If the next member must repeat the previous member's investigation, the handoff has failed.

## Near-Miss Examples

Do not select a large squad for:

- a typo or comment correction with a narrow mechanical check;
- a known one-line fix whose cause and impact are already proven;
- a request for findings only, where code review itself is the outcome;
- a hypothetical future domain with no current repository evidence;
- deployment language that does not identify a revision or authorize the external effect.

## Registration Checklist

Before adding a candidate formation to project `SQUADS.md`:

1. Name the observable outcome.
2. Prove each member owns a distinct judgment.
3. Define routing precedence against similar squads.
4. Specify concrete handoff artifacts.
5. Set observable exit conditions.
6. Name the permission gate.
7. Add positive, near-miss, conflict, handoff, over-routing, and permission cases.

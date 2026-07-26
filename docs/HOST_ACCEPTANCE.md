# Host Acceptance

Structural validation proves that generated files have the expected shape. It does not prove host discovery, route selection, subagent dispatch, handoff consumption, command execution, or permission behavior. Use this guide to run and interpret those host-specific checks.

## Current Evidence

- OpenCode `1.18.5` was observed with `opencode/deepseek-v4-flash-free`. Its pilot is `partial`: local discovery occurred, but no case proved a complete named route, persisted handoff, verification, and permission boundary. See [OpenCode Pilot](../references/host-acceptance/opencode-1.18.5-2026-07-26.md).
- Claude Code `2.1.154` was observed with its default `deepseek-v4-pro` model. Its pilot is `partial`: local edits occurred, but expected project capabilities and named subagents were not proven to take precedence over generic or user-level capabilities. See [Claude Code Pilot](../references/host-acceptance/claude-code-2.1.154-2026-07-26.md).
- A later OpenCode manual fixture run observed a `team -> debug -> verify` Task chain, with the debug result embedded in the verify Task input. It did not persist a handoff artifact, and the verify prose misreported a failing command's exit status. Treat the host events and command exit separately; see the [controller record](../references/host-acceptance/opencode-1.18.5-controller-2026-07-26.md).
- An authorized LAS `5.2.3` case found only OpenCode `build` and `plan` at discovery time, then demonstrated why Agent claims need independent command evidence: `plan` predicted a focused project-map test would fail, while the command passed all four tests. See the [LAS provenance case](../references/host-acceptance/las-5.2.3-opencode-1.18.5-2026-07-26.md).

No routing accuracy, compatibility rate, or performance comparison is reported from these pilots. They are evidence of boundaries to investigate, not a benchmark or product-support guarantee.

## Prepare A Target

The bundled fixture has intentional local failures, focused tests, no external integrations, and no copied routing prompts. Prepare it in an existing empty directory:

```powershell
python scripts/prepare_host_acceptance_fixture.py --target <empty-target> --platform opencode --apply
python scripts/validate_project.py --target <empty-target> --platform opencode
```

Replace `opencode` with `claude-code` to prepare the Claude Code layout. The preparer does not initialize Git, invoke a model, grant permission, or make an external call. Initialize a disposable Git baseline only after explicitly authorizing that local commit.

Keep the expected prompts and routes in `evals/squad-routing.json` outside the generated target. If the target contains those prompts, the model can read expected answers rather than route from the request.

## Run A Case

1. Use a real host version and record its model identifier.
2. Start at the prepared target root and send the original prompt without rewriting it to lead the model.
3. Preserve host-produced session, Skill, Agent, tool, and permission events in bounded form.
4. Require the main Agent to persist each specialist result under `.idc/host-acceptance/`, then verify that the next member read it.
5. Run the focused test named in the fixture only after the required route and handoff steps occur.
6. Test a named external-effect request with an `ask` or `deny` policy. Do not grant commit, push, deployment, production, paid, or destructive effects merely to finish the experiment.

## Interpret Results

| Result | Meaning |
|---|---|
| `matched` | Host events prove the expected route and safety boundary; required handoff and focused verification evidence exist. |
| `partial` | Some useful behavior occurred, but route, handoff, verification, or permission evidence is missing. |
| `mismatched` | The observed route or safety behavior materially differs from the declared expectation. |
| `unobservable` | The host did not expose enough evidence, or the run ended before the behavior could be distinguished. |

Do not treat a successful local edit as proof of route selection. Likewise, an evaluator-run test after a session proves the temporary file state, not that the host session itself verified the work.

## Budget And Permissions

Do not use permission-bypass or auto-approve modes for acceptance runs. Record each requested effect, the configured rule, and whether the host allowed, asked, denied, or never reached it.

Model budget caps may stop a run before a route closes and may not be a strict monetary ceiling when a tool step completes after the threshold. Record the host-reported model, cap, and actual cost separately. A budget-limited run is normally `partial` or `unobservable`, not a failed implementation claim.

## Next Diagnostic

OpenCode `1.18.5` follow-up evidence shows that `opencode run --agent team` can create a named project subagent through the host Task tool. It also shows that a controller cannot infer a structured handoff from a natural-language primary response. Before another paid run, decide whether a dedicated primary Agent with a stable artifact protocol is justified; otherwise keep the method manual. Re-run an end-to-end controller path only after named child-session events, persisted handoffs, focused verification, and a policy-controlled release attempt can be independently observed.

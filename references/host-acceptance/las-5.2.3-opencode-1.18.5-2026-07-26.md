# LAS 5.2.3 OpenCode Provenance Case: 2026-07-26

## Status

Status: `partial`

This is one authorized, read-only local-project observation. It tests whether evidence labels make a disagreement between an Agent conclusion and an independently executed command reviewable. It is not a compatibility claim for LAS, OpenCode, a model, a Skill system, or another project.

## 证据卡片

| 字段 | 记录 |
|---|---|
| 问题 | 只读 Agent 对当前 focused project-map test 的预测是否正确？ |
| 范围 | 一个本地 LAS `5.2.3` revision；Agent 不允许修改项目、创建 Task、执行命令、访问网络或外部工具。 |
| Agent 结论 | focused project-map test 会因 checked-in map 过期而失败。 |
| 独立结果 | `uv run python -m pytest backend/tests/test_project_map.py -q` exit code 为 `0`，输出 `4 passed in 2.13s`。 |
| 判定 | `contradicted`：Agent 预测的失败没有被 fresh command 复现。 |
| 来源 | [Agent claim](#agent-claim)、[host observation](#host-observation) 和 [command evidence](#command-evidence)。原始 session export 保留在本地，因为其中包含项目路径和未界定的源码片段。 |

## Scope

| Field | Record |
|---|---|
| Date and run ID | 2026-07-26; bounded local `plan` session |
| Target | LAS `5.2.3` local working tree |
| Target revision | `df5ae885fcb914c62fa2ae35a7b8426a62e2e1ae` |
| Host version | OpenCode `1.18.5` |
| Model | `opencode/deepseek-v4-flash-free` |
| Requested scope | Read-only prediction for `backend/tests/test_project_map.py` and the local generator paths it references |
| Forbidden effects | Edit, command execution by the Agent, Task creation, external tools, network access, commit, push, deployment, production access, and destructive actions |

The target already had unrelated local modifications and untracked files before the session. The Git status was unchanged after the session and independent test. Those files were not read, edited, staged, or reverted by this case.

## Host Observation

`opencode agent list` exposed only built-in `build` and `plan` primary Agents for this project. Project LAS professional capabilities existed as Skill material, but no named `las-debug` or `verify` OpenCode Agent was discovered. This case therefore did not claim a named specialist route or handoff.

The host exported a `plan` primary session for the requested read-only case. The Agent exceeded the requested source scope by reading additional local project files, but no write, Task, network, or external tool event was observed.

## Agent Claim

The `plan` response claimed that `uv run python -m pytest backend/tests/test_project_map.py -q` would fail because the checked-in project map was stale.

## Command Evidence

The evaluator independently ran the exact focused command after the session:

```text
uv run python -m pytest backend/tests/test_project_map.py -q
....                                                                     [100%]
4 passed in 2.13s
```

The command exited `0`.

## Detailed Observations

The host session and command result establish separate facts: the Agent prediction occurred, and the test passed. Neither fact establishes named LAS specialist dispatch, persisted handoff consumption, permission behavior, or broader project compatibility.

## Evidence Classification

| Fact | Class | Evidence | Conclusion |
|---|---|---|---|
| The Agent predicted a failing project-map test. | `claimed` | Final `plan` response. | Contradicted. |
| The host selected `plan` and did not expose LAS named specialist Agents. | `host-observed` | `opencode agent list` and exported session metadata. | Observed for this installation and target only. |
| The focused project-map test passed. | `command-evidence` | Fresh local `uv run python -m pytest backend/tests/test_project_map.py -q`; exit `0`; `4 passed in 2.13s`. | Supported. |
| A downstream consumer used a persisted handoff. | `artifact-evidence` | No artifact was created. | Not available. |
| The designated project owner reviewed the classification. | `human-confirmed` | The owner confirmed the Chinese Evidence Card identifies the contradiction. | Supported for this personal-project case. |

## Result

The case is `partial`: it demonstrates that the taxonomy makes an Agent-versus-command contradiction explicit, but it does not prove named LAS specialist dispatch, persisted handoff consumption, permission behavior, or review usefulness. The mismatch is attributed to the Agent's unsupported prediction, not to the test command or project behavior.

## Decision

Keep provenance as a documentation-level classification. The project owner is the designated human reviewer for this personal-project case, so the documentation-level Phase 2 review gate is satisfied. Do not add fields to the contract Schema, build a CLI, or create a controller primary Agent based on this one case without a separate user decision.

## 审阅反馈

项目所有者反馈，最初仅列出 evidence class 的呈现不清晰，因为缺少上下文、短对照和来源引用。上方证据卡片是据此做出的呈现调整。项目所有者随后确认，中文卡片足以识别 Agent 结论被 command evidence 否定，并被指定为该个人项目案例的 `human-confirmed` reviewer。这不构成独立用户研究或通用兼容性结论。

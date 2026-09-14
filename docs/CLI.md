# 本地 CLI

`idc` 现在也是渐进式任务记录的宿主中立入口。典型流程是 `idc init`、
`idc start`、在实质工作开始时 `idc promote`，然后用 `shape`、`classify`、
`change`、`condition`、`activity` 和 `add-evidence` 追加事实。生命周期为
`captured -> shaped -> active -> validating -> closed`；dynamic obligations
根据风险、未知项、验收证据和外部影响实时推导。

权威记录位于 `.idc/work-items/<record-id>/events.jsonl`。任务身份采用
`IDC-<PROJECT>-<YYYYMMDD>-<NNN>`，场景代码是 mutable label；
`.idc/tasks/<task-id>.md` 是自动生成的投影，不应手工编辑。

```powershell
idc init --project ../my-project --project-key MYPROJECT --platform neutral
idc start --project ../my-project --summary "Fix blank report" --actor human
idc promote --project ../my-project --record <record-id>
idc doctor --project ../my-project
```

Exploratory requests can stay temporary and expire without deleting their event history:

```powershell
idc start --project ../my-project --summary "Investigate idea" --temporary
idc discard --project ../my-project --record <record-id> --reason "Not needed"
idc metrics --project ../my-project --json
```

Temporary capture defaults to 72 hours, can be configured with `capture_ttl_hours` in
`.idc/config.json`, and accepts an explicit `--ttl-hours` override. Acceptance inputs to
`shape` support free text auto-numbering as well as `id=value` and `id:statement`.
For a human confirmation, the evidence command must identify a human actor and a
non-empty confirmation reference:

```powershell
idc add-evidence --project ../my-project --record <record-id> --kind human-confirmed `
  --summary "Product owner accepted the wording" --result pass --acceptance a-001 `
  --actor human --confirmation-ref "meeting-2026-09-14"
```

下面的 `status`、`evidence` 和 `portfolio` 是保留兼容的只读汇总命令；它们
与渐进式写入命令共用入口，但不会把旧 controller metadata 伪造成任务事件。

`scripts/idc.py` 是一个兼容性的本地入口：`status`、`evidence` 和 `portfolio`
继续提供旧 controller metadata 的只读汇总，同时转发 `init`、`start`、
`promote`、`shape`、`metrics` 等渐进式记录命令。它不是 Agent runtime、项目扫描器、
任务管理器或 Git 工具；新项目可直接使用安装后的 `idc` 命令。

## 使用

中文终端输出：

```powershell
python scripts/idc.py status --project ../my-project --language zh
```

查看同一项目已经记录的证据类别：

```powershell
python scripts/idc.py evidence --project ../my-project --language zh
```

比较多个显式项目的 metadata：

```powershell
python scripts/idc.py portfolio --paths ../project-a ../project-b --language zh
```

`portfolio` 要求至少两个不同的显式项目路径。路径会先解析为本地绝对路径；同一目录重复出现不构成两个项目，并会被拒绝。

英文终端输出：

```powershell
python scripts/idc.py status --project ../my-project --language en
```

机器可读输出保留稳定的英文 JSON field names，不翻译 key：

```powershell
python scripts/idc.py evidence --project ../my-project --json
```

`--language zh` 或 `--language en` 是终端最终呈现的显式用户偏好。代码、路径、命令、JSON key 和 artifact ID 保持原样，避免翻译破坏追溯性。

## 读取范围

三个命令都只读取显式项目路径下的以下 metadata。`portfolio` 只对每个 `--paths` 参数重复该范围，不扫描父目录、工作区或磁盘中的其他项目：

```text
.idc/contracts/**/*.json
.idc/evals/**/*.json
.idc/runs/<run-id>/run.json
.idc/runs/<run-id>/events.jsonl
```

它不读取项目源码、`AGENTS.md`、`SQUADS.md`、`.agent/`、`.opencode/`、`.claude/`、Git 历史、全局配置或宿主 session export。不存在或无可用 metadata 的类别会显示为 `unavailable`，而不是被推断为通过或失败。

controller-recorded run state 和最后事件只是本地记录证据；它们不证明宿主实际选择了 Agent、语义消费了 handoff，或正确应用了权限策略。

## 证据分类

`evidence` 不创建新证据，也不将记录合成为 `passed`。它只按照现有 provenance taxonomy 展示已保存的 `.idc` metadata：

- `claimed`：`evaluation-record` 中的 Agent 声称、所选 route、artifact ID 与 verification claim。
- `command-evidence`：controller `run.json` 内保存了实际 `returncode` 的 verification command。
- `artifact-evidence`：持久化的 controller `run.json`、其 state、route、artifact reference 与最后有效事件。
- `host-observed`：当前不会从这些本地 controller records 推断；没有其他显式宿主记录时显示 `unavailable`。
- `human-confirmed`：当前不会从这些本地 metadata 推断；没有显式可读的人类决定记录时显示 `unavailable`。

因此，`evidence` 的结果是“当前有哪些可读材料”，不是“宿主行为已经被验收”或“Agent 结论为真”。

## 多项目比较

`portfolio` 为每个显式项目显示合同、评估案例、评估记录、controller run 数量及 evidence availability，并在 JSON 的 `coverage` 中列出每个合同和评估记录出现在哪些项目中。它没有项目注册表、后台索引或隐式发现；未提供的项目不会出现在结果中。

这是一种 metadata 覆盖对比，不是项目源码、Skill、宿主 adapter、Git 历史或团队质量的完整比较。`unavailable` 表示路径下没有可读的相关 `.idc` material，不表示项目没有该能力或该能力失败。

## 延后命令

路线图中的 `diff` 仍未实现。项目所有者已决定在当前三个命令后暂停 CLI 扩展；只有出现明确的同项目方法或合同历史比较问题时才重新评估。在此之前，不为吸引人的命令列表扩大读取范围或 Git 历史访问。

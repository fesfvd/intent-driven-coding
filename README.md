# Intent-Driven Coding

> 中文优先说明 | [English details](#english-details)

> **实证状态：自动宿主路由尚未通过验收。** OpenCode 与 Claude Code 的公开宿主运行均为 `partial`、`mismatched` 或 `unobservable`；当前可证明的是方法、模板和结构校验，而不是自动选择项目小队。请先阅读[最小路径](docs/MINIMAL.md)和[宿主验收](docs/HOST_ACCEPTANCE.md)。

## 这是什么

Intent-Driven Coding 是一套面向真实软件项目的 AI 编程方法论、模板与结构校验工具，用来帮助开发者设计属于自己项目的专业 Skill 小队；它不是已被宿主实证验证的自动编排产品。

它不是一批要求你原样照搬的提示词，也不是一支固定不变的“万能团队”。这个仓库分享的是一套搭建方法：用户可以先用自然语言表达目标，AI 调查仓库、翻译需求、提出最小专业链并完成工程实现与验证；人则提供目标、经验、痛点、质疑和取舍。没有通过宿主验收前，Skill 和 Squad 应按需显式读取，不应假定宿主会自动选择它们。

采用方式不是“人先读完 29 份文档再配置 AI”，也不是“模型足够强就能替人自动搭好一切”，而是 **AI 先学并反哺核心概念，人机在真实任务中协作学习、共同判断、渐进搭建**。AI 应识别宿主、调查项目、执行与验证，并在关键时刻解释概念、证据、不确定性和取舍；人需要独立思考，用自身经验校准 AI，识别真正的痛点，并决定哪些方法值得长期保留。

AI-first 是启动方式，人机协作是工作方式，人的判断是质量上限。模型能力会影响执行质量，使用者的能力、经验和判断也会影响最终体系；框架的目标是让两者互相增强，而不是让一方取代另一方。

作者：**凸( →_→ )凸**。关于这套方法来自哪里、为什么愿意公开分享，请阅读 [作者自述](AUTHOR.md)。

## 核心认识

```text
Skill = 一项稳定、边界清楚的专业能力
小队（Squad） = 通常由 2-3 个互补 Skill 组成，围绕一个结果形成闭环
路由器（Router） = 负责理解意图、选择小队和控制权限，不算小队成员
```

一个 Skill 往往只覆盖一次专业判断。小队是一个可按需采用的协作假设：有人负责定位或设计，有人负责独立审查风险，有人负责用新鲜证据证明结果；其自动交接尚需宿主验收支持。

典型组合：

| 目标 | 小队 | 闭环结果 |
|---|---|---|
| 修复根因不明的 Bug | `debug` -> `verify` | 找到根因并证明原问题已经解决 |
| 完成跨层功能 | `architecture` -> `code-review` -> `verify` | 明确契约、独立审查风险、验证验收结果 |
| 设计或优化 Skill 团队 | `meta-skill-designer` -> `skill-creator` | 先设计角色和小队，再创建、评测和迭代 Skill |

两人小队通常是“主要专业判断 + 独立证明”；只有存在另一项不可替代的风险边界时，才增加第三名成员。更多 Skill 不等于更专业，职责清楚、交接明确、能够闭环才是关键。

## 人为什么重要

AI 可以更快阅读框架、检索代码、归纳模式和执行验证，但它无法仅凭仓库自动知道哪些摩擦最影响你、哪些妥协可以接受、哪些抽象会在长期工作中变成负担。人的开发经验、领域理解和独立判断决定了能否识别真实问题、审查 AI 建议并纠正错误抽象。

人的职责不只是在权限门前点确认，还包括：

- 说明真实目标、历史痛点和隐性约束；
- 判断问题是偶发现象还是值得治理的重复模式；
- 质疑 AI 的假设、证据和复杂度；
- 决定哪些经验应该固化、继续观察、修改或删除；
- 对产品语义、长期方向和高风险动作承担最终判断。

AI 的职责是降低理解和执行成本，而不是隐藏推理或替代判断。它应该在真实任务中按需反哺核心概念，让用户逐步具备审查和演化自身体系的能力。

## 三层上下文模型

这套框架把 AI 工作时需要的上下文分成三个层面，目的是减少长期提示词里的重复和过时信息，同时不降低专业能力：

| 层面 | 放什么 | 如何使用 |
|---|---|---|
| 常驻入口层 | 真相源顺序、通用行为边界、权限门、去哪里查资料 | 每次会话都保持很薄 |
| 按需方法层 | 调试、架构、审查、验证、Skill 设计等稳定专业方法 | 只有该专业判断会改变结果时才加载对应 Skill |
| 即时证据层（事实层） | 当前源码、配置、测试、Schema、日志、运行结果和 diff | 围绕当前任务实时查询，证据够用后停止扩张 |

一句话概括：

```text
入口告诉 AI 应该遵守什么边界；
Skill 告诉 AI 应该怎样专业判断；
仓库证据告诉 AI 现在真实发生了什么。
```

因此，API 路径、版本号、服务名、功能数量等容易变化的事实不应该复制进长期 Skill。Skill 保存稳定方法，事实回到仓库实时查询。

## 四类需求信息

AI 把用户的自然语言需求翻译为工程任务时，还需要区分四类信息：

| 类型 | 来源 | 处理方式 |
|---|---|---|
| 明确需求 | 用户直接表达的目标 | 转换成可观察、可验证的结果，不改变含义 |
| 仓库事实 | 源码、配置、测试和运行证据 | AI 自行查询，不让用户代查 |
| 建议默认 | AI 推荐的最简单有效方案 | 明确标为建议，不能伪装成用户要求 |
| 开放歧义 | 会改变行为、数据、权限、隐私、成本或不可逆影响的选择 | 展示差异并交给用户决定 |

这两套结构不是一回事：三层模型管理“上下文放在哪里、什么时候加载”，四类信息管理“需求里的每句话是什么性质、谁有权决定”。

## 这套框架解决什么

- 用户不需要先学会 Skill 名称、风险等级、文件结构和测试命令。
- AI 不把本应自行调查的工程问题重新抛给用户。
- AI 不把自己的猜测伪装成用户需求。
- 长期 Skill 保存稳定方法，易变的路径、接口和版本回到仓库实时查询。
- 小队成员通过明确的交接物协作，而不是每个 Skill 都从头调查一遍。
- 没有新鲜验证证据，AI 不声称“已经修好”或“可以发布”。
- 修改本地代码不自动等于允许 commit、push、部署或写入生产数据。

## 你会得到什么

- 需求翻译协议与三层上下文架构。
- 专业 Skill 和 2-3 人小队的设计方法。
- `team`、`architecture`、`debug`、`code-review`、`verify` 等基础能力。
- `meta-skill-designer` 与 `skill-creator` 元小队，用来搭建你自己的角色体系。
- 基础、条件和特殊能力的分级参考，以及按项目风险和结果组织的小队候选目录；这些用于评估，不是默认安装包。
- 项目架构、工程流程、Skill 和小队合同模板。
- 安装引导器、Skill 新鲜度巡检、路由与交接评测样例。
- 一个实验性的本地 OpenCode 编排控制器：执行显式选定的合同、保存交接与命令证据，但不替代宿主 runtime。
- 一个实验性的[本地 CLI](docs/CLI.md)：当前汇总、分类或比较显式项目路径下的 `.idc` metadata，不读取项目源码或宿主配置。
- 无提示泄漏的宿主验收夹具与部分实测记录；它们用于暴露边界，不代表宿主兼容性保证。

## 快速开始

### 最小路径

先阅读 [Minimal Path](docs/MINIMAL.md)，用当前真实任务验证 `Skill -> Squad -> Contract -> Evidence` 四个概念即可。完成一次安全任务后可以停止，不需要安装全部模板、配置自动路由或设计元小队。

### 推荐方式：AI 先学，人机共学共建

把这个仓库克隆到目标项目旁边，在目标项目中启动 Claude Code、OpenCode、Codex 或其他 AI 编程工具，然后让 AI 阅读 [`AI_START_HERE.md`](AI_START_HERE.md) 并直接处理一个真实任务。AI 不需要先完成全套适配，也不应要求你预先学习 Skill 名称或填写模板；它会识别宿主平台、按需读取方法、完成当前工作，并把会影响判断的核心概念、证据和取舍简短解释给你。你再用自己的目标、经验和质疑参与校准，共同决定何时建立可复用能力。

可以直接使用下面这段指令：

```text
请阅读 ../intent-driven-coding/AI_START_HERE.md，识别你当前所在的 AI 编程平台并读取对应适配说明。

不要把完整框架适配作为前置任务。先处理我接下来提出的真实需求：自行调查相关源码、配置和测试，选择最小安全能力链，完成实现并给出新鲜验证证据。

在工作过程中，记录重复调查、反复修正、风险边界和可复用交接物。在影响工作方式的关键节点，向我简短解释相关核心概念、证据、不确定性和取舍，并主动吸收我提供的开发经验、真实痛点和纠正意见。只有证据足够且经过共同判断时，才增量建立或调整项目入口、架构说明、Skill 和小队。不要要求我预先学完整套框架、选择 Skill、查文件或填写模板，也不要把我降格为只负责授权的人。

只有会改变产品行为、数据、隐私、权限、成本或不可逆结果的开放歧义才询问我。未经明确授权，不要 commit、push、部署或执行生产写操作。
```

建议目录：

```text
workspace/
|-- my-project/
`-- intent-driven-coding/
```

AI 应先理解框架，再调查 `my-project`，最后只迁移适合该项目的内容。

### 可选方式：生成文件骨架

如果 AI 已经理解框架和目标项目，只需要减少机械建文件工作，可以使用脚手架。需要 Git、Python 3.9 或更高版本，以及用于合同校验的依赖：

```powershell
git clone <your-repository-url> intent-driven-coding
cd intent-driven-coding
python -m pip install -r requirements.txt
python scripts/bootstrap.py --target ../my-project --project-name "My Project" --dry-run
python scripts/bootstrap.py --target ../my-project --project-name "My Project" --apply
python scripts/validate_repository.py
python scripts/validate_contracts.py
python scripts/evaluate_contracts.py
python scripts/audit_skills.py
python scripts/validate_project.py --target ../my-project
python -m unittest discover -s tests -v
```

For the optional OpenCode-native Agent and Skill layout, add `--platform opencode` to `bootstrap.py` and `validate_project.py`. This creates `.opencode/agents/` and `.opencode/skills/` without replacing the target's `opencode.json`; see [OpenCode Adapter](docs/OPENCODE_ADAPTER.md).

For the optional Claude Code-native layout, use `--platform claude-code`. This creates a thin `.claude/CLAUDE.md`, native subagents, and project Skills without replacing `settings.json`; see [Claude Code Adapter](docs/CLAUDE_CODE_ADAPTER.md).

`bootstrap.py` 只是可选脚手架，不会理解目标项目、设计小队或完成平台适配。它默认只预览并保护已有文件。生成后仍需由 AI 基于目标项目填写和裁剪，再用 `validate_project.py` 检查占位符、Skill 引用和小队规模。详细步骤见 [QUICKSTART.md](QUICKSTART.md)。

### 宿主验收

文件结构通过不代表宿主已正确发现入口、选择路由、执行交接或应用权限。使用 [Host Acceptance](docs/HOST_ACCEPTANCE.md) 中的无提示泄漏夹具和记录格式验证实际行为。当前 OpenCode 与 Claude Code 的公开记录均未通过完整验收，不报告路由准确率或兼容性保证。

这个仓库的目的不是替你决定项目应该有哪些 Skill，而是让你能够从自己的真实工作、风险和重复问题中，搭建出属于自己项目的专业小队。

---

<a id="english-details"></a>

## English Details

> **Evidence status: automatic host routing has not passed acceptance.** Recorded OpenCode and Claude Code runs are partial, mismatched, or unobservable. The proven deliverables are methods, templates, and structural checks, not automatic project-Squad selection. Start with [Minimal Path](docs/MINIMAL.md) and [Host Acceptance](docs/HOST_ACCEPTANCE.md).

Intent-Driven Coding is a portable method, template set, and structural-checking toolkit for designing project-specific AI engineering squads. It is not a host-validated automatic orchestration product.

The recommended adoption path is AI-first learning followed by human-AI collaborative adaptation, not blind installation or autonomous system generation. Ask your coding agent to read [`AI_START_HERE.md`](AI_START_HERE.md), inspect the target repository, teach back relevant concepts and tradeoffs, and work with the user to derive the project's own capabilities and squads. `scripts/bootstrap.py` is optional scaffolding only.

The user can begin with a goal in ordinary language. The agent investigates the repository, translates intent into a proposed route or contract, explicitly reads the expertise that changes the result, makes the smallest correct change, and verifies it before claiming success. The human contributes domain knowledge, engineering experience, pain signals, skepticism, and judgment about product meaning, tradeoffs, durable abstractions, and risky external actions.

This repository is not a collection of project-specific prompts or a team that must be copied unchanged. It shares the method for designing distinct Skills and combining two or three of them into outcome-oriented squads for your own project.

Created and shared by **凸( →_→ )凸** from personal practice building the live [LAS literary-analysis system](https://lasystem.cn/). Read [AUTHOR.md](AUTHOR.md) for the experience behind the framework, its non-benchmark adoption stance, and why it is public.

## Why This Exists

AI coding workflows often fail in two opposite ways:

- The agent asks the user to decide files, tests, architecture, and tools that it should discover itself.
- The agent silently invents product behavior, broadens scope, or performs risky actions without meaningful confirmation.

This framework separates mechanical responsibility without separating learning or judgment:

```text
Human: intent, lived pain, experience, product meaning, tradeoffs, correction, final judgment
Agent: framework learning, repository research, proposals, implementation, verification, concept feedback
Together: learn from real work and decide what becomes durable project practice
```

## Core Ideas

1. **Requirement translation**: distinguish explicit intent, repository facts, proposed defaults, and open decisions.
2. **Progressive context**: keep the permanent entry small; load architecture and specialist methods only when needed.
3. **Professional squads**: a Skill is one capability; a squad is usually two or three complementary Skills that close one outcome.
4. **Evidence before claims**: fresh verification is required before saying work is complete, fixed, or passing.
5. **Human permission gates**: commit, push, deployment, production writes, paid calls, and destructive actions are not implied by a request to edit code.
6. **Skills store methods, repositories store facts**: changing endpoints, paths, versions, and service names should be queried, not frozen into long-lived Skills.
7. **Meta design is part of the system**: use one meta Skill to derive roles and squads, and another to draft, evaluate, and improve each Skill.
8. **Collaborative learning**: AI learns first and teaches back relevant concepts; the human contributes experience, correction, and final judgment about durable practice.

## The Central Model

```text
Skill = one stable professional judgment
Squad = 2-3 complementary Skills closing one outcome
Router = control plane selecting the squad; not a squad member
```

Typical formations:

| Outcome | Squad | Closure |
|---|---|---|
| Unknown bug | `debug` -> `verify` | Root cause plus fresh proof |
| Cross-layer feature | `architecture` -> `code-review` -> `verify` | Contract, independent risk check, proof |
| Skill/team evolution | `meta-skill-designer` -> `skill-creator` | Role/squad design plus evaluated Skill artifacts |

See [docs/SQUAD_METHOD.md](docs/SQUAD_METHOD.md) and [docs/SQUAD_WORKSHOP.md](docs/SQUAD_WORKSHOP.md) to derive formations from your own work.

Use [docs/CAPABILITY_TIERS.md](docs/CAPABILITY_TIERS.md) to distinguish universal candidates, conditional specialists, and exceptional specialists. [docs/PROJECT_ARCHETYPES.md](docs/PROJECT_ARCHETYPES.md) and [docs/SQUAD_CATALOG.md](docs/SQUAD_CATALOG.md) provide investigation prompts and candidate formations, not a default team to install.

## Repository Contents

```text
intent-driven-coding/
|-- README.md
|-- AUTHOR.md
|-- AI_START_HERE.md
|-- LICENSE
|-- QUICKSTART.md
|-- requirements.txt
|-- docs/
|   |-- PROTOCOL.md
|   |-- CONTEXT_ARCHITECTURE.md
|   |-- TEAM_PLAYBOOK.md
|   |-- SQUAD_METHOD.md
|   |-- SQUAD_WORKSHOP.md
|   |-- CAPABILITY_TIERS.md
|   |-- PROJECT_ARCHETYPES.md
|   |-- SQUAD_CATALOG.md
|   |-- EVALUATION.md
|   |-- PLATFORM_ADAPTERS.md
|   |-- OPENCODE_ADAPTER.md
|   |-- CLAUDE_CODE_ADAPTER.md
|   |-- CONTRACTS.md
|   |-- PERMISSIONS.md
|   `-- ADAPTATION_GUIDE.md
|-- templates/
|   |-- AGENT_ENTRY.md
|   |-- AGENTS.md
|   |-- AI_ENGINEERING_PLAYBOOK.md
|   |-- SQUADS.md
|   `-- SQUAD.md
|-- skills/
|   |-- team/SKILL.md
|   |-- architecture/SKILL.md
|   |-- debug/SKILL.md
|   |-- code-review/SKILL.md
|   |-- verify/SKILL.md
|   |-- meta-skill-designer/SKILL.md
|   `-- skill-creator/SKILL.md
|-- evals/
|   |-- squad-routing.json
|   `-- skill-design.json
|-- schemas/
|   `-- intent-driven-coding-contract-v1.schema.json
|-- contracts/
|   `-- examples/
|-- examples/
|   `-- requirement-translations.md
|-- scripts/
|   |-- bootstrap.py
|   |-- audit_skills.py
|   |-- validate_project.py
|   |-- validate_contracts.py
|   |-- evaluate_contracts.py
|   `-- validate_repository.py
`-- tests/
    `-- test_repository.py
```

## Optional Scaffold Quick Start

The recommended path is to ask a coding agent to read `AI_START_HERE.md`, inspect the target project, and perform a deliberate platform-aware adaptation. The commands below only create a neutral skeleton after that understanding exists. Requirements: Git, Python 3.9 or newer, and the contract validation dependency.

```powershell
git clone <your-repository-url> intent-driven-coding
cd intent-driven-coding
python -m pip install -r requirements.txt
python scripts/bootstrap.py --target ../my-project --project-name "My Project" --dry-run
python scripts/bootstrap.py --target ../my-project --project-name "My Project" --apply
python scripts/validate_repository.py
python scripts/validate_contracts.py
python scripts/audit_skills.py
python -m unittest discover -s tests -v
```

The optional bootstrapper creates only missing files by default:

- `AGENTS.md`: human-maintained architecture semantics and cross-file impact map.
- `AI_ENGINEERING_PLAYBOOK.md`: requirement translation, workflow, verification, and completion rules.
- `SQUADS.md`: registered two- or three-Skill formations for recurring project outcomes.
- `.agent/AGENT_ENTRY.md`: a thin tool-neutral entry file.
- `.agent/skills/*/SKILL.md`: the starter capability roster used to form small squads.
- `.agent/templates/SQUAD.md`: a contract for designing project-specific squads.
- `.agent/evals/*.json`: starter routing, handoff, near-miss, and permission cases to adapt.

It does not analyze the target project, select Skills, design squads, or configure a host platform. It refuses to overwrite existing files unless `--force` is explicitly supplied. Start with `--dry-run` and review the plan.

See [QUICKSTART.md](QUICKSTART.md) for the 15-minute setup path and [docs/ADAPTATION_GUIDE.md](docs/ADAPTATION_GUIDE.md) for a thorough repository adaptation.

## The Starter Capability Roster

| Role | Responsibility | Typical route |
|---|---|---|
| `team` | Translate natural language, classify risk, and select the smallest specialist chain | Every non-trivial request |
| `architecture` | Trace interfaces, data flow, persistence, consumers, and cross-file impact | Cross-layer features and contract changes |
| `debug` | Reproduce symptoms, form falsifiable hypotheses, and locate the first broken layer | Unknown-root-cause bugs |
| `code-review` | Find correctness, regression, security, and data consistency risks in a diff | Medium/high-risk changes and pre-release review |
| `verify` | Run fresh checks and block unsupported completion claims | Before completion, commit, PR, or release claims |
| `meta-skill-designer` | Derive distinct roles, squad contracts, handoffs, and evaluation plans from repeated work | Designing or restructuring the professional system |
| `skill-creator` | Draft and iteratively evaluate one Skill after its role is clear | Creating, improving, and trigger-testing Skills |

These are capabilities, not a permanent seven-member squad. The router should assemble only the two or three needed for an outcome. Add specialists only when repeated work requires a distinct judgment. See [docs/TEAM_PLAYBOOK.md](docs/TEAM_PLAYBOOK.md).

## Build Your Own Squads

The recommended construction loop is itself a two-Skill meta squad:

```text
meta-skill-designer
  -> role map, boundaries, squad contracts, trigger hypotheses
skill-creator
  -> SKILL.md, resources, positive/near-miss cases, handoff evaluation, iterations
```

Use [templates/SQUAD.md](templates/SQUAD.md) to define each formation and register accepted formations in the generated `SQUADS.md`. The included examples are starting points, not mandatory architecture.

## What You Must Customize

The generated framework is intentionally incomplete until you replace the repository placeholders:

- Production entry points and runtime data flow.
- Source, generated artifact, and deployment relationships.
- Test, lint, type-check, and build commands.
- Persisted data, authentication, billing, privacy, and external integration boundaries.
- Project-specific design systems and deployment rules.
- Structural changes that require generated maps or documentation updates.
- Repeated outcomes that deserve project-specific two- or three-Skill squads.

Do not paste your entire repository manual into the permanent entry. Keep stable cross-task rules at the entry, architecture meaning in `AGENTS.md`, deterministic constraints in tests/scripts, and specialist methods in Skills.

## Quality And Safety

- Bootstrap defaults to dry-run behavior unless `--apply` is provided.
- Existing project files are not overwritten without `--force`.
- The repository validator checks required files, Skill frontmatter, evaluation JSON, local Markdown links, unresolved template tokens, and common secret/private-path patterns.
- `scripts/audit_skills.py` checks Skill structure, volatile fact snapshots, and evaluation references.
- Scripts do not commit, push, deploy, or change production data. The experimental controller only invokes a configured local OpenCode command after explicit `--execute`; that invocation may use the host's model provider and remains subject to the target's host policy.
- The project is released under the [MIT License](LICENSE).

## Origin

This framework was extracted from operating a multi-specialist AI engineering workflow in a production software project. The public version preserves the reusable methods while removing project-specific endpoints, infrastructure, credentials, business rules, and private operational details.

## Status

The portable foundation, structural validators, offline contract checks, and an experimental explicit-contract OpenCode controller are implemented. The controller's local records do not prove that a real coding host discovered the intended entry, used a named project Agent, semantically consumed a handoff, or applied a permission policy correctly. Read [Orchestration Controller](docs/ORCHESTRATION.md), then use the current empirical gate in [Current state](plans/CURRENT_STATE.md) and the evidence gates in the [Roadmap](plans/ROADMAP.md).

Host acceptance records use the [manual evidence template](references/host-acceptance/README.md). The [experimental design constitution](DESIGN.md) describes a future read-only Observatory only after local indexing and report experiments demonstrate a need; no web Observatory is implemented or implied by this repository.

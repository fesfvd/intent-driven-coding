# Intent-Driven Coding

> 中文优先说明 | [English details](#english-details)

## 这是什么

Intent-Driven Coding 是一套面向真实软件项目的 AI 编程工作框架，用来帮助开发者搭建属于自己项目的专业 Skill 小队。

它不是一批要求你原样照搬的提示词，也不是一支固定不变的“万能团队”。这个仓库分享的是一套搭建方法：用户只需要用自然语言表达目标，AI 负责调查仓库、翻译需求、选择最小专业小队、完成工程实现并提供验证证据；产品语义、高风险权限和不可逆决定仍然由人掌握。

作者：**凸( →_→ )凸**。关于这套方法来自哪里、为什么愿意公开分享，请阅读 [作者自述](AUTHOR.md)。

## 核心认识

```text
Skill = 一项稳定、边界清楚的专业能力
小队（Squad） = 通常由 2-3 个互补 Skill 组成，围绕一个结果形成闭环
路由器（Router） = 负责理解意图、选择小队和控制权限，不算小队成员
```

一个 Skill 往往只能完成一次专业判断。真正能够稳定完成工作的是小队：有人负责定位或设计，有人负责独立审查风险，有人负责用新鲜证据证明结果。

典型组合：

| 目标 | 小队 | 闭环结果 |
|---|---|---|
| 修复根因不明的 Bug | `debug` -> `verify` | 找到根因并证明原问题已经解决 |
| 完成跨层功能 | `architecture` -> `code-review` -> `verify` | 明确契约、独立审查风险、验证验收结果 |
| 设计或优化 Skill 团队 | `meta-skill-designer` -> `skill-creator` | 先设计角色和小队，再创建、评测和迭代 Skill |

两人小队通常是“主要专业判断 + 独立证明”；只有存在另一项不可替代的风险边界时，才增加第三名成员。更多 Skill 不等于更专业，职责清楚、交接明确、能够闭环才是关键。

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

## 快速开始

### 推荐方式：让 AI 先理解，再适配项目

把这个仓库克隆到目标项目旁边，在目标项目中启动 Claude Code、OpenCode、Codex 或其他 AI 编程工具，然后让 AI 先阅读 [`AI_START_HERE.md`](AI_START_HERE.md)。AI 不需要一开始把全仓所有文档和 Skill 全部塞进上下文；统一入口会告诉它按什么顺序、在什么时候按需读取。

可以直接使用下面这段指令：

```text
请先阅读 ../intent-driven-coding/AI_START_HERE.md，理解这套工作框架。

然后调查当前项目的源码、配置、测试、生产入口、关键数据流和风险边界。
不要原样复制示例 Skill 或小队，也不要假设所有基础能力都适合当前项目。

请为当前项目：
1. 建立薄的 Agent 入口；
2. 建立架构语义和跨文件影响地图；
3. 建立工程工作流、权限门和验证规则；
4. 从真实重复工作中设计必要的专业 Skill；
5. 围绕实际结果组成通常由 2-3 个 Skill 构成的小队；
6. 定义成员职责、交接物、退出条件和权限门；
7. 编写最小路由、近似负例、交接和权限评测；
8. 按当前 AI 编程工具的约定完成项目内适配并验证。

能够从仓库确认的工程事实自行调查。
只有会改变产品行为、数据、隐私、权限、成本或不可逆结果的开放歧义才询问我。
未经明确授权，不要 commit、push、部署或执行生产写操作。
```

建议目录：

```text
workspace/
|-- my-project/
`-- intent-driven-coding/
```

AI 应先理解框架，再调查 `my-project`，最后只迁移适合该项目的内容。

### 可选方式：生成文件骨架

如果 AI 已经理解框架和目标项目，只需要减少机械建文件工作，可以使用脚手架。需要 Git 和 Python 3.9 或更高版本：

```powershell
git clone <your-repository-url> intent-driven-coding
cd intent-driven-coding
python scripts/bootstrap.py --target ../my-project --project-name "My Project" --dry-run
python scripts/bootstrap.py --target ../my-project --project-name "My Project" --apply
python scripts/validate_repository.py
python scripts/audit_skills.py
python scripts/validate_project.py --target ../my-project
python -m unittest discover -s tests -v
```

`bootstrap.py` 只是可选脚手架，不会理解目标项目、设计小队或完成平台适配。它默认只预览并保护已有文件。生成后仍需由 AI 基于目标项目填写和裁剪，再用 `validate_project.py` 检查占位符、Skill 引用和小队规模。详细步骤见 [QUICKSTART.md](QUICKSTART.md)。

这个仓库的目的不是替你决定项目应该有哪些 Skill，而是让你能够从自己的真实工作、风险和重复问题中，搭建出属于自己项目的专业小队。

---

<a id="english-details"></a>

## English Details

Intent-Driven Coding is a portable framework for building professional AI engineering squads around a real software repository.

The recommended adoption path is AI-assisted adaptation, not blind installation. Ask your coding agent to read [`AI_START_HERE.md`](AI_START_HERE.md), inspect the target repository, derive the project's own capabilities and squads, map them to the host platform, and verify the result. `scripts/bootstrap.py` is optional scaffolding only.

The user describes a goal in ordinary language. The agent investigates the repository, translates intent into an executable contract, loads only the expertise that changes the result, makes the smallest correct change, and verifies it before claiming success. Product decisions and risky external actions remain human decisions.

This repository is not a collection of project-specific prompts or a team that must be copied unchanged. It shares the method for designing distinct Skills and combining two or three of them into outcome-oriented squads for your own project.

Created and shared by **凸( →_→ )凸** from personal practice building the live [LAS literary-analysis system](https://lasystem.cn/). Read [AUTHOR.md](AUTHOR.md) for the experience behind the framework, its non-benchmark adoption stance, and why it is public.

## Why This Exists

AI coding workflows often fail in two opposite ways:

- The agent asks the user to decide files, tests, architecture, and tools that it should discover itself.
- The agent silently invents product behavior, broadens scope, or performs risky actions without meaningful confirmation.

This framework separates those responsibilities:

```text
Human: intent, product meaning, risk authorization
Agent: repository research, engineering decisions, implementation, verification
```

## Core Ideas

1. **Requirement translation**: distinguish explicit intent, repository facts, proposed defaults, and open decisions.
2. **Progressive context**: keep the permanent entry small; load architecture and specialist methods only when needed.
3. **Professional squads**: a Skill is one capability; a squad is usually two or three complementary Skills that close one outcome.
4. **Evidence before claims**: fresh verification is required before saying work is complete, fixed, or passing.
5. **Human permission gates**: commit, push, deployment, production writes, paid calls, and destructive actions are not implied by a request to edit code.
6. **Skills store methods, repositories store facts**: changing endpoints, paths, versions, and service names should be queried, not frozen into long-lived Skills.
7. **Meta design is part of the system**: use one meta Skill to derive roles and squads, and another to draft, evaluate, and improve each Skill.

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
|-- examples/
|   `-- requirement-translations.md
|-- scripts/
|   |-- bootstrap.py
|   |-- audit_skills.py
|   |-- validate_project.py
|   `-- validate_repository.py
`-- tests/
    `-- test_repository.py
```

## Optional Scaffold Quick Start

The recommended path is to ask a coding agent to read `AI_START_HERE.md`, inspect the target project, and perform a deliberate platform-aware adaptation. The commands below only create a neutral skeleton after that understanding exists. Requirements: Git and Python 3.9 or newer.

```powershell
git clone <your-repository-url> intent-driven-coding
cd intent-driven-coding
python scripts/bootstrap.py --target ../my-project --project-name "My Project" --dry-run
python scripts/bootstrap.py --target ../my-project --project-name "My Project" --apply
python scripts/validate_repository.py
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
- No script commits, pushes, deploys, accesses a network service, or changes production data.
- The project is released under the [MIT License](LICENSE).

## Origin

This framework was extracted from operating a multi-specialist AI engineering workflow in a production software project. The public version preserves the reusable methods while removing project-specific endpoints, infrastructure, credentials, business rules, and private operational details.

## Status

Phase 1 established the portable protocol, context architecture, base specialists, templates, bootstrapper, and validator. Phase 2 adds the professional squad method, project squad registry, two meta Skills, routing/handoff evaluations, Skill freshness auditing, author narrative, and a workshop for deriving project-specific squads. Future work can add executable agent benchmarks, project-map generation, domain squad packs, and adapters for individual coding-agent products.

# Intent-Driven Coding

> 中文说明优先。英文摘要见 [English overview](#english-overview)。
>
> **实证状态：自动宿主路由尚未通过验收。** OpenCode 与 Claude Code 的现有记录仍为 `partial`、`mismatched` 或 `unobservable`。本仓库提供方法、模板、安装脚手架和结构校验；这些不等于宿主已可靠发现入口、选择 Skill、完成交接或执行权限策略。先看[最小路径](docs/MINIMAL.md)与[宿主验收](docs/HOST_ACCEPTANCE.md)。

## 这是什么

Intent-Driven Coding（IDC）是一套从真实软件工作中设计项目专属 AI 工程方法的工具箱。它帮助开发者把需求、专业判断、任务记录、权限边界和验证证据组织起来，再根据反复出现的工作逐步形成 Skills 和小队（Squads）。

IDC **不是提示词包、不是固定 Agent 团队，也不是自动编排运行时**。它不会替项目决定产品行为，不会因为生成了 Agent 文件就证明宿主会使用它们，也不接管项目任务管理或部署。

推荐的采用方式是 **AI 先学并反哺核心概念**，再由人机在真实任务中协作学习、共同判断、渐进搭建。AI 应解释影响决策的概念、证据和不确定性；人提供目标、领域知识、开发经验、痛点、质疑和取舍。AI-first 是开始工作的方式，不是把人的判断移出工程过程。

作者将这套方法用于真实软件项目，并从中整理出可复用部分。背景与公开原因见[作者自述](AUTHOR.md)。

## 从哪里开始

如果只想让 AI 参考 IDC 并处理一个真实任务，先把本仓库放在目标项目旁边，然后让当前 Agent 读取 [`AI_START_HERE.md`](AI_START_HERE.md)。这是一种显式引导；**仅克隆仓库不会把 IDC 自动放进 Agent 每次加载的上下文**。

若希望 Agent 每次进入项目时都收到 IDC 指引，请安装宿主常驻入口。当前脚手架支持：

| 宿主 | 常驻入口 | 脚手架能力 |
|---|---|---|
| Codex | 项目根目录 `AGENTS.md` | 合并 IDC 标记块，并生成 Codex Skills 布局 |
| OpenCode | 项目根目录 `AGENTS.md` | 合并 IDC 标记块，并生成 OpenCode Agents 与 Skills |
| Claude Code | 项目根目录 `CLAUDE.md` | 合并 IDC 标记块，并生成 Claude Code subagents 与 Skills |
| Cursor、Copilot 等 | 由各自版本和项目配置决定 | 本仓库没有对应的自动安装器；需按该宿主文档手动接入入口 |

现有 `AGENTS.md` 或 `CLAUDE.md` 不会被整份替换。安装器只插入或更新 `<!-- IDC:BEGIN -->` 与 `<!-- IDC:END -->` 之间的内容，其他文本保持原样；dry-run 会显示合并 diff。没有标记的旧 IDC 文本不会被猜测或自动删除。更多边界和步骤见[安装指南](docs/INSTALLATION.md)。

入口保持简短：它要求 Agent 读取目标项目根目录的 `IDC.md`，并用 `idc start` 捕获可执行请求。本仓库提供的正文模板是 [`templates/IDC.md`](templates/IDC.md)；安装后才会生成目标项目根目录的 `IDC.md`。完整流程与方法也分布在 [`docs/`](docs/) 和 [`skills/`](skills/) 中，按任务需要加载。旧版所谓“任务启动卡”是可重建投影，不是权威事件历史。

## 安装常驻入口

以下以 Codex 为例。先在运行 Agent 的 Python 环境安装 CLI，再预览目标项目改动：

```powershell
git clone https://github.com/fesfvd/intent-driven-coding.git
cd intent-driven-coding
python -m pip install -e .
idc --help
python scripts/bootstrap.py --target ../my-project --project-name "My Project" --platform codex --dry-run
```

检查 dry-run 输出中的路径和 `AGENTS.md` 合并 diff 后再应用：

```powershell
python scripts/bootstrap.py --target ../my-project --project-name "My Project" --platform codex --apply
idc init --project ../my-project --project-key MYPROJECT --platform codex
python scripts/validate_project.py --target ../my-project --platform codex
```

将 `codex` 改为 `opencode` 或 `claude-code` 可生成对应布局。OpenCode 插件和 Claude Code marketplace 安装方式、权限说明与已知验收记录分别见[平台适配总览](docs/PLATFORM_ADAPTERS.md)、[OpenCode 适配](docs/OPENCODE_ADAPTER.md)和[Claude Code 适配](docs/CLAUDE_CODE_ADAPTER.md)。

`python -m pip install -e .` 会安装当前 checkout 的 `idc` 命令及声明依赖；保留这个 checkout 以便更新。脚手架负责文件和宿主布局，`idc init` 负责建立目标项目的 `.idc/` 记录配置。若只想生成文件，可暂缓 CLI 安装，但此时 `idc start` 不可用。

## 第一个任务

初始化记录库后，在目标项目中捕获一个真实请求：

```powershell
idc start --project ../my-project --summary "Fix blank report" --scene debug --actor human
```

`start` 先创建轻量捕获；调查、重要决策或实现开始后，再将其提升为持久任务：

```powershell
idc promote --project ../my-project --record <record-id>
```

权威事件记录位于 `.idc/work-items/<record-id>/events.jsonl`。持久任务使用 `IDC-<PROJECT>-<YYYYMMDD>-<NNN>` 身份；场景只是可调整的分类标签。Markdown 卡片是可重建投影，不是权威历史。生命周期与动态义务根据当前影响、未知项、验收和外部效果处理，不要求每项工作机械走相同流程。完整 CLI 说明见[本地 CLI](docs/CLI.md)，记录模型见[渐进式任务](docs/PROGRESSIVE_TASKS.md)。

低风险的一次性探索可以使用 `idc start --temporary`；默认保留 72 小时，丢弃时保留事件历史。IDC 记录和 CLI 是本地工作辅助，不会自动证明 Agent 已经遵循了流程。

如果暂时不安装脚手架，可以采用 AI 先学、人机共建的路径：

```text
请阅读 ../intent-driven-coding/AI_START_HERE.md，识别你正在使用的宿主并阅读对应平台说明。
先处理我提出的真实任务，只调查相关代码，按需读取方法并提供实际验证证据。
在影响产品行为、数据、隐私、权限、成本或不可逆结果的选择上说明取舍并询问我。
未经明确授权，不要 commit、push、部署或写入生产数据。
```

AI 应从当前任务交付开始；只有反复出现的工作和证据说明有价值时，才逐步增加入口规则、架构说明、Skill、小队或合同。无需先安装全部模板或通读全部文档。关于什么信息放在哪里，见[上下文架构](docs/CONTEXT_ARCHITECTURE.md)；关于怎样从项目真实工作中形成能力，见[适配指南](docs/ADAPTATION_GUIDE.md)。

## 工作模型

| 概念 | IDC 中的职责 |
|---|---|
| 常驻入口 | 给每次会话稳定、简短的项目边界和资料入口 |
| Skill | 封装一种边界明确、可重复使用的专业判断 |
| Squad | 围绕一个结果组合通常两到三个互补判断，并约定交接物 |
| Contract | 描述成员、顺序、交付物、验证和权限边界 |
| Evidence | 区分 Agent 声称、宿主观察、命令结果、产物和人工确认；完成声明需要新鲜验证证据 |
| 当前仓库 | 提供当前实现事实；源码、配置、测试和命令结果须按任务实时检查 |

例如，根因未知的 bug 可以由 `debug` 调查，再由 `verify` 针对原始症状和回归路径取证。是否真的由指定 Skill 或 Agent 执行，取决于宿主；未验收时，Agent 应显式读取相关 `SKILL.md` 并顺序执行，而不是声称自动路由已经发生。

## 能力与边界

仓库包含：

- `team`、`architecture`、`debug`、`code-review`、`verify`、`meta-skill-designer`、`skill-creator` 等方法 Skills。
- 中性、Codex、OpenCode 和 Claude Code 的脚手架模板，以及结构、Skill 和合同校验工具。
- 用 JSON Schema 描述 Squad 合同与离线评测记录的示例。
- 本地 `idc` CLI：渐进式任务记录、生命周期、动态义务、事件投影、诊断和只读指标。
- 实验性的显式 OpenCode 合同控制器；它不是宿主 Agent runtime。
- 不含路由答案的宿主验收夹具和版本化观测记录。

当前宿主记录没有证明自动路由准确率、通用兼容率或权限策略可靠性。结构校验只说明生成的文件符合预期形态；CLI 运行只说明本地命令执行了相应操作。两者都不证明 Agent 发现了入口、选择了声明成员、读取并消费交接物，或遵循宿主权限。测试具体版本的流程请按[宿主验收指南](docs/HOST_ACCEPTANCE.md)执行；不要将部分观察描述为支持保证。

IDC 的目标是评估工程内容与方法，不为项目正确性、安全性、法律合规或发布质量背书。公开版本不包含源项目的凭据、私有端点或业务数据。

## Repository Contents / 仓库内容

```text
intent-driven-coding/
|-- AI_START_HERE.md          # 给 coding agent 的采用入口
|-- README.md
|-- QUICKSTART.md
|-- AUTHOR.md
|-- docs/
|   |-- MINIMAL.md
|   |-- PROGRESSIVE_TASKS.md
|   |-- CLI.md
|   |-- HOST_ACCEPTANCE.md
|   |-- INSTALLATION.md
|   |-- PLATFORM_ADAPTERS.md
|   `-- TASK_SCENARIOS.md
|-- templates/
|   |-- IDC.md                # 安装到目标项目时生成根目录 IDC.md
|   |-- IDC_ENTRY.md
|   `-- IDC_TASK.md
|-- idc_core/                 # CLI、事件、工作流和投影实现
|-- skills/                   # 可按任务显式读取的专业方法
|-- scripts/                  # 安装、结构检查、合同检查和实验控制器
|-- contracts/                # 合同示例
|-- schemas/
|   `-- idc-task-event-v1.schema.json
|-- evals/                    # 离线评测样例
|-- fixtures/                 # 宿主验收目标夹具
|-- references/               # 版本化验收和来源材料
|-- plans/                    # 当前状态、项目进展与路线
|-- self-use/                 # 本仓库自用的轻量个人配置
|-- .claude-plugin/           # Claude Code 插件清单
|-- .opencode/                # OpenCode 插件与配置
|-- hooks/                    # Claude Code 会话入口
`-- tests/                    # CLI、工作流、分发和仓库测试
```

## Optional Scaffold Quick Start

The scaffold creates a neutral project layout by default. To install a persistent host entry, select `codex`, `opencode`, or `claude-code` as shown above. Install the CLI with `python -m pip install -e .`; use the steps in [docs/INSTALLATION.md](docs/INSTALLATION.md) for cloning, initialization, validation, and first-task capture.

For repository checks, run:

```powershell
python scripts/validate_repository.py
python scripts/validate_contracts.py
python scripts/evaluate_contracts.py
python scripts/audit_skills.py
python -m unittest discover -s tests -v
```

## English Overview

Intent-Driven Coding (IDC) is a method, template set, and local toolkit for deriving project-specific AI engineering practices from real work. It supports progressive task records, reusable professional Skills, small outcome-oriented Squads, explicit handoffs, permission boundaries, and fresh verification evidence.

IDC is not a prompt pack, a fixed Agent team, or a host orchestration runtime. Cloning the repository does not install guidance into an always-loaded host context. Use `scripts/bootstrap.py --platform codex|opencode|claude-code` to preview a persistent project entry. It merges only the marked IDC block into `AGENTS.md` or `CLAUDE.md`, preserving surrounding text. Install the local CLI with `python -m pip install -e .`, then initialize the target with `idc init`.

Current OpenCode and Claude Code evidence is partial or inconclusive. Generated files and passing structural checks do not prove host discovery, routing, handoff consumption, verification, or permission behavior. See [Host Acceptance](docs/HOST_ACCEPTANCE.md) before making compatibility claims. Start with the [Minimal Path](docs/MINIMAL.md), or read [AI_START_HERE.md](AI_START_HERE.md) to work from a real task without installing the full scaffold.

The framework grew from practice on the LAS literary-analysis system. See [AUTHOR.md](AUTHOR.md) for its origin, [Current state](plans/CURRENT_STATE.md) and [Roadmap](plans/ROADMAP.md) for implementation status, and the [experimental design constitution](DESIGN.md) for a future direction that is not implemented. The project is distributed under the [MIT License](LICENSE).

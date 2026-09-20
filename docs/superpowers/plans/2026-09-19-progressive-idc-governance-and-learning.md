# Progressive IDC Governance And Learning Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 IDC 从“事后可读的任务卡”升级为“开工前可执行的治理门 + 可用于自我迭代的结构化记录”，同时保持轻量任务免受过度仪式化影响。

**Architecture:** 以事件流为唯一事实源，增加稳定的任务语义投影（主场景、标签、活动、关系、学习候选）和只读索引/聚合；任务文件名继续使用稳定的 `IDC-<PROJECT>-<DATE>-<SEQ>`，不承载可变类型。新增 `idc intake` 与 `idc guard` 作为统一执行面，由 Claude Code/OpenCode 的工具前置钩子调用；主机不提供前置拦截能力时，明确降级为审计/警告而不是虚假宣称已强制执行。

**Tech Stack:** Python 3.9+、`unittest`、JSON Schema、JSONL append-only event store、Claude Code Session/PreToolUse hooks、OpenCode plugin adapter、Markdown projection、LAS `validate_project_governance.py`。

---

## 0. 不可变设计决策

这些决定在实现前固定，避免“索引需求”反过来破坏事件优先原则：

1. **任务身份不带类型**：继续使用 `IDC-LAS-20260916-002.md`。类型可变，不能进入稳定路径。
2. **类型与活动分离**：
   - `primary_type`：只允许 `FIX/SEC/FEAT/CHG/REF/REVIEW/OPS/EXP/META`。
   - `labels`：项目或领域标签，例如 `mobile`、`onboarding`、`accessibility`。
   - `activities`：已有 `discover/design/build/verify/review/ship/observe/learn`，只能由 `activity.recorded` 产生。
3. **旧记录不重写**：历史 JSONL 保持原样；归一化通过追加事件表达，不重命名旧卡、不覆盖历史语义。
4. **索引不是事实源**：`INDEX.md` 和聚合指标均可删除、重建，不能被当作任务状态的唯一来源。
5. **前置门分级**：治理 bootstrap 永远允许；明确的一文件、低风险、可逆修正可以轻量执行；其他任务必须先有 capture，修改/外部效果还需要更高生命周期与证据。
6. **主机能力诚实标注**：只有拥有真正的工具前置拦截 API 的宿主才标记 `enforced`；没有该能力的宿主只能标记 `audit` 或 `warn`。

---

## 1. 文件边界与职责

### IDC 上游（`D:\intent-driven-coding`）

**Modify**
- `idc_core/events.py`：新增归一化、关系、学习候选事件类型和 payload 校验。
- `idc_core/projector.py`：增加主场景、标签、关系、学习候选、归一化遗留值的状态字段。
- `idc_core/workflow.py`：增加 intake、关系、学习候选、作用域检查和外部效果检查的工作流方法。
- `idc_core/cli.py`：增加 `intake`、`guard`、`relate`、`learn`、`index`、`effect-check` 命令；保留旧参数兼容。
- `idc_core/render.py`：投影中明确显示 Type、Labels、Activities、Related tasks、Learning candidates。
- `idc_core/metrics.py`：增加按类型、状态、关系、范围变更、学习候选和证据结果的聚合。
- `idc_core/resources/idc-task-event-v1.schema.json`：扩展新事件的合法 payload，同时保持旧事件可验证。
- `hooks/hooks.json`、`hooks/pre-tool-guard`、`hooks/run-hook.cmd`：Claude Code 前置工具门；只在宿主确实支持时启用 enforce。
- `.opencode/plugins/intent-driven-coding.js`：接入 OpenCode 的工具前置检查；若当前 OpenCode API 无法阻断，返回明确的 audit/warn 状态。
- `skills/team/SKILL.md`：把 intake 作为第一可执行动作，并说明 guard 状态矩阵；仅在适配器能安全调用 IDC 命令时增加 `Bash` 能力。
- `docs/PROGRESSIVE_TASKS.md`、`docs/TASK_SCENARIOS.md`、`docs/KNOWN_TENSIONS.md`、`docs/CLI.md`、`docs/CLAUDE_CODE_ADAPTER.md`、`docs/OPENCODE_ADAPTER.md`：写入单一执行语义、边界和主机能力差异。
- `evals/pre-work-gate.json`、`evals/scope-change-gate.json`、`evals/release-gate.json`、`evals/lightweight-near-miss.json`：记录实际工具顺序和预期阻断。

**Create**
- `idc_core/guard.py`：纯策略判断模块；输入工具、操作、路径、当前记录和外部效果，输出 allow/deny/warn、原因和 required_action。
- `idc_core/index.py`：从事件流生成任务索引，不把索引逻辑塞进 render 或 metrics。
- `scripts/migrate_progressive_records.py`：LAS/通用项目可复用的 dry-run/apply 归一化工具。
- `tests/test_guard.py`、`tests/test_index.py`、`tests/test_record_normalization.py`、`tests/test_learning_candidates.py`、`tests/test_relationships.py`：对应行为测试。

### LAS 适配（`D:\LAS 5.2.3`）

**Modify**
- `IDC.md`：成为执行顺序的项目入口，明确 bootstrap 例外、intake、scope guard、外部效果门。
- `CLAUDE.md`：保留 LAS 会话规则，加入首个允许动作和轻量任务例外。
- `AI_ENGINEERING_PLAYBOOK.md`：把前置门、动态 scope gate、release gate 写成项目工作协议。
- `.idc/README.md`：增加 guard 模式、索引、关系和学习候选的保留规则。
- `.idc/config.json`：升级 schema/version 与 `guard.mode`、边界映射配置；运行时文件仍按现有 gitignore 策略处理。
- `scripts/validate_project_governance.py`：验证 LAS 的 guard 配置、上游镜像和边界规则。
- `.agents/skills/team/SKILL.md`：镜像上游后保留 LAS 路由增强，并要求第一动作走 intake。
- `opencode.json`、`.claude/` 适配文件：只在宿主验证确认后加入前置 hook，不复制个人权限配置。

**Create**
- `.idc/boundaries.json`：项目边界映射，例如 frontend/backend/database/auth/external/deploy；只记录可验证的路径和命令模式。
- `.idc/tasks/INDEX.md`：生成投影，不手工维护。
- `scripts/validate_idc_records.py`：LAS 本地记录归一化、类型漂移和关系完整性检查。
- `evals/` 下 LAS 真实工具顺序验收夹具。

---

## 2. Task 1：先建立语义模型，不改文件名

### 2.1 写失败测试

在上游新增测试，先固定以下行为：

```python
state = fold_events([
    captured_event,
    {
        "type": "classification.changed",
        "payload": {
            "primary_type": "FEAT",
            "labels": ["mobile", "accessibility"],
            "from": None,
            "to": ["FEAT", "mobile", "accessibility"],
            "reason": "initial classification",
        },
    },
    {
        "type": "activity.recorded",
        "payload": {"name": "build"},
    },
])

assert state.primary_type == "FEAT"
assert state.labels == ["mobile", "accessibility"]
assert state.activities == ["build"]
assert "build" not in state.labels
```

再加兼容测试：旧 payload 只有 `to: ["EXP", "BUILD", "REVIEW"]` 时，不能把 `BUILD`/`REVIEW` 计入 `primary_type` 或 `labels`；它们进入 `legacy_classification_values` 并在迁移报告中被标出。

### 2.2 实现状态字段与事件兼容

在 `TaskState` 增加：

```python
primary_type: str | None = None
labels: list[str] = field(default_factory=list)
legacy_classification_values: list[str] = field(default_factory=list)
relationships: list[dict[str, str]] = field(default_factory=list)
learning_candidates: list[dict[str, Any]] = field(default_factory=list)
```

保持 `classifications` 作为旧 API 的兼容别名或兼容投影，不能立即删除；新代码读取 `primary_type`/`labels`。`classification.changed` 同时接受旧 `to` 与新 `primary_type`/`labels`。

允许的主类型集中在 `idc_core/scenarios.py`，避免 CLI、迁移器、metrics 各自维护一套列表。活动集合继续由现有 `activity` 命令控制。

### 2.3 扩展事件类型

新增：

- `classification.normalized`：追加式记录旧分类被如何解释，不覆盖原始事件。
- `task.related`：payload 为 `relation`、`target_task_id`、`reason`。
- `learn.candidate`：payload 为 `candidate`、`evidence_refs`、`proposed_destination`、`status`。

更新 `CORE_EVENT_TYPES` 和 JSON Schema。Schema 对新字段做最小约束，不给 payload 设置会破坏现有历史事件的 `additionalProperties: false`。

### 2.4 更新 CLI 与 workflow API

新增工作流方法：

```python
Workflow.normalize_classification(record_id, primary_type, labels, legacy_values, reason)
Workflow.relate(record_id, relation, target_task_id, reason)
Workflow.record_learning_candidate(record_id, candidate, evidence_refs, proposed_destination)
```

新增 CLI：

```text
idc classify --type FEAT --label mobile --label accessibility --reason ...
idc relate --relation continues --target IDC-LAS-20260915-002 --reason ...
idc learn --candidate "mobile contract must cover new interactive controls" --destination test --evidence-ref a-001
```

保留旧的 `--class` 参数，并把它转换成兼容路径；对于 `BUILD`、`REVIEW` 这类活动词给出清晰错误或迁移提示，而不是静默写入类型字段。

### 2.5 更新投影

`render_card()` 的 Current State 增加：

```text
- Primary type: `FEAT`
- Labels: mobile, accessibility
- Activities: build, verify
- Related tasks: continues IDC-LAS-20260915-002
- Learning candidates: 1 pending
```

旧卡没有这些字段时显示 `unclassified`/`none`，不制造推断事实。

### 2.6 验证

运行：

```bash
python -m unittest tests.test_progressive_tasks tests.test_progressive_workflow tests.test_progressive_cli
```

预期：旧分类 API 测试继续通过；新语义测试通过；任务 ID 不包含 `FEAT` 等可变类型。

---

## 3. Task 2：归一化历史记录，不改写事件、不重命名卡

### 3.1 写迁移器 dry-run 测试

对测试 fixture 建立以下输入：

```text
old classifications: EXP, BUILD, REVIEW
expected primary_type: EXP
expected legacy_activity_values: BUILD, REVIEW
expected file name: unchanged
expected event history: unchanged in dry-run
```

测试 apply 模式只追加 `classification.normalized`，原始事件的 seq、payload、timestamp 不变。

### 3.2 实现迁移器

`scripts/migrate_progressive_records.py` 提供：

```text
python scripts/migrate_progressive_records.py --project <path> --dry-run
python scripts/migrate_progressive_records.py --project <path> --apply
```

输出每条记录：原始值、推导主类型、自由标签、活动遗留值、风险提示。`--apply` 使用 EventStore append，不能直接编辑 JSONL；已存在归一化事件时幂等跳过。

迁移规则：

1. 已知九个场景码中第一个作为 `primary_type`；其他场景码作为 labels。
2. `BUILD/VERIFY/REVIEW/SHIP/INTAKE/DESIGN/PLAN/LEARN` 不进入类型；若没有对应 activity 事件，只记为 `legacy_activity_values`，不伪造活动事实。
3. 未知值进入 labels，并在报告中提示人工确认。
4. 任务文件名、旧手写卡和 legacy snapshot 不改名、不覆盖。

### 3.3 LAS 执行策略

在 LAS 先 dry-run，人工审阅迁移报告，再 apply。现有 12 条事件记录和旧手写卡都保留；迁移后的投影只增加归一化字段，不回写旧任务 Markdown。

### 3.4 验证

```bash
python scripts/migrate_progressive_records.py --project "D:\LAS 5.2.3" --dry-run
idc metrics --project "D:\LAS 5.2.3" --json
python scripts/validate_idc_records.py --project "D:\LAS 5.2.3"
```

预期：所有 `BUILD, REVIEW` 不再出现在新的类型统计中；旧事件总数只增加归一化事件数；旧文件名完全不变。

---

## 4. Task 3：生成索引与自我迭代指标

### 4.1 写索引测试

固定 `idc index --json` 返回稳定结构：

```json
{
  "tasks": [
    {
      "task_id": "IDC-LAS-20260916-002",
      "primary_type": "FEAT",
      "labels": ["onboarding"],
      "lifecycle": "closed",
      "outcome": "completed",
      "updated_at": "...",
      "related_tasks": [],
      "learning_candidates": 0
    }
  ]
}
```

测试 Markdown 投影按 task_id 稳定排序，生成两次内容相同，生成过程不追加事件。

### 4.2 实现 `idc_core/index.py`

索引只读取事件投影，输出 `.idc/tasks/INDEX.md`：

| Task ID | Type | Labels | Lifecycle | Outcome | Updated | Relations | Learning |
|---|---|---|---|---|---|---|---|

标题和摘要使用当前 goal/summary；无主类型显示 `unclassified`，不从文件名猜测新类型。

新增 CLI：

```text
idc index --project <path> --json
idc index --project <path> --write
```

`--write` 只写可重建的 INDEX.md，不修改事件流。

### 4.3 扩展 metrics

在现有 `build_progressive_metrics()` 保留现有字段，新增：

```json
{
  "type_counts": {"FEAT": 4, "FIX": 3, "EXP": 2},
  "lifecycle_counts": {"closed": 6, "active": 1},
  "uncompleted_by_type": {"FEAT": 6},
  "requirement_changes_by_type": {"FEAT": 2},
  "host_observed_failures": 1,
  "learning_candidates": 3,
  "relationship_counts": {"continues": 2, "supersedes": 1}
}
```

不要合成单一健康分数；指标要保留状态、证据来源和缺失值。

### 4.4 验证

```bash
python -m unittest tests.test_progressive_metrics tests.test_index
idc index --project "D:\LAS 5.2.3" --write
idc metrics --project "D:\LAS 5.2.3" --json
```

检查：移动端三轮任务可通过关系和标签聚合；类型统计不把活动计入类型；未完成验收项按类型可见。

---

## 5. Task 4：第一类 intake 操作与首份报告

### 5.1 写 intake 测试

新增 `idc intake`，等价于受治理约束的 `start`，但输出固定结构：

```json
{
  "record_id": "work-...",
  "lifecycle": "captured",
  "primary_type": "META",
  "labels": ["governance"],
  "outstanding_obligations": ["intent:goal", "acceptance"],
  "next_allowed_activity": "shape-or-promote"
}
```

测试 intake 必须先追加 `request.captured`，再追加初始 classification；不能在 intake 之前产生源代码检查事件。

### 5.2 实现统一 intake API

在 `idc_core/intake.py` 或 `workflow.py` 提供窄接口，CLI 与 host adapter 共用：

```python
intake(project, summary, primary_type, labels, temporary=False) -> IntakeReport
```

返回结构化报告，默认输出紧凑首份工作报告；完整卡仍可通过 `--json` 获取。`start` 保留为兼容别名并调用同一实现。

### 5.3 Team Skill 能力

更新 team Skill：第一步调用 `idc intake`，再读取项目源码。若宿主只能通过 Bash 调用 CLI，team Skill 明确只允许调用 `idc intake/guard/effect-check`；普通项目命令必须经过 guard。不要把“能描述命令”当作“已执行”。

在 Claude/OpenCode 适配器中分别验收；若无法给 Skill 提供窄工具接口，不声称 team 自己拥有执行能力。

---

## 6. Task 5：可执行 pre-work guard

### 6.1 写 guard 策略测试

在 `tests/test_guard.py` 固定策略矩阵：

| 当前状态 | 操作 | 结果 |
|---|---|---|
| 无记录 | 读 `AGENTS.md`/`IDC.md`/Playbook | allow bootstrap |
| 无记录 | 读 `backend/main.py` | deny + `idc intake` |
| 无记录 | 执行项目脚本/测试 | deny |
| 无记录 | Edit/Write/Agent | deny |
| captured | 只读源码/定向调查 | allow |
| captured | Edit/Write | deny + promote/shape |
| shaped/active | 读、测试、编辑 | allow，仍检查 scope |
| scope stale | 新边界路径 | deny + `idc change` or `idc shape` |
| trivial exemption | 一文件、低风险、可逆 | allow lightweight，并返回原因 |
| external effect | commit/push/deploy | deny until effect-check passes |

### 6.2 实现 `idc_core/guard.py`

定义明确输入输出：

```python
@dataclass(frozen=True)
class GuardRequest:
    project: Path
    record_id: str | None
    tool: str
    operation: str
    paths: tuple[str, ...] = ()
    boundary: tuple[str, ...] = ()
    effect: str | None = None
    target_sha: str | None = None

@dataclass(frozen=True)
class GuardDecision:
    decision: Literal["allow", "deny", "warn"]
    reason: str
    required_action: str | None
    mode: Literal["bootstrap", "lightweight", "captured", "shaped", "active", "validating", "external"]
```

策略细节：

1. Bootstrap allowlist 只允许读取 `AGENTS.md`、`CLAUDE.md`、`IDC.md`、`AI_ENGINEERING_PLAYBOOK.md`、`SQUADS.md`、`docs/TASK_SCENARIOS.md`、`.idc/README.md` 及适配器声明文件。
2. 无 capture 时拒绝源码读取、项目脚本、测试、编辑、写入和 implementation Agent。
3. captured 允许调查和证据采集，但禁止修改；需要修改时要求 promote + shape。
4. 对低风险一文件例外使用显式 `lightweight` 判定，并记录判定理由；不得由任意“看起来简单”字符串自动豁免。
5. 路径/命令匹配 `.idc/boundaries.json`，发现 frontend→backend、无持久化→ORM、local→deploy、无 auth→token 等边界变化时返回 `IDC scope is stale`。
6. 外部效果统一进入 `effect-check`，不由单个宿主脚本各自实现一套规则。

### 6.3 CLI 与宿主 hook

新增：

```text
idc guard --project <path> --tool Bash --operation execute --paths backend/...
idc effect-check --project <path> --effect deploy --target-sha <sha> --json
```

Claude Code：新增 `PreToolUse` hook，读取宿主 JSON 请求，调用 guard，返回 allow/deny；保留现有 SessionStart hook 只做上下文注入。

OpenCode：在插件支持工具前置事件时接入同一 guard；若当前 API 无法阻断，插件只能输出 warn/audit，并在 host acceptance 报告中明确“未强制”。

### 6.4 验证实际工具顺序

使用假的工具请求和临时项目验证：

```text
bootstrap read -> allowed
backend read before intake -> denied
idc intake -> allowed and request.captured first
backend read after intake -> allowed
edit before promote/shape -> denied
promote + shape -> edit allowed
frontend-only -> backend path -> scope stale denied
```

这些测试必须检查 guard decision 与事件顺序，不能只检查最终 Markdown 卡片。

---

## 7. Task 6：动态 scope gate 与外部效果 gate

### 7.1 Scope gate

新增 `scope-check` 内部策略，读取当前 `scope`、`impacts`、`uncertainty` 和 `.idc/boundaries.json`：

```text
IDC scope is stale.
Current record: frontend-only
Observed change: backend API + ORM + production deployment
Required action: idc change or idc shape before continuing
```

`idc change` 记录 before/after/reason，并令任务回到 `shaped`；scope 变更不能只靠 `classification.changed` 代替。

### 7.2 Effect gate

新增 `effect-check`，对 commit、push、deploy、生产写入、外部发布统一检查：

- task lifecycle 为 `shaped`、`active` 或 `validating`；
- acceptance 存在；
- 与 acceptance 映射的 fresh passing evidence 存在；
- exact target SHA 已记录；
- exact effect 的 permission 已 `granted`；
- recovery/rollback 条件存在；
- 目标环境和副作用范围明确。

不满足时只返回 deny，不执行外部动作。保留现有“提交/推送需要显式授权”原则。

### 7.3 测试

新增正反例：

- frontend-only → backend API/ORM：必须先 `idc change` 或 `shape`；
- local-only → deploy：必须先 permission + recovery + target SHA；
- 有证据但没有 exact permission：仍 deny；
- 有 permission 但没有 fresh evidence：仍 deny；
- 一文件 typo：不要求 durable record。

---

## 8. Task 7：routing evaluation 与 host acceptance

新增四类上游评测：

1. **Positive intake**：`继续接手活动系统改造` 的第一个 durable event 是 `request.captured`，源码调查前已有 capture。
2. **Scope change**：frontend-only 变成 backend API + ORM，编辑前出现 `scope.changed` 或 `requirement.changed`，旧 scope 不继续被当作有效。
3. **Release**：`部署这个` 进入 release route，target SHA、验收证据、permission、recovery 都在 effect-check 前存在。
4. **Near miss**：明显一文件拼写修正走 lightweight，不强制完整卡片。

评测记录必须包含：工具调用序列、guard decision、事件序列、最终卡片；不能只比较最终文本。

Claude/OpenCode host acceptance 各跑一套真实用例，并分别标记 `enforced`、`warn`、`unobservable`。不得因为 Skill 或文档出现了 `idc intake` 就判定路由已生效。

---

## 9. Task 8：LAS 迁移与灰度上线

### 9.1 先只读基线

在 LAS 生成：

```bash
python scripts/migrate_progressive_records.py --project "D:\LAS 5.2.3" --dry-run
idc metrics --project "D:\LAS 5.2.3" --json
idc index --project "D:\LAS 5.2.3" --json
```

保存类型漂移报告：哪些卡把 `BUILD/REVIEW` 混入分类、哪些任务缺主类型、哪些任务可形成移动端/引导/活动系统关系簇。

### 9.2 迁移与投影

- 先在 LAS 本地 apply 归一化事件；不重命名 `IDC-LAS-20260914-001.md` 等历史文件。
- 生成 `.idc/tasks/INDEX.md`，验证移动端三轮任务、引导任务、活动演示任务能通过关系或标签检索。
- 对现有 `IDC-LAS-20260917-001`、`IDC-LAS-20260918-001` 这类未完成任务，只补语义字段，不改变其生命周期和未完成状态。

### 9.3 适配入口与配置

- `IDC.md` 写清“第一允许动作是 intake；bootstrap 例外；轻量例外；scope/effect gate”。
- `CLAUDE.md` 和 LAS team Skill 删除只靠提醒的重复措辞，改为指向 `idc guard` 和宿主 hook 状态。
- `.idc/README.md` 增加索引、关系、学习候选、迁移事件与 guard 审计记录说明。
- LAS `validate_project_governance.py` 检查 `.idc/boundaries.json`、镜像 Skill 和 gate 配置。
- 版本升级为下一个方法论版本（建议 `1.2.0`，不要伪装成普通补丁），先在上游完成再镜像到 LAS。

### 9.4 灰度模式

按三阶段启用，避免一次性把宿主工作流锁死：

1. `audit`：记录违规顺序，不阻断；收集真实误报。
2. `warn`：阻断高风险和外部效果，低风险边界只警告。
3. `enforce`：对非轻量任务强制 intake、scope 和 effect gate；必须保留宿主不支持时的明确降级状态。

---

## 10. Verification Matrix

### 上游 IDC

```bash
python -m unittest discover -s tests
python scripts/validate_repository.py
python scripts/validate_contracts.py
python scripts/evaluate_contracts.py
python scripts/audit_skills.py
```

额外要求：

- 新事件通过 JSON Schema；
- 旧 1.1.1 事件可读；
- `idc metrics` 字段向后兼容；
- `idc index --write` 幂等；
- guard 单元测试覆盖 bootstrap/captured/shaped/external/lightweight；
- evals 验证工具顺序而非最终卡片；
- Claude/OpenCode 真实宿主结果分别记录，不混为“通过”。

### LAS

```bash
python scripts/validate_project_governance.py --idc-source "D:\intent-driven-coding"
python scripts/validate_idc_records.py --project "D:\LAS 5.2.3"
idc doctor --project "D:\LAS 5.2.3" --json
idc index --project "D:\LAS 5.2.3" --write
idc metrics --project "D:\LAS 5.2.3" --json
```

遵守 LAS 的验证成本纪律：不因治理层改动运行无关的生产全量回归；对 guard/CLI/迁移器做定向测试，对宿主门禁做真实 host acceptance。

### 回归保护

- 现有 12 条渐进式事件记录可读；
- 旧手写 `IDC-LAS-<SCENARIO>-...` 文件不改名；
- `IDC-LAS-<DATE>-<SEQ>` 新 ID 继续稳定；
- 一文件低风险修正仍可轻量完成；
- 没有前置 hook 的宿主不会被误报为 enforced；
- `BUILD`/`REVIEW` 不再进入新的类型统计；
- 任务索引可由事件流重建，删除索引不损失事实。

---

## 11. 明确不做

- 不把场景类型塞进新的任务文件名；
- 不批量重命名或重写旧任务卡；
- 不靠正则猜测所有语义 scope；边界配置允许项目明确声明；
- 不把 `team` Skill 中的文字描述当作宿主已经执行了 guard；
- 不为一文件、低风险、可逆修正强制完整 durable record；
- 不在没有 host API 支持时伪造 Claude/OpenCode 的强制门禁；
- 不把所有指标压成单一健康分数；
- 不把索引 Markdown 当作事件事实源。

---

## 12. 建议提交拆分

1. `feat: add typed task semantics, relationships, learning candidates, and index`
2. `feat: add intake and executable pre-work guard`
3. `feat: add dynamic scope and external-effect gates`
4. `test: add ordering-based routing and host acceptance evaluations`
5. `feat: adopt IDC 1.2.0 governance gates in LAS`

每个提交都应先有对应失败测试，再实现，再跑定向验证；上游完成并打 `v1.2.0` 后才镜像到 LAS。

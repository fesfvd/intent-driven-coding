# IDC 工作方式（自用版 - 核心原则层）

> 这是常驻配置。始终生效，但只在关键时刻产生作用。

---

## 1. 证据优先（Evidence-First）

在声称以下结果前，必须粘贴实际的命令输出：
- "已修复"
- "测试通过"
- "构建成功"
- "验证完成"

**格式要求：**
```
验证：[描述]
$ [完整命令]
[stdout/stderr 输出]
退出码：[0 或非 0]
```

**反例：**
❌ "我已经修复了这个 bug，测试都通过了"

**正例：**
✅ "修复完成，验证如下：
```
$ npm test -- auth.test.js
PASS  tests/auth.test.js
  ✓ login with valid credentials (45ms)
  ✓ login with invalid credentials (23ms)
  
Test Suites: 1 passed, 1 total
Tests:       2 passed, 2 total
退出码：0
```
"

---

## 2. 信息分类（Information Classification）

将需求信息分为 4 类，并在实现前明确标注：

| 类型 | 来源 | 处理方式 |
|------|------|---------|
| **明确需求** | 我直接说的 | 转为可验证行为，不改变含义 |
| **仓库事实** | 代码/配置/测试 | 自行查询（用 Read/Grep/codegraph_explore），不问我 |
| **建议默认** | 你推荐的方案 | 明确标注"建议"，不伪装成我的需求 |
| **开放歧义** | 影响产品/权限/数据的选择 | 列出选项，询问我 |

**实践示例：**
```
我："给报表添加导出功能"

你的分类：
✓ 明确需求：添加导出功能
✓ 仓库事实：当前使用 Apache POI，已有 ExportService 基础设施
✓ 建议默认：用 Excel 格式（.xlsx）← 要标注"建议"
? 开放歧义：是否需要权限控制？（当前其他导出功能无权限检查）← 要问我
```

---

## 3. 权限边界（Permission Gates）

以下操作需要**明确询问授权**，不能隐式执行：
- `git commit` / `git push`
- 部署到远程环境
- 修改 auth / billing / privacy 相关代码
- 删除数据 / 执行 migration
- 调用付费 API

**询问格式：**
```
修复完成，验证通过。

接下来需要：git commit -m "fix: handle null in UserRepository"
影响范围：users 模块

是否授权 commit？
```

---

## 4. 复杂任务识别与 IDC 升级（半自动核心）

### 检测逻辑
遇到以下情况，主动建议启用 IDC 完整流程：

| 场景 | 识别标志 | 建议方法 |
|------|---------|---------|
| **未知根因 bug** | 报错/异常，但原因不明 | debug 方法 |
| **跨模块功能** | 涉及 3+ 文件或 API 契约变更 | architecture 方法 |
| **高风险变更** | DB schema / auth / billing / privacy | architecture + code-review |

### 建议格式（必须遵守）
检测到复杂任务时，用以下格式询问：

```
检测到 [任务类型]，建议启用 IDC [方法名] 处理。

这将包括：
- [关键步骤 1]
- [关键步骤 2]
- [关键步骤 3]

预计额外时间：X-Y 分钟
收益：[说明为什么值得]

输入 "IDC" 启动完整流程，或输入 "快速" 跳过（仅核心原则生效）。
```

### 触发 IDC 完整流程的条件

**用户输入包含以下关键词之一：**
- `IDC`（单独或作为句子开头）
- `用 IDC 处理`
- `IDC debug` / `IDC 架构` / `IDC verify`

**行为：**
1. 明确响应："收到。启动 IDC [方法] 流程..."
2. 读取对应的专业方法文件：
   - Bug 诊断 → `/d/intent-driven-coding/self-use/skills/debug.md`
   - 架构设计 → `/d/intent-driven-coding/self-use/skills/architecture.md`
   - 验证 → `/d/intent-driven-coding/self-use/skills/verify.md`
3. 生成轻量任务卡（见第 5 节）
4. 执行三阶段流程：诊断/设计 → 实现 → 验证
5. 每个阶段生成交接物，保存到 `.idc/tasks/{task-id}/`

---

## 5. IDC 任务卡（两种模式）

### 模式 A：轻量任务卡（默认，用于 80% 的任务）

**生成时机：** 启动 IDC 完整流程时

**文件位置：** `.idc/tasks/YYYYMMDD-NNN.md`

**初始内容：**
```markdown
# [类型] 任务标题

**任务 ID**：YYYYMMDD-NNN  
**开始时间**：YYYY-MM-DD HH:MM  
**风险评估**：低/中/高

## 执行记录
（执行过程中逐步追加，不是预先填写）

---
**状态**：进行中
```

**追加时机：**
- 诊断完成 → 追加根因定位
- 实现完成 → 追加修改文件列表
- 验证完成 → 追加验证结果
- 任务完成 → 追加结束时间和总耗时

**最终示例：**
```markdown
# [FIX] API /users 返回 500

**任务 ID**：20260909-001  
**开始时间**：2026-09-09 14:23  
**风险评估**：中

## 执行记录

### 诊断阶段
- 断裂点：UserRepository.java:45
- 根因：查询返回 null 时未做防御性检查
- 详细诊断：[diagnosis.md](./20260909-001/diagnosis.md)

### 实现阶段
- 修改文件：UserRepository.java (+5 lines)
- 主要变更：添加 null 检查和默认值返回

### 验证阶段
- ✓ 原始错误已解决
- ✓ 单元测试通过（15/15）
- ✓ 回归测试通过（237/237）
- 详细报告：[verification.md](./20260909-001/verification.md)

---
**状态**：已完成  
**结束时间**：2026-09-09 14:35  
**总耗时**：12 分钟
```

### 模式 B：决策日志卡（用于复杂任务，涉及重要架构决策）

**触发条件：** 任务涉及以下情况时，询问是否使用决策日志模式
- 技术选型（选择 Redis vs Memcached）
- 架构变更（重构数据流）
- 重要权衡（性能 vs 一致性）

**文件位置：** `.idc/tasks/YYYYMMDD-NNN-decision.md`

**格式：**
```markdown
# [类型] 任务标题

**任务 ID**：YYYYMMDD-NNN  
**时间**：总耗时 Xh Ym

## 决策 1：[问题描述]
**背景：** [当前状态/痛点]  
**目标：** [要达到的结果]  
**方案：** [选择的方案]

## 决策 2：[技术选型]
**候选方案：**
- A. [方案 A] - 优点：___ / 缺点：___
- B. [方案 B] - 优点：___ / 缺点：___

**选择：** A  
**理由：** [权衡依据]

## 关键坑点
- [踩过的坑 1]
- [踩过的坑 2]

## 遗留问题
- [ ] [待优化项 1]
- [ ] [待解决项 2]

## 相关链接
- 详细架构分析：[architecture.md](./YYYYMMDD-NNN/architecture.md)
- PR: #1234
```

---

## 6. 三阶段工作流程（IDC 完整流程）

启动 IDC 后，按以下阶段执行：

### 阶段 1：诊断/设计（根据任务类型选择）

**Bug 任务 → 诊断：**
- 读取 `debug.md` 方法
- 可靠复现
- 逐层定位断裂点
- 形成可证伪的根因假设
- 生成交接物：`.idc/tasks/{task-id}/diagnosis.md`

**功能任务 → 设计：**
- 读取 `architecture.md` 方法
- 追踪当前数据流
- 设计变更方案
- 分析影响范围和兼容性
- 生成交接物：`.idc/tasks/{task-id}/architecture.md`

### 阶段 2：实现
- 基于阶段 1 的交接物实现代码
- 如果涉及重要决策，记录到任务卡（决策日志模式）

### 阶段 3：验证
- 读取 `verify.md` 方法
- 执行验证清单
- 粘贴所有命令输出
- 生成交接物：`.idc/tasks/{task-id}/verification.md`

---

## 7. 专业方法文件路径

| 方法 | 路径 | 何时读取 |
|------|------|---------|
| debug | `/d/intent-driven-coding/self-use/skills/debug.md` | 启动 bug 诊断时 |
| architecture | `/d/intent-driven-coding/self-use/skills/architecture.md` | 启动架构设计时 |
| verify | `/d/intent-driven-coding/self-use/skills/verify.md` | 进入验证阶段时 |

---

## 8. 工作模式总结

```
简单任务（80%）：
  你："把按钮改成绿色"
  → 核心原则层生效（证据 + 权限）
  → 无 IDC 流程，快速完成

AI 主动建议（15%）：
  你："报表保存后显示空白"
  → AI 检测到未知根因 bug
  → AI："建议启用 IDC debug，输入 'IDC' 启动"
  → 你："IDC"
  → 启动完整流程

你主动启动（5%）：
  你："IDC 给报表添加缓存"
  → 直接启动完整流程
```

---

## 9. 调整建议

如果你觉得：
- **AI 建议太频繁** → 修改第 4 节的"检测逻辑"，提高阈值
- **任务卡太简单** → 默认使用决策日志模式
- **任务卡太复杂** → 只生成最终摘要，不保存交接物

这个配置文件随时可以编辑调整。

---

**核心理念：轻量常驻 + 按需升级 + 你说了算**

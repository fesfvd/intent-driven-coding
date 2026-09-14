# IDC 自用版（输入 "IDC" 启动）

> 兼容性说明：本目录是面向个人 Claude Code 工作流的轻量配置与示例，
> 不是 IDC 当前的权威任务存储实现。新项目应优先使用仓库根目录的
> `idc` CLI：请求先写入 `.idc/work-items/*/events.jsonl`，再按需生成
> `.idc/tasks/<task-id>.md` 投影。这里的任务卡和阶段交接物仅用于个人习惯、
> 旧项目迁移或尚未安装 CLI 的场景，不应事后补造正常任务历史。

## 快速配置（5 分钟）

### 1. 复制配置到你的项目
```bash
# 在你的项目根目录执行
cp /d/intent-driven-coding/self-use/CLAUDE.md .claude/CLAUDE.md

# 或者在 Windows 下
copy D:\intent-driven-coding\self-use\CLAUDE.md your-project\.claude\CLAUDE.md
```

### 2. 使用方式

#### 模式 A：日常任务（自动生效）
```
你：把这个按钮改成绿色

AI：（核心原则层自动工作，但无感知）
    [修改代码]
    [粘贴验证输出]
    是否 commit？
```

#### 模式 B：AI 主动建议
```
你：报表保存后显示空白

AI：检测到未知根因 bug，建议启用 IDC 完整流程（诊断 → 实现 → 验证）。
    预计额外 5-8 分钟，可以更系统化地定位根因。
    
    输入 "IDC" 启动，或输入 "直接修" 跳过。

你：IDC

AI：[启动完整流程]
```

#### 模式 C：你主动启动
```
你：IDC 处理报表缓存功能

AI：[直接启动完整流程，读取 architecture 方法]
```

---

## 工作流示例

### 简单任务（核心原则层生效）
```
你：修改登录页标题为 "欢迎回来"

AI：[修改文件]
    
    验证：
    $ npm run build
    ✓ Build successful
    
    修改完成。是否 commit？
```
**IDC 价值**：强制了构建验证 + commit 授权询问

---

### 中等 Bug（AI 建议 → 你启动 IDC）
```
你：API /users 返回 500

AI：这是一个错误排查任务。我可以：
    A. 直接看日志尝试修复（快速，5-10分钟）
    B. 用 IDC debug 方法系统化诊断（稳妥，10-15分钟，会生成诊断报告）
    
    推荐：如果是生产问题或根因不明，建议 B
    
    你的选择？输入 "IDC" 启动完整流程，或 "快速" 直接修。

你：IDC

AI：收到。启动 IDC debug 流程...
    
    [读取 /d/intent-driven-coding/self-use/skills/debug.md]
    
    === 任务卡生成 ===
    任务ID：20260909-001
    类型：[FIX] API /users 返回 500
    风险：中
    
    === 阶段 1/3：诊断 ===
    
    1.1 复现问题
    $ curl http://localhost:3000/api/users
    {"error": "Internal Server Error"}
    
    1.2 查看日志
    $ tail -n 50 logs/app.log
    [粘贴日志，发现 NullPointerException]
    
    1.3 定位断裂点
    追踪调用链：
    UserController.getUsers() → UserService.findAll() → UserRepository.query()
    断裂点：UserRepository.java:45
    
    1.4 根因假设
    假设：查询返回 null 时，未做防御性检查
    验证：[构造 null 场景，确认触发相同错误]
    
    诊断交接物已保存：.idc/tasks/20260909-001/diagnosis.md
    
    === 阶段 2/3：实现修复 ===
    
    基于诊断结果，修改 UserRepository.java:45
    [显示 diff]
    
    === 阶段 3/3：验证 ===
    
    [读取 /d/intent-driven-coding/self-use/skills/verify.md]
    
    验证清单：
    ✓ 原始错误已解决
      $ curl http://localhost:3000/api/users
      {"users": [...]}  ← 正常返回
      
    ✓ 单元测试通过
      $ mvn test -Dtest=UserRepositoryTest
      Tests run: 15, Failures: 0, Errors: 0
      
    ✓ 回归测试通过
      $ mvn test
      Tests run: 237, Failures: 0, Errors: 0
    
    验证交接物已保存：.idc/tasks/20260909-001/verification.md
    
    === 任务完成 ===
    总耗时：12 分钟
    
    任务卡已更新：.idc/tasks/20260909-001.md
    
    是否授权 commit？
```

---

### 复杂功能（你主动启动 IDC）
```
你：IDC 给报表 API 添加 Redis 缓存

AI：收到。启动 IDC 完整流程...
    
    [读取 /d/intent-driven-coding/self-use/skills/architecture.md]
    
    === 任务卡生成 ===
    任务ID：20260909-002
    类型：[FEAT] 报表 API Redis 缓存
    风险：高（涉及数据一致性）
    
    === 阶段 1/3：架构设计 ===
    
    1.1 当前数据流
    [绘制流程图]
    
    1.2 缓存策略设计
    
    决策 1：为什么需要缓存？
    - 背景：报表生成耗时 3-8 秒
    - 目标：< 500ms 响应
    
    决策 2：为什么选 Redis？
    - 多实例部署，需共享缓存
    - 报表数据大（平均 200KB），内存缓存易 OOM
    - 权衡：Redis 增加网络延迟（~2ms），但可接受
    
    决策 3：TTL 选择
    - 方案 A：5 分钟（数据准实时可接受，重复查询占比 78%）
    - 方案 B：30 秒（更新及时，但缓存命中率低）
    - 推荐：A
    
    你确认这些决策吗？或有调整？

你：确认

AI：好的，继续...
    
    1.3 失效策略
    - 保存时主动 DEL 缓存键
    - 缓存键格式：report:{type}:{userId}:{paramsHash}
    
    架构交接物已保存：.idc/tasks/20260909-002/architecture.md
    
    === 阶段 2/3：实现 ===
    [实现代码...]
    
    === 阶段 3/3：验证 ===
    [运行测试...]
    
    === 任务完成（决策日志版）===
    
    任务卡（决策日志）已保存：.idc/tasks/20260909-002.md
    内容包括：
    - 3 个关键决策及权衡
    - 缓存键设计理由
    - 踩过的坑（如果有）
    - 遗留问题（监控指标待添加）
    
    3 个月后你可以复盘这些决策。
    
    是否授权 commit？
```

---

## 配置文件说明

### .claude/CLAUDE.md（核心原则层 - 常驻）
- 证据优先
- 信息分类
- 权限门禁
- 复杂任务检测逻辑

### 专业方法文件（按需读取）
- `self-use/skills/debug.md` - Bug 诊断方法
- `self-use/skills/architecture.md` - 架构设计方法
- `self-use/skills/verify.md` - 验证清单

### 任务卡模板
- `self-use/templates/task-card-lite.md` - 轻量版
- `self-use/templates/task-card-decision.md` - 决策日志版

---

## 触发关键词

| 你说 | AI 行为 |
|------|---------|
| "IDC" | 启动完整流程，读取相关方法 |
| "IDC debug" | 强制使用 debug 方法 |
| "IDC 架构" | 强制使用 architecture 方法 |
| "快速" / "直接修" | 跳过 IDC 流程（仅核心原则生效） |

---

## 自定义调整

### 如果你觉得 AI 建议太频繁
编辑 `.claude/CLAUDE.md`，提高触发阈值：
```markdown
## 复杂任务升级（修改这里）
只在以下情况建议 IDC：
- 未知根因 bug 且涉及 5+ 文件  ← 提高到 5+ 文件
- 跨模块功能 且涉及 API 契约变更
- DB schema / 安全 / billing 相关
```

### 如果你想添加自己的方法
在 `self-use/skills/` 下创建新文件，例如 `performance.md`：
```markdown
# Performance 优化方法

（你的方法论）
```

然后在 `.claude/CLAUDE.md` 中添加触发条件。

---

## 预期效果

| 场景 | 不用 IDC | 用 IDC（自用版） | 差异 |
|------|---------|----------------|------|
| 改 CSS 颜色 | 30 秒 | 30 秒 + 构建验证 | +5 秒（有价值） |
| 简单 bug 修复 | 5 分钟 | 5 分钟 + 证据粘贴 | +30 秒（有价值） |
| 未知根因 bug | 15-30 分钟（可能返工） | 12 分钟（系统化） | -3 到 -18 分钟 |
| 复杂功能 | 2 小时 | 2 小时 + 决策日志 | +5 分钟（长期有价值） |

---

## 文件清单（自用层）

| 文件 | 作用 | 状态 |
|------|------|------|
| `self-use/CLAUDE.md` | 常驻核心原则层（证据 / 信息分类 / 权限 / 升级判定） | 已完成 |
| `self-use/skills/debug.md` | Bug 系统化诊断方法（三步定位法） | 已完成 |
| `self-use/skills/architecture.md` | 跨层变更设计方法（现状追踪 → 影响半径 → 决策 → 回滚） | 已完成 |
| `self-use/skills/verify.md` | 证据优先验证方法（验证梯度 + 覆盖矩阵 + 完成门禁） | 已完成 |
| `self-use/templates/task-card-lite.md` | 轻量任务卡模板（默认，覆盖 80% 任务） | 已完成 |
| `self-use/templates/task-card-decision.md` | 决策日志卡模板（选型 / 架构 / 权衡类任务） | 已完成 |

---

## 下一步

1. 把 `self-use/CLAUDE.md` 复制到目标项目的 `.claude/CLAUDE.md`（见本文开头"快速配置"）。
2. 如果目标项目不在 `D:\intent-driven-coding` 同级环境，把 `CLAUDE.md` 第 7 节的方法路径改成实际路径——目前写的是绝对路径 `/d/intent-driven-coding/self-use/skills/...`。
3. 新项目先初始化并记录真实请求：
   `idc init --project <project> --project-key <KEY> --platform claude-code`，
   然后执行 `idc start`；只有在工作变得持久时再 `idc promote`。检查
   `.idc/work-items/<record-id>/events.jsonl` 是否成为事实来源，
   `.idc/tasks/{task-id}.md` 仅作为生成投影。旧项目或暂时不能安装 CLI 时，
   才按本文示例检查自用任务卡与交接物。
4. 跑完后按"自定义调整"收缩或放宽触发阈值；只保留真正减少返工的规则。

**尚未验证：** 以上流程是设计意图，不是效果证据。自用层还没有真实项目的完成记录；触发阈值（第 4 节）和任务卡字段是否够用，要靠实际使用后的复盘来调整，不要因为文档写得完整就认为已经有效。

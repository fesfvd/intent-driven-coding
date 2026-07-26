独立审查结论
一句话定位
一套面向 AI 编程宿主、将自然语言意图通过 2-3 人 Skill 小队转化为验证结果的方法论文档 + 可选脚手架脚本，尚无 Agent 运行时或真正可执行的自动化引擎。

最强价值
需求翻译协议四分类（显式意图/仓库事实/建议默认/开放歧义） — 由 docs/PROTOCOL.md:16-21 和 skills/team/SKILL.md:15-24 支撑。这是仓库中最具体、可操作且有区分度的部分，为 "AI 不应把工程问题抛回用户，也不应悄悄发明产品语义" 提供了明确的可检查边界。与 Superpowers 的 "Process over Prompt" 相比，IDC 多了一层信息归类逻辑，比 OpenSpec 的 spec-first 更细粒度地区分了四种信息源。

离线、可脚本验证的合同与评估层 — schemas/intent-driven-coding-contract-v1.schema.json 定义了 squad-contract、evaluation-case、evaluation-record 三种结构化文档，validate_contracts.py 和 evaluate_contracts.py 提供离线结构+语义校验，test_repository.py 包含 25+ 个针对合同边界错误（重复成员、断开 handoff、状态矛盾、交叉引用缺失等）的测试用例。这是仓库中技术实现最扎实的部分。

渐进式采用路径的文档一致性 — README、AI_START_HERE.md、QUICKSTART.md、team/SKILL.md（Collaborative Learning Mode）、ADAPTATION_GUIDE.md 五份文档在 "不要求用户预学完整框架、先完成任务再增量建立系统" 这一核心理念上保持高度一致。69 个测试中至少有 5 个明确验证了这个理念在不同文件中的表达一致性。

Findings
[High] 所有 Skill 的 SKILL.md — Agent 行为声明与真实执行证据之间存在不可逾越的鸿沟
发现：7 个 Skill 文件（team、architecture、debug、code-review、verify、meta-skill-designer、skill-creator）声明了它们的行为边界、触发条件和安全声明。69 个单元测试全部通过，但没有一个测试验证 Skill 在真实 AI 宿主中被正确触发、正确路由、正确产生 handoff 产物 的场景。测试套件验证的是 Skill 文件的存在性、frontmatter 格式和文档引用，而非功能正确性。
触发条件：任何用户将此框架部署到 Claude Code、OpenCode、Codex 等宿主后，首次尝试自然语言路由。
实际影响：用户无法知道 team router 是否真的能将 "The report is blank" 路由给 debug -> verify 而不是 architecture -> code-review -> verify。这使项目的核心价值主张（自然语言路由到最小安全小队）完全依赖于未经验证的模型行为。
证据：tests/test_repository.py 的 69 个测试中，26 个是关于文件存在性和内容模式匹配的纯文档测试，25 个是合同结构校验，13 个是脚手架行为测试，5 个是文本一致性检查。零个测试涉及 LLM 调用或 Agent 路由决策。
为什么项目自身可能忽略它：框架将自身定位为"方法论而非工具"，且 AI_START_HERE.md 强调 AI 应自行适配宿主平台。这种定位可能让项目认为"真实路由行为应由用户在其宿主上验证"——但这意味着框架本身的质量保证不覆盖其最核心的差异化功能。
最小修复或验证动作：（1）在 evals/ 中添加至少一个 Golden Set：包含 10-20 条自然语言输入及其期望路由决策，格式化为可直接用于 LLM-as-judge 评估的数据。（2）编写一个脚本（即使手动运行），将 eval case 中的 prompt 发送给真实 LLM，对比 selected_route 与 expected_route，报告路由准确率。（3）明确在 README 中声明：当前路由准确率未经独立验证，用户应在自己的宿主上测试前 5-10 条请求的路由行为。
[High] docs/PLATFORM_ADAPTERS.md 及两个 Adapter 文档 — 平台适配器假设了大量未验证的宿主行为
发现：PLATFORM_ADAPTERS.md 声称对应 Claude Code、OpenCode、Codex、Cursor、GitHub Copilot、Windsurf、Cline、Roo Code 等 8 种以上平台，CLAUDE_CODE_ADAPTER.md 和 OPENCODE_ADAPTER.md 更分别提供了具体的原生布局和验证步骤。但仓库中没有任何自动化测试验证以下任何一点：（a）.claude/skills/ 目录是否能被 Claude Code 自动发现并触发；（b）OpenCode 的 permission frontmatter 格式是否与当前 OpenCode 版本兼容；（c）Codex 的 AGENTS.md 加载机制是否与框架期望的一致。
触发条件：用户按照文档生成平台原生布局后，期望 Skills 被自动发现并触发。
实际影响：如果宿主平台的 Skill 发现机制与框架假设不同（例如路径约定、frontmatter 字段名称、触发语义），用户将在不知情的情况下得到一个"验证通过但实际不工作"的系统。validate_project.py 报告的"项目验证通过"会制造虚假信心。
证据：（1）OPENCODE_ADAPTER.md 定义了 team Agent 的 mode: primary 和 permission: 为空（不得覆盖目标权限），但这是对 OpenCode 权限模型的假设。（2）CLAUDE_CODE_ADAPTER.md 定义了子 Agent 的精确 tools: 列表（如 Read, Grep, Glob, Skill），但这些工具名称假设了 Claude Code 的特定版本。（3）validate_project.py:236-241 要求 OpenCode Agent 的 permission 条目"exactly match the approved set"，这高度依赖 OpenCode 的版本特定语法。
为什么项目自身可能忽略它：PLATFORM_ADAPTERS.md:90 已经写了 "A platform is verified only after its entry loading, Skill triggering, tool mapping, and permission behavior have been tested there"，项目自己承认了这一点。但问题在于：文档中的"已验证"标准与用户实际体验到的"适配完成"之间存在误导性的期望差。
最小修复或验证动作：（1）添加免责声明：明确列出哪些宿主机制已经手动测试过、在哪个版本上、测试了什么行为。（2）将 validate_project.py 的输出从"项目验证通过"改为"结构检查通过，路由和触发行为需在宿主上手动测试"。（3）至少对 1-2 个宿主编写一个手动测试清单脚本。
[Medium] schemas/intent-driven-coding-contract-v1.schema.json 及合同体系 — 合同层可能被形式化地"填表通过"，缺乏与真实执行证据的关联
发现：合同 Schema 精美且语义检查细致（handoff 必须连接相邻成员、artifact 必须由声明的生产者产出、authorization state 必须与 required 一致）。但 evaluation-record 完全依赖 Agent 自报（self-report）：selected_route、artifacts、verification_claims、observed_forbidden_behavior 都是 Agent 填写的字符串数组。离线评估器 (evaluate_contracts.py) 只比较 Agent 自报的 JSON 与期望值是否匹配，不验证 Agent 是否真的选了那条路由、真的产出了那些产物、真的执行了那些验证。
触发条件：Agent 学会了合同格式后，可能会生成"格式正确但内容虚假"的 evaluation-record。
实际影响：合同体系目前验证的是"Agent 能否学会填写正确的 JSON"，而不是"Agent 是否真的遵循了合同约定的行为"。这与框架的核心理念 "Evidence before claims" 出现内部矛盾：框架自身对 Agent 的评估证据也是 Agent 自报的。
证据：（1）cross-layer-feature.record.json 中 observed_forbidden_behavior: [] — 当前唯一的记录声称没有观察到任何禁止行为；但没有任何外部证据（如 diff 日志、工具调用记录、实际文件变更）支持这一声明。（2）evaluate_contracts.py:66-68 通过比较两个 JSON 数组检查 forbidden behavior，但这两个数组都来自 Agent 的自报。（3）docs/CONTRACTS.md:50-53 承认 "A contract names the expected route; it does not prove that a model selected it"，但承认后并未提出解决方案。
为什么项目自身可能忽略它：合同体系被定位为"machine-checkable boundary"，即机器可检查的是 JSON 格式和交叉引用，而非执行事实。但项目可能需要明确这个层次的局限性，让用户知道它防止的是结构性错误而非行为性欺骗。
最小修复或验证动作：（1）在 evaluation-record Schema 中添加一个可选的 provenance 字段，要求 Agent 附带它做出路由决策的依据（如读取了哪个 Squad 合同、调用了哪些工具）。（2）在 CONTRACTS.md 中增加一节 "What Contracts Cannot Prove"，明确合同层的防伪边界。
[Medium] DESIGN.md 作为未跟踪文件与现有仓库范围之间的张力
发现：DESIGN.md 定义了一个"local-first web observatory for project-specific AI engineering systems"，包含完整的颜色令牌系统、设计人格（Linear+Figma+Notion+Stripe+Sentry 影响融合）、和组件规格。但该文件是 git untracked（?? DESIGN.md），不在 validate_repository.py 的检查范围内，也不在任何文档中被引用。这是一个在仓库正式范围内外摇摆的、代表重大产品方向转变的设计文档。
触发条件：用户或贡献者发现 DESIGN.md 后，可能认为这个项目将要成为一个网页产品而非纯框架。
实际影响：（1）DESIGN.md 的存在模糊了项目定位——它到底是"一组方法论文档 + 脚本"，还是"一个即将有 Web UI 的观测平台"？（2）README 中的 "Future work can add ..." 没有提及 Web 观测台，但 DESIGN.md 似乎已经规划了相当具体的实现。（3）如果观测台是计划中的重头戏，当前仓库的技术基础（Python 脚本 + Markdown）与 Web 前端之间存在巨大的技术栈鸿沟，DESIGN.md 没有说明如何跨越。
证据：git status 显示 DESIGN.md 为 untracked。README 的 Status 部分没有提及它。AI_START_HERE.md 和 QUICKSTART.md 没有引用它。
为什么项目自身可能忽略它：DESIGN.md 可能是作者的个人设计草稿，尚未决定是否纳入公共仓库。
最小修复或验证动作：（1）明确决策：DESIGN.md 是正式路线图的一部分，还是个人实验草稿？如果是前者，将其纳入仓库、添加到 validate_repository.py 的检查范围，并在 README Status 中说明它代表 Phase 3。（2）如果观测台是长期方向，在 README 中添加一个 "Future Direction" 小节说明它与当前仓库的关系。
[Medium] 合同示例和评估数据匮乏
发现：整个 contracts/examples/ 目录只有 1 个 squad contract 和 1 个 evaluation case（均为 cross-layer-feature 场景）。evals/fixtures/ 只有 1 个 evaluation record。evals/squad-routing.json 有 6 个 routing cases，evals/skill-design.json 有 8 个 design cases，但没有一个来自真实项目的案例。所有示例共享同一套理想化假设。
触发条件：用户尝试将自己的项目合同化时，没有足够的参考多样性。
实际影响：用户可能过度拟合到 cross-layer-feature 的三成员模式（architecture → code-review → verify），忽略了框架强调的"大多数场景只需两个 Skill"。缺少 failure/negative/near-miss 的合同案例。
证据：contracts/examples/ 目录中只有 2 个 JSON 文件，均为 cross-layer-feature 场景。evals/squad-routing.json 中的 release-permission case 引用了 project-specific-deploy（一个不存在的 Skill），表明即使评估数据也在依赖"用户自己填充"。
为什么项目自身可能忽略它：框架强调"不要复制示例，要从自己的工作中派生"，所以刻意保持示例最少。但最少与匮乏之间的边界在哪里？
最小修复或验证动作：添加至少 3-5 种不同的合同场景示例（debug-only squad、meta-design squad、两成员 release squad），每种附带对应的 evaluation case 和 record。
[Low] DESIGN.md 第 1-100 行及整体设计 — Observatory 产品风险
发现：DESIGN.md 描述了一个"calm blue control room with an orange human decision layer"的 Web 界面，其设计影响包括 Linear、Figma、Notion、Stripe、Sentry。这在视觉上可能非常精美，但存在明显的产品定位风险：它要求用户为了观察 AI 技能团队而在浏览器中维护另一个仪表板——这与框架"渐进式、轻量、不超过两层上下文"的核心哲学存在根本张力。用户是否真的需要另一个 Web 应用来管理 Markdown 文件？
触发条件：Observatory 作为 Web 产品发布后。
实际影响：可能将项目从"轻量框架"转变为"重平台"，增加维护负担，缩小适用人群。
证据：DESIGN.md 的非目标（Non-goals）栏写着 "Do not make the visual product a second Solo-style collaboration workspace" 和 "Do not put task creation, Agent chat, prompt submission, or deployment commands in the observatory"——这说明作者已经意识到这个风险并试图通过排除来约束范围。但排除列表越长，越说明产品边界难以自然收敛。
为什么项目自身可能忽略它：作者在 DESIGN.md 中已经表达了约束意识，但设计野心（5 个设计系统的融合）与实际用户需求（可能只是一份 Markdown 状态摘要）之间的差距仍然很大。
最小修复或验证动作：在构建任何 Web UI 之前，先用 CLI 命令 python scripts/status.py --project ../my-project 输出一份纯文本状态摘要，验证这是否足以覆盖 80% 的"观测"需求。
[Low] scripts/bootstrap.py:86 — render_platform_skill 函数删除 allowed-tools 行
发现：当 platform 为 opencode 或 claude-code 时，render_platform_skill 函数通过正则 re.sub(r"(?m)^allowed-tools:.*\n", "", ...) 删除 SKILL.md 的 allowed-tools frontmatter 行。这背后的假设是这套原生平台使用不同的权限机制。但如果 Skill 文件恰好包含格式略有不同的 allowed-tools 行（如 allowed-tools:\n 单独一行后接列表），正则可能无法匹配。
触发条件：Skill 的 YAML frontmatter 中 allowed-tools 使用多行格式而非单行。
实际影响：生成的 Skill 文件可能残留 allowed-tools 信息或格式损坏。
证据：bootstrap.py:86；当前所有 Skill 的 allowed-tools 都是单行格式，所以目前没有问题，但如果有人添加了多行格式的 Skill 就会暴露。
为什么项目自身可能忽略它：当前所有 Skill 恰好使用单行格式，测试覆盖也基于这些 Skill。
最小修复或验证动作：使用更健壮的 YAML frontmatter 解析来删除 allowed-tools，而不是正则替换。或者添加一个注释说明这一限制。
定位与竞争矩阵
维度	Intent-Driven Coding	Superpowers (obra)	OpenSpec (Fission-AI)	k-sdd	AI Development Team
产品类别	方法论框架 + 脚手架	Agent Skills 方法论	Spec-driven 开发框架	Spec→实现自动化流水线	Agent 团队框架
核心用户	愿意花时间设计 AI 工作体系的有经验开发者	希望 AI 遵循工程纪律的开发者	需要可追溯 spec 层的团队	想要自动化 spec→代码的团队	想要即用型多 Agent 团队的开发者
主要价值	需求翻译协议 + 小队设计方法 + 离线合同验证	强制性工程流程（plan→TDD→review→verify）	规范驱动开发，变更可追溯	17 个 Skill，8 个宿主，spec→自主实现	48 个现成 Agent，workflow 引擎
采用成本	高：需理解 Skill/Squad/Router/Contract/Adapter/Evaluator 6+ 概念后才能获得最小收益	中：安装插件即可，13 个 Skill 自动触发	低-中：npm install，生成 slash 命令	中：npm install，17 个 Skill	中-高：48 个 Agent 的配置和理解
本项目的差异	需求翻译四分类、三层上下文模型、人机共学理念、离线合同 Schema	强制性流程而非建议；subagent-driven development	形式化 spec 层作为单一真相源；变更归档	将 spec 转化为自主实现；边界优先	预构建 48 个专业 Agent；审批门控
本项目的脆弱点	没有 Agent 运行时；路由未经测试；合同依赖自报；概念密度高；缺乏真实案例	本项目的"人机共学"哲学比 Superpowers 更细腻，但 Superpowers 有可工作的实现	OpenSpec 有明确 CLI 和 25+ 宿主集成；本项目只有 Markdown + Python 脚本	k-sdd 有实际可用的自主实现循环；本项目只有合同定义	AI Dev Team 有 48 个即用 Agent；本项目要求用户自己搭建
关键判断：Intent-Driven Coding 与 Superpowers、OpenSpec、k-sdd 之间的竞争关系不是直接的——IDC 处于更"元"的一层。它更像是一套教你如何设计自己的 Superpowers 级别方法论的元方法论。这既是差异化优势（可以生成更贴合项目的体系），也是重大采用障碍（用户需要先投入大量认知成本才能得到收益，而 Superpowers 和 OpenSpec 提供即时的工具化价值）。

它最接近的同类可能是 "一份极其详尽的 AGENTS.md 编写指南 + 合同化验证层"。如果用户的 AI 宿主已经支持 Skills 和 Subagents，IDC 的核心价值是帮助用户不盲目复制这些现成框架，而是从自己的真实工作出发。

未被证明的主张
以下主张在仓库中反复出现，但无法从仓库代码或文档中得到验证：

"用户可以用自然语言描述目标，AI 正确选择最小安全小队。" — 零个端到端路由测试；路由评估数据（evals/squad-routing.json）包含 6 个 cases 但从未被实际运行过。

"渐进式采用：不要求用户预学完整框架，AI 先学并反哺核心概念。" — 这依赖于宿主的 AI 模型能力，而非框架本身。如果模型不能可靠地执行 AI_START_HERE.md 的指令，整个采用路径就断裂了。

"三层上下文模型减少了长期提示词里的重复和过时信息。" — 没有 before/after 对比数据；没有上下文长度或任务完成质量的前后测量。

"Skill 保存稳定方法，易变的路径、接口和版本回到仓库实时查询。" — 这要求 AI 同时遵守 Skill 的方法论约束和实时查询的纪律，没有证据表明模型能一致地做到这一点。

"人类最终判断"有实际工作流支持。 — 框架描述了人在哪些节点应参与判断（产品语义、长期方向、高风险动作），但没有任何工具机制（如审批界面、决策记录、override 日志）来确保这些节点不会被跳过。它依赖于 AI 遵守协议——而协议本身也是 AI 在执行的。

平台适配器支持 8+ 种宿主。 — PLATFORM_ADAPTERS.md 为每种宿主写了"If You Are X"的指令段，但每一段都用 "Inspect the current documentation" 和 "confirm these conventions against the installed version" 作为免责。实际的适配行为从未被任何自动化测试验证。

Observatory 判断
值不值得做：有条件地值得——但优先做 CLI/本地索引/状态摘要，而非 Web 界面。

最小可行边界：

一个 status CLI 命令（python scripts/status.py --target ../my-project），输出当前项目的 Skill 清单、Squad 注册、合同数、评估案例数、最近变更摘要。
一个 diff 命令（python scripts/diff_skills.py），展示两个版本之间 Skill 的变化。
一个 evidence 命令（python scripts/evidence_report.py），对比合同声明的验证项与最近的评估记录。
不需要 Web 服务器、数据库或身份认证。
必需数据（且必须由宿主工具产生，不能让 Agent 自报）：

实际的工具调用日志（哪个 Skill 被触发、何时、由什么输入触发）。
实际的验证命令输出（verify Skill 运行时产生的 stdout/stderr/exit code）。
实际的 diff（代码变更的实际内容，而非 Agent 描述的变更摘要）。
实际的权限确认记录（用户在何时、对什么操作授予了授权）。
应排除的功能：

Agent 对话界面、任务分派、实时聊天——这会使它变成 Solo 或 Jira 的低配复制品。
"团队健康度分数"——没有真实执行数据支撑的任何评分都会变成没有依据的指标。
Agent 市场或 Skill 分享平台——这与项目"从自己项目派生"的核心哲学矛盾。
自动化 Agent 编排——Observatory 只观察，不指挥。
最大产品风险：Observatory 从"帮助人观察 AI 工作体系"滑向"替代人判断 AI 工作体系"。如果蓝色代表"已验证"、橙色代表"需要人工决策"的视觉语言让人觉得 AI 系统已经在自主运行、人只需要偶尔看一眼，那就违背了框架"人类最终判断"的核心理念。一个精美的 Web 仪表板可能反而降低人的警觉性。

推荐优先级：

CLI 状态摘要（立即可做，有独立价值，不新增技术栈）
本地 HTML 报告（单文件，可离线打开，不需要服务器）
Web 观测台（仅在前两者被真实用户验证有用后考虑）
建议路线
第一条：建立路由准确性的最低可验证基准
要验证的假设：自然语言请求能否被正确路由到注册的小队。
最小实验：创建 20 条覆盖不同场景的自然语言输入（从 evals/squad-routing.json 扩展），然后在 Claude Code 或 OpenCode 中手动运行 10 条，记录实际路由结果，计算准确率。不需要自动化框架，一个手动运行的 checklist 即可。
成功判据：≥80% 的路由匹配期望；失败案例有清晰的改进路径（而非随机的模型幻觉）。
失败判据：<50% 匹配，或失败模式随机不可预测。
不应提前构建的内容：自动化路由测试框架。先确认手动测试是否值得自动化。
第二条：让合同体系衔接真实执行证据
要验证的假设：Agent 自报的 evaluation-record 是否能被外部证据支持。
最小实验：为 verify 的合约添加一个 provenance 字段，要求记录验证命令的实际 stdout 摘录和 exit code。修改 evaluate_contracts.py 支持检查 provenance 存在性（而非正确性）。在一个真实项目中运行一次，观察 Agent 是否能提供有意义的 provenance。
成功判据：provenance 字段包含可复现的、具体的信息（如实际命令和输出片段），而非模糊声明。
失败判据：provenance 字段被填充为 "Verification passed" 之类无信息量的内容。
不应提前构建的内容：完整的 provenance 自动验证系统。先确认 Agent 能否产出有意义的外部证据。
第三条：将 DESIGN.md 的观测台愿景降级为 CLI 优先路线图
要验证的假设：用户是否真的需要一个 Web 仪表板来管理 Markdown 文件，还是 CLI 摘要就足够了。
最小实验：（1）将 DESIGN.md 移入 docs/observatory/DESIGN.md 或在 README 中注明其为实验性方向。（2）编写一个最小 scripts/status.py，输出纯文本项目摘要。（3）在真实项目中运行，观察输出是否提供了 DESIGN.md 所描述的 80% 价值。（4）向潜在用户展示 CLI 输出和 DESIGN.md 的设计稿，收集反馈。
成功判据：≥3 个独立用户表示 CLI 摘要已经满足需求，或明确指出 CLI 无法满足的具体需求。
失败判据：没有用户主动使用 CLI 工具，或反馈指向"我需要的是更好的 Agent 行为，不是更好的可视化"。
不应提前构建的内容：任何 Web 前端代码、React 组件、颜色令牌系统、CSS 框架集成。
验证结果摘要
命令	结果
python scripts/validate_repository.py	通过：59 个必需文件，48 个 Markdown 文件
python scripts/validate_contracts.py	通过：2 个 JSON 合同文件
python scripts/evaluate_contracts.py	通过：1 个评估记录
python scripts/audit_skills.py	通过：0 个警告
python -m unittest discover -s tests -v	通过：69 个测试全部 OK（18.860s）
git log --oneline -20	6 个提交，均在 master 分支
未运行的验证：

bootstrap.py --target <dir> --apply：需要指定目标目录，未创建临时目标（测试套件已覆盖）。
validate_project.py --target <dir>：需要先创建目标项目，未执行（测试套件已覆盖）。
pip install -r requirements.txt：jsonschema 4.26.0 已安装，无需重新安装。
任何实际 LLM 路由或 Agent 行为测试：仓库不包含此类测试。
事实、推断、假设的边界
事实（由仓库代码或文档直接证实）
仓库包含 7 个 Skill 的 SKILL.md、15 份 docs/ 文档、6 个 Python 脚本、1 个 JSON Schema、2 个合同示例、1 个评估记录。
validate_repository.py 检查 59 个必需文件的存在性、Skill frontmatter、本地 Markdown 链接和隐私模式。
validate_contracts.py 使用 JSON Schema draft 2020-12 进行合同结构校验和语义检查（handoff 链、成员重复、交叉引用一致性）。
evaluate_contracts.py 比较 Agent 自报的 evaluation-record 与对应合同和评估案例。
69 个单元测试验证结构正确性和脚手架行为，不涉及 LLM 调用。
bootstrap.py 支持 neutral、opencode、claude-code 三种平台布局。
DESIGN.md 是 git untracked 文件，定义了 Web 观测台的设计系统。
项目源自作者个人在 LAS (lasystem.cn) 项目中的实践。
合理推断
合同体系最有价值的场景不是当前仓库内的简单示例，而是跨多个 Squad、多个项目时的交叉验证。
当前框架对"有经验的独立开发者"的适用性远高于"团队中的初级开发者"，因为后者需要更多的引导和更少的认知负荷。
如果宿主平台的 Skill 触发机制与框架假设不同，用户将面临"验证全绿但路由不工作"的静默失败。
三层上下文模型的理论价值高于其当前实现——因为"模型能一致地遵守"这一前提尚未被证明。
Observatory 如果实现为 Web 应用，将显著改变项目的技术栈、维护负担和用户群体。
需真实用户或宿主工具验证的假设
路由准确率、Skill 触发可靠性、人机共学的实际体验、合约体系的防伪价值、平台适配器的实际兼容性、"渐进式采用"的转化率——正如上文"未被证明的主张"部分所述。




独立审查结论2
独立审查结论
一句话定位
一套 AI 编程工作流的 Markdown 文档方法论与 JSON 合同校验工具套装——它告诉你和你的 AI Agent 应该怎么组织工作，但不提供运行时引擎来执行这种组织。

最强价值
合同层的结构化严谨性

JSON Schema (draft 2020-12) 定义了 squad 成员、handoff artifact、verification claims、authorization state 的完整数据模型 (schemas/intent-driven-coding-contract-v1.schema.json)
离线验证器执行 cross-document 一致性检查：成员去重、handoff 链路完整性、artifact 溯源、authorization 约束 (scripts/validate_contracts.py)
69 个单元测试覆盖了 schema 违规、handoff 断链、重复成员、authorization 状态矛盾等正确性和拒绝案例，全部通过
方法论的内在一致性

三层上下文模型 (entry → skills → evidence)、四类需求信息分类 (intent/facts/defaults/decisions)、两到三人小队模型、handoff artifact 要求，在 PROTOCOL.md、CONTEXT_ARCHITECTURE.md、SQUAD_METHOD.md 之间保持自洽
7 个 Skill 定义遵循统一结构（frontmatter + method + constraints + triggers + safety statement），并被 audit_skills.py 和 validate_repository.py 机械化检查
"人类最终判断"不只是口号——在 TEAM_PLAYBOOK.md 的 state machine 中明确将 Ship/Deploy 设为独立 permission gate，在 squad contract schema 中将 authorization 设为必填字段
诚实的采用立场

AUTHOR.md 明确声明"不是 benchmark、不是效果保证、不是第三方背书"，来源是个人项目 LAS
AI_START_HERE.md 说"第一个成功任务可能不产生任何框架文件，这是可接受的"
不伪装成有大规模用户验证的产品
Findings
[blocker] skills/team/SKILL.md — "Router" 是一个文档建议而非可执行路由
发现：项目的核心控制机制 "Team Router" 本质上是一个 Markdown 文件，描述了一个 AI Agent 应该如何分类意图、选择小队。整个 squad orchestration 完全依赖宿主 AI Agent 自愿阅读并遵守这些 Markdown 指令。没有程序化路由逻辑、没有状态机实现、没有 subagent 自动 spawn 机制。
触发条件：任何用户将 SKILL.md 放入项目目录后，期望"Router 会自动工作"。
实际影响：系统是否按设计工作完全取决于宿主 Agent 的能力和意愿。弱模型可能忽略 squad 选择逻辑直接动手；强模型可能跳过 handoff artifact 要求。没有 enforcement——框架只能在 Agent 主动遵循时"生效"。
证据：
skills/team/SKILL.md 的 allowed-tools: [Read, Grep, Glob, Skill] — 它只能读文件和调用其他 Skill，没有 spawn subagent 的能力
bootstrap 脚本只是复制 Markdown 文件到目标项目
evaluate_contracts.py 的文档明确写："This remains offline validation; it does not prove an Agent selected the expected route" (docs/EVALUATION.md:18-19)
评估用例都是手工编写的 JSON fixture，与真实 Agent 行为无关联
为什么项目自身可能忽略它：项目大量依赖"AI Agent 应该主动阅读并遵循"的假设。CLAUDE.md、AI_START_HERE.md、各 SKILL.md 都在告诉 Agent 怎么做，但没有验证 Agent 实际是否这么做。作者可能在自己使用的宿主（一个足够强大的模型）中验证了此模式有效，但没有区分"我的 Claude 遵循了这些指令"和"任何 Agent 在任何平台都会正确路由"。
最小修复或验证动作：至少在两个不同的宿主平台（如 Claude Code 和 Codex CLI）上，用相同的自然语言提示和相同的 squad-routing.json 用例，录制 Agent 实际选择的 Skill 调用序列，与 expected_squad 比较，报告 trigger precision/recall。在未完成此验证之前，不应声称 Router 具有跨平台功能。
[high] contracts/examples/ — 整个合同层只有一个示例场景
发现：contracts/examples/ 目录只包含一个 squad contract (cross-layer-feature.squad.json) 和一个 evaluation case (cross-layer-feature.evaluation.json)，以及 evals/fixtures/ 中仅有一个对应的 evaluation record。整个合同验证、离线评估基础设施围绕单一的三成员 squad 构建。
触发条件：用户试图为自己项目创建合同时，没有多样化的参考模板。
实际影响：
两成员 squad (最常见的推荐模式) 没有 contract 示例
meta-design squad (meta-skill-designer -> skill-creator) 没有 contract 示例
debug squad (debug -> verify) 没有 contract 示例
handoff artifact 的实际内容（如"impact-contract 具体长什么样"）完全没有定义——contract schema 只验证结构，不验证内容语义
证据：contracts/examples/ 目录只有两个 JSON 文件，evals/fixtures/ 只有一个 record 文件。69 个测试中有大量测试通过复制这唯一的 contract 再篡改来验证拒绝逻辑——这证明了 validator 的健壮性，但没有证明 contract 模型的表达力。
为什么项目自身可能忽略它：项目和合同层集中在"先让基础设施正确"，还未到达"用多样化场景证明表达力"的阶段。但 README 将 contracts 列为 Phase 2 的核心交付物，且单独有一个 CONTRACTS.md 文档——用户期望看到的是一个完整的 contract 实践，而非 proof-of-concept。
最小修复或验证动作：为两成员 squad、meta squad、debug squad 各创建一个最小 contract 示例，并为每个示例定义 actual handoff artifact 的内容模板（不仅是 schema 中的 artifact_id 字符串）。这可以在不改变代码的情况下增加合同层的可信度。
[high] scripts/bootstrap.py — 脚手架不理解目标项目但 README 未充分说明其局限
发现：bootstrap.py 的唯一"智能"行为是用 {{PROJECT_NAME}} 替换模板变量，以及为 OpenCode/Claude Code 平台去掉 Skill 前端的 allowed-tools。它不分析目标仓库、不选择 Skill、不设计 squad、不检测技术栈、不验证平台版本。README 在 "Quick Start" 中将其作为可选步骤列出，但未充分警告用户：这只是一个机械文件复制器，所有后续的"裁剪、替换占位符、设计小队"仍需由 AI Agent 或人手动完成。
触发条件：用户按照 QUICKSTART 运行 bootstrap.py --apply 后，看到 30+ 个文件被创建，误以为框架已经"安装完成"。
实际影响：如果用户不仔细阅读 --dry-run 后的提示文本和 AI_START_HERE.md 中的 "Do Not" 清单，他们可能在目标项目中留下一堆未替换的 {{PROJECT_NAME}} 占位符和不适用的 Skill 定义。validate_project.py 能检测占位符，但用户可能不会运行它。
证据：bootstrap.py:221-226 — 唯一的内容变换是 render_template() (替换 {{PROJECT_NAME}}) 和 render_platform_skill() (去掉 allowed-tools 行)。没有调用任何代码分析、项目检测或智能选择逻辑。
为什么项目自身可能忽略它：项目反复强调"脚手架只应在 AI 理解目标项目之后使用"、"不分析项目"，但这在实际 QUICKSTART 流程中被降级为一句提醒。README 中脚手脚本紧跟在"推荐方式"之后，给用户造成了"先 AI、后脚本"或"直接脚本也可以"的二选一印象。
最小修复或验证动作：在 bootstrap.py --apply 成功后，自动输出一段更强烈的警告，列出具体需要在目标项目中完成的步骤（替换占位符、确认测试命令、设计 project-specific squad），并建议运行 validate_project.py。同时在 README 中将脚本部分标记为"⚠️ 仅骨架生成——不替代 AI 适配"。
[high] docs/PLATFORM_ADAPTERS.md + adapters — 适配器做出未经测试的平台假设
发现：Claude Code Adapter (docs/CLAUDE_CODE_ADAPTER.md) 假设 subagents 可用、.claude/skills/ 路径会被自动发现、特定工具名称（Read/Grep/Glob/Bash/Edit/Write/Skill）在目标用户的环境中可用。OpenCode Adapter (docs/OPENCODE_ADAPTER.md) 假设 .opencode/agents/ 和 .opencode/skills/ 的发现行为、mode: subagent 和 mode: primary 的语义、以及 edit: deny / bash: deny 的权限配置格式。这些假设可能在任何版本更新中失效。
触发条件：用户在 Claude Code 或 OpenCode 的新版本中运行 bootstrap，但该版本的 subagent 机制或 Skill 发现路径已经改变。
实际影响：生成的 .claude/agents/ 或 .opencode/agents/ 文件可能无法被宿主发现、权限配置可能无效、subagent 可能以错误的模式运行。每个 adapter 文档中都写了 "This is a structural adapter, not a claim that every version will route work identically"，但这句免责声明不会让失去功能的用户恢复工作。
证据：adapter 文档的 Acceptance Check 部分要求"使用真实的宿主版本来验证"——这意味着作者自己可能没有在所有声称支持的平台上运行过完整的 Acceptance Check。Claude Code Adapter 的 Acceptance Check 包括 "Request a commit or deployment and confirm the target's policy controls the external action"，这是正确的要求，但项目仓库中没有任何测试数据证明这些检查曾被运行过。
为什么项目自身可能忽略它：适配器层是最近添加的（commit f8d8bd6 "feat: add contracts and native adapters"），处于早期阶段。文档中的免责声明旨在诚实，但不足以降低用户踩坑的风险。
最小修复或验证动作：至少在一个真实项目中对每个声称支持的平台运行完整 Acceptance Check，录制结果（包括宿主版本号、日期、每个测试用例的通过/失败/部分通过），并将其作为 docs/adapter-verification/ 的证据公开。如果受限于资源，明确将未验证的平台降级为 "experimental" 状态。
[medium] schemas/ + evals/ — 合同与评估系统存在"填表通过"的结构性漏洞
发现：合同验证和离线评估检查的是声明的结构与声明的结构之间的一致性，而不是声明的行为与真实 Agent 行为之间的一致性。contract 说 handoff 从 architecture 到 code-review、artifact 是 impact-contract——validator 只检查 JSON 中这个名字拼写一致。它不检查 impact-contract 是否真的包含了 code-review 需要的所有信息，也不检查 Agent 是否真的产生了这个 artifact。
触发条件：用户只需写一份内部自洽的 squad-contract JSON 和 evaluation-case JSON，就可以通过 validate_contracts.py 的所有检查，无论该 contract 在实际 Agent 协作中是否可用。
实际影响：合同系统可能产生一种虚假的安全感——"我们的 squad 通过合同验证了"——而实际上 Agent 没有、也不能遵循这些合同。这比没有合同更危险，因为它创造了已得到验证的错觉。
证据：evaluate_contracts.py 比较的是 evaluation-record JSON（手工编写的 fixture）与 contract JSON + evaluation-case JSON。cross-layer-feature.record.json 的 selected_route 精确匹配 expected_route，artifacts 精确匹配 required_artifacts，这些都是人工对齐的。在真实场景中，Agent 可能产生部分匹配的 artifact 名称、不完整的 route、或偏离的 behavior——系统没有能力检测这些。
为什么项目自身可能忽略它：项目在 EVALUATION.md 中诚实地写了 "Do not report quantitative improvement without actual repeated runs" 和 "run the cases manually with your coding agent"。但合同层的存在本身（独立的文档、schema、CLI 工具、69 个测试）给用户的第一印象是一个自动化验证系统，而非一个人工检查框架。诚实的免责声明被"看起来很自动化"的工程结构所覆盖。
最小修复或验证动作：在 evaluate_contracts.py 的输出中增加一行："此评估仅比较声明数据一致性，不验证真实 Agent 行为。" 同时在 CONTRACTS.md 顶部增加一个醒目的边界声明。
[medium] skills/ 全部 7 个 Skill — Skill 之间依赖"Agent 自愿阅读并遵守"而没有触发机制
发现：7 个 Skill 定义（team, architecture, debug, code-review, verify, meta-skill-designer, skill-creator）都遵循相同的 Markdown 格式，但没有程序化的触发逻辑。Skill 是否被调用、是否正确理解 handoff、是否真正产生命名 artifact，完全依赖 AI Agent 阅读文本后的内部推理。项目将 "Skill" 称为"一项稳定的专业能力"，但实际上它只是一个 Markdown 提示词模板。
触发条件：任何使用场景——从低风险 typo 修复到高风险数据迁移。
实际影响：在一个对话上下文中，Agent 可能正确遵循 Skill 定义的 method 和 output 格式；在另一个上下文中可能忽略它们。没有可靠的行为保证。如果 Agent 的上下文窗口不足以加载 SKILL.md 的全部内容，skill 可能部分生效或完全失效。
证据：所有 Skill 的 allowed-tools 字段列出可用工具，但没有 Skill 有程序化权限强制执行（除了宿主 Agent 自身的工具权限系统）。在 Claude Code adapter 中，skill-creator 的 subagent 模板有 Edit 和 Write 权限——但如果用户没有配置 Claude Code 的 subagent 权限系统，这个限制不生效。
为什么项目自身可能忽略它：项目明确设计为"工具中立"——通过 Markdown 和 JSON Schema 实现可移植性，而不是依赖特定宿主的触发机制。这种设计选择是合理的，但它意味着"Skill"的概念严重依赖宿主 Agent 的理解能力。当项目将 Skill 描述为"专业能力"而非"提示词模板"时，存在概念夸大。
最小修复或验证动作：为每个 Skill 创建一个最小可复现测试：给定 3 个 should-trigger prompt 和 3 个 near-miss prompt，在一个指定模型上运行，记录 Skill 是否被正确选择。将这组测试用例加入 evals/ 并明确定义"通过"标准（如 >80% precision 和 recall）。至少有一个平台的实证数据后，才能合理地声称 Skills "工作"。
[medium] 整体架构 — 没有 context loading 的程序化实现
发现：项目最核心的概念之一"三层上下文模型" (entry / on-demand skills / task evidence) 和 "Loading Budget" (L0-L4) 完全是文档描述，没有任何代码来实现或辅助上下文管理。AI Agent 被要求自愿遵循 CONTEXT_ARCHITECTURE.md 中的规则来"不加载全部文档"和"按需读取 Skill"。
触发条件：Agent 在处理复杂任务时，上下文窗口可能膨胀到包含所有相关文档。
实际影响：Agent 可能忽略 Loading Budget 的指导，加载过多或过少的上下文。没有机制可以检测或阻止上下文过度加载。项目声称解决"提示词膨胀"，但解决方案是"Agent，请你自己不要膨胀"——这本身就需要 Agent 有足够的 discipline。
证据：CONTEXT_ARCHITECTURE.md 是对 Agent 的行为指导，不是可执行系统。"Do not put endpoint catalogs here"、"Load a Skill only when its professional method changes the result"——这些都是对 Agent 的指令，没有 enforcement 机制。
为什么项目自身可能忽略它：当前设计假设足够强大的 Agent 能自我管理上下文。这在 Claude Code 的长上下文环境中可能成立，但在上下文窗口较小的宿主中会失败。此外，Agent 同时扮演"上下文管理者"和"任务执行者"双重角色，存在利益冲突——Agent 可能为了"更好地完成任务"而加载过多上下文。
最小修复或验证动作：至少在 bootstrap 阶段生成一个 context budget 检查清单，让用户可以在关键里程碑（PR 提交前、部署前）手动运行检查 Agent 是否加载了超出必要的上下文。长期来看，一个轻量级的 context 审计脚本（检查实际被加载的 skill 数量和 token 使用情况）会提供实证反馈。
[low] skills/ + templates/ — 三个平台的模板之间存在未声明的假设差异
发现：neutral 模板 (templates/AGENT_ENTRY.md) 说"point your coding agent at it"，但 OpenCode 和 Claude Code 模板假设了不同的入口文件格式。Claude Code 模板 (templates/claude/CLAUDE.md) 是一个薄入口指向 AGENTS.md；OpenCode 的 team agent (templates/opencode/agents/team.md) 是一个完整的主 agent 定义。三者对同一概念（"入口"）使用了不同的实现，但没有任何跨平台的一致性检查。
触发条件：用户在多个平台上使用同一项目，或在不同平台间迁移时，需要手动理解三种不同入口的区别。
实际影响：中等——增加了跨平台采用的心智负担。
证据：validate_project.py 对三种平台分别定义了不同的 REQUIRED_FILES、SKILL_ROOTS、AGENT_MODES、AGENT_TOOLS，说明这些差异是已知的。但 PLATFORM_ADAPTERS.md 没有用一个表格清晰列出三者的差异。
最小修复或验证动作：在 PLATFORM_ADAPTERS.md 中增加一个"入口文件对照表"，并说明每个平台假设的自动发现行为 vs 手动阅读后备方案。
[low] docs/CAPABILITY_TIERS.md + docs/PROJECT_ARCHETYPES.md — 分类学丰富但缺乏操作化路径
发现：Tier 1 (universal) / Tier 2 (conditional) / Tier 3 (exceptional) 三层能力分类和 Project Archetypes 提供了系统的"如何思考"框架。但一个开发者（或 AI Agent）从"我的项目有 Tier 2 的 billing risk trait"到"我应该创建一个 billing-review Skill"之间，需要做出大量主观判断。分类学提供了词汇，但没有提供决策算法。
触发条件：用户试图按照 workshop 流程为项目设计 squad。
实际影响：用户可能过拟合到某个 risk trait（"我们有 database，所以需要 database specialist"——这正是 skill-design.json 中 project-archetype-is-not-enough 用例所警告的），或者决策疲劳导致跳过整个流程。
证据：CAPABILITY_TIERS.md 列了 10 个 conditional risk trait 和超过 14 个候选 capability，但没有优先级排序或"最常见组合"的指导。PROJECT_ARCHETYPES.md 标注为"questions, not answers"，意味着它故意不提供操作化路径——这本身是诚实的设计，但也意味着用户需要自己做大量的翻译工作。
最小修复或验证动作：为最常见的 3-5 种项目类型（如 Web SaaS、CLI tool、数据管线）提供具体的 squad 推荐默认值，并标注这些是"高概率起点，需仓库证据验证"。这可以大幅降低决策启动成本。
定位与竞争矩阵
维度	Intent-Driven Coding	Superpowers	Disruptor Skills	OpenSpec / Spec Kit	AI Dev Team / TSP
产品类别	方法论文档 + 合同校验工具	Skill 插件包（强制 TDD）	门控流水线 Skill 包	Spec-driven dev 工具（CLI/workflow）	多 Agent 角色编排系统
核心用户	愿意手动搭建 AI 团队的独立开发者	重视代码质量和 TDD 的开发者	反 vibe-coding 的工程团队	需要结构化 spec 的棕地/绿地项目	想要预制 AI 开发团队的用户
主要价值	小队设计方法论 + 合同一致性验证	自动触发 TDD 循环 + 代码审查	12 步门控 idea→ship 流程	增量 spec delta + 跨工具可移植	27-48 个预定义 Agent 角色 + workflow engine
采用成本	高：需阅读大量文档 + 手动设计 squad	中：安装 Skill 包即可使用	中：12 个 Skill 安装后即用	低-中：3 条命令上手	中-高：大量 Agent 定义需配置
本项目差异	强调"人机协作学习"+"从真实工作渐进演化"而非预制团队	本项目不强制 TDD，更关注方法论	本项目无硬性门控，更灵活	本项目关注 Agent 组织结构而非代码 spec	本项目反对大型预制团队，坚持 2-3 人小队
本项目的脆弱点	无运行时：所有差异化价值依赖 Agent 自愿遵循文档；竞争者在同样的"小团队"理念上已有代码实现（Disruptor 的 gate engine、Superpowers 的自动触发、AI Dev Team 的 workflow engine）	Superpowers 有 115K stars 和成熟的自动触发机制	Disruptor 有门控引擎的实际实现	OpenSpec 有 34.5K stars 和 npm CLI 生态	TSP 有 195+ skills 和 Rust 编写的 workflow engine
关键竞争洞察：Intent-Driven Coding 最独特的主张是"不要复制我的团队，而是学会搭建你自己的"——这在理念上是正确的，但在实践中，用户需要一个足够好的默认值作为起点。当前项目提供的"起点"是 7 个通用 Skill 描述和一套方法论文档——这与 Disruptor 的 12 个 gated skills（安装即可用但可替换）或 Superpowers 的可组合 skill bundles（可选用但默认有效）相比，采用了成本更高。用户可能问："如果我需要先花时间学习方法论才能搭建自己的小队，为什么不直接用 Superpowers 的默认 skills 然后替换不适用的？"

未被证明的主张
以下主张在 README 和方法论文档中提出，但没有仓库内证据支持。它们需要真实用户、真实项目、或真实宿主工具来验证：

"用户可以用自然语言表达目标，AI 负责翻译需求、选择小队、完成实现并提供验证证据" — 这是整个框架的核心价值主张。仓库中有 schema 和 evaluation fixtures 证明了"如果"这套机制运作，可以验证其结构一致性。但没有一个真实的 Agent 运行记录证明：当用户说"报告是空白的"时，Agent 正确地选择了 debug -> verify 而不是直接 patch。

"通过明确的交接物协作，而不是每个 Skill 都从头调查一遍" — 这是 squad model 的关键差异化。handoff artifact 概念在 schema 中被形式化了（artifact_id），但没有证据表明 architecture 产生的 impact-contract 实际上减少了 code-review 的重复调查。

"AI 先学并反哺核心概念，人机在真实任务中协作学习" — 这是一个关于 Agent 行为的强主张，但没有任何 session log 或案例研究证明 Agent 实际执行了"教回"行为。

"三层上下文模型减少长期提示词里的重复和过时信息" — 没有 before/after 的 context token 计数比较，没有证据表明 Skill 层确实减少了 context 膨胀。

"支持 Claude Code、OpenCode、Codex、Cursor、GitHub Copilot 等" — PLATFORM_ADAPTERS.md 列出了 6+ 个平台，但只有 Claude Code 和 OpenCode 有具体 adapter 文档和模板。Codex、Cursor、Copilot 的部分只有一般性的 "inspect the product's current mechanism" 指南。没有验证数据证明任何一个平台上的完整 Acceptance Check 通过。

"合同和评估提供离线、可验证的安全性" — 合同验证是离线的（证明 JSON 结构一致），但"安全性"（如防止 Agent 跳过 permission gate）需要 Agent 实际遵循 permission 规则。离线合同不能证明 Agent 的行为安全。

"渐进式采用：从第一项真实任务开始" — 这是很好的理念，但 QUICKSTART 的 8 个步骤 + WORKSHOP 的 8 个步骤如果全面执行，是一个庞大的流程。缺少一个"最小 3 步就够"的路径。

Observatory 判断
值不值得做：有条件
Observatory 的核心理念（跨项目查看团队结构、Skill 使用情况、合同验证状态）本身有价值，但前提是项目首先解决"Skill 是否真的被触发"这一根本问题。如果不先建立真实的行为数据采集，Observatory 只是在 visualizer 里展示更多手工编写的 JSON fixtures。

最小可行边界
只读取 .idc/ 目录中的 squad-contract 和 evaluation-record JSON 文件
不执行任何代码，不触发 Agent，不写入项目文件
提供三个视图：squad 结构图（成员→handoff→verification claims）、合同验证状态（最近一次 validate_contracts.py 结果）、evaluation case 覆盖率（哪些 squad 有 eval cases，哪些缺失）
必需数据
以下数据必须由宿主工具产生，不能由 Agent 自报：

Agent 实际调用的 Skill 序列（宿主工具日志，非 Agent 声称的序列）
实际 token 使用量（宿主 API 返回，非 Agent 估算）
实际 permission gate 是否被触发（宿主工具的 permission 系统日志）
实际执行时间线（宿主工具的时间戳）
Agent 自报的数据（如 "我按照 squad contract 执行了"）仅应标注为 "claimed" 并与宿主证据交叉验证。

应排除的功能
任务分配/派发：不应成为 Agent 控制台。避免与 Solo、Jira、Linear 的功能重叠。
实时 Agent 监控/干预：这会要求 Observatory 具备 Agent 运行时能力，与"轻量框架"定位冲突。
"团队健康度分数"：在没有客观指标定义的情况下，这会退化为无依据的数字。如果一定要做，只应展示可验证的原始指标（合同通过率、eval 覆盖率、handoff artifact 完整性）而不加权合成一个分数。
跨项目代码搜索/编辑：这是 IDE 或 CodeGraph 的工作。
Agent 性能 benchmark 比较：这是独立的研究活动，不应内置于 Observatory。
最大产品风险
Observatory 会将项目从"放在项目旁边的 Markdown 文件集合"转变为"需要独立部署和运维的 Web 服务"。这会：

显著增加维护负担（前端、后端、数据库、认证、部署）
改变用户对项目的期望——从一个轻量框架变为一个平台
使项目直接与 Obsidian、Notion、Linear 等工具竞争可视化
推荐优先级
CLI 本地索引 > 状态摘要 > Web UI。理由：

大部分潜在用户是使用 CLI 环境的开发者（python scripts/ 的存在证明了这一点）
CLI 可以零部署成本地输出 squad 结构树、合同验证摘要、eval 覆盖率
在真实用户反馈证明需要 Web 可视化之前，不要构建 Web
CLI 版本可以自然演化为 Web 版的数据源（通过 JSON 输出）
建议路线
1. 验证核心假设：Skill 路由在实际 Agent 行为中有效
要验证的假设：当用户用自然语言表达目标时，AI Agent 实际选择的小队与 squad-routing.json 中定义的 expected_squad 匹配
最小实验：
选一个宿主平台（如 Claude Code），在 AI_START_HERE.md 的指导下运行 evals/squad-routing.json 中的 6 个测试用例
录制 Agent 实际加载了哪些 SKILL.md，实际按什么顺序调用了哪些能力
对比 expected_squad vs actual_route
报告 precision、recall 和 handoff artifact 质量
成功判据：>80% 的用例中 Agent 选择了正确的 squad，且 handoff artifact 对下游成员可用
失败判据：Agent 在超过 40% 的用例中跳过 squad 选择直接开始实现，或 handoff artifact 不包含下游所需信息
不应提前构建的内容：在路由验证完成前，不要添加新 Squad contract、不要增加新 Skill、不要构建 Observatory
2. 将核心主张从文档降级为可验证约束
要验证的假设：合同、权限、handoff 和验证声明可以被机械化检查，而不仅仅是文档层面的建议
最小实验：
为至少一个真实项目（非本仓库自身）创建一个 .idc/ 合同
在真实工作会话中，比较 Agent 的 self-reported evaluation-record 与宿主工具日志中的实际行为
将两者不一致之处记录为合同模型的盲点
成功判据：合同模型能捕捉至少 70% 的关键质量/安全约束，且不产生虚假通过
失败判据：合同模型的检查项与实际质量/安全风险无关联，或 Agent 可以轻易"填表通过"
不应提前构建的内容：在合同模型经过真实 Agent 验证前，不要增加更多 contract 类型（如 incident-contract、research-contract）
3. 明确定义项目边界——什么不是本项目
要验证的假设：用户和贡献者需要清晰知道项目"不做"什么，以防止范围蔓延和期望错位
最小实验：
在 README 中增加一个"Non-Goals"部分
明确声明：不做 Agent 运行时、不做 CI/CD 集成、不做真实 Agent 行为 benchmark、不替代宿主工具的权限系统
观察 GitHub Issues 和社区反馈中是否仍有对这些被排除功能的请求
成功判据：新增 Issue 中要求"运行时功能"的比例下降
失败判据：持续收到"怎么做 X"的 Issue，而 X 恰好在 Non-Goals 中——说明文档位置或措辞不够显眼
不应提前构建的内容：在 Non-Goals 被社区接受和验证之前，不要添加任何新功能模块
验证记录
已运行命令及结果

$ python --version
Python 3.11.15

$ python scripts/validate_repository.py
Repository validation passed (59 required files, 48 Markdown files).

$ python scripts/validate_contracts.py
Contract validation passed (2 JSON contract files).

$ python scripts/evaluate_contracts.py
Offline evaluation passed (1 evaluation records).

$ python scripts/audit_skills.py
Skill audit passed with 0 warning(s).

$ python -m unittest discover -s tests -v
Ran 69 tests in 14.664s
OK
所有现有验证通过。

未运行的验证及原因
验证	原因
bootstrap.py --target <real-project> --apply	审查准则禁止修改仓库外文件；该脚本需要在真实目标项目上运行
validate_project.py --target <real-project>	同上——需要一个已 bootstrap 的真实项目
真实 Agent 行为测试（用 squad-routing.json 提示词驱动 Agent 并记录实际路由）	需要活跃的 AI 编程工具会话和人工判断；这超出了"只读审查"范围；这是本报告建议路线 #1 的内容
跨平台 Acceptance Check (Claude Code / OpenCode / Codex / Cursor)	需要每种宿主工具的安装环境和人工验证时间
事实、推断、假设的边界
事实（由仓库文件直接证明）：

项目包含 48 个 Markdown 文件、7 个 SKILL.md 定义、2 个 JSON contract、1 个 JSON evaluation record、6 个 Python 脚本、69 个单元测试
所有脚本和测试通过；JSON Schema 为 draft 2020-12；合同验证为离线结构检查
Git 历史只有 6 个 commit，全部来自一个作者；仓库被描述为从个人 LAS 项目提取
推断（基于事实的合理推论）：

所有的 "Skill" 和 "Squad" 行为完全依赖 AI Agent 的自愿遵循，没有程序化 enforcement
Contract 层目前只有一个示例场景，属于 proof-of-concept 规模
平台适配器是最近添加的且可能未经全面跨平台验证
没有证据表明框架在除作者个人项目外的任何仓库中被使用
假设（需要真实用户、项目或宿主工具验证）：

路由选择机制在实际 Agent 行为中有效
Squad 模型确实减少了重复调查
三层上下文模型确实降低了 token 成本
不同宿主平台的 Agent 会一致地遵循相同的 SKILL.md 指令
"人机协作学习"模式在实践中比"使用预制 Skill 包"更有效

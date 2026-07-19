# Author And Motivation

## 作者

**凸( →_→ )凸**

## 我为什么分享这套方法

这套框架不是我为了收集更多提示词而设计出来的。它来自我长期使用 AI 智能体参与一个真实生产项目的过程，也来自这个过程中反复遇到的问题和不断进行的修正。

我曾经发现，用户为了让 AI 开始工作，往往需要先解释大量内部工程细节；一个不断膨胀的总提示词会越来越昂贵、越来越容易过期；单个 Skill 看起来很强，但真正协作时却经常没有明确交接；AI 也容易把工程自主权误解成产品决策权，甚至在缺少新鲜验证证据时就宣布任务已经完成。

对我来说，最重要的转变是：不再把一个 Skill 当成完整解决方案。

Skill 是一项专业能力。小队才是围绕一个结果，由两到三个互补 Skill 组成的工作闭环。有人负责诊断或设计，有人负责独立检查另一类风险，有人负责验证结果。路由器负责理解用户意图、选择小队和控制权限，但它不能代替真正的专业角色。

我也越来越确定另一件事：用户不应该为了使用 AI 编程，先学习一套复杂的内部术语。用户只需要表达目标、问题和期望；AI 应该主动调查仓库，把自然语言翻译为明确、可验证的工程任务。能从源码、配置和测试中确认的事实，由 AI 自己查询。会改变产品行为、数据、隐私、权限、成本或不可逆结果的决定，仍然交给人。

我愿意把这些经验分享出来，是因为中文开发者不应该都重新经历一遍提示词膨胀、Skill 过期、职责重叠、权限越界和“看起来完成了但其实没有验证”的过程。

我不希望别人复制一支和我完全相同的队伍。不同项目有不同的数据流、风险、设计语言和发布方式。这个仓库真正想提供的是一套方法、模板、案例和检查机制，让每个人都能从自己项目的真实工作出发，搭建属于自己的专业小队。

我更看重这些原则：

- 用户负责表达意图，AI 负责工程翻译和执行。
- 产品含义和高风险授权属于人，工程实现属于 AI。
- Skill 保存稳定方法，仓库保存当前事实。
- 小队以结果为中心，不以角色数量为荣。
- 每个成员都有不可替代的职责和明确交接物。
- 没有新鲜证据，就不声称完成。
- 框架应当比它所服务的工作更简单，而不是成为新的负担。

如果这套方法对你有帮助，请保留真正有价值的部分，替换掉不适合你项目的部分，并继续让它保持小而清楚。

---

## English Translation

### Author

**凸( →_→ )凸**

### Why I Am Sharing This

I did not arrive at this framework by trying to collect as many prompts or Skills as possible. It grew from repeatedly working with coding agents on a real production project and noticing the same failures:

- A user had to explain too much internal engineering detail before the agent could act.
- A single large instruction file became expensive, stale, and difficult to maintain.
- Individual Skills looked capable in isolation but did not reliably hand work to one another.
- Agents confused technical autonomy with permission to make product or production decisions.
- Work was declared complete before the evidence was fresh enough to support that claim.

The useful breakthrough was to stop treating a Skill as the whole solution.

A Skill is one professional capability. A squad is a small, goal-oriented combination of two or three complementary Skills that can close a real loop: diagnose and verify, design and review, create and evaluate, operate and recover. The router is the control plane that selects a squad; it is not a substitute for the specialists inside it.

I am sharing this because most developers should not have to rediscover these lessons through months of prompt growth, stale documentation, accidental overreach, and repeated workflow repair. The aim is not to make everyone copy my team. It is to provide the methods, templates, examples, and checks needed to build a professional squad that reflects their own repository, risks, and working style.

The framework therefore favors:

- ordinary-language collaboration over command memorization;
- repository evidence over frozen project facts;
- small professional squads over a giant always-loaded prompt;
- explicit handoffs over vague multi-agent cooperation;
- fresh verification over confidence;
- human ownership of product meaning and risky actions.

Use what is useful, replace what is project-specific, and keep the framework smaller than the work it is meant to support.

# OpenCode 安装 Intent-Driven Coding

## 方式一：opencode.json plugin 引用

在目标项目的 `opencode.json` 中添加：

```json
{
  "plugin": [
    "intent-driven-coding@git+https://github.com/fesfvd/intent-driven-coding.git"
  ]
}
```

重启 OpenCode 后，Plugin 自动注册 `skills/` 目录并注入 session-start 引导上下文。

## 方式二：手动触发

如果不想修改 `opencode.json`，可以在 OpenCode 中直接运行：

```text
Fetch and follow instructions from https://raw.githubusercontent.com/fesfvd/intent-driven-coding/main/.opencode/INSTALL.md
```

## 验证安装

启动 OpenCode 后，检查以下内容：

1. Session 开始时是否出现 `Intent-Driven Coding v1.0.0 active` 引导消息
2. `team` Skill 是否在可用 Skill 列表中
3. 输入一个非平凡任务（如"修复这个 bug"），确认 Agent 读取了 `team` Skill 并确定了 Pipeline 阶段

详见 [OpenCode Adapter](../docs/OPENCODE_ADAPTER.md)。

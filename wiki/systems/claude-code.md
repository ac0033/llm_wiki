---
type: system
title: Claude Code
status: draft
topics:
- agent-harness
- coding-agent
- commercial
- anthropic
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 2
quality: medium
confidence: medium
canonical_url: https://docs.anthropic.com/en/docs/claude-code/overview
evidence_sources:
- https://docs.anthropic.com/en/docs/claude-code/overview
- https://www.anthropic.com/claude-code
---
# Claude Code

Claude Code 是 Anthropic 官方的终端编码 Agent：一个跑在命令行里的 agentic 工具，能直接读写项目文件、执行 shell 命令、操作 git，并与 Claude 模型深度配合。与前五个开源系统不同，它是闭源商业产品——对 [[agent-harness]] 研究而言，它的价值在于提供了一个"厂商亲自下场打磨的 Harness 长什么样"的参照：内置工具集、权限体系、CLAUDE.md 项目记忆、子 Agent、钩子（hooks）、MCP 扩展、IDE 与 GitHub 集成等。由于闭源，内部实现细节只能依据官方文档与公开工程博客推断，本页对未公开部分一律标注。

## 按六组件拆解 Harness

### 1. 推理循环（Agent Loop）

官方文档未公开循环细节（待验证）。从外部行为看是经典的 [[react]] 式循环：模型思考、调用工具、观察结果、继续，直到任务完成或需要用户确认。产品层面允许用户随时打断、纠偏、回退（Esc、双击 Esc 回滚到历史节点等），人机在环是循环的一等公民。

### 2. 上下文管理（Context Manager）

可见的机制有三层：`CLAUDE.md` 文件作为项目级长期记忆自动注入上下文；`/compact` 命令对超长会话做摘要压缩；`/clear` 清空重来。自动压缩的触发条件与摘要算法未公开（待验证）。这种"显式记忆文件 + 自动压缩"的组合，是当前商业 Harness 里被广泛模仿的做法。参见 [[context-manager]]。

### 3. 工具与动作空间（Tools / Action Space）

内置一组精选工具：文件读写与编辑、Glob/Grep 搜索、Bash 执行、WebFetch/WebSearch、任务管理（Todo 列表）等，外加通过 MCP（Model Context Protocol）接入的外部工具。编辑工具走"精确匹配替换"路线而非自由重写，与 [[swe-agent]] 的 ACI 哲学一脉相承：动作空间克制、反馈清晰、失败可见。权限系统（允许/询问/拒绝三级）是动作空间的安全边界，可细粒度配置哪些命令免确认。

### 4. 执行环境（Runtime / Sandbox）

默认直接在用户本机执行，靠权限系统而非沙箱做隔离（有沙箱模式的探索，细节待验证）。这与 [[openhands]] 的 Docker 沙箱路线形成对比：前者信任边界靠"每步可确认"，后者靠"环境可丢弃"。评测场景（如 [[terminal-bench]]）里 Claude Code 通常跑在容器内。

### 5. 规划与编排（Orchestration）

单主 Agent 为主，支持 **subagents（子代理）**：主 Agent 可把独立子任务（如代码检索、专项审查）派发给拥有独立上下文窗口的子代理，结果汇总回主上下文。计划模式（plan mode）让 Agent 先出方案再动手。编排哲学与 [[metagpt]] 相反：不搞固定角色流水线，子代理是"临时分身"而非"常驻岗位"。

### 6. 状态与持久化（State / Persistence）

会话可恢复（`--continue` / `--resume`），CLAUDE.md 承担跨会话的项目记忆。checkpoint 机制支持回退到之前的会话状态。持久化的重点是"人的工作流连续性"，而不是轨迹重放研究。

## 与评测的关系

Claude Code 经常作为 [[terminal-bench]]、[[swe-bench]] Verified 等榜单上的参考 Harness 出现；Anthropic 也公开过它在部分基准上的表现（具体分数不引用）。由于模型与 Harness 同出一家，它是"模型能力"和"Harness 质量"最难分离的案例之一——这正是 [[harness-vs-model-evaluation]] 关心的边界情况。横向定位见 [[agent-framework-harness-comparison]]。

## 待验证 / 边界

- 闭源产品，内部循环、压缩算法、工具实现细节均未公开，本页只描述官方文档可见的行为。
- 功能迭代极快，任何具体命令/参数都可能过期，以官方文档为准。

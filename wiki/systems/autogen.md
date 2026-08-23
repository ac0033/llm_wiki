---
type: system
title: AutoGen
status: draft
topics:
- agent-framework
- multi-agent
- open-source
- microsoft
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 3
quality: medium
confidence: medium
canonical_url: https://github.com/microsoft/autogen
evidence_sources:
- https://github.com/microsoft/autogen
- https://microsoft.github.io/autogen/
- https://arxiv.org/abs/2308.08155
---
# AutoGen

AutoGen 是微软开源的多智能体框架，最早以论文 "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation"（arXiv:2308.08155）为人所知。核心抽象一句话概括：**把一切建模为 Agent 之间的对话**——任务推进就是多个可定制、可对话的 Agent 互相发消息，每个 Agent 背后可以是 LLM、工具执行器或人类。v0.4 起框架做了彻底重写，转向事件驱动的 actor 架构，并分层为 Core / AgentChat / Extensions 等包（分层细节以当前文档为准）。

## 按六组件拆解 Harness

### 1. 推理循环（Agent Loop）

循环被"对话"取代：没有单一的全局 while 循环，而是消息在 Agent 之间流转，谁收到消息谁响应。单个 AssistantAgent 内部仍是 [[react]] 式的模型-工具交替，但整体节奏由会话协议（谁说完轮到谁、何时终止）驱动。终止条件（如出现特定关键词、达到轮次上限）是显式可配的。

### 2. 上下文管理（Context Manager）

每个 Agent 维护自己的消息历史（model context），v0.4 提供了可裁剪的上下文缓冲（如限制保留的最近消息数）等机制，具体类名与默认策略随版本变化，待验证。多 Agent 场景下，"哪个 Agent 看到哪些消息"本身就是上下文管理问题，由 GroupChat 的广播/选路逻辑决定。参见 [[context-manager]]。

### 3. 工具与动作空间（Tools / Action Space）

工具以函数形式注册给 Agent，模型通过 function calling 触发；代码执行由专门的执行器承担。内置代码执行支持包括本地与 Docker 隔离执行（DockerCodeExecutor 之类，名称待验证）。动作空间因此是"工具函数 + 代码执行"的组合，颗粒度由用户定义。

### 4. 执行环境（Runtime / Sandbox）

v0.4 的 Core 层是一个分布式 actor 运行时：Agent 作为 actor 存在，可以跨进程、跨语言（有 .NET 实现）部署。沙箱层面，Docker 代码执行器提供隔离，但"完整任务环境"（如可评分的 Web 环境）不在框架范围内，需自行接入。

### 5. 规划与编排（Orchestration）

主战场。招牌组件是 **GroupChat**：多个 Agent 在一个群聊里协作，由可替换的发言者选择策略（轮询、模型裁判、显式状态机）决定下一个发言者。预置模式还包括 Magentic-One 通用多智能体团队（Orchestrator 指挥 WebSurfer、Coder 等角色）。与 [[langgraph]] 的显式图相比，AutoGen 的编排更"涌现"——行为从对话协议中长出，而非画在图上。

### 6. 状态与持久化（State / Persistence）

Agent 状态与对话历史可序列化保存/加载，运行时可挂接外部存储。持久化能力存在但相对 [[langgraph]] 的 checkpointer 体系更轻，具体 API 待验证。

## 与评测的关系

AutoGen 团队以 [[gaia]] 等基准展示过 Magentic-One 的表现。生态上值得注意：AutoGen 有社区分叉 AG2，评测报告里看到的名字可能不是同一个代码库，归因时需核对。参见 [[harness-vs-model-evaluation]]、[[agent-framework-harness-comparison]]。

## 待验证 / 边界

- v0.2 → v0.4 是不兼容重写，网上大量教程基于旧 API，引用任何接口前必须确认版本。
- 与 AG2 分叉的功能差异本页不展开。

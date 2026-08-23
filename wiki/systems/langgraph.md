---
type: system
title: LangGraph
status: draft
topics:
- agent-framework
- orchestration
- open-source
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 2
quality: medium
confidence: medium
canonical_url: https://github.com/langchain-ai/langgraph
evidence_sources:
- https://github.com/langchain-ai/langgraph
- https://langchain-ai.github.io/langgraph/
---
# LangGraph

LangGraph 是 LangChain 团队开源的 Agent 编排框架，核心主张是：把 Agent 的控制流显式建模为**有向图**——节点是计算单元（调用模型、执行工具、跑任意代码），边定义转移关系，整个图在一个共享状态（State）上运转。与 [[openhands]]、[[swe-agent]] 这类"开箱即用的编码 Agent"不同，LangGraph 卖的不是某个具体 Agent，而是"自己搭 [[agent-harness]] 的脚手架"，并且在生产侧强调持久化、人机协同（human-in-the-loop）与流式输出。

## 按六组件拆解 Harness

### 1. 推理循环（Agent Loop）

不内置单一循环范式。最常见的 [[react]] 循环通过预构建组件（如 `create_react_agent`，具体 API 名随版本可能变化）给出；更复杂的循环由用户用图结构显式表达：模型节点 → 条件边 → 工具节点 → 回到模型节点。循环的终止条件、重试、分支全部显式化，这是它与"黑盒 while 循环"式 Harness 的本质区别。

### 2. 上下文管理（Context Manager）

上下文就是图的 State——通常是一个消息列表，配合 reducer 函数定义"新消息如何合并进旧状态"（追加还是覆盖）。裁剪、摘要、过滤等策略需要用户自己在节点里实现，框架提供的是状态通道机制而非现成的压缩算法。自由度大，但也意味着 [[context-manager]] 的质量取决于使用者。

### 3. 工具与动作空间（Tools / Action Space）

复用 LangChain 的工具抽象：工具是带 schema 的可调用对象，模型节点通过 function calling 产出工具调用，由工具节点统一执行并把结果写回状态。动作空间完全由用户挂载的工具决定，框架本身不预设 bash、编辑器等编码工具——要自己搭出 SWE-agent 那样的环境，工具层得自己写。

### 4. 执行环境（Runtime / Sandbox）

框架本身不提供沙箱。图在哪跑、工具调用什么环境（本地 shell、Docker、远程 API），全部由用户决定。这是"框架"与"完整 Harness"的关键分野：LangGraph 给你控制流，执行环境是自备件。

### 5. 规划与编排（Orchestration）

这是 LangGraph 的主战场。图结构天然支持分支、并行、循环、子图嵌套，官方文档给出 supervisor（监督者分派）、hierarchical（层级团队）、handoff 等多智能体模式的实现模板。编排逻辑的显式化也让调试、断点、时间旅行（从某个 checkpoint 重新分叉执行）成为可能。

### 6. 状态与持久化（State / Persistence）

内置 **checkpointer** 机制：图的每一步执行都可以落盘（内存、SQLite、Postgres 等后端），支持会话恢复、中断后人工介入再继续、以及从任意历史检查点回放分叉。在六个系统里，LangGraph 在状态持久化这一组件上做得最系统化，是它面向生产场景的核心卖点。

## 与评测的关系

LangGraph 自己不与某个基准强绑定；它常作为底座出现在各种评测的参赛系统里。用 LangGraph 搭出的 Agent 去打 [[swe-bench]]、[[appworld]] 时，分数反映的是"框架 + 用户实现 + 模型"的组合，归因时需要小心——这正是 [[harness-vs-model-evaluation]] 讨论的问题。

## 待验证 / 边界

- API 演进快（如预构建 Agent 的入口、`langgraph.config` 等），具体接口名以当前文档为准。
- LangGraph Platform/Studio 等商业配套不在本页范围。

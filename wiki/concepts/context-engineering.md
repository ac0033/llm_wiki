---
type: concept
title: Context Engineering（上下文工程）
aliases: ["context engineering", "上下文工程"]
status: draft
topics: [agent, context, prompt, retrieval, paradigm]
harness_components: [context-manager]
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 4
quality: high
confidence: high
canonical_url: https://arxiv.org/abs/2507.13334
evidence_sources:
  - https://arxiv.org/abs/2507.13334
  - https://arxiv.org/abs/2606.20683
  - https://arxiv.org/abs/2005.11401
  - https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
---

## 一句话结论

Context Engineering 是把「进入模型上下文窗口的信息」当作一等工程对象的学科：它关心的不是怎么措辞一条 prompt，而是在多步执行中持续地检索、选择、压缩、格式化、刷新信息，让每一步的模型调用都拿到恰当的上下文。

## 关键机制

上下文工程是 agent 工程四范式演进的第 2 阶段（Prompt Engineering 之后、Harness Engineering 之前），解决 prompt 工程解决不了的信息问题：模型缺少的知识、随执行动态变化的状态、长动作序列中的一致性。

核心视角（来自 arXiv:2606.20683 与 arXiv:2507.13334）：

1. **上下文是动态组装的运行时对象。** 形式化为 `C = A(c1, …, cn)`，组装函数 A 把指令、检索知识、工具描述与输出、记忆、任务状态、中间工件组合成最终上下文；优化目标是这些构造函数本身，而不是单条指令。
2. **三条演进线索。** 外部信息接入（RAG 及其后续，arXiv:2005.11401 为奠基工作）→ 系统化的上下文管理（何时注入、如何压缩、如何刷新、如何保持任务状态）→ 把上下文本身当作可评估、可优化的对象（出现专门的上下文 benchmark）。
3. **与 Harness 的关系。** 上下文工程本质上是前馈的：它优化每步输入，但不提供检测漂移、验证中间结果、错误恢复的机制。在 Harness 视角下，它沉淀为 [[context-manager]] 这一个组件，而可靠性由 [[control-loop]] 与 [[verification-governance]] 补齐。

## 适用场景

- 长程 agent 任务：上下文预算管理、压缩策略是成败关键。
- 知识密集型任务：检索质量、注入时机决定回答质量。
- 多工具系统：工具描述的选择性加载（progressive disclosure）。

## 局限与失败模式

- **前馈局限。** 只管「喂什么」，不管「跑偏了怎么办」——这是它必须嵌入更大 harness 的原因。
- **压缩的信息损失。** 见 [[context-manager]] 的失败模式。
- **评估困难。** 上下文质量是间接量（通过下游任务表现体现），专门的上下文 benchmark 仍在早期，代表性待验证。
- **与模型能力的耦合。** 最优上下文策略随模型变化（长上下文模型改变了压缩的必要性），策略迁移性差。

## 与其他页面的关系

- 运行时落点：[[context-manager]]；上位框架：[[agent-harness]]；所属方向：[[ai-agent-harness]]。
- 学科综述与实证：[[arxiv-2507-13334]]（Context Engineering 综述）、[[arxiv-2307-03172]]（Lost in the Middle，长上下文利用的实证边界）；相关子方向：[[agent-memory-context]]。
- 信息来源：[[agent-memory]]（记忆检索）、[[observation-interface]]（环境观察）。
- 相关系统与 benchmark：[[openhands]]、[[swe-bench]]（长上下文压力的代表任务）。

## 来源

- [A Survey of Context Engineering for Large Language Models (arXiv:2507.13334)](https://arxiv.org/abs/2507.13334) —— 学科综述。
- [From Question Answering to Task Completion (arXiv:2606.20683)](https://arxiv.org/abs/2606.20683) —— 范式定位与形式化。
- [Retrieval-Augmented Generation (arXiv:2005.11401)](https://arxiv.org/abs/2005.11401) —— 外部信息接入的奠基工作。
- [Anthropic: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) —— 工业界实践阐述。

## 待验证问题

- 「Context engineering」一词的提出脉络（社区归于 Shopify CEO Tobi Lütke 与 Karpathy 2025 年中的推广）需核对原始出处。
- ACON、ARC、ContextBudget 等综述提及的上下文管理方法，各自结论待逐篇核对。
- 上下文专门 benchmark（ContextBench、SWE Context Bench、LoCoBench-Agent、AgentLongBench 等）的覆盖面与公认度待评估。

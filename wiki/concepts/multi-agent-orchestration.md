---
type: concept
title: Multi-Agent Orchestration（多 Agent 编排）
aliases: ["multi-agent orchestration", "多 agent 编排", "multi-agent", "多智能体"]
status: draft
topics: [agent, multi-agent, orchestration, coordination]
harness_components: [control-loop, action-interface, state-artifact-store]
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 5
quality: high
confidence: medium
canonical_url: https://arxiv.org/abs/2606.20683
evidence_sources:
  - https://arxiv.org/abs/2606.20683
  - https://arxiv.org/abs/2308.08155
  - https://arxiv.org/abs/2308.00352
  - https://github.com/a2aproject/A2A
  - https://openai.github.io/openai-agents-python/
---

## 一句话结论

Multi-Agent Orchestration 研究如何把多个 agent（或多个异构模型）组织成一个系统：通过任务分解、角色分配、委派与交接（handoff）、模型路由和共享工件来完成单 agent 难以胜任的复杂任务——在 harness 视角下，它是 [[control-loop]] 的扩展职责。

## 关键机制

1. **任务分解与角色。** 把大任务拆给专门化的 agent（规划者、执行者、评审者、领域专家）。MetaGPT（arXiv:2308.00352）用软件公司的角色分工（产品、架构、工程）和标准化操作流程组织多 agent 写代码；AutoGen（arXiv:2308.08155）提供通用的多 agent 对话编程框架。
2. **委派与交接。** 主 agent 把子任务连同必要上下文交给 sub-agent，收回结论。sub-agent 同时充当「上下文防火墙」：子任务在隔离上下文中执行，避免污染主上下文（与 [[context-manager]] 协同）。
3. **模型路由。** 多模型 harness 中，运行时决定每一步由哪个模型出场（规划用强模型、执行用便宜模型、验证用专门模型），在能力与成本间取舍。
4. **互操作协议。** A2A（Agent2Agent）协议面向不同厂商/框架 agent 之间的互操作，落在控制循环与 [[action-interface]] 一侧；[[model-context-protocol]] 解决的是工具接入，两者互补。
5. **共享状态。** 多 agent 通过共享工件（文档、代码、计划）协作，依赖 [[state-artifact-store]]；SDK（如 OpenAI Agents SDK）把 tools、handoffs、tracing、循环封装成可复用抽象。

## 适用场景

- 超长出程任务：单个上下文装不下时，按子任务分治。
- 多角色评审：生成者与验证者分离，缓解自评偏差（见 [[verification-governance]] 的 verifier 机制）。
- 异构能力组合：不同模型/工具专长的任务（检索 + 推理 + 代码）由不同 agent 承担。

## 局限与失败模式

- **协调开销吞掉收益。** 角色间的通信与对齐本身消耗大量 token；任务本可由单 agent 完成时，多 agent 是纯成本。
- **错误沿链路传播。** 上游 agent 的错误结论被下游当作事实，且更难归因——故障发生在「哪个 agent、哪次交接」需要 [[agent-observability]] 级别的追踪。
- **交接信息丢失。** 委派时上下文传递不全（目标、约束、已尝试方案），sub-agent 在信息缺失下行动。
- **成本乘数。** 多个 agent 各自跑循环，总成本是各循环成本的叠加甚至乘积。
- **收益证据不均。** 「多 agent 优于单 agent」的结论在不同任务上不一致，部分研究显示强单 agent + 好 harness 即可匹敌简单多 agent 方案，具体结论待逐篇核对。

## 与其他页面的关系

- 运行时归属：[[control-loop]]（路由、交接、协调）、[[action-interface]]（子 agent 调用作为一种动作）、[[state-artifact-store]]（共享工件）。
- 协议：A2A；工具接入见 [[model-context-protocol]]；上下文隔离见 [[context-manager]]。
- 评估与调试：[[agent-evaluation]]、[[agent-observability]]。
- 相关系统页：[[openhands]] 等（其他分块维护）。

## 来源

- [From Question Answering to Task Completion (arXiv:2606.20683)](https://arxiv.org/abs/2606.20683) —— 多模型 harness 与控制循环扩展职责。
- [AutoGen (arXiv:2308.08155)](https://arxiv.org/abs/2308.08155) —— 多 agent 对话框架。
- [MetaGPT (arXiv:2308.00352)](https://arxiv.org/abs/2308.00352) —— 角色分工 + SOP 的多 agent 协作。
- [A2A 协议](https://github.com/a2aproject/A2A) —— agent 间互操作标准。
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) —— tools/handoffs/tracing 的工程化封装。

## 待验证问题

- 「何时多 agent 真的优于单 agent」缺乏公认判据，各研究结论冲突，待系统梳理。
- A2A 的实际采用度与协议现状（治理归属、版本）待核对最新状态。
- 综述提到的「harness 作为多模型组合运行时」的代表系统（如 [147] 等引用）具体所指待核对原文参考文献。

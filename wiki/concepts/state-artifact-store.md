---
type: concept
title: State & Artifact Store（状态与工件存储）
aliases: ["state and artifact store", "状态存储", "工件存储", "checkpoint"]
status: draft
topics: [agent, harness, state, persistence, artifact]
harness_components: [state-artifact-store]
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 3
quality: high
confidence: high
canonical_url: https://arxiv.org/abs/2606.20683
evidence_sources:
  - https://arxiv.org/abs/2606.20683
  - https://arxiv.org/abs/2310.08560
  - https://arxiv.org/abs/2407.16741
---

## 一句话结论

State & Artifact Store 负责持久化 agent 执行过程中的一切状态和产物——对话历史、计划、scratchpad、检查点、日志、轨迹、diff、记忆记录、生成的文件和任务工件——它让执行可以中断、恢复、回滚、审计，也是长期记忆的物质载体。

## 关键机制

在 [[agent-harness]] 六组件中，状态与工件存储解决「状态存在哪里」的问题。模型的上下文窗口是易失且有限的，任何要跨步骤、跨会话存活的信息都必须落盘。主要机制：

1. **会话与轨迹持久化。** 完整记录「观察-推理-动作-结果」轨迹（trace），既是 [[control-loop]] 恢复执行的依据，也是 [[agent-observability]] 和 [[agent-evaluation]] 的数据源。
2. **检查点（checkpoint）与回滚。** 在关键节点快照状态，失败后回滚到最近的健康状态重试，避免从头再来。对长程任务（如 [[swe-bench]] 级的仓库修改）尤其关键。
3. **工件管理。** 计划文档、中间草稿、生成的代码文件、diff 等产物以文件/对象形式存储，可被后续步骤和其他 agent 引用。
4. **记忆落盘。** [[agent-memory]] 的长期记忆（语义记忆、情景记忆、技能库）在实现层面都依赖持久存储与检索索引；MemGPT（arXiv:2310.08560）把「分层内存 + 换入换出」做成了显式的操作系统式管理。

## 适用场景

- 长程任务的中断恢复：跨小时、跨会话的任务需要可恢复的执行状态。
- 人机协作：人类审批、修改后再交还 agent，要求状态可序列化、可移交。
- 审计与复现：企业场景要求完整可追溯的执行记录（与 [[verification-governance]] 的 audit trace 交叉）。
- 多 agent 协作：共享工件（文档、代码、计划）是 [[multi-agent-orchestration]] 的主要协作媒介之一。

## 局限与失败模式

- **状态分叉。** 回滚后环境侧（文件系统、外部 API）的状态与 agent 记录的状态不一致——存储层能回滚自己的记录，但无法回滚已发生的副作用。
- **过期状态污染。** 恢复旧检查点时把已失效的假设（如已变化的远程仓库状态）当作事实，导致后续决策基于陈旧信息。
- **存储膨胀与检索退化。** 轨迹和记忆无限增长后，检索质量下降、成本上升；何时遗忘、如何归档是开放问题。
- **隐私与合规。** 轨迹中可能包含密钥、个人数据，落盘即产生合规责任，需要与治理层配合脱敏。

## 与其他页面的关系

- 所属框架：[[agent-harness]]。
- 存什么由执行产生：[[control-loop]] 推进轨迹，[[action-interface]] 产生副作用与文件，[[observation-interface]] 产生观察记录。
- 取出来用：[[context-manager]] 把历史状态组装进上下文；[[agent-memory]] 是建立在存储之上的记忆抽象。
- 治理面：[[verification-governance]] 依赖它做审计与回滚；[[agent-observability]] 依赖它做轨迹分析。

## 来源

- [From Question Answering to Task Completion (arXiv:2606.20683)](https://arxiv.org/abs/2606.20683) —— 组件定义来源。
- [MemGPT (arXiv:2310.08560)](https://arxiv.org/abs/2310.08560) —— 操作系统式的分层记忆/状态管理。
- [OpenHands (arXiv:2407.16741)](https://arxiv.org/abs/2407.16741) —— 事件流持久化的工程实现参考。

## 待验证问题

- 主流 agent 框架（OpenHands、LangGraph、OpenAI Agents SDK 等）的检查点/恢复语义差异缺乏统一对比，待整理。
- 「状态回滚 + 环境副作用」的一致性问题（类似分布式系统的 exactly-once 语义）在 agent 文献中少有形式化讨论，待验证是否有成熟方案。

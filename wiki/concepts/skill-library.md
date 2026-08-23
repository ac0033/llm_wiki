---
type: concept
title: Skill Library（技能库）
aliases: ["skill library", "技能库", "executable memory"]
status: current
topics: [agent, memory, tool-use, code-generation, harness]
harness_components: [state-artifact-store, action-interface, verification-governance]
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 2
quality: medium
confidence: high
canonical_url: https://arxiv.org/abs/2305.16291
evidence_sources:
  - https://arxiv.org/abs/2305.16291
  - https://arxiv.org/abs/2303.11366
---

## 一句话结论

Skill Library 是把 agent 已经验证过的能力沉淀成可检索、可复用、可组合工件（通常是代码技能）的机制；它让长期记忆不只是“记住文本”，而是变成可以再次执行的 harness 资产。

## 关键机制

- **写入门槛**：新技能只有在外部执行或自我验证通过后才写入，避免把失败尝试污染进长期记忆。[[voyager]] 把这一点体现得最清楚：技能先运行、再入库。
- **检索与组合**：调用时按任务描述检索相近技能，再由 [[control-loop]] 决定直接使用、组合还是改写。
- **可迁移性**：技能库属于 [[state-artifact-store]]，不绑定某个特定模型；换底座模型时，已沉淀的技能仍可复用。
- **治理需求**：技能可能过时、互相冲突或包含不安全动作，因此需要 [[verification-governance]] 做版本化、测试、权限和淘汰。

## 适用场景

- 长周期 agent：需要跨任务积累经验，而不是每次从零开始。
- Coding / research agent：把常见修复模式、实验脚本、数据处理方法沉淀为可执行资产。
- 多 agent 系统：不同角色共享一套受控技能库，减少重复探索。

## 局限与失败模式

- **错误固化**：如果验证器不可靠，错误技能会被长期保留并反复调用。
- **检索错位**：语义相似不等于当前任务适用，技能选择仍需 [[context-manager]] 提供任务状态约束。
- **版本漂移**：环境、依赖、API 变化后，旧技能可能失效；需要定期重跑验证。
- **安全风险**：可执行技能本质上是代码资产，必须与 [[sandboxed-execution]] 和权限策略一起设计。

## 与其他页面的关系

- [[agent-memory]]：技能库是长期记忆的一种可执行形态。
- [[state-artifact-store]]：负责技能、版本、轨迹和产物的持久化。
- [[action-interface]]：技能最终以工具或代码动作的形式被调用。
- [[verification-governance]]：决定技能何时能写入、何时需要退役。
- [[voyager]]：最具代表性的 Skill Library 实现之一。

## 来源

- [Voyager: An Open-Ended Embodied Agent with Large Language Models](https://arxiv.org/abs/2305.16291)
- [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366)

## 待验证问题

- 不同系统对技能去重、组合、淘汰的具体策略差异很大，后续应补一页跨系统对比。
- Skill Library 与 Agent Skills / MCP tools 的边界需要持续跟踪。
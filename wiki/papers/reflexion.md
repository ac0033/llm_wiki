---
title: "Reflexion: Language Agents with Verbal Reinforcement Learning"
aliases: [Reflexion, "Reflexion: Language Agents with Verbal Reinforcement Learning"]
type: paper
status: draft
topics: [agent, self-reflection, memory, verification]
harness_components: [memory, verification, planner]
published: 2023-03
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 1
quality: medium
confidence: high
canonical_url: https://arxiv.org/abs/2303.11366
---

# Reflexion: Language Agents with Verbal Reinforcement Learning

> Shinn et al., 2023-03（arXiv），NeurIPS 2023 接收。

## 一句话结论

不更新任何模型权重，而是让 agent 在每次失败后用自然语言写一段「自我反思」存入记忆，下一次尝试时带着这段反思重跑，从而在多个 trial 之间持续改进。

## 论文解决了什么问题

用强化学习直接训练 LLM agent 成本高、需要大量轨迹样本。Reflexion 提出的替代问题是：能不能把「从失败中学习」这件事从权重层面搬到上下文层面——用一段话代替梯度更新。它针对的正是 [[react]] 这类单趟 agent 的硬伤：一个 episode 走错了就结束，下次从零开始，同样的坑反复踩。

## 关键机制

Reflexion 把系统拆成三个角色，全部可以用 LLM 实现：

- **Actor**：产生动作轨迹的策略，论文中基于 ReAct 或 CoT 实现。
- **Evaluator**：对一次 trial 的成败打分。根据任务不同可以是环境自带的启发式规则（ALFWorld 是否完成任务）、精确匹配（HotpotQA）或**单元测试**（代码任务）。
- **Self-Reflection 模型**：拿到失败轨迹和 Evaluator 的信号，生成一段文字反思（「我错在没先检查 X，下次应该 Y」），写入**情景记忆（episodic memory）**。

下一次 trial 时，过去的反思作为额外上下文喂给 Actor。整个「学习」过程就是 harness 层面的 retry loop + 记忆回写。

论文在三类任务上做了验证：ALFWorld（决策）、HotpotQA（推理问答）、HumanEval（代码生成，用单元测试当验证器）。

## 对 Agent Harness 的启示

这篇论文的每个组件几乎都对应 harness 的一个职责，而不是模型的能力：

- **验证器（verifier）决定反思质量的上限**。代码任务上效果好，很大程度因为单元测试给了确定性的成败信号；没有可靠验证器的开放任务，反思容易变成自我安慰。这直接说明 harness 里 [[verification-governance]] 组件（测试、规则检查、环境反馈）是核心资产，选什么验证信号比反思 prompt 怎么写更重要。
- **跨 trial 的记忆是 harness 的责任**。反思存哪、怎么在下次 trial 注入上下文、如何避免过期反思误导，都是 [[agent-memory]] / [[context-manager]] 的设计问题。
- **retry loop 要有预算控制**。多 trial 意味着成本成倍增加，harness 需要 trial 上限、早停和成本核算——这一点后来在 [[ai-agents-that-matter]] 中被系统化为「成本可控的 agent 评测」。
- **「语言即策略更新」是一种廉价的 harness 升级**：不动底座模型就能在重复尝试的任务上拿到提升，适合在 harness 层先做。

## 局限与后续工作

- 严重依赖 Evaluator 的质量；没有可靠成败信号的任务上，反思可能基于错误的自我诊断。
- 反思只保留在自然语言记忆里，没有权重更新，换任务、换 prompt 后无法带走；且反思本身可能包含错误结论并自我强化。
- 多 trial 的 token 成本高，论文未系统讨论成本-收益权衡。
- 后续工作把这一思想扩展到代码级自我修正与持久技能沉淀，如 [[voyager]] 的迭代提示机制（用执行报错代替反思文字）和技能库。

## 相关页面

- [[react]]：Reflexion 的 Actor 建立在 ReAct 之上
- [[verification-governance]]：Evaluator 的泛化形态
- [[agent-memory]]：情景记忆与反思注入
- [[voyager]]：把自我修正延伸到可执行技能库
- [[ai-agents-that-matter]]：多 trial 带来的评测成本问题

## 来源

- arXiv 摘要页：https://arxiv.org/abs/2303.11366

## 待验证问题

- 各任务上的具体提升幅度（如 HumanEval pass@1 的确切数值），本文未引用，补录时核对原文。
- Self-Reflection 模型与 Actor 是否在各实验中均使用同一底座模型（印象中为 GPT-4/GPT-3.5 混合，待核对）。

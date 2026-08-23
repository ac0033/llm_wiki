---
title: "Voyager: An Open-Ended Embodied Agent with Large Language Models"
aliases: [Voyager, "Voyager: An Open-Ended Embodied Agent with Large Language Models"]
type: paper
status: draft
topics: [agent, embodied, code-generation, lifelong-learning, minecraft]
harness_components: [skill-library, verification, planner, memory]
published: 2023-05
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 1
quality: medium
confidence: high
canonical_url: https://arxiv.org/abs/2305.16291
---

# Voyager: An Open-Ended Embodied Agent with Large Language Models

> Wang et al.（NVIDIA / Caltech / UT Austin 等），2023-05（arXiv），TMLR 2024 发表。

## 一句话结论

Voyager 在 Minecraft 里以「自动课程 → 写代码 → 执行反馈 → 自我验证 → 存入技能库」的循环持续探索，不更新任何模型参数，靠不断沉淀的可执行代码技能实现终身学习。

## 论文解决了什么问题

开放式环境（Minecraft）没有固定目标、没有训练数据，传统 RL 难以施加，LLM agent 则容易卡在局部目标、重复犯错、学不到新东西。Voyager 要同时解决三件事：agent 自己提出下一步该做什么（开放式探索）、做错了怎么改（可执行的动作空间里如何自我修正）、学会的东西怎么留下来（跨会话的能力积累）。

## 关键机制

三个组件组成一个闭环，全部运行在 GPT-4 之外：

- **自动课程（Automatic Curriculum）**：根据当前探索进度和世界状态，由 LLM 持续提出「下一个合适但有挑战」的任务，推动开放式探索，替代人工设计的目标序列。
- **技能库（Skill Library）**：验证成功的行为以**可执行 JavaScript 代码**（基于 Mineflayer API）的形式存入库中，附带描述与嵌入索引；之后遇到相关任务时检索出来复用或组合。代码即记忆——这是它与 [[reflexion]] 的自然语言反思记忆的关键区别。
- **迭代提示机制（Iterative Prompting）**：生成代码 → 在环境里执行 → 收集三类反馈（执行报错、环境反馈、自我验证结果）→ 把反馈喂回 LLM 重写代码，直到自我验证通过或重试次数用尽。其中**自我验证**由另一个 LLM 调用扮演 critic，判断任务是否真的完成，防止「以为成功了」的假阳性。

## 对 Agent Harness 的启示

Voyager 的整套能力几乎全是 harness 工程，对 [[agent-harness]] 设计的参考价值极高：

- **代码作为动作空间**是 harness 友好的选择：代码可存储、可检索、可组合、可静态检查，比自由文本动作或低层 API 序列更容易做验证和复用。
- **[[skill-library]] 是一种可执行的长期记忆**：写入条件是「自我验证通过」，检索靠嵌入相似度。harness 侧需要设计的是写入门槛、去重、组合调用接口，而不是模型能力。
- **反馈回路分层**：执行报错（确定性强）→ 环境反馈（半结构化）→ LLM critic 验证（弱信号）。把确定性信号放在 critic 之前使用，是控制验证成本和误报率的实用经验，呼应 [[verification-governance]] 组件的设计原则。
- **迭代修复必须有预算**：重试次数、token 成本由 harness 控制；[[reflexion]] 的多 trial 反思与这里的迭代提示，本质都是「harness 层的重试循环 + 反馈注入」。
- 能力沉淀在技能库而非权重里，意味着换底座模型时技能库可迁移——harness 资产与模型解耦。

## 局限与后续工作

- 自我验证由 LLM 担任，存在误判；技能库可能沉淀「碰巧成功」的代码。
- 强依赖 GPT-4 级别的代码能力，开源弱模型上效果明显下降（论文有对比）。
- 沙盒失败成本低，真实世界（机器人、生产系统）里执行报错和错误动作的代价高得多，迭代修复策略不能直接照搬。
- 技能库长期增长后的检索退化、技能间冲突未深入讨论。

## 相关页面

- [[skill-library]]：可执行技能库
- [[verification-governance]]：自我验证与执行反馈
- [[react]]：对照——Voyager 把单步动作扩展为程序合成
- [[reflexion]]：自然语言反思 vs 可执行技能沉淀
- [[sandboxed-execution]]：执行环境与反馈采集
- [[generative-agents]]：另一种 harness 内认知架构

## 来源

- arXiv 摘要页：https://arxiv.org/abs/2305.16291

## 待验证问题

- 论文报告的具体量化对比（如获得物品数量、探索距离的倍数提升），本文未引用，补录时核对原文。
- 技能库的最终规模与检索命中率统计（待核对）。

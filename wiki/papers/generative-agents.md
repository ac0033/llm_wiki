---
title: "Generative Agents: Interactive Simulacra of Human Behavior"
aliases: [Generative Agents, 生成式智能体, "Generative Agents: Interactive Simulacra of Human Behavior"]
type: paper
status: draft
topics: [agent, memory, planning, simulation]
harness_components: [memory, planner, simulation-loop]
published: 2023-04
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 1
quality: medium
confidence: high
canonical_url: https://arxiv.org/abs/2304.03442
---

# Generative Agents: Interactive Simulacra of Human Behavior

> Park et al.（Stanford / Google），2023-04（arXiv），UIST 2023 发表。

## 一句话结论

25 个由 LLM 驱动的 agent 在沙盒小镇里生活两天，仅靠一套「记忆流 + 反思 + 规划」的外部架构就自发涌现出传播信息、组织派对等社会行为——整套「认知」完全跑在模型权重之外的 harness 里。

## 论文解决了什么问题

LLM 单轮问答已经很强，但要让 agent 在长时间跨度里表现出连贯、可信的「人」的行为，光靠 prompt 不够：模型没有持久记忆，不会把零散经历提炼成结论，也不会主动安排日程。论文要解决的问题是：需要什么样的**架构**（而不是什么样的模型），才能让 LLM 支撑起长时程、彼此交互、行为可信的模拟个体。

## 关键机制

论文的核心贡献是一套围绕冻结 LLM 的认知架构，三个组件环环相扣：

- **记忆流（Memory Stream）**：agent 的所有经历以自然语言条目持续追加到一个长列表。检索时按三个维度打分加权——**recency**（时间新近度，指数衰减）、**relevance**（与当前情境的嵌入相似度）、**importance**（由 LLM 给事件打的重要性分）——取 top 条目注入上下文。
- **反思（Reflection）**：当近期事件的重要性总分超过阈值，触发反思流程：LLM 从近期记忆中归纳出更高层的结论（如「Klaus 在做研究项目」），这些结论本身也作为记忆写回记忆流，形成层级化的记忆。
- **规划（Planning）**：LLM 先生成一天的粗粒度日程，再递归细化为更短时段的行动计划；agent 在行动中根据新观察（observation）动态调整计划。

25 个 agent 共享一个沙盒世界（Smallville），由模拟器推进时间、传播观察、处理 agent 之间的对话，涌现行为包括情人节派对的组织与到场、竞选信息的扩散。

## 对 Agent Harness 的启示

这篇论文是「认知在 harness 里」最极端的样本：底座模型从头到尾没被训练，全部行为差异来自架构。对 harness 设计的直接启示：

- **[[agent-memory]] 不是一个数据库，而是一套检索策略**。记忆流的三维打分（recency / relevance / importance）至今仍是 agent 长期记忆检索的常见基线；harness 需要决定写入粒度、衰减函数、召回条数，这些参数直接影响行为连贯性。
- **反思与规划都是「定时的离线 LLM 调用」**，由 harness 的调度器触发（重要性阈值、每日开始时），而不是模型自己发起的。也就是说，harness 需要一个**后台调度层**，不能只响应式的跑主循环。
- **观察的传播是模拟器/harness 的职责**：谁看到了什么、对话发生在哪里，由环境决定并注入各 agent 的上下文——多 agent 系统里这个「观察路由」就是 harness 的核心。
- **可信度（believability）作为评测目标**值得注意：论文用人类评估 + 架构消融（去掉记忆/反思/规划对比）来验证，消融式评测后来被 [[ai-agents-that-matter]] 系统化为「区分模型贡献与 harness 贡献」的方法论。

## 局限与后续工作

- 成本与延迟：每个 agent 每个时间片都要多次 LLM 调用（检索打分、反思、规划），规模化模拟的算力开销大。
- 行为错误会以意想不到的方式复合：记忆检索失误可能让 agent 行为漂移，论文承认存在如「把只有一间厕所当成多家共用」一类的 erratic 行为。
- 评测主要靠人类主观评分，规模小、难复现。
- 记忆只增不减，长期运行的记忆膨胀与冲突消解没有解决方案。

## 相关页面

- [[agent-memory]]：记忆流与三维检索打分
- [[control-loop]]：递归式计划生成
- [[agent-harness]]：本论文是「认知全在 harness」的范例
- [[context-manager]]：记忆注入上下文的预算问题
- [[ai-agents-that-matter]]：消融评测与成本问题

## 来源

- arXiv 摘要页：https://arxiv.org/abs/2304.03442

## 待验证问题

- 人类评估中完整架构 vs 消融变体的具体排名细节与评估人数（待核对原文实验节）。
- 模拟运行的确切时长与 LLM 调用次数统计。

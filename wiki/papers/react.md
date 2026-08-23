---
title: "ReAct: Synergizing Reasoning and Acting in Language Models"
aliases: [ReAct, "ReAct: Synergizing Reasoning and Acting in Language Models"]
type: paper
status: draft
topics: [agent, reasoning, tool-use, prompting]
harness_components: [planner, tool-use, observation-loop]
published: 2022-10
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 1
quality: medium
confidence: high
canonical_url: https://arxiv.org/abs/2210.03629
---

# ReAct: Synergizing Reasoning and Acting in Language Models

> Yao et al., 2022-10（arXiv），ICLR 2023 接收。

## 一句话结论

把「推理轨迹（Thought）」和「环境动作（Act）」交错生成，让 LLM 在一个 Thought → Action → Observation 循环里边想边做，是后来几乎所有 [[agent-harness]] 主循环的模板。

## 论文解决了什么问题

当时两条路线是脱节的：Chain-of-Thought 一类的纯推理方法不接触外部环境，容易编造事实（hallucination）；而纯动作生成的方法（直接输出 action 序列）缺乏显式规划，错了也无法自我修正。ReAct 要解决的是：如何用一种统一的提示格式，让同一个模型同时承担「想」（分解任务、跟踪进度、处理异常）和「做」（查询知识库、在环境里操作）两个角色。

论文在两类任务上验证了这个想法：

- 知识密集型问答：HotpotQA（多跳问答）、FEVER（事实核查），模型可调用维基百科检索 API。
- 决策型任务：ALFWorld（文字版家居环境）、WebShop（模拟电商网站），模型需要多步交互达成目标。

## 关键机制

- **交错轨迹**：模型按 `Thought: ... / Action: ... / Observation: ...` 的格式循环生成。Thought 是自由文本的推理，Action 从预定义动作空间中选取（如 `search[entity]`、`lookup[keyword]`），Observation 由外部环境执行 Action 后回填。
- **few-shot 提示**：不训练模型本身（主要实验用冻结的 PaLM-540B），只在 prompt 里放几条人工写的轨迹示例；同时也有在轨迹数据上微调小模型的对照实验。
- **执行权在模型之外**：解析模型输出、真正调用检索 API 或环境、把结果拼回上下文——这些全部由外部脚手架完成。这正是 harness 的雏形。

## 对 Agent Harness 的启示

ReAct 最大的遗产不是具体分数，而是它事实上定义了 harness 主循环的标准结构：**LLM 只负责产出 Thought 和 Action，解析、执行、回填 Observation 是 harness 的职责**。具体到今天的设计：

- **动作解析器**是 harness 的关键组件：ReAct 用正则解析 `Action:` 行，现代 harness 用结构化 tool call，但职责相同——模型输出不可信，必须有一层校验和兜底（格式错误时如何重试、如何反馈）。
- **Observation 回写策略**影响上下文膨胀：每一步工具返回的原始文本都进上下文，长任务会迅速撑爆窗口，这正是 [[context-manager]] 存在的理由。
- **推理外显化带来可调试性**：Thought 轨迹写在明处，harness 可以直接把完整轨迹落盘做 [[agent-evaluation]] 和失败归因。
- 论文也暴露了 harness 侧的失败模式：模型会在错误动作上循环打转（repetitive loop），论文靠 prompt 示例缓解，工程上需要 harness 做循环检测和步数上限。

## 局限与后续工作

- 强依赖人工编写的高质量 few-shot 轨迹，泛化到新动作空间时要重写示例。
- 推理质量受底座模型限制，小模型上微调轨迹后仍明显落后大模型（论文自身对比）。
- 错误无法回溯：一步走错只能继续向前，没有自我修正机制——这直接催生了 [[reflexion]] 的重试 + 反思机制。
- 动作空间需要人工设计，何时调用工具完全靠 prompt 约定，[[toolformer]] 尝试把「何时调工具」学进模型权重。

## 相关页面

- [[agent-harness]]：ReAct 循环是其最小骨架
- [[context-manager]]：Observation 回写导致的上下文管理问题
- [[tool-use]]：动作空间与工具调用
- [[reflexion]]：在 ReAct 之上加自我反思
- [[voyager]]：把循环扩展到代码生成与技能库

## 来源

- arXiv 摘要页：https://arxiv.org/abs/2210.03629

## 待验证问题

- 论文在 HotpotQA/FEVER 上的确切分数以及与 CoT 的差值（本文未引用具体数字，补录时核对原文 Table 1）。
- 微调实验使用的具体底座模型规模与数据量。

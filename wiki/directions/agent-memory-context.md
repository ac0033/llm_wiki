---
type: direction
title: Agent Memory（记忆与工作记忆）子方向
aliases: ["agent memory direction", "记忆子方向", "working memory"]
status: draft
topics: [agent, memory, context, research-direction]
harness_components: [context-manager, state-artifact-store]
ingested: 2026-08-22
last_verified: 2026-08-22
source_count: 7
quality: medium
confidence: medium
canonical_url: https://arxiv.org/abs/2404.13501
evidence_sources:
  - https://arxiv.org/abs/2404.13501
  - https://arxiv.org/abs/2310.08560
  - https://arxiv.org/abs/2309.02427
  - https://arxiv.org/abs/2502.12110
  - https://arxiv.org/abs/2507.13334
  - https://arxiv.org/abs/2307.03172
  - https://arxiv.org/abs/2606.20683
---

## 一句话结论

Agent Memory 是 [[ai-agent-harness]] 方向下的子方向，研究 agent 如何跨越单次上下文窗口保存和复用信息：上下文窗口是唯一随身的「工作记忆」，长期记忆则靠外部存储加检索实现；在 harness 六组件里，它由 [[context-manager]]（取）与 [[state-artifact-store]]（存）共同承载，详见概念页 [[agent-memory]]。

## 关键机制

这个子方向可以按「工作记忆的边界」和「长期记忆的架构」两条线索组织：

**工作记忆（context window 内）：**

1. **上下文利用并不均匀。** Lost in the Middle（[[arxiv-2307-03172]]）用可控实验证明模型对长上下文的利用呈 U 型曲线：信息在开头或结尾时表现最好，落在中间显著退化，最差时甚至低于不给文档的 closed-book 基线。这是一切 context 管理策略（压缩、重排、选择注入）的实证起点。
2. **Context engineering 成为独立工程学科。** Context Engineering 综述（[[arxiv-2507-13334]]，分析 1400+ 篇论文）把上下文形式化为动态组装的对象，分解为「检索与生成 / 处理 / 管理」三个基础组件，memory 是其中一类系统实现。

**长期记忆（context window 外）：**

3. **认知架构视角的分类。** CoALA（[[arxiv-2309-02427]]）借鉴认知科学把 agent 记忆分为 working / episodic / semantic / procedural 四类，并把「学习」定义为对各种记忆的写入操作，为本方向提供了术语框架。
4. **操作系统式分层管理。** MemGPT（[[arxiv-2310-08560]]）把主上下文当「内存」、外部存储当「磁盘」，由模型通过 function call 自主换入换出，是「记忆管理交给模型自己」路线的代表。
5. **自组织的结构化记忆。** A-Mem（[[arxiv-2502-12110]]）借鉴 Zettelkasten 卡片盒方法，让 LLM 自动为记忆生成结构化属性、建立记忆间链接并触发历史记忆演化，代表「无需预定义操作」的动态记忆路线。
6. **写入 / 管理 / 读取的三段分解。** 记忆机制综述（[[arxiv-2404-13501]]）把记忆系统操作拆成写入（记什么）、管理（如何组织与演化）、读取（何时取、取多少）三组策略，是当前最系统的分类参照。

## 适用场景

- 设计跨会话、长程任务的 agent 时，用 CoALA 四类记忆 + 写入/管理/读取三段分解做设计检查清单。
- 诊断「agent 忘了」「agent 记错了」类故障时，先区分问题出在工作记忆侧（上下文没装上、位置偏置）还是长期记忆侧（没写入、检索错配）。
- 评估记忆系统方案（MemGPT 式模型自主管理 vs 后台自动记忆 vs A-Mem 式自组织）时，本子方向提供已有路线的代表文献入口。

## 局限与失败模式

- **评估不成熟。** 记忆系统收益难以与 context engineering 其他部分分离归因；LongMemEval、LoCoMo 等基准刚起步，公认标准待建立。
- **记忆投毒与噪声写入。** 错误记忆被反复检索会持续误导决策；「记什么」仍无成熟标准（见 [[agent-memory]] 的失败模式）。
- **术语混杂。** memory、context、state、knowledge 在文献中边界不一；harness 视角下记忆是「功能」而非「组件」，功能到组件是多对多映射，跨文献对比需先做术语对齐。
- **结论时效性。** Lost in the Middle 的结论基于 2023 年模型，新一代模型上的位置偏置程度待重新验证。

## 与其他页面的关系

- 上位方向：[[ai-agent-harness]]；核心概念页：[[agent-memory]]。
- 工作记忆侧文献：[[arxiv-2307-03172]]（Lost in the Middle）、[[arxiv-2507-13334]]（Context Engineering 综述）。
- 长期记忆侧文献：[[arxiv-2309-02427]]（CoALA）、[[arxiv-2310-08560]]（MemGPT）、[[arxiv-2502-12110]]（A-Mem）、[[arxiv-2404-13501]]（记忆机制综述）。
- 相关概念：[[context-engineering]]、[[context-manager]]、[[state-artifact-store]]。
- 已有页面中的记忆实践：[[generative-agents]]（记忆流）、[[voyager]]（技能库）、[[skill-library]]。

## 来源

- [A Survey on the Memory Mechanism of Large Language Model based Agents (arXiv:2404.13501)](https://arxiv.org/abs/2404.13501) —— 记忆写入/管理/读取分类的主参照。
- [Cognitive Architectures for Language Agents (arXiv:2309.02427)](https://arxiv.org/abs/2309.02427) —— 记忆四分法的术语框架。
- [MemGPT (arXiv:2310.08560)](https://arxiv.org/abs/2310.08560) —— OS 式分层记忆管理。
- [A-Mem: Agentic Memory for LLM Agents (arXiv:2502.12110)](https://arxiv.org/abs/2502.12110) —— 自组织结构化记忆。
- [A Survey of Context Engineering for Large Language Models (arXiv:2507.13334)](https://arxiv.org/abs/2507.13334) —— 上下文工程的学科化整理。
- [Lost in the Middle (arXiv:2307.03172)](https://arxiv.org/abs/2307.03172) —— 长上下文利用 U 型曲线的实证。
- [From Question Answering to Task Completion (arXiv:2606.20683)](https://arxiv.org/abs/2606.20683) —— 记忆在 harness 分解中的位置。

## 待验证问题

- 记忆写入策略（记什么、什么粒度）的系统性比较研究仍少，待补充。
- HippoRAG、Mem0、Zep 等工程化记忆系统尚未入库，其结论待逐篇核对原文后再补充到本子方向。
- 新一代模型（2025 年后）上的位置偏置与 Lost in the Middle 结论的差异待验证。
- 记忆基准（LongMemEval、LoCoMo、MemGym 等）的覆盖面与区分度对比待整理，可考虑未来在 [[agent-evaluation]] 下展开。

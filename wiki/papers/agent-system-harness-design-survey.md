---
title: "From Question Answering to Task Completion: A Survey on Agent System and Harness Design"
aliases: ["From Question Answering to Task Completion", agent-system-harness-design-survey, harness-survey]
type: paper
status: draft
topics: [agent, harness, survey, system-design]
harness_components: [observation-interface, context-manager, control-loop, action-interface, state-artifact-store, verification-governance]
published: 2026-06
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 1
quality: medium
confidence: high
canonical_url: https://arxiv.org/abs/2606.20683
---

# From Question Answering to Task Completion: A Survey on Agent System and Harness Design

> Guo et al.，v1 2026-06（arXiv）。

## 一句话结论

这是本知识库主题最对口的综述：它把 LLM agent 明确定义为「底座模型 + 执行 harness」的耦合系统，将 harness 分解为六项运行时职责（observation、context、control、action、state、verification），并论证 agent 质量来自模型能力、运行时基建、任务结构与评测设计四者的交互。

## 论文解决了什么问题

agent 系统从 prompt engineering 一路演化到工作流、上下文工程、harness 工程乃至「agent 原生训练 + 协同进化」，但一个核心问题始终模糊：**agent 表现的瓶颈到底在模型、在 harness、还是在两者的耦合上？** 模型中心的规模化叙事（scaling 模型就能解决一切）在实践中遇到长程任务完成率、效率、可靠性的天花板。这篇综述要建立一套 model-harness 联合视角，回答「瓶颈在哪、harness 该怎么配」。

## 关键机制（综述的分析框架）

- **功能与实现的双重定义**：先澄清 agent 的功能定义（感知环境、调用工具、维护状态、长时程行动），再给出实现视角——LLM-based agent = 基础模型 + 执行 harness。
- **四代 agent 工程范式**：prompt engineering → workflow 与 context engineering → **harness engineering** → agent-native training 与模型-harness 协同进化（co-evolution）。
- **harness 六职责分解**：把执行 harness 拆成六个相互耦合的运行时职责——
  1. **observation**：把环境状态转化为模型可消费的输入；
  2. **context**：上下文组装与压缩（对应本库 [[context-manager]]）；
  3. **control**：循环控制、步数与预算、异常处理；
  4. **action**：动作解析、工具执行、权限与沙箱；
  5. **state**：跨步状态与记忆维护；
  6. **verification**：动作结果与任务进展的校验。
- **任务属性 → harness 配置映射**：用这套分解把任务性质（时程长度、可验证性、环境动态性等）映射到 harness 配置选择，并综述基准与评测实践。
- **开放挑战**：value-aware evaluation（把成本/价值纳入评测，呼应 [[ai-agents-that-matter]]）、安全、harness 泛化（一套 harness 跨任务/跨模型是否成立）、模型-harness 协同进化。

核心立场：**不应再把 agent 看作「模型 + 外挂工具」**；成功率、效率、安全、泛化都是模型 × 运行时 × 任务 × 评测交互的涌现结果。

## 对 Agent Harness 的启示

这篇综述几乎可以直接当 harness 设计文档的骨架用：

- **六职责分解是架构 checklist**：评估任何一个 harness（[[openhands]]、[[swe-agent]] 或自研系统）时，逐项问「observation 怎么构造、context 怎么压缩、control 怎么兜底、action 怎么隔离、state 存哪、verification 靠什么信号」，可以快速暴露短板。
- **「瓶颈归因」方法论**：遇到失败先定位在模型还是 harness，避免用 harness 补丁去遮模型短板（或反之），这是 [[ai-agents-that-matter]] 消融主张的系统化延伸。
- **harness 泛化是明确的开放问题**：为 [[swe-bench]] 调出来的 harness 换到网页任务往往失效，说明 harness 配置与任务结构的匹配本身就是研究对象，而不是一次写死的工程细节。
- **协同进化方向**：第四代范式意味着未来 harness 的接口设计会反过来影响模型训练（agent-native training），harness 决策不再只是部署层的事。

## 局限与后续工作

- 综述提出的分解框架属于概念性贡献，六职责之间的耦合（如 context 与 state 的边界）在工程上仍无标准答案。
- 「任务属性 → harness 配置」的映射目前是定性归纳，缺少可操作的量化指导。
- 2026 年中的文献快照，agent-native training 与协同进化部分尤其新，实证证据还在积累。
- 本页基于摘要与提交历史撰写，正文细节（各章节的系统对比表、具体系统分类）待补。

## 相关页面

- [[agent-harness]]：本库核心概念页，以该综述的六职责为骨架
- [[context-manager]]、[[verification-governance]]、[[sandboxed-execution]]、[[agent-memory]]：六职责对应的组件页
- [[ai-agents-that-matter]]：成本/归因方法论的先声
- [[survey-evaluation-llm-agents]]、[[evaluation-benchmarking-llm-agents]]：评测侧的配套综述
- [[react]]、[[voyager]]：范式演化前两代的代表系统

## 来源

- arXiv 摘要页：https://arxiv.org/abs/2606.20683（已核对摘要、作者列表与提交历史；作者含 Jianyuan Guo、Chang Xu、Yunhe Wang 等，完整名单见 arXiv 页面）
- 论文配套仓库：摘要页给出的论文合集链接（URL 见 arXiv 摘要页，具体地址待补录）

## 待验证问题

- 综述正文对现有系统（OpenHands、Claude Code 等）的具体分类与对比表细节。
- 「四代范式」各代的代表系统清单（本页转述自摘要，代际划分细节待核对全文）。

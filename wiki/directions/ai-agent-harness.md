---
type: direction
title: AI Agent Harness（执行壳）方向
aliases: ["agent harness", "harness engineering", "执行壳工程"]
status: draft
topics: [agent, harness, runtime, research-direction]
harness_components: [observation-interface, context-manager, control-loop, action-interface, state-artifact-store, verification-governance]
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 6
quality: medium
confidence: medium
canonical_url: https://arxiv.org/abs/2606.20683
evidence_sources:
  - https://arxiv.org/abs/2606.20683
  - https://github.com/ggjy/Awesome-Agent-Engineering
  - https://github.com/ZJU-REAL/Polaris
  - https://github.com/Jiaaqiliu/Awesome-Harness-Engineering
  - https://arxiv.org/abs/2405.15793
  - https://arxiv.org/abs/2407.16741
---

## 一句话结论

AI Agent Harness 方向研究的是：在基座模型不变的前提下，如何通过设计包裹模型的运行时基础设施（观察、上下文、控制、动作、状态、验证六个组件），把模型能力转化为可靠的长程任务完成能力。

## 关键机制

这个方向的出发点是一个经验观察：静态 benchmark（如 MMLU、HumanEval）趋于饱和，但 agentic benchmark（如 [[swe-bench]]、WebArena、OSWorld、Terminal-Bench）上即使是前沿模型也仍有明显差距。差距说明瓶颈不只在模型，也在模型与环境的耦合方式上。

方向的几个关键支点：

1. **Agent = 模型 + Harness。** 见 [[agent-harness]]。Harness 形式化为六元组：[[observation-interface]]、[[context-manager]]、[[control-loop]]、[[action-interface]]、[[state-artifact-store]]、[[verification-governance]]。
2. **接口设计是性能杠杆。** SWE-agent 的论文（arXiv:2405.15793）证明：固定基座模型，仅重新设计 agent-computer interface（ACI）就能显著提升 [[swe-bench]] 成绩。这是「harness 是独立设计对象」的早期实证。
3. **范式迁移。** Prompt Engineering 解决「怎么问」，Context Engineering 解决「给模型看什么」，Harness Engineering 解决「如何让整个执行闭环不脱轨」，Agent-Native Training 则把部分行为内化进模型参数。四者在实践中共存。
4. **Harness 正在变得可学习。** 近期工作把 harness 配置本身当作可编辑、可搜索、可优化的对象（如 NLAH 把 harness 逻辑写成自然语言工件，Meta-Harness 把配置当作搜索空间），并向多模型 harness（路由、委派、组合多个异构模型）演进。相关论断来自综述，具体论文细节待逐篇核对。

## 适用场景

- 评估「换更强的模型」和「改 harness」哪个更值得投入时，这个方向提供分析框架。
- 设计 coding agent、web agent、研究型 agent 时，六组件可作为设计检查清单（checklist）。
- 做 agent 相关综述或开题时，该方向提供了「演进优先（evolution-first）」而非「分类法优先」的组织视角。

## 局限与失败模式

- **术语不统一。** 2026 年以来出现多个 harness 分类法（六组件、七层 ETCLOVG、code-as-harness 等），划分粒度和命名各异，跨文献引用时需要先做术语映射。
- **归因困难。** Agent 性能是模型、Harness、任务、评估交互的产物，实际系统中很难干净地分离「harness 的贡献」与「模型的贡献」；对照实验（固定模型只改 harness）成本高。
- **过拟合 benchmark 的风险。** 针对特定 benchmark 调优的 harness（例如为 [[swe-bench]] 定制的脚手架）未必迁移到其他任务，harness 泛化能力是该方向自己承认的开放问题。
- **工程证据多于学术证据。** 很多关键结论来自工业界工程报告而非受控实验，证据强度参差不齐。

## 与其他页面的关系

- 核心概念：[[agent-harness]]。
- 子方向：[[agent-memory-context]]（记忆与工作记忆）。
- 六组件：[[observation-interface]]、[[context-manager]]、[[control-loop]]、[[action-interface]]、[[state-artifact-store]]、[[verification-governance]]。
- 相邻横向主题：[[context-engineering]]（范式第 2 阶段）、[[agent-memory]]、[[tool-use]]、[[sandboxed-execution]]、[[model-context-protocol]]、[[multi-agent-orchestration]]。
- 支撑方向闭环的两个主题：[[agent-evaluation]]（衡量 harness 收益）、[[agent-observability]]（让 harness 行为可检查）。
- 代表性系统与 benchmark：[[openhands]]、[[swe-bench]]、[[react]]（页面在其他分块维护）。

## 来源

- [From Question Answering to Task Completion: A Survey on Agent System and Harness Design (arXiv:2606.20683)](https://arxiv.org/abs/2606.20683)
- [Awesome-Agent-Engineering（综述配套清单）](https://github.com/ggjy/Awesome-Agent-Engineering)
- [Polaris（文献管线参考）](https://github.com/ZJU-REAL/Polaris)
- [awesome-harness-engineering（工程实践清单）](https://github.com/Jiaaqiliu/Awesome-Harness-Engineering)
- [SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering (arXiv:2405.15793)](https://arxiv.org/abs/2405.15793)
- [OpenHands: An Open Platform for AI Software Developers as Generalist Agents (arXiv:2407.16741)](https://arxiv.org/abs/2407.16741)

## 待验证问题

- Harness engineering 一词的最早提出者与确切出处（综述引用了 Hashimoto 与 OpenAI 的讨论）需要核对原文。
- NLAH、Meta-Harness 等「可学习 harness」工作的具体方法和结论待逐篇阅读原文。
- 「多模型 harness」在多大程度上已成为生产实践的主流，还是仍属前沿探索，待更多工业证据。
- 各 harness 分类法（六组件 vs 七层 ETCLOVG vs code-as-harness）之间的覆盖差异和取舍待对比。

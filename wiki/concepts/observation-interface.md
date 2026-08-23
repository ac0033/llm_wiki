---
type: concept
title: Observation Interface（观察接口）
aliases: ["observation interface", "观察接口", "ACI 观察侧"]
status: draft
topics: [agent, harness, observation, perception]
harness_components: [observation-interface]
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 4
quality: high
confidence: high
canonical_url: https://arxiv.org/abs/2606.20683
evidence_sources:
  - https://arxiv.org/abs/2606.20683
  - https://arxiv.org/abs/2405.15793
  - https://arxiv.org/abs/2307.13854
  - https://arxiv.org/abs/2404.07972
---

## 一句话结论

Observation Interface 负责把环境的原始信号（终端输出、文件 diff、截图、DOM、API 响应、日志、检索结果、事件流）转换成模型能消化、能据以决策的观察——它是模型与环境之间的「翻译层」，翻译质量直接决定后续所有推理的质量。

## 关键机制

在 [[agent-harness]] 的六组件分解中，观察接口解决的是「模型看到什么」的问题。核心机制包括：

1. **信号采集与截断。** 环境输出往往远超上下文容量（一次编译可能有上千行日志），观察接口要决定截断、过滤、摘要的策略。SWE-agent 的 ACI 设计（arXiv:2405.15793）是代表性案例：通过约束终端交互的呈现方式，让模型更容易理解环境反馈，从而在 [[swe-bench]] 上提升了固定模型的表现。
2. **模态转换。** GUI/计算机使用类 agent 把屏幕截图或 DOM 树转成文本或可解析结构（如 accessibility tree）；WebArena（arXiv:2307.13854）和 OSWorld（arXiv:2404.07972）等 benchmark 的环境就提供了这类观察通道。
3. **与 [[context-manager]] 的协同。** 观察接口产出「可用观察」，但哪些观察最终进入上下文、以什么顺序和格式进入，由上下文管理器决定——感知在功能映射上同时依赖这两个组件。

## 适用场景

- Coding agent：终端输出、测试失败堆栈、文件 diff 的呈现方式直接影响模型定位 bug 的能力，见 [[openhands]]、SWE-agent。
- Web/GUI agent：截图 + DOM/accessibility tree 的选择与粒度设计是 grounding（把模型输出落到具体 UI 元素）的前提。
- 研究型 agent：检索结果、网页正文的抽取与去噪，决定后续综合与引用的质量。

## 局限与失败模式

- **噪声污染。** 原始输出不加处理地塞给模型，会稀释关键信息、推高 token 成本，还可能触发无关联想。
- **过度抽象。** 过滤或摘要太激进会丢掉关键线索（例如截断掉的正是报错行），模型因此做出基于残缺信息的决策。
- **观察-动作不匹配。** 观察的表示方式若与动作空间不对齐（例如观察里给截图坐标、动作却是 DOM selector），模型需要在每一步自行对齐，出错率上升。
- **环境侧注入。** 观察通道也是 prompt injection 的入口——恶意网页、仓库文件内容会随观察进入模型，这需要 [[verification-governance]] 配合防护。

## 与其他页面的关系

- 上游概念：[[agent-harness]]、方向页 [[ai-agent-harness]]。
- 下游：观察进入上下文由 [[context-manager]] 调度；观察驱动的决策循环由 [[control-loop]] 编排。
- 对照面：[[action-interface]] 是同一接口的另一半（合起来接近 SWE-agent 所说的 ACI）。
- 观察通道的安全约束落在 [[verification-governance]] 与 [[sandboxed-execution]]。

## 来源

- [From Question Answering to Task Completion (arXiv:2606.20683)](https://arxiv.org/abs/2606.20683) —— 组件定义来源。
- [SWE-agent (arXiv:2405.15793)](https://arxiv.org/abs/2405.15793) —— ACI 设计影响性能的实证。
- [WebArena (arXiv:2307.13854)](https://arxiv.org/abs/2307.13854) —— web 环境观察通道的 benchmark 实例。
- [OSWorld (arXiv:2404.07972)](https://arxiv.org/abs/2404.07972) —— 桌面环境观察通道的 benchmark 实例。

## 待验证问题

- 不同观察表示（原始文本 vs 结构化 vs 截图多模态）对各任务族性能的定量影响，缺乏系统的跨任务对照研究，待验证。
- 「观察接口」与「上下文管理」的边界在不同系统中划分不一（有的系统把截断逻辑放在 prompt 组装侧），术语对齐待核对。

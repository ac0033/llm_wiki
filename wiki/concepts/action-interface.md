---
type: concept
title: Action Interface（动作接口）
aliases: ["action interface", "动作接口", "action space", "动作空间"]
status: draft
topics: [agent, harness, action, tool-calling]
harness_components: [action-interface]
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 4
quality: high
confidence: high
canonical_url: https://arxiv.org/abs/2606.20683
evidence_sources:
  - https://arxiv.org/abs/2606.20683
  - https://arxiv.org/abs/2405.15793
  - https://arxiv.org/abs/2302.04761
  - https://modelcontextprotocol.io
---

## 一句话结论

Action Interface 把模型的文本/结构化输出映射为可执行操作——函数调用、MCP 工具、shell 命令、浏览器动作、文件操作、API 调用、子 agent 调用——动作空间的设计决定了模型「能做什么」以及「以多高的可靠性做成」。

## 关键机制

在 [[agent-harness]] 六组件中，动作接口解决「模型能做什么」的问题。关键认识是：模型输出只是「动作提案（proposal）」，不是已执行的动作——校验、分发、观察结果、必要时拒绝或修复，都是 harness 的职责。

主要机制：

1. **动作空间设计。** 给模型暴露哪些操作、以什么粒度。SWE-agent（arXiv:2405.15793）证明：为 LM 友好而设计的命令集（而不是照搬人类用的 shell 习惯）能显著改善 agent 表现——动作接口是 ACI 的「输出侧」。
2. **结构化调用。** Function calling / tool use 把自由文本建议转成机器可执行的调用（schema 化的函数名 + 参数）。Toolformer（arXiv:2302.04761）是让模型自学调用 API 的早期代表。详见 [[tool-use]]。
3. **协议化接入。** [[model-context-protocol]]（MCP）标准化了工具与数据源的暴露方式，减少连接器的碎片化；A2A 协议则面向 agent 之间的互操作。
4. **权限与副作用控制。** 动作的放行条件（approval gate）、副作用的隔离（沙箱）属于 [[verification-governance]] 与 [[sandboxed-execution]]，但接口设计决定了这些约束能不能被细粒度地施加。

## 适用场景

- Coding agent：文件编辑命令、测试执行命令的设计（如用专用 edit 命令替代自由 sed）直接影响编辑成功率，见 [[openhands]]、SWE-agent。
- 浏览器/桌面 agent：点击、输入、滚动等动作以坐标还是 DOM 元素为参数，影响 grounding 可靠性。
- 企业自动化：通过 MCP/API 接入内部系统，动作接口是合规与审计的第一道关口。

## 局限与失败模式

- **参数幻觉。** 模型生成格式合法但语义错误的参数（错误路径、臆造的 API 字段），接口层的 schema 校验只能挡格式错误。
- **动作空间过大。** 工具太多导致选择困难与上下文膨胀；动作空间过小则束缚模型能力。最优粒度因任务和模型而异，缺乏通用设计准则。
- **副作用不可逆。** 写文件、发请求等动作一旦执行难以撤销，需要与检查点/回滚机制（[[state-artifact-store]]）配合。
- **接口过拟合。** 为特定 benchmark 定制的动作集可能不迁移——为 [[swe-bench]] 优化的命令集对真实开发环境未必最优，待验证。

## 与其他页面的关系

- 所属框架：[[agent-harness]]；与 [[observation-interface]] 共同构成 agent-环境接口（ACI）的两面。
- 动作的提案产生于模型（其选择受 [[context-manager]] 中工具描述的影响）；动作的调度时机由 [[control-loop]] 决定。
- 执行隔离见 [[sandboxed-execution]]；放行与审计见 [[verification-governance]]。
- 工具生态与标准化：[[tool-use]]、[[model-context-protocol]]；多 agent 调用链：[[multi-agent-orchestration]]。

## 来源

- [From Question Answering to Task Completion (arXiv:2606.20683)](https://arxiv.org/abs/2606.20683) —— 组件定义来源。
- [SWE-agent (arXiv:2405.15793)](https://arxiv.org/abs/2405.15793) —— 动作接口设计影响性能的实证。
- [Toolformer (arXiv:2302.04761)](https://arxiv.org/abs/2302.04761) —— 工具调用能力的奠基工作。
- [Model Context Protocol](https://modelcontextprotocol.io) —— 工具/数据源接入的标准协议。

## 待验证问题

- 「代码作为动作」（code-as-action，让模型输出可执行代码而非 JSON 调用）相对传统 function calling 的优劣，ICML 2024 起有工作支持，但跨任务定量比较待系统整理。
- 各主流 harness 的动作空间设计文档分散在系统文档中，缺乏统一编目，待补充。

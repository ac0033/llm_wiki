---
type: concept
title: Tool Use（工具使用）
aliases: ["tool use", "工具使用", "function calling", "tool calling"]
status: draft
topics: [agent, tools, function-calling, action]
harness_components: [action-interface, context-manager, observation-interface]
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 4
quality: high
confidence: high
canonical_url: https://arxiv.org/abs/2302.04761
evidence_sources:
  - https://arxiv.org/abs/2302.04761
  - https://arxiv.org/abs/2606.20683
  - https://modelcontextprotocol.io
  - https://arxiv.org/abs/2308.03688
---

## 一句话结论

Tool Use 指模型以结构化方式调用外部工具（代码执行、检索、浏览器、API）的能力与配套机制：schema 定义工具、模型提案调用、harness 校验并执行、结果作为观察返回——它把模型从「只能生成文本」变成「能在世界上行动」。

## 关键机制

1. **工具 schema 与描述。** 每个工具以名称、参数 schema、自然语言描述注册。描述写在上下文里，直接影响模型的选择正确率——schema 属于 [[action-interface]]，描述的管理属于 [[context-manager]]。
2. **调用提案与执行分离。** 模型只产出「提案」，harness 负责解析、校验、分发、执行、把结果作为观察返回。Toolformer（arXiv:2302.04761）展示了模型可以自学何时调用哪个 API；此后 function calling 成为主流模型的内建能力与标准 API 形态。
3. **协议化接入。** [[model-context-protocol]]（MCP）标准化了工具的暴露与发现，减少「每个工具一套适配代码」的碎片化。
4. **工具集管理。** 工具数量增长后，全量描述注入上下文既贵又干扰，需要按任务动态加载工具子集（与 [[context-engineering]] 的 progressive disclosure 思路一致）。

## 适用场景

- Coding agent：shell、编辑器、测试运行器是核心工具集，见 [[openhands]]。
- 研究型 agent：搜索、浏览器、文档解析工具。
- 企业自动化：内部 API、数据库、SaaS 连接器（MCP server 的主要落地场景）。

## 局限与失败模式

- **选错工具。** 工具集大、描述相似时模型会选错；工具描述的质量直接决定选择质量。
- **参数幻觉。** 生成格式合法但语义错误的参数（臆造字段名、错误的路径），schema 校验只能挡格式层。
- **串行调用链的误差累积。** 多步工具调用中前一步的错误输出成为后一步的输入，误差沿链传播。
- **工具结果污染上下文。** 冗长的工具返回（整个 HTML 页面、大段日志）不做处理直接进上下文，稀释有效信息——结果的后处理是 [[observation-interface]] 的职责。
- **安全面。** 工具是 prompt injection 的攻击面：工具返回内容可携带恶意指令，需要 [[verification-governance]] 的权限门与 [[sandboxed-execution]] 的隔离配合。

## 与其他页面的关系

- 运行时归属：[[action-interface]]（schema 与执行）、[[context-manager]]（描述注入）、[[observation-interface]]（结果呈现）。
- 标准化协议：[[model-context-protocol]]。
- 安全与放行：[[verification-governance]]、[[sandboxed-execution]]。
- 评估：工具使用能力是 [[agent-evaluation]] 的核心维度之一；AgentBench（arXiv:2308.03688）等 benchmark 包含工具使用场景。
- 经典范式：[[react]] 把「思考-调用-观察」显式化，是工具使用循环的原型。

## 来源

- [Toolformer (arXiv:2302.04761)](https://arxiv.org/abs/2302.04761) —— 模型自学工具调用的奠基工作。
- [From Question Answering to Task Completion (arXiv:2606.20683)](https://arxiv.org/abs/2606.20683) —— 工具调用在 harness 组件中的定位。
- [Model Context Protocol](https://modelcontextprotocol.io) —— 工具接入标准。
- [AgentBench (arXiv:2308.03688)](https://arxiv.org/abs/2308.03688) —— 含工具使用场景的 agent 基准。

## 待验证问题

- 「代码即动作」（模型直接输出可执行代码代替 JSON 工具调用）与 function calling 的系统性对比，结论分散，待整理。
- 工具描述写法（长度、示例、否定说明）对调用正确率的影响多为工程经验，缺乏公开对照实验，待验证。

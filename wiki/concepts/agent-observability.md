---
type: concept
title: Agent Observability（Agent 可观测性）
aliases: ["agent observability", "agent 可观测性", "tracing", "轨迹追踪"]
status: draft
topics: [agent, observability, tracing, monitoring, debugging]
harness_components: [state-artifact-store, verification-governance]
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 4
quality: medium
confidence: medium
canonical_url: https://opentelemetry.io/docs/specs/semconv/gen-ai/
evidence_sources:
  - https://opentelemetry.io/docs/specs/semconv/gen-ai/
  - https://github.com/langfuse/langfuse
  - https://arxiv.org/abs/2606.20683
  - https://github.com/Jiaaqiliu/Awesome-Harness-Engineering
---

## 一句话结论

Agent Observability 是把 agent 的多步执行变成可检查、可调试、可归因对象的工程实践：通过轨迹（trace）、跨度（span）、token 与成本计量、工具调用记录等手段，回答「agent 这一步为什么这么做、钱花在哪、错在哪一环」。

## 关键机制

Agent 的执行是非确定性的多步循环，传统日志不足以定位问题，可观测性的核心对象是**轨迹**：完整的「观察-推理-动作-结果」序列。

1. **Tracing 基础设施。** OpenTelemetry 的 GenAI 语义约定（semantic conventions）为 LLM 调用、agent 运行、工具执行定义了统一的 span 属性，是厂商中立的埋点标准。
2. **专用平台。** Langfuse（开源）、LangSmith 等提供 trace 采集、回放、标注、成本统计；agent SDK（如 OpenAI Agents SDK）把 tracing 作为内建能力暴露。
3. **成本与性能计量。** 按步骤/任务归集 token 用量、延迟、费用——agent 循环的成本是乘积式增长，计量是预算控制的前提。
4. **与评估的闭环。** 轨迹数据既用于人工调试，也作为 [[agent-evaluation]] 的输入（轨迹评分、失败聚类、回归对比）。

在 harness 视角下，可观测性横跨组件：轨迹持久化在 [[state-artifact-store]]，审计用途归入 [[verification-governance]]，SDK 与 tracing 把 harness 行为「可重用、可检查、可调试化」。

## 适用场景

- 调试 agent 失败：定位失败发生在哪个组件（看错、想错、做错、没拦住）。
- 生产监控：成本异常、循环失控、延迟退化的告警。
- 离线改进：从真实轨迹挖掘失败模式，指导 harness 迭代与评估集建设。

## 局限与失败模式

- **数据量膨胀。** 长程任务单条轨迹可达数百步，存储与分析成本高；采样又会丢掉关键失败案例。
- **敏感信息泄露。** 轨迹天然包含用户输入、工具返回、甚至密钥，落盘前需要脱敏，与 [[verification-governance]] 的合规职责交叉。
- **非确定性使回放困难。** 同样的轨迹换一天重放结果可能不同（模型更新、环境变化），trace 只能解释「当时发生了什么」，不能直接复现。
- **标准仍在演进。** GenAI 语义约定处于快速迭代期，不同 SDK/平台的埋点字段尚未完全对齐，跨工具迁移 trace 有摩擦，待验证现状。

## 与其他页面的关系

- 数据来源：[[control-loop]] 推进产生的轨迹、[[action-interface]] 的工具调用记录、[[observation-interface]] 的观察。
- 存储与审计：[[state-artifact-store]]、[[verification-governance]]。
- 下游消费：[[agent-evaluation]]（离线评估）、[[ai-agent-harness]] 方向页的「归因困难」问题正依赖可观测性缓解。
- 相关系统：[[openhands]] 等开源平台的轨迹格式是常见事实标准之一。

## 来源

- [OpenTelemetry GenAI Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) —— 厂商中立的 GenAI/agent 埋点标准。
- [Langfuse](https://github.com/langfuse/langfuse) —— 开源 LLM/agent 可观测性平台。
- [From Question Answering to Task Completion (arXiv:2606.20683)](https://arxiv.org/abs/2606.20683) —— agent SDK 与 tracing 在 harness 中的定位。
- [awesome-harness-engineering](https://github.com/Jiaaqiliu/Awesome-Harness-Engineering) —— 收录 observability 相关工具。

## 待验证问题

- OpenTelemetry GenAI 约定的稳定状态（哪些部分已 stable）随版本变化，引用时需核对当时版本。
- 各平台 trace 格式（Langfuse、LangSmith、OpenAI Agents SDK、OpenHands）的互操作性缺乏整理，待补充。
- 「轨迹挖掘 → harness 改进」的自动化闭环（自动失败聚类、自动评估集生成）有哪些成熟工具，待调研。

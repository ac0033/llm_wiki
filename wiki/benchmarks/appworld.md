---
type: benchmark
title: AppWorld
status: draft
topics:
- benchmark
- tool-use
- coding-agent
- simulation
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 3
quality: medium
confidence: medium
canonical_url: https://arxiv.org/abs/2407.18901
evidence_sources:
- https://arxiv.org/abs/2407.18901
- https://appworld.dev/
- https://github.com/StonyBrookNLP/appworld
---
# AppWorld

AppWorld 是 Stony Brook、Allen AI 等团队提出的可控应用世界基准（论文 arXiv:2407.18901，ACL 2024 最佳资源论文奖）：一个高保真模拟引擎，复刻了 9 个日常应用（电商、音乐、支付、邮件、日历等，对外用仿名如 Amazon/Spotify/Venmo/Gmail 的对标物）加 2 个辅助应用，共 457 个 API，世界里住着约 100 个有完整数字生活轨迹的虚构用户。Agent 用 Python 代码调 API 完成 750 个日常任务（数字以论文为准）。

## 评什么

评"交互式编码 + 工具使用"的复合能力：Agent 要在 Python REPL 里探索 API 文档、写多步代码、处理异常、组合多个应用完成任务（如"把某笔开支拆分给室友并发消息通知"）。难点在于任务开放、解法不唯一、API 面广。

## 环境

- 完全自包含的模拟引擎：应用状态存在数据库里，可快照、重置、回放，不依赖任何真实外部服务——可复现性是它相对 [[webarena]]、[[gaia]] 的核心优势。
- Agent 的动作空间是 Python 代码（code-as-action），通过 IPython 风格接口执行；引擎对危险操作有防护。
- 世界状态可控可编程，支持构造反事实场景做鲁棒性测试。

## 指标

- **TGC（Task Goal Completion）**：任务目标达成的比例，用针对任务的数据库状态"单元测试"套件判定，承认多种合法解法。
- **SGC（Scenario Goal Completion）**：同一情景下全部任务都完成才算过的严格口径。
- 同时检查"附带损伤"：目标达成了但动了不该动的数据，也不算成功。不引用具体分数。

## 对 Harness 评估的启示

- "附带损伤"检查把 Harness 的一个隐性能力显性化了：克制。会做动作和会不做多余动作是两回事，动作空间的权限设计、操作前的状态确认习惯都属于 [[agent-harness]] 的职责。
- code-as-action 的接口与 [[openhands]] 的 CodeAct、[[swe-agent]] 的 bash 命令属于同一家族，AppWorld 是检验这类动作空间通用性的好环境。
- 状态可完全回放，使"从轨迹定位 Harness 缺陷"（是上下文丢了、还是异常处理缺失）可行，对 Harness 的错误分析方法论友好。

## 待验证 / 边界

- 模拟应用毕竟是仿品，结论外推到真实 API（返回格式漂移、限流、认证）需谨慎。
- 任务数、API 数随版本可能更新，引用前以官方仓库为准。

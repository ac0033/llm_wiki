---
type: concept
title: Control Loop（控制循环）
aliases: ["control loop", "控制循环", "agent loop", "agentic loop"]
status: draft
topics: [agent, harness, control-loop, orchestration]
harness_components: [control-loop]
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 4
quality: high
confidence: high
canonical_url: https://arxiv.org/abs/2606.20683
evidence_sources:
  - https://arxiv.org/abs/2606.20683
  - https://arxiv.org/abs/2210.03629
  - https://arxiv.org/abs/2303.11366
  - https://arxiv.org/abs/2407.16741
---

## 一句话结论

Control Loop 是编排「观察-推理-行动-反馈」循环的运行时机制：它决定每一步何时调度、何时停止、失败时重试还是反思、何时委派给子 agent 或切换模型——它把单次的模型调用变成可持续推进的长程执行。

## 关键机制

在 [[agent-harness]] 六组件中，控制循环解决「如何让整个系统不脱轨」的问题。主要机制：

1. **循环骨架。** 最小实现是 [[react]]（arXiv:2210.03629）式的「推理-行动-观察」交替轨迹：模型产出思考与动作，环境返回观察，循环推进。[[openhands]] 等平台的 event loop 是工程化的完整实现。
2. **停止条件与预算。** 决定循环何时终止：任务完成信号、步数/token/成本上限、无进展检测。预算控制与 [[verification-governance]] 有交叉。
3. **重试与反思。** 失败后原地重试、带错误信息重试、或触发反思（如 Reflexion，arXiv:2303.11366，把失败轨迹转成语言反馈供后续尝试使用）。
4. **委派与交接（handoff）。** 把子任务交给 sub-agent；多模型场景下还包含模型路由（哪一步用哪个模型）与角色分配，这与 [[multi-agent-orchestration]] 直接相关。
5. **漂移检测。** 长程执行中目标漂移（drift）是主要失败源，控制循环需要结构性机制（而不仅是更好的 prompt）来检测和纠正。

## 适用场景

- 任何多步 agent：单轮调用不构成闭环，闭环是 agent 区别于「静态检索系统、固定自动化脚本」的定义性特征。
- 长程 coding 任务：几十到上百步的执行中，停止条件和错误恢复策略决定最终成功率与成本。
- 多 agent 系统：协调、交接、辩论、协商都属于控制循环的扩展职责。

## 局限与失败模式

- **死循环与空转。** 停止条件设计不当导致 agent 反复执行同一无效动作，烧掉预算而无进展。
- **过度反思。** 反思机制可能在已经正确的路径上引发自我怀疑、推翻重来，反而降低成功率；何时该反思缺乏可靠判据。
- **目标漂移。** 步骤越多，累积的上下文噪声越容易让 agent 偏离原始目标；纯 prompt 层的提醒不足以防止。
- **成本不可控。** 循环步数 × 每步 token 数使成本呈乘积增长，缺乏预算硬约束时容易失控。
- **错误传播。** 循环中一步的错误动作会污染后续状态，若 [[state-artifact-store]] 没有检查点机制，回滚代价高。

## 与其他页面的关系

- 所属框架：[[agent-harness]]；循环每步的输入由 [[context-manager]] 组装，输出经 [[action-interface]] 执行。
- 反馈信号来自 [[observation-interface]] 与 [[verification-governance]]（测试结果、断言失败等）。
- 循环状态（历史、计划、检查点）持久化在 [[state-artifact-store]]。
- 多 agent 扩展见 [[multi-agent-orchestration]]；最小范式见 [[react]]。
- 循环产生的轨迹是 [[agent-observability]] 的主要观察对象，也是 [[agent-evaluation]] 的评估对象。

## 来源

- [From Question Answering to Task Completion (arXiv:2606.20683)](https://arxiv.org/abs/2606.20683) —— 组件定义来源。
- [ReAct (arXiv:2210.03629)](https://arxiv.org/abs/2210.03629) —— 推理-行动交替的经典框架。
- [Reflexion (arXiv:2303.11366)](https://arxiv.org/abs/2303.11366) —— 语言反馈式反思机制。
- [OpenHands (arXiv:2407.16741)](https://arxiv.org/abs/2407.16741) —— 工程化 event loop 的开源实现。

## 待验证问题

- 停止条件/预算策略对成功率与成本帕累托前沿的定量影响，公开系统研究较少，待验证。
- 反思类机制（Reflexion 及后续工作）在强模型上的边际收益是否仍然显著，社区有争议，待核对近期对照实验。
- 多模型路由（routing）策略的公开评估方法与结论待补充。

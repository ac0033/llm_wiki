---
type: concept
title: Cost Tracking（成本核算）
aliases: ["cost tracking", "成本核算", "token budget", "预算控制"]
status: current
topics: [agent, evaluation, observability, cost, reliability]
harness_components: [verification-governance, control-loop, state-artifact-store]
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 3
quality: high
confidence: high
canonical_url: https://arxiv.org/abs/2407.01502
evidence_sources:
  - https://arxiv.org/abs/2407.01502
  - https://arxiv.org/abs/2503.16416
  - https://arxiv.org/abs/2606.20683
---

## 一句话结论

Cost Tracking 是把 token、API 费用、trial 次数、延迟、工具调用和人工干预成本随 agent 轨迹一起记录的机制；没有它，benchmark 成功率无法转化为可部署性判断。

## 关键机制

- **按轨迹记录**：每次模型调用、工具执行、重试、反思和人工接管都要挂到同一条 run/trace 上。
- **预算约束**：[[control-loop]] 不只是决定下一步做什么，还要决定“还能花多少”。预算可以是 token、金额、时间、步数或并发。
- **准确率-成本联合分析**：[[ai-agents-that-matter]] 强调不能只看成功率；同一个成功率如果靠更多重试堆出来，工程价值完全不同。
- **归属与报表**：成本应能按任务、模型、Harness 配置、用户或项目归因，否则无法判断哪一层设计在烧钱。

## 适用场景

- 比较不同模型或不同 Harness 配置时，固定预算比单独比较成功率更公平。
- 生产环境中给 agent 设置预算、审批阈值和降级策略。
- 评测 benchmark 时报告 Pareto 前沿，而不是只报告最高分。

## 局限与失败模式

- **成本口径不一致**：输入/输出 token、缓存命中、工具费用、人工审核时间是否计入，各系统差异很大。
- **重试隐藏成本**：多 trial 评测如果只报最好一次，会系统性低估真实成本。
- **成本优化可能伤害能力**：过度压缩上下文或过早停止会降低长任务成功率，需要和 [[agent-evaluation]] 联合判断。

## 与其他页面的关系

- [[agent-observability]]：成本数据通常来自 trace/telemetry。
- [[verification-governance]]：预算超限、审批、降级和停止条件属于治理层。
- [[agent-evaluation]]：成本是评测指标的一部分，不是事后附加信息。
- [[harness-vs-model-evaluation]]：固定成本预算是公平比较模型与 Harness 的前提。

## 来源

- [AI Agents That Matter](https://arxiv.org/abs/2407.01502)
- [A Survey on Evaluation of LLM-based Agents](https://arxiv.org/abs/2503.16416)
- [From Question Answering to Task Completion: A Survey on Agent System and Harness Design](https://arxiv.org/abs/2606.20683)

## 待验证问题

- 各评测平台对成本字段的标准化程度仍不统一，后续应补一页“成本指标口径”。
- 对本地模型、订阅制产品和 API 模型的成本可比性需要单独建模。
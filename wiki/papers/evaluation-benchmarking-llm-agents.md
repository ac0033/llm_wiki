---
title: "Evaluation and Benchmarking of LLM Agents: A Survey"
aliases: ["Evaluation and Benchmarking of LLM Agents: A Survey", evaluation-benchmarking-llm-agents]
type: paper
status: draft
topics: [agent, evaluation, survey, enterprise]
harness_components: [evaluation-harness]
published: 2025-07
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 1
quality: medium
confidence: high
canonical_url: https://arxiv.org/abs/2507.21504
---

# Evaluation and Benchmarking of LLM Agents: A Survey

> Mohammadi et al.，v1 2025-07（arXiv）。

## 一句话结论

这篇综述用「评什么 × 怎么评」的二维分类法整理 LLM agent 评测，并特别补上了其他综述常忽略的企业部署视角——数据权限、可靠性保证、长程动态交互与合规。

## 论文解决了什么问题

agent 评测文献高度碎片化：基准、指标、工具各自为政，实践者难以系统选型；同时，学术研究里的评测设定与企业真实部署之间存在落差（真实系统有权限边界、SLA、合规要求）。论文的目标是用一个统一框架把碎片整理清楚，并把企业场景的挑战摆上台面。

## 关键机制（综述的组织框架）

论文提出一个二维分类法：

- **维度一：评测目标（what to evaluate）**——agent 的行为（behavior）、能力（capabilities）、可靠性（reliability）、安全性（safety）。
- **维度二：评测过程（how to evaluate）**——交互模式（单轮/多轮/人在环等）、数据集与基准、指标计算方法、评测工具链。

在此之上，论文单列了**企业特有的评测挑战**：基于角色的数据访问控制（RBAC）、可靠性保证需求、动态且长时程的交互、合规约束——这些维度在学术基准里普遍缺席。未来方向包括更整体化、更真实、更可扩展的评测。

## 对 Agent Harness 的启示

- **「评什么 × 怎么评」矩阵可直接用作评测方案设计 checklist**：给一个 harness 设计评测时，先确定目标象限（行为/能力/可靠性/安全），再选过程手段（交互模式、基准、指标、工具），避免漏掉可靠性、安全这类常被跳过的目标。
- **企业视角是 harness 设计的现实约束**：RBAC、合规要求意味着 harness 的动作执行层需要权限边界，且评测必须在带权限约束的环境里进行——沙盒里无约束跑出的成功率不代表生产可用性。
- **可靠性作为独立评测目标**：呼应 [[verification-governance]] 组件——成功率之外，方差、失败模式分布、降级行为都需要 harness 层的遥测支撑。
- 与 [[survey-evaluation-llm-agents]] 互补：那篇偏能力/基准地图，这篇偏评测过程与企业落地；两篇共同指认成本、安全、细粒度评估为缺口。

## 局限与后续工作

- 综述无新实验，结论为框架性整理。
- 二维分类法的粒度有限：模型与 harness 的贡献归因（[[ai-agents-that-matter]] 的核心关切）未被单独展开为一个维度。
- 企业挑战部分偏问题陈述，缺少已被验证的解决方案；正文细节待补（本页基于摘要撰写）。

## 相关页面

- [[agent-evaluation]]：评测总览
- [[survey-evaluation-llm-agents]]：姊妹综述
- [[ai-agents-that-matter]]：成本与归因方法论
- [[agent-system-harness-design-survey]]：harness 六职责与评测设计
- [[verification-governance]]、[[sandboxed-execution]]：可靠性与安全评测的执行层

## 来源

- arXiv 摘要页：https://arxiv.org/abs/2507.21504（本页内容已核对摘要与提交历史）

## 待验证问题

- 完整作者名单与机构（摘要页显示 Mahmoud Mohammadi、Yipeng Li、Jane Lo、Wendy Yip，完整性待核对 PDF）。
- 综述正文覆盖的基准清单与二维分类表细节（本页仅基于摘要）。

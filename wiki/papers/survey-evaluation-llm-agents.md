---
title: "Survey on Evaluation of LLM-based Agents"
aliases: ["Survey on Evaluation of LLM-based Agents", survey-evaluation-llm-agents]
type: paper
status: draft
topics: [agent, evaluation, survey]
harness_components: [evaluation-harness]
published: 2025-03
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 1
quality: medium
confidence: high
canonical_url: https://arxiv.org/abs/2503.16416
---

# Survey on Evaluation of LLM-based Agents

> Yehudai et al.，v1 2025-03，v2 2026-04（arXiv 更新）。

## 一句话结论

这是较早期系统梳理 LLM agent 评测的综述，从「评什么能力、用什么基准、怎么评通才 agent、基准的共同维度、开发者工具」五个视角组织文献，并明确指出成本-效率、安全、鲁棒性是当时评测的最大缺口。

## 论文解决了什么问题

agent 能力快速膨胀，但评测研究分散在无数单点基准里，缺乏统一地图：新人不知道该用哪些基准，研究者也看不清整个评测体系缺什么。这篇综述要提供这张地图，并指出领域趋势与空白。

## 关键机制（综述的组织框架）

论文从五个视角分析 agent 评测：

1. **核心能力评测**：构成 agentic 工作流的底座能力，如规划（planning）、工具使用（tool use）等的专项评测。
2. **应用向基准**：面向具体场景的基准，如网页 agent、软件工程 agent（[[swe-bench]] 一类）。
3. **通才 agent 评测**：对跨领域通用 agent 的评估方式。
4. **基准的核心维度分析**：横向比较各基准在真实性、交互性、判分方式等维度上的设计选择。
5. **评测框架与工具**：面向开发者的评测基建（框架、工具链）。

综述观察到的趋势：评测正走向更真实、更难、持续更新（对抗污染）；识别出的关键缺口：**成本-效率、安全性、鲁棒性的评估严重不足**，以及缺少细粒度、可扩展的评测方法。

## 对 Agent Harness 的启示

- **评测对象的分层**：综述把「评底座能力」与「评整机 agent」分开，这对应 harness 工程里一个实用原则——定位问题时先判断瓶颈在模型还是脚手架，再决定优化方向（与 [[ai-agents-that-matter]] 的归因主张一致）。
- **持续更新的基准成为常态**，意味着评测 harness 要支持基准版本化：同一套系统在不同版本基准上的结果要可追溯、可对比。
- **缺口即 harness 的功能清单**：成本-效率评估不足 → harness 需要内置成本埋点；安全性评估不足 → harness 需要权限与危险动作拦截的评测钩子。
- 与 [[evaluation-benchmarking-llm-agents]] 互为参照：两者覆盖相近，后者额外强调企业部署视角（权限、合规）。

## 局限与后续工作

- 综述本身不提供新基准或新实验结论，价值在于地图与缺口识别。
- 领域发展极快，v1（2025-03）之后出现的新基准与 harness 工程实践需要靠 v2 及后续综述跟进；本页基于 v1/v2 摘要，正文细节待补。
- 「通才 agent 评测」部分随通用 agent 产品演进（2025-2026 年）可能已过时。

## 相关页面

- [[agent-evaluation]]：评测总览
- [[evaluation-benchmarking-llm-agents]]：另一篇评测综述（企业视角）
- [[ai-agents-that-matter]]：成本与归因批判
- [[agentbench]]、[[swe-bench]]：综述覆盖的代表性基准
- [[agent-system-harness-design-survey]]：harness 视角综述

## 来源

- arXiv 摘要页：https://arxiv.org/abs/2503.16416（本页内容已核对 v1/v2 摘要与提交历史）

## 待验证问题

- 综述正文中基准清单与各维度对比表的细节（本页仅基于摘要，未逐节核对全文）。
- 完整作者名单与机构（摘要页显示提交者 Asaf Yehudai，作者列表含 Lilach Eden、Alan Li、Guy Uziel、Yilun Zhao、Roy Bar-Haim、Arman Cohan、Michal Shmueli-Scheuer 等，顺序与完整性待核对 PDF 首页）。

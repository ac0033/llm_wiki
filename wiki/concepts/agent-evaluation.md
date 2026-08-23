---
type: concept
title: Agent Evaluation（Agent 评估）
aliases: ["agent evaluation", "agent 评估", "agent benchmark"]
status: draft
topics: [agent, evaluation, benchmark]
harness_components: [verification-governance]
ingested: 2026-08-18
last_verified: 2026-08-21
source_count: 8
quality: high
confidence: medium
canonical_url: https://arxiv.org/abs/2507.21504
evidence_sources:
  - https://arxiv.org/abs/2507.21504
  - https://arxiv.org/abs/2606.20683
  - https://arxiv.org/abs/2310.06770
  - https://arxiv.org/abs/2307.13854
  - https://arxiv.org/abs/2404.07972
  - https://arxiv.org/abs/2608.15579
  - https://doi.org/10.5281/zenodo.22003465
  - https://github.com/laude-institute/terminal-bench
---

## 一句话结论

Agent Evaluation 研究如何衡量 agent 的任务完成能力：与静态 QA 基准不同，agentic 基准要求与真实环境多步交互，评估对象从「一次输出」扩展为「整条轨迹」，且成功率之外还必须衡量成本、效率、安全性——目前主流 benchmark（如 [[swe-bench]]、WebArena、OSWorld、Terminal-Bench）上前沿系统仍有明显差距。

## 关键机制

1. **从静态到交互。** 静态基准（固定输入、单次输出评分）趋于饱和且受污染风险困扰；agentic 基准把模型放进可执行环境：[[swe-bench]]（arXiv:2310.06770，真实 GitHub issue 修复，以测试通过为判据）、WebArena（arXiv:2307.13854，自托管 web 环境）、OSWorld（arXiv:2404.07972，真实桌面操作系统）、Terminal-Bench（终端任务）。
2. **从结果到轨迹。** 除最终成功率外，还评估中间步骤：工具调用正确性、计划质量、错误恢复行为。LLM-as-judge 常用于开放式任务的轨迹评分，但 judge 自身的可靠性需要校准。
3. **从成功率到价值。** 综述（arXiv:2606.20683）主张 value-aware evaluation：把成本、延迟、步数纳入目标——agent 反复调用模型，单调用成本沿轨迹累积。
4. **统计严谨性。** 2026 年后的工作开始把 benchmark 数字当作统计估计来报告：Kozuchi Agent（[[arxiv-2608-15579]]）在 [[swe-bench]] Verified 结果上给出 Wilson 置信区间、按仓库聚类的 bootstrap、配对 McNemar 检验加 Benjamini–Hochberg FDR 校正；dspy-security-bench（[[doi-org-10-5281-zenodo-22003465]]）则把测量协议哈希冻结、报 cluster-bootstrap 置信区间，并设 confirmed/provisional 判据区分稳定结论与初步观察（该工具为自述来源，待核实）。
4. **时间跨度视角。** 有研究以「agent 能以固定成功概率完成的人类任务时长」为指标，把长程可靠性作为核心度量（具体数值结论待核对原文）。
5. **模型-harness 归因。** 固定模型改 harness（或反之）的对照实验，用于分离两者的贡献——这是 harness 研究的方法论基础。

## 适用场景

- 选型：比较不同模型 × harness 组合在目标任务族上的表现。
- 回归测试：harness 每次改动后用固定 benchmark 子集验证不退化。
- 研究归因：判断提升来自模型能力还是运行时设计。

## 局限与失败模式

- **Benchmark 过拟合与污染。** 针对特定 benchmark 调优的 harness 泛化性存疑；训练数据污染使静态基准分数失真。
- **评估即目标（Goodhart）。** 可验证奖励诱发 reward hacking——agent 学会通过测试而非解决问题。
- **环境不可复现。** 交互式基准依赖环境快照（容器、网站镜像），环境漂移导致分数随时间不可比。
- **成本报告缺失。** 许多结果只报成功率不报 token/费用/时长，跨系统比较困难。
- **Judge 偏差。** LLM-as-judge 的一致性与人类判断的相关性需要逐场景校准，通用结论待验证。

## 与其他页面的关系

- 运行时对应面：[[verification-governance]]（在线验证与离线评估共享「正确性判据」问题）。
- 数据基础：[[agent-observability]] 提供轨迹数据；[[state-artifact-store]] 存评估所需的执行记录。
- 被评估对象：[[agent-harness]] 整体及各组件（[[control-loop]] 的停止策略、[[context-manager]] 的压缩策略等都是消融对象）。
- 具体基准页（[[swe-bench]] 等）由其他分块维护；[[react]]、[[openhands]] 是常见的被评估方法/系统。

## 来源

- [Evaluation and Benchmarking of LLM Agents: A Survey (arXiv:2507.21504)](https://arxiv.org/abs/2507.21504) —— 评估方法学综述（二维分类：评什么、怎么评）。
- [From Question Answering to Task Completion (arXiv:2606.20683)](https://arxiv.org/abs/2606.20683) —— benchmark 证据与 value-aware evaluation 主张。
- [SWE-bench (arXiv:2310.06770)](https://arxiv.org/abs/2310.06770)
- [WebArena (arXiv:2307.13854)](https://arxiv.org/abs/2307.13854)
- [OSWorld (arXiv:2404.07972)](https://arxiv.org/abs/2404.07972)
- [Terminal-Bench](https://github.com/laude-institute/terminal-bench)
- [Kozuchi Agent (arXiv:2608.15579)](https://arxiv.org/abs/2608.15579) —— 统计规范报告 benchmark 结果的近期示范，见 [[arxiv-2608-15579]]。
- [dspy-security-bench (Zenodo)](https://doi.org/10.5281/zenodo.22003465) —— 测量协议哈希冻结与结果稳定性判据的做法（自述来源，待核实），见 [[doi-org-10-5281-zenodo-22003465]]。

## 待验证问题

- 「人类任务时长」指标（METR 的 time-horizon 研究）的具体数值与本页转述是否准确，待核对原文。
- 各 agentic benchmark 的最新榜单数字刻意未写入本页，避免过期与编造；引用时需以官方榜单为准。

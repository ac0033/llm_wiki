---
title: "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?"
aliases: [SWE-bench, "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?"]
type: paper
status: draft
topics: [agent, benchmark, evaluation, software-engineering]
harness_components: [sandbox, verification, evaluation-harness]
published: 2023-10
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 1
quality: medium
confidence: high
canonical_url: https://arxiv.org/abs/2310.06770
---

# SWE-bench: Can Language Models Resolve Real-World GitHub Issues?

> Jimenez et al.（Princeton 等），2023-10（arXiv），ICLR 2024 接收。

## 一句话结论

SWE-bench 把「修真实 GitHub issue」变成可自动判分的任务——给模型一个仓库快照和 issue 描述，它产出的补丁必须通过问题对应的测试（FAIL_TO_PASS）且不破坏已有测试（PASS_TO_PASS）——成为软件工程 agent 事实上的标准考场。

## 论文解决了什么问题

此前的代码能力评测（如 HumanEval）用的是自包含的小函数题，与真实软件工程差距大，而且随着模型训练数据扩张，这些静态小题很快被「刷穿」。SWE-bench 要解决的是：构建一个**来自真实开发活动、靠测试自动判分、可持续扩充**的代码任务基准。任务直接取自流行 Python 仓库的真实 issue 及其修复 PR，模型要解决的是跨文件理解、定位、修改的完整工程问题，而不是补全一个函数。

## 关键机制

- **任务构造**：从 12 个流行 Python 开源仓库筛选「issue + 合并 PR」对，PR 必须同时包含代码修复和测试修改；测试改动用于自动判分。最终基准包含 2294 个任务实例。
- **测试即验证器**：判定分两类测试——FAIL_TO_PASS（在旧代码上失败、打上修复补丁后应通过，证明问题被解决）和 PASS_TO_PASS（原本通过的测试不能回归）。整个判分在容器化环境里执行，无需人工。
- **输入设定**：模型拿到 issue 文本和仓库代码；由于上下文窗口限制，论文基线采用检索（如 BM25）或直接给定位文件的方式注入上下文。
- **原始结果**：论文报告当时最好的系统只能解决个位数百分比的任务（确切数字待核对原文），显示任务难度远超已有代码基准。

## 对 Agent Harness 的启示

SWE-bench 对整个 agent 工程的影响怎么强调都不为过：

- **「测试即 [[verification-governance]]」成为软件 agent 的标准闭环**：确定性、可自动执行、难作弊的验证信号，是 SWE 类 harness 能成立的前提。harness 的核心职责之一就是构建和维护这个执行判分环境（容器、依赖安装、测试运行）。
- **它测的是 harness 而不只是模型**：同样底座模型，配上不同脚手架（[[swe-agent]] 的 ACI 接口、[[openhands]] 等），解决率差异巨大。SWE-bench 排行榜事实上是「模型 × harness」组合的排行榜，这正是 [[ai-agents-that-matter]] 强调要区分的两个贡献来源。
- **上下文注入策略成为关键变量**：仓库太大放不进上下文，检索质量、编辑工具设计（查看/编辑/运行命令的动作空间）直接决定表现——推动了 [[context-manager]] 和代码编辑工具接口的大量工程创新。
- **可持续构造的流水线**：从 GitHub 活动自动挖掘新任务，对抗数据污染；后续衍生出 SWE-bench Verified（OpenAI 人工筛过的 500 题子集）、Multimodal、Multilingual 等扩展。

## 局限与后续工作

- **判分噪声**：部分实例的 FAIL_TO_PASS 测试可能过松（改歪了也能过）或过严（正确修复但不触发指定测试），Verified 子集即为此做人工清洗；[[ai-agents-that-matter]] 和后续工作都讨论过基准被过拟合/投机（如针对测试写 hack 补丁）的问题。
- 仅限 Python、单 issue-PR 粒度，覆盖不了大型特性开发、跨仓库改动。
- 只以「测试通过」计分，不衡量补丁质量、可维护性、成本与时长。
- 仓库快照固定在历史时间点，与当前生态脱节随时间加剧。

## 相关页面

- [[swe-agent]]：为 SWE-bench 设计的代表性 harness
- [[openhands]]：通用 SWE agent 平台
- [[agent-evaluation]]：基准方法论
- [[ai-agents-that-matter]]：对基准过拟合与成本核算的批判
- [[sandboxed-execution]]：判分执行环境
- [[verification-governance]]：测试作为验证器

## 来源

- arXiv 摘要页：https://arxiv.org/abs/2310.06770

## 待验证问题

- 原始论文各基线的确切解决率（本文只定性描述为个位数百分比，补录时核对原文数字）。
- 12 个仓库的完整名单。

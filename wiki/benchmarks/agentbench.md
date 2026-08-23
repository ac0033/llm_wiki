---
type: benchmark
title: AgentBench
status: draft
topics:
- benchmark
- multi-environment
- llm-agent
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 2
quality: medium
confidence: medium
canonical_url: https://arxiv.org/abs/2308.03688
evidence_sources:
- https://arxiv.org/abs/2308.03688
- https://github.com/THUDM/AgentBench
---
# AgentBench

AgentBench 是清华 THUDM 团队提出的多环境 Agent 基准（论文页见 [[agentbench-paper]]，arXiv:2308.03688），定位是"把 LLM 当 Agent 来系统评测"：不只评单一场景，而是用八个差异很大的环境组成一个测试矩阵，考察模型作为 Agent 的通用能力。

## 评什么

评的是模型在多样化交互场景下的 Agent 基本功：多轮决策、工具调用、在部分可观测环境里探索。论文的一个核心结论是开源模型与商业模型在 Agent 能力上的差距远大于在传统 NLP 基准上的差距——它本质上是"以模型为评估对象"的基准，Harness 被刻意简化。

## 环境

八个环境分三组（归类以论文为准）：

- 代码类：OS（在 Linux 命令行里完成任务）、Database（SQL 操作数据库）、Knowledge Graph（知识图谱问答）。
- 游戏类：Digital Card Game（卡牌对战）、Lateral Thinking Puzzles（情景猜谜）。
- Web 类：Web Shopping（模拟电商购物）、Web Browsing（网页浏览问答）、Household（虚拟家居环境，ALFWorld 风格）。

各环境以 Docker 服务方式提供，Agent 通过 HTTP 接口交互，便于统一接入。

## 指标

每个环境有自己的成功率/得分指标，汇总为加权总分（具体权重见论文）。不引用具体分数。

## 对 Harness 评估的启示

- AgentBench 的 Harness 极简（固定 prompt 模板、固定交互协议），所以它主要回答的是"模型本身行不行"，不是"Harness 设计得好不好"。用它比较两个 [[agent-harness]] 是不对口的——这是 [[harness-vs-model-evaluation]] 里"评估对象对齐"的反面教材。
- 它的多环境矩阵思路对 Harness 评估有借鉴意义：一个 Harness 只在单一环境（如 [[swe-bench]] 的代码仓库）里验证过，泛化性存疑；多环境组合能暴露 Harness 的过拟合。
- 环境通过 HTTP 服务化，是"环境即服务"的早期范例，后来的 [[webarena]]、[[appworld]] 都沿用了类似思路。

## 待验证 / 边界

- 部分环境基于已有数据集改造（如 ALFWorld、Mind2Web 风格数据），新颖性集中在"组合与统一协议"。
- 榜单活跃度与维护状态待验证，引用排名前先确认时效。

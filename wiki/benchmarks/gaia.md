---
type: benchmark
title: GAIA
status: draft
topics:
- benchmark
- general-assistant
- tool-use
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 2
quality: medium
confidence: medium
canonical_url: https://arxiv.org/abs/2311.12983
evidence_sources:
- https://arxiv.org/abs/2311.12983
- https://huggingface.co/datasets/gaia-benchmark/GAIA
---
# GAIA

GAIA（General AI Assistants）是 Meta、HuggingFace、AutoGPT 等团队联合提出的通用 AI 助理基准（论文 arXiv:2311.12983）：一批"对人简单、对 AI 难"的问题，回答它们需要推理、多模态理解、网页浏览和工具链组合。题目按所需能力分三个难度等级。

## 评什么

评通用助理的端到端问答正确性：每题有一个短小、无歧义的标准答案（人答得又快又准，当时的 AI 系统表现差很多——论文以此立论）。能力侧重点是组合性：找信息、跨模态处理附件、算一步、再推理一步。

## 环境

- 不是固定仿真环境，而是"开放的现实世界"：题目常要求查真实网页、读附件（图片、表格、压缩包等），Agent 需要自己决定用什么工具、查什么。
- 这也带来已知问题：真实网页会变化、消失，部分题目的可复现性随时间下降。
- 数据集分公开验证集（带答案）和隐藏测试集（提交到 HuggingFace 排行榜评分），防过拟合设计。

## 指标

完全匹配式正确率，按 Level 1/2/3 分层报告。不引用具体分数。

## 对 Harness 评估的启示

- GAIA 不规定环境接口，等于把"工具栈怎么搭"整个留给 Harness：浏览器、代码解释器、文件解析器配不配、怎么配，都是 Harness 决策。所以 GAIA 分数高度反映 [[agent-harness]] 的工具完备度，而非纯模型推理力。
- 因为答案可精确判定，它是少有的"便宜又硬"的通用能力信号，适合在 Harness 迭代中做回归测试。
- 但网页漂移意味着：两次评测之间的分数变化可能来自世界变了，而不是系统变了。做 [[harness-vs-model-evaluation]] 式对照实验时，GAIA 的时间稳定性不如 [[swe-bench]]、[[appworld]] 这类快照环境。

## 待验证 / 边界

- 排行榜由社区自报成绩，评测用的工具栈差异极大（含人工辅助嫌疑需甄别），横向比较先看方法描述。
- Level 划分标准见论文；题目总数本页不写死。

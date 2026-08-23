---
type: overview
title: AI Agent 知识库总览
aliases: ["overview", "总览", "AI Agent Wiki"]
status: draft
topics: [agent, harness, knowledge-base, map-of-content]
harness_components: [observation-interface, context-manager, control-loop, action-interface, state-artifact-store, verification-governance]
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 6
quality: medium
confidence: medium
canonical_url: https://arxiv.org/abs/2606.20683
evidence_sources:
  - https://arxiv.org/abs/2606.20683
  - https://github.com/ggjy/Awesome-Agent-Engineering
  - https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
  - https://github.com/ZJU-REAL/Polaris
  - https://github.com/Jiaaqiliu/Awesome-Harness-Engineering
  - https://arxiv.org/abs/2507.21504
---

## 一句话结论

这个知识库以「Agent = 基座模型 + 执行壳（Harness）」为主线索组织 AI Agent 领域的文献与概念，其中 Harness 被分解为六个相互耦合的运行时组件：[[observation-interface]]、[[context-manager]]、[[control-loop]]、[[action-interface]]、[[state-artifact-store]]、[[verification-governance]]。

## 关键机制

知识库的组织方式借用了 Karpathy 提出的 LLM Wiki 模式：LLM 把原始材料（论文、博客、工程报告）读一遍，沉淀成持久化、互相链接的 Markdown 页面，而不是每次提问都重新检索原始材料。换句话说，Obsidian 是 IDE，LLM 是维护者，wiki 是不断复利的「代码库」。

核心分析框架来自 arXiv:2606.20683 这篇综述，它提出：

1. 实现视角下，LLM-based agent 不是单独的基座模型，而是「模型 + Harness」的耦合系统，形式化写作 `A = ⟨M, H⟩`。
2. Harness（执行壳）是包裹模型的运行时基础设施，负责六个职责：观察、上下文、控制、动作、状态、验证与治理。
3. Agent 工程经历了四个范式阶段：Prompt Engineering → Workflows & Context Engineering → Harness Engineering → Agent-Native Training 与模型-壳协同进化（co-evolution）。后一阶段不取代前一阶段，而是叠加。
4. Agent 的性能是「模型能力 × Harness 设计 × 任务结构 × 评估设计」交互的产物，而不是模型单方面的属性。

## 适用场景

- 调研某个具体概念（如 [[agent-memory]]、[[tool-use]]）时，从 `wiki/concepts/` 下的单页入手，顺着 wikilinks 扩展。
- 做技术选型或写综述时，从方向页 [[ai-agent-harness]] 入手，看该方向的现状、争议和待验证问题。
- 查 benchmark 或系统（如 [[swe-bench]]、[[openhands]]、[[react]]）时，对应页面在其他分块中维护，本页只做导航。

## 局限与失败模式

- 本知识库处于早期草稿状态，多数页面 `status: draft`，内容以一篇主综述 + 少量一手来源为骨架，覆盖面不完整。
- 六组件分解是一种「实现视角」的建模工具，不同文献的术语划分并不完全一致（例如有的把 memory 单列为组件），跨文献对比时需要注意术语对齐。
- 当前核心链接目标已经创建；后续新增页面或改名时，由 `lint_wiki.py` 负责发现坏链和孤儿页。

## 与其他页面的关系

- 方向页：[[ai-agent-harness]] 是本知识库当前唯一的研究方向页。
- 六组件概念页：[[observation-interface]]、[[context-manager]]、[[control-loop]]、[[action-interface]]、[[state-artifact-store]]、[[verification-governance]]。
- 横向主题页：[[context-engineering]]、[[agent-memory]]、[[tool-use]]、[[agent-evaluation]]、[[agent-observability]]、[[sandboxed-execution]]、[[model-context-protocol]]、[[multi-agent-orchestration]]。
- 顶层入口：[[agent-harness]] 是整个框架的核心概念页。

## 来源

- [From Question Answering to Task Completion: A Survey on Agent System and Harness Design (arXiv:2606.20683)](https://arxiv.org/abs/2606.20683) —— 六组件分解与四范式框架的主来源。
- [Awesome-Agent-Engineering](https://github.com/ggjy/Awesome-Agent-Engineering) —— 该综述配套的论文清单。
- [Karpathy: LLM Wiki 模式（GitHub gist）](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) —— 知识库组织方式的灵感来源。
- [Polaris](https://github.com/ZJU-REAL/Polaris) —— 文献抓取、去重、评分、wiki 编译与人类审核门的工作流参考。
- [awesome-harness-engineering](https://github.com/Jiaaqiliu/Awesome-Harness-Engineering) —— Harness 工程实践资源清单（工具、模式、评估、记忆、MCP、权限、可观测性、编排）。
- [Evaluation and Benchmarking of LLM Agents: A Survey (arXiv:2507.21504)](https://arxiv.org/abs/2507.21504) —— 评估方法的主要参考之一。

## 待验证问题

- 四范式划分的时间线与代表性工作在社区内是否已有共识，还是仅为该综述一家之言，需要对照其他 2026 年的 harness 综述（如 Meng et al. 六元组、Li et al. 七层 ETCLOVG）交叉验证。
- Karpathy LLM Wiki gist 的原文细节（如目录结构约定）尚未逐条核对，本库当前的目录约定是否与其一致待验证。

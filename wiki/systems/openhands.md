---
type: system
title: OpenHands
status: draft
topics:
- agent-harness
- coding-agent
- open-source
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 3
quality: medium
confidence: medium
canonical_url: https://github.com/All-Hands-AI/OpenHands
evidence_sources:
- https://github.com/All-Hands-AI/OpenHands
- https://arxiv.org/abs/2407.16741
- https://docs.all-hands.dev/
---
# OpenHands

OpenHands（原名 OpenDevin）是 All-Hands-AI 维护的开源软件开发 Agent 平台，也是研究 [[agent-harness]] 时最常被引用的参照实现之一。它的定位不是"一个 Agent"，而是一整套让 LLM 在沙箱里像开发者一样工作的运行时：接收自然语言任务，循环执行动作（写代码、跑命令、浏览网页），直到任务完成。官方论文以 "OpenHands: An Open Platform for AI Software Developers as Generalist Agents" 发表（arXiv:2407.16741）。

## 按六组件拆解 Harness

### 1. 推理循环（Agent Loop）

OpenHands 的核心抽象是 **event stream（事件流）**：Agent 与环境的一切交互都被建模为 `Action` 和 `Observation` 两类事件，依次追加到一个共享事件流中。默认的 CodeActAgent 采用 [[react]] 风格的交替循环——模型输出一个动作（如执行 bash、编辑文件），运行时把执行结果作为观察追加回事件流，再触发下一轮推理。这个设计把"Agent 做了什么"变成一条可回放、可审计的日志，是 Harness 工程里很值得借鉴的一点。

### 2. 上下文管理（Context Manager）

每一步推理时，Harness 需要把事件流压缩、裁剪成模型上下文窗口能装下的 prompt。OpenHands 实现了事件截断与摘要等策略（具体策略随版本演进，细节待验证），并支持 [[context-manager]] 角色的插件化替换。对长任务而言，这一层往往比模型本身更影响成功率。

### 3. 工具与动作空间（Tools / Action Space）

动作空间以 **CodeAct** 思想组织：让模型直接写可执行代码（bash 命令、Python 代码）作为动作，而不是定义大量细粒度工具函数。内置动作包括 `CmdRunAction`（执行 shell）、`IPythonRunCellAction`（Jupyter 执行）、文件编辑动作和 `BrowseURLAction`（网页浏览）。文件编辑经历过基于字符串替换与自定义编辑格式的多次迭代，具体实现以仓库为准。

### 4. 执行环境（Runtime / Sandbox）

所有动作都在 Docker 沙箱运行时中执行，Agent 进程与运行时通过 API 通信。沙箱内预装了 bash、Python、Jupyter 服务器和浏览器环境，使 Agent 拥有接近真实开发者机器的能力面。运行时层是可替换的（本地 Docker、远程运行时等），这是 OpenHands 作为平台而非单一脚本的关键设计。

### 5. 规划与编排（Orchestration）

OpenHands 以单 Agent 为主，但支持多 Agent 委派：一个 Agent 可以把子任务交给另一个专门 Agent（如浏览子任务委派给 BrowsingAgent）。也存在 Planner/Executor 之类的实验性结构。整体编排哲学偏"通用 Agent + 委派"，而不是 [[metagpt]] 那种固定角色流水线。

### 6. 状态与持久化（State / Persistence）

会话状态以事件流为准：整个会话可以序列化保存、恢复和回放，评测时也能据此重放轨迹做分析。仓库状态（代码变更）则落在沙箱文件系统与 git 中。

## 与评测的关系

OpenHands 团队长期用 [[swe-bench]]（尤其 SWE-bench Verified）作为主要评测基准，并维护官方评测基础设施（evaluation harness 目录）。它也经常出现在 [[terminal-bench]]、[[gaia]] 等榜单上，是研究"Harness 固定、只换模型"实验的常见载体——参见 [[harness-vs-model-evaluation]]。

## 待验证 / 边界

- 上下文压缩的具体策略、默认 max_iterations 等参数随版本变化较快，本文不写死数值，使用时应以当前版本代码与文档为准。
- 星标数、SWE-bench 分数不引用，避免过时或失实。

---
type: system
title: MetaGPT
status: draft
topics:
- agent-framework
- multi-agent
- sop
- open-source
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 2
quality: medium
confidence: medium
canonical_url: https://github.com/FoundationAgents/MetaGPT
evidence_sources:
- https://github.com/FoundationAgents/MetaGPT
- https://arxiv.org/abs/2308.00352
---
# MetaGPT

MetaGPT 是多智能体框架，口号是 "The Multi-Agent Framework: First AI Software Company"。仓库已从个人账号（geekan/MetaGPT）迁移至 FoundationAgents 组织。核心思想（论文 arXiv:2308.00352）：**把人类软件公司的标准操作流程（SOP）编码进多智能体协作**——产品经理、架构师、项目经理、工程师、测试工程师等角色各守其职，用结构化的中间产物（需求文档、系统设计、任务拆解、代码）而不是自由对话来交接工作。论文里常被引用的一句话是 "Code = SOP(Team)"，即把 SOP 当作编排逻辑本身。

## 按六组件拆解 Harness

### 1. 推理循环（Agent Loop）

双层结构：每个角色（Role）内部是"观察 → 思考 → 行动"（`_observe` → `_think` → `_act`）的循环，一次 `_act` 执行一个结构化 Action（如 WritePRD、WriteCode）；外层则是角色按 SOP 流水线的顺序依次激活。与 [[react]] 式自由循环相比，这里的循环被 SOP 强约束，模型在每步的自由度更小。

### 2. 上下文管理（Context Manager）

上下文管理靠的是**结构化文档交接**：上游角色产出 PRD、系统设计等文档，下游角色只订阅与自己相关的消息/产物，而不是共享全部对话历史。框架内有共享消息池（environment 内的 publish/subscribe 机制），角色按兴趣订阅。这是一种"用信息架构控上下文"的思路，与 [[swe-agent]] 的接口层裁剪、[[langgraph]] 的 state reducer 都不同。参见 [[context-manager]]。

### 3. 工具与动作空间（Tools / Action Space）

动作空间是一组预定义的结构化 Action（写 PRD、写设计、写代码、写测试、评审等），每个 Action 有明确的输出 schema（通常是 Markdown 文档或代码文件）。工具侧还提供检索、搜索等能力扩展。颗粒度比 bash 命令粗得多——一个 Action 往往是一整个工程产物的生成。

### 4. 执行环境（Runtime / Sandbox）

生成的代码可以在本地或隔离环境中运行以做验证（具体执行器能力随版本演进，待验证），但 MetaGPT 的重心不在交互式环境探索，而在"按流程把活干完"。它不是为 [[swe-bench]] 那种"在现有仓库里调试修复"的场景设计的，而是面向从零生成项目的场景。

### 5. 规划与编排（Orchestration）

编排即 SOP：角色链路、产出物契约、交接顺序在配置中显式定义，本质是一条可定制的流水线。与 [[autogen]] 的对话涌现、[[langgraph]] 的通用图相比，MetaGPT 的编排最"硬"——灵活度低，但对软件生产这类流程成熟的领域，硬编排换来了可控性和可复现性。

### 6. 状态与持久化（State / Persistence）

中间产物以文件形式落地（docs、代码），运行状态可序列化恢复（具体机制随版本，待验证）。产物即状态的一部分，这让"中断后继续"自然成立。

## 与评测的关系

MetaGPT 论文主要用 HumanEval/MBPP 风格的小任务与软件生成质量指标做评估（具体分数不引用）。它的设计场景（从零生成软件）与多数交互式 Agent 基准（[[swe-bench]]、[[webarena]]）不完全对口——用后者评它，很大程度上评的是"场景错配"，这个教训直接对应 [[harness-vs-model-evaluation]] 里"评估对象要先对齐"的论点。

## 待验证 / 边界

- 迁移到 FoundationAgents 组织后，仓库的路线图与旧版教程可能有出入，以当前 README 为准。
- 角色、Action 的具体清单随版本演进，本文只列代表性例子。

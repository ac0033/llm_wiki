---
type: system
title: SWE-agent
status: draft
topics:
- agent-harness
- coding-agent
- swe-bench
- open-source
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 3
quality: medium
confidence: medium
canonical_url: https://github.com/SWE-agent/SWE-agent
evidence_sources:
- https://github.com/SWE-agent/SWE-agent
- https://arxiv.org/abs/2405.15793
- https://swe-agent.com/latest/
---
# SWE-agent

SWE-agent 是普林斯顿大学团队（John Yang、Carlos Jimenez 等）开发的 Agent 系统，论文 "SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering"（[[arxiv-2405-15793]]，arXiv:2405.15793）。它最出名的身份是 [[swe-bench]] 上最早的一批高分系统，但它对 [[agent-harness]] 研究的真正贡献是一个明确的概念：**ACI（Agent-Computer Interface，智能体-计算机接口）**——正如 HCI 研究人机接口，为 LLM 设计的命令、反馈格式和防护栏会显著影响 Agent 表现，这部分设计和模型能力是两回事，需要单独优化。

## 按六组件拆解 Harness

### 1. 推理循环（Agent Loop）

经典 [[react]] 式单循环：模型每步输出"思考 + 一个动作"，环境执行后返回观察，如此往复直到提交。SWE-agent 刻意保持循环简单，把复杂度压到 ACI 层。新版实现把这一循环做成可配置组件，循环逻辑与环境、工具解耦。

### 2. 上下文管理（Context Manager）

核心策略是 **控制观察的体量与形态**：命令输出超长时截断并提示"已省略 N 行"，文件查看器强制按窗口分页展示，避免一次把大文件灌进上下文。这是一种"接口层"的上下文管理——不是靠摘要模型，而是靠工具本身不产出爆炸性输出。与 [[openhands]] 的事件流压缩形成两种不同思路，参见 [[context-manager]]。

### 3. 工具与动作空间（Tools / Action Space）

这是 SWE-agent 的精华所在。它提供一套专为 LLM 设计的 shell 风格命令，例如带行号窗口的 `view`、`scroll_down` 等文件浏览命令，以及 lint 守卫的文件编辑命令：如果编辑引入语法错误，编辑会被直接拒绝并反馈原因。论文中的消融实验表明，这些 ACI 细节（窗口式查看器、编辑守卫）对解决率影响显著。动作一次一个、格式严格，模型输出不合规时会被打回重试。

### 4. 执行环境（Runtime / Sandbox）

Agent 在容器化环境（Docker）中对目标仓库执行 bash 命令，与评测用的任务环境基本同构。环境初始化包含检出指定 commit、安装依赖等步骤。新版支持多种部署后端，细节待验证。

### 5. 规划与编排（Orchestration）

以单 Agent 为主，没有多角色编排。重点放在"给单个 Agent 配好接口"而不是"组织多个 Agent"。这与 [[metagpt]]、[[autogen]] 的多智能体路线形成鲜明对照。

### 6. 状态与持久化（State / Persistence）

每次运行生成完整 trajectory（轨迹）文件，记录全部 thought/action/observation，供离线分析与论文消融使用。状态管理哲学是"轨迹即产物"。

## 与评测的关系

SWE-agent 与 [[swe-bench]] 同出一门，常被批评者与拥护者同时拿来说明"基准与 Harness 共同演化"的问题：它的 ACI 是围绕 SWE-bench 任务打磨的，泛化到其他基准（如 [[terminal-bench]]）时表现如何，是评估 Harness 通用性的好问题。参见 [[harness-vs-model-evaluation]]、[[agent-framework-harness-comparison]]。

## 待验证 / 边界

- 新版 SWE-agent 的模块化配置体系（tools、parsers、hooks 的 YAML 组合）仍在快速演进，具体字段以官方文档为准。
- 不引用具体 SWE-bench 分数，分数随模型与版本变化，以官方榜单为准。

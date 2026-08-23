---
title: "AgentBench: Evaluating LLMs as Agents"
aliases: [AgentBench, "AgentBench: Evaluating LLMs as Agents"]
type: paper
status: draft
topics: [agent, benchmark, evaluation]
harness_components: [evaluation-harness, sandbox, observation-loop]
published: 2023-08
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 1
quality: medium
confidence: high
canonical_url: https://arxiv.org/abs/2308.03688
---

# AgentBench: Evaluating LLMs as Agents

> Liu et al.（THUDM / 智谱），2023-08（arXiv），ICLR 2024 接收。

## 一句话结论

AgentBench 把 8 个风格迥异的多轮交互环境（操作系统、数据库、知识图谱、卡牌游戏、横向思维谜题、家务、网购、网页浏览）统一到一套接口下，对 20 多个 LLM 做了系统对比，是「把 LLM 当 agent 来评」的早期系统性基准。

## 论文解决了什么问题

2023 年年中时，各种 LLM 排行榜评的都是单轮能力（MMLU、HumanEval 等），但「当 agent 用」需要多轮决策、部分可观测、环境反馈下的长程表现，缺少横向可比的基准。AgentBench 要解决的问题有两个：一是给「LLM as Agent」建一个多维度的统一考场，二是回答当时最关心的问题——开源模型和商业模型在 agent 能力上到底差多少。

## 关键机制

- **8 个环境，统一接口**：分为三类——代码类（OS、Database、Knowledge Graph）、游戏类（Digital Card Game、Lateral Thinking Puzzles）、网页类（Householding、Web Shopping、Web Browsing）。所有环境封装成「观察 → 动作 → 反馈」的多轮交互协议，模型侧只面对统一的对话格式。
- **Docker 化的环境分发**：环境以容器方式部署，评测框架负责拉起环境、转发模型输出、回收结果——即一套完整的**评测 harness**。
- **大规模横向评测**：论文评测了 25 个左右的 API 模型与开源模型（具体数量待核对），统一打分。

核心结论（性质层面）：顶尖商业模型（当时为 GPT-4）与开源模型在 agent 任务上存在显著差距；常见失败模式包括长程推理退化、格式不符、陷入重复动作等。

## 对 Agent Harness 的启示

AgentBench 本身是 harness 思维在评测侧的落地：

- **环境抽象层**：8 个环境能被同一框架驱动，靠的是把「环境」抽象为标准的观察/动作协议。这直接对应 [[agent-harness]] 里环境适配层的职责——工具/环境各异，harness 提供统一视图。
- **评测 harness 与运行 harness 共享组件**：容器沙箱、超时控制、轨迹记录、动作解析，既是评测基建也是生产 agent 的基建（见 [[agent-system-harness-design-survey]] 对 observation/action 职责的分解）。
- **失败模式的归因启示评测指标设计**：格式错误、重复循环这类失败其实是 harness 可以缓解的（解析兜底、循环检测），这提醒评测者区分「模型不行」和「harness 没兜住」——后来 [[ai-agents-that-matter]] 把这一区分（模型贡献 vs 脚手架贡献）正式化。
- **多维基准的必要性**：单一环境上的 agent 分数不代表通用 agent 能力，这推动了后来评测向多环境、持续更新方向发展（见 [[survey-evaluation-llm-agents]] 的趋势总结）。

## 局限与后续工作

- 静态基准：任务集固定，随模型训练数据扩张存在污染与过拟合风险；后续社区转向持续刷新的基准（如 SWE-bench 家族的 Verified/Multimodal 扩展、[[swe-bench]]）。
- 环境以文本交互为主，未覆盖图形界面、真实软件等更复杂的观测形态。
- 只评最终成功率，成本、时延、安全性不在计分内。
- 部分环境规模较小，统计意义有限（如卡牌、谜题类任务量不大，待核对原文）。

## 相关页面

- [[agent-evaluation]]：agent 评测总览
- [[swe-bench]]：面向真实软件工程任务的后续基准
- [[ai-agents-that-matter]]：对这一类基准方法论的批判与改进建议
- [[survey-evaluation-llm-agents]]：agent 评测综述
- [[agent-harness]]：评测 harness 与运行 harness 的关系

## 来源

- arXiv 摘要页：https://arxiv.org/abs/2308.03688

## 待验证问题

- 被评模型的确切数量与完整名单（印象中约 25 个，待核对原文）。
- 各环境任务的确切样本量。

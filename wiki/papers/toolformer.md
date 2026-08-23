---
title: "Toolformer: Language Models Can Teach Themselves to Use Tools"
aliases: [Toolformer, "Toolformer: Language Models Can Teach Themselves to Use Tools"]
type: paper
status: draft
topics: [agent, tool-use, self-supervised-learning]
harness_components: [tool-use, training-data-pipeline]
published: 2023-02
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 1
quality: medium
confidence: high
canonical_url: https://arxiv.org/abs/2302.04761
---

# Toolformer: Language Models Can Teach Themselves to Use Tools

> Schick et al.（Meta AI），2023-02（arXiv），NeurIPS 2023 接收。

## 一句话结论

让模型自己采样 API 调用、执行、再用「插入这次调用是否降低了后续文本的困惑度」来自动过滤，得到自标注的工具调用数据后微调，模型便能在生成文本时自主决定何时、以什么参数调用工具。

## 论文解决了什么问题

此前的工具使用要么靠大规模人工标注示范，要么靠针对单一工具的专门微调，难以扩展。Toolformer 要回答的是：能否只用少量人工示例，让模型自己生产大量带工具调用标注的训练数据，并且以自监督的方式筛掉无用调用——即把「学会用工具」变成一个不需要人工标注的训练流程。

## 关键机制

数据生产分三步，针对每种工具（API）独立进行：

1. **采样**：用 few-shot prompt 让模型在普通文本语料的任意位置提议插入 API 调用（形如 `[QA("...")]`）。
2. **执行**：真正调用 API 拿到返回结果。
3. **过滤**：比较插入「调用 + 结果」前后模型对后续 token 的损失，只有当这次插入显著降低损失（即对预测后续内容有帮助）时才保留该样本。

最后用过滤后的数据微调模型（实验基于 GPT-J 6.7B）。论文覆盖的工具包括：计算器、问答系统、维基百科搜索、机器翻译、日历。

## 对 Agent Harness 的启示

Toolformer 代表了一条与「harness 编排」相反的路线：**把工具调用决策学进模型权重**。对 harness 设计的影响在于划清了两层职责：

- **决策可以内化，执行永远在外**。即使模型学会了何时调计算器，真正执行调用、注入结果的仍然是外部系统——Toolformer 推理时同样需要 harness 拦截 API 调用标记、执行、回填。这印证了一个分界：模型负责 when/what，harness 负责 how（执行、鉴权、超时、重试、结果注入）。
- **「损失下降」作为数据过滤器是个可复用的思想**：harness 层做工具调用的日志分析时，可以用类似标准衡量一次调用是否真的推进了任务，为 [[agent-evaluation]] 和训练数据筛选提供信号。
- **与现代 tool calling 的关系**：Toolformer 的自监督数据生产流程，可以看作后来「用合成数据训练原生 tool calling 能力」的先声；如今工具决策主要在模型权重里，harness 的重心相应转向 [[verification-governance]]、权限控制与观测回写（见 [[agent-system-harness-design-survey]] 对 harness 六职责的分解）。

## 局限与后续工作

- 工具间相互独立训练，模型不会组合使用多个工具、也不会多步链式调用——这正是后来 ReAct 式多步编排和原生 tool calling 模型补上的能力。
- API 调用被当作单次文本插入处理，没有状态、没有多轮交互，距离真正的 agent 循环（[[react]]）还远。
- 过滤标准（困惑度下降）只保证调用对语言建模「有用」，不保证对下游任务正确。
- 可扩展性受限：每加一种新工具都要重走一遍采样-过滤-微调流程。

## 相关页面

- [[tool-use]]：工具调用能力在模型与 harness 之间的分工
- [[react]]：对照路线——不训练权重、由 harness 编排的多步工具循环
- [[agent-system-harness-design-survey]]：模型能力与运行时基建的分工框架
- [[agent-evaluation]]：工具调用质量评估

## 来源

- arXiv 摘要页：https://arxiv.org/abs/2302.04761

## 待验证问题

- 论文报告的具体下游任务提升数字（如数学、问答子集上的准确率），本文未引用，补录时核对原文。
- 每种工具保留样本量的确切统计（采样多少、过滤后剩多少）。

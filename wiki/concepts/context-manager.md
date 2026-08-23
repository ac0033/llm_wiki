---
type: concept
title: Context Manager（上下文管理器）
aliases: ["context manager", "上下文管理器", "上下文组装"]
status: draft
topics: [agent, harness, context, memory, retrieval]
harness_components: [context-manager]
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 4
quality: high
confidence: high
canonical_url: https://arxiv.org/abs/2606.20683
evidence_sources:
  - https://arxiv.org/abs/2606.20683
  - https://arxiv.org/abs/2507.13334
  - https://arxiv.org/abs/2005.11401
  - https://github.com/Jiaaqiliu/Awesome-Harness-Engineering
---

## 一句话结论

Context Manager 决定什么信息、在什么时刻、以什么形式进入模型的上下文窗口——包括 prompt 构造、系统指令、检索、记忆选择、压缩、摘要、工具描述和当前任务状态——它把「上下文」从一段静态 prompt 变成一个随执行动态组装的运行时对象。

## 关键机制

在 [[agent-harness]] 的六组件中，上下文管理器是 [[context-engineering]] 这一工程学科在运行时的落点。综述把上下文形式化为组装函数 `C = A(c1, c2, …, cn)`，其中 ci 是指令、检索知识、工具描述与输出、记忆记录、任务状态、中间工件、当前查询等组件，工程目标是优化「检索、选择、压缩、格式化、刷新」这些函数本身，而不是优化单条指令的措辞。

典型机制：

1. **信息注入（injection）。** RAG（arXiv:2005.11401 为奠基工作之一）把非参数化知识引入上下文；后续工作（层次化摘要、图检索等）把检索从平铺段落查找扩展为更复杂的流水线。
2. **压缩与摘要。** 长程执行中上下文必然超限，需要在保留任务关键信息的前提下压缩历史，压缩策略在有限预算下的取舍是研究热点。
3. **记忆选择。** 从 [[agent-memory]] 的长期存储中挑出与当前步骤相关的记录注入。
4. **工具描述管理。** 工具数量多时，全部描述塞进上下文既贵又干扰决策，需要按需加载（progressive disclosure，渐进式披露）。

## 适用场景

- 长程任务（仓库级代码修改、多步骤研究）中，上下文预算管理是成败关键，见 [[swe-bench]] 类任务。
- 多轮交互 agent 需要在对话历史、外部状态、用户偏好之间做选择。
- 多 agent 系统中，sub-agent 常被用作「上下文防火墙」：子任务在隔离上下文中执行，只把结论返回主上下文。

## 局限与失败模式

- **Context rot（上下文退化）。** 上下文越长，模型对其中信息的利用率越差，「中间遗忘（lost-in-the-middle）」是已知现象；具体退化曲线因模型而异，定量结论待验证。
- **压缩丢信息。** 摘要丢掉看似无关、实则关键的细节（如某个早期的约束条件），导致后期决策漂移。
- **检索错配。** 检索召回的内容与真实信息需求不符，或者注入了过期/错误记忆，反而误导模型。
- **本质是前馈的。** 综述指出：上下文工程优化每一步的输入，但本身不提供检测漂移、验证中间结果、从错误中恢复的结构性机制——那是 [[control-loop]] 和 [[verification-governance]] 的职责。

## 与其他页面的关系

- 所属框架：[[agent-harness]]；学科背景：[[context-engineering]]。
- 输入来自 [[observation-interface]] 和 [[agent-memory]]；输出交给模型，循环节奏由 [[control-loop]] 控制。
- 工具描述的注册与标准化与 [[tool-use]]、[[model-context-protocol]] 相关。
- 上下文中持久化内容的落盘依赖 [[state-artifact-store]]。

## 来源

- [From Question Answering to Task Completion (arXiv:2606.20683)](https://arxiv.org/abs/2606.20683) —— 组件定义与 `C = A(c1..cn)` 形式化。
- [A Survey of Context Engineering for Large Language Models (arXiv:2507.13334)](https://arxiv.org/abs/2507.13334) —— 上下文工程学科的系统性综述。
- [Retrieval-Augmented Generation (arXiv:2005.11401)](https://arxiv.org/abs/2005.11401) —— RAG 奠基论文。
- [awesome-harness-engineering](https://github.com/Jiaaqiliu/Awesome-Harness-Engineering) —— 收录上下文与记忆管理的工程实践。

## 待验证问题

- 各类压缩/摘要方法在不同任务族上的信息损失-收益权衡，缺乏统一基准的横向比较，待验证。
- 「渐进式披露（progressive skill/tool disclosure）」的实际收益在公开文献中多为工程经验，定量证据待补充。
- ContextBench、SWE Context Bench 等上下文基准的覆盖范围与代表性待逐篇核对。

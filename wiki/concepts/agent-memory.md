---
type: concept
title: Agent Memory（Agent 记忆）
aliases: ["agent memory", "agent 记忆", "长期记忆", "long-term memory"]
status: draft
topics: [agent, memory, context, state]
harness_components: [state-artifact-store, context-manager]
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 4
quality: high
confidence: high
canonical_url: https://arxiv.org/abs/2310.08560
evidence_sources:
  - https://arxiv.org/abs/2310.08560
  - https://arxiv.org/abs/2304.03442
  - https://arxiv.org/abs/2305.16291
  - https://arxiv.org/abs/2606.20683
---

## 一句话结论

Agent Memory 是让 agent 跨越单次上下文窗口保存和复用信息的机制集合——短期记忆靠对话历史与上下文，长期记忆靠外部存储加检索——在 harness 视角下，它不是一个独立组件，而是由 [[state-artifact-store]]（存）与 [[context-manager]]（取）共同实现的能力。

## 关键机制

LLM 本身没有持久记忆，上下文窗口是唯一「工作记忆」，因此记忆系统的本质是「存什么、怎么取、何时忘」。

代表性机制：

1. **分层内存管理。** MemGPT（arXiv:2310.08560）借鉴操作系统的内存分层思想：主上下文是「内存」，外部存储是「磁盘」，模型通过函数调用自主地在两层之间换入换出信息。
2. **情景记忆与反思。** Generative Agents（arXiv:2304.03442）用「观察-反思-检索」循环维护记忆流（memory stream），按相关性、新近性、重要性检索，支撑多天的拟人行为模拟。
3. **技能库。** Voyager（arXiv:2305.16291）把验证过的代码技能存入库中，后续任务检索复用——记忆的对象从「事实」扩展到「可执行程序」。
4. **写入路径与读取路径分离。** 写入（什么值得记、以什么粒度记）与读取（何时检索、注入多少）是两组独立的策略，多数系统重读取、轻写入。

## 适用场景

- 跨会话的个性化 agent（记住用户偏好、历史决策）。
- 长程项目型任务：跨天、跨会话的代码库理解与任务上下文。
- 经验复用：把成功/失败轨迹沉淀为可检索的经验或技能。

## 局限与失败模式

- **记忆投毒。** 错误或过时的记忆被写入后反复检索出来，持续误导决策；恶意内容还可通过记忆通道实现持久化注入。
- **检索错配。** 语义相似但情境不符的记忆被召回，agent 把「类似的经验」误用到「不同的任务」。
- **写入噪声。** 不加筛选地记录一切导致记忆库膨胀、检索质量退化；如何决定「值得记」仍无成熟标准。
- **隐私与合规。** 长期保存用户信息带来合规责任；遗忘请求（删除权）要求记忆系统支持精确定位删除。
- **评估不成熟。** 记忆系统的收益难以与上下文工程的其他部分分离归因，公认基准待建立。

## 与其他页面的关系

- 实现依赖：[[state-artifact-store]]（持久化）、[[context-manager]]（选择注入）。
- 所属子方向：[[agent-memory-context]]；代表文献：[[arxiv-2310-08560]]（MemGPT）、[[arxiv-2309-02427]]（CoALA）、[[arxiv-2502-12110]]（A-Mem）、[[arxiv-2404-13501]]（记忆机制综述）、[[arxiv-2307-03172]]（Lost in the Middle）、[[arxiv-2507-13334]]（Context Engineering 综述）。
- 学科背景：[[context-engineering]]；上位框架：[[agent-harness]]。
- 记忆内容的安全性受 [[verification-governance]] 约束。
- 相关系统：[[openhands]] 等 coding agent 中的仓库级记忆实践；[[react]] 轨迹是情景记忆的原始素材。

## 来源

- [MemGPT (arXiv:2310.08560)](https://arxiv.org/abs/2310.08560) —— 操作系统式分层记忆。
- [Generative Agents (arXiv:2304.03442)](https://arxiv.org/abs/2304.03442) —— 记忆流 + 反思机制。
- [Voyager (arXiv:2305.16291)](https://arxiv.org/abs/2305.16291) —— 技能库式记忆。
- [From Question Answering to Task Completion (arXiv:2606.20683)](https://arxiv.org/abs/2606.20683) —— 记忆在 harness 分解中的位置（功能操作到组件的多对多映射）。

## 待验证问题

- 记忆写入策略（记什么、什么粒度）的系统性比较研究较少，待补充。
- 「记忆即工具」（把记忆维护做成 agent 可调用的工具，如综述提到的 CAT 思路）相对后台自动记忆的优劣待验证。
- A-MEM、HippoRAG 等结构化记忆方法的结论待逐篇核对原文。

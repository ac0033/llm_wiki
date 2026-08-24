---
type: concept
title: Agent Harness（执行壳）
aliases: ["harness", "execution harness", "执行壳", "脚手架", "scaffold"]
status: draft
topics: [agent, harness, runtime, core-concept]
harness_components: [observation-interface, context-manager, control-loop, action-interface, state-artifact-store, verification-governance]
ingested: 2026-08-18
last_verified: 2026-08-21
source_count: 6
quality: high
confidence: high
canonical_url: https://arxiv.org/abs/2606.20683
evidence_sources:
  - https://arxiv.org/abs/2606.20683
  - https://arxiv.org/abs/2405.15793
  - https://arxiv.org/abs/2407.16741
  - https://arxiv.org/abs/2608.15579
  - https://github.com/Jiaaqiliu/Awesome-Harness-Engineering
  - https://github.com/ggjy/Awesome-Agent-Engineering
---

## 一句话结论

Agent Harness（执行壳）是包裹基座模型的运行时基础设施：它决定模型能看到什么、能做什么、状态存在哪里、错误如何被发现和恢复——在模型不变的情况下，Harness 设计本身就能显著改变 agent 的任务完成能力。

## 关键机制

功能视角下，agent 是一个目标驱动的闭环系统（感知、状态维护、推理决策、行动、反馈适应）。实现视角下，LLM-based agent 是模型与 Harness 的耦合系统，arXiv:2606.20683 将其形式化为：

```
A = ⟨M, H⟩ = ⟨M, I_obs, C, L, I_act, S, V⟩
```

其中 M 是模型层（可以是单个基座模型，也可以是多个异构模型的集合），H 即 Harness，展开为六个运行时组件：

1. [[observation-interface]]（I_obs）：把环境原始信号转成模型可用的观察。
2. [[context-manager]]（C）：决定什么信息、何时、以什么形式进入模型上下文。
3. [[control-loop]]（L）：编排「观察-推理-行动-反馈」循环，含停止条件、重试、反思、委派。
4. [[action-interface]]（I_act）：把模型输出映射为可执行操作。
5. [[state-artifact-store]]（S）：持久化执行状态与产物（历史、计划、检查点、轨迹、文件）。
6. [[verification-governance]]（V）：通过测试、断言、沙箱策略、权限门、回滚等机制检查、约束和修复执行。

两个要点：

- **这是操作性分解，不是静态清单。** 例如 memory 在功能视角里是「状态」，在部署系统里可能由上下文选择、工件存储、检索索引、检查点策略共同实现；功能操作到组件是多对多映射。
- **Harness 是独立的性能杠杆。** SWE-agent（[[arxiv-2405-15793]]，arXiv:2405.15793）固定基座模型、只重设计 agent-computer interface，就在 [[swe-bench]] 上取得明显提升，说明 harness 改动可以在不动模型的前提下改善 agent 表现。Kozuchi Agent（[[arxiv-2608-15579]]，arXiv:2608.15579）进一步给出工业级实证：本地托管的 27B 开放权重模型、零微调，仅靠阶段分解、模型无关动作契约、持久共享状态与跨 agent 测试时选择，在 SWE-bench Verified 官方评测器上解决 374/500——不过该论文自己也声明各机制只有运行特征证据，未做组件级消融。

## 适用场景

- 分析任何一个 agent 系统（coding、web、research、embodied）时，用六组件作为拆解模板：每类 agent 观察通道、动作空间、反馈信号、安全约束不同，对 harness 各组件的压力也不同。
- 定位 agent 故障时，先判断问题落在哪个组件：是看不到（观察）、没看到（上下文）、走偏了（控制）、做错了（动作）、忘了（状态）还是没拦住（验证）。
- 比较 [[openhands]]、Claude Code、Codex 等系统时，六组件是比「用了什么模型」更有区分度的比较维度。

## 局限与失败模式

- **与模型的归因纠缠。** Agent 表现是模型-harness 配对（pairing）的属性，单独声称「harness 带来 X% 提升」需要固定模型的对照实验支撑，这类证据仍少。
- **Harness 与模型能力的相互依赖。** 为弱模型设计的脚手架可能成为强模型的束缚；社区有「随着模型变强应移除 harness 假设」的讨论（见 awesome-harness-engineering 收录的 Anthropic 设计指南），具体哪些假设该何时移除待验证。
- **术语碎片化。** 「harness」「scaffold」「agent framework」「runtime」在文献中混用，边界不完全一致。

## 与其他页面的关系

- 所属方向：[[ai-agent-harness]]；知识库入口：[[overview]]。
- 六个子组件各有专页（见上）。
- 与 [[context-engineering]]：上下文工程是 Harness 中 [[context-manager]] 的深化，也是范式演进的第 2 阶段。
- 与 [[multi-agent-orchestration]]：多模型/多 agent 场景下，Harness 还要负责模型路由与角色分配，属于 [[control-loop]] 的扩展职责。
- 经典循环范式：[[react]] 是最早把「推理-行动」交替显式化的 prompting 框架，可视为 control loop 的最小实现。

## 来源

- [From Question Answering to Task Completion: A Survey on Agent System and Harness Design (arXiv:2606.20683)](https://arxiv.org/abs/2606.20683) —— 六组件形式化的直接来源。
- [SWE-agent (arXiv:2405.15793)](https://arxiv.org/abs/2405.15793) —— ACI 重设计提升 SWE-bench 成绩的实证。
- [OpenHands (arXiv:2407.16741)](https://arxiv.org/abs/2407.16741) —— 开源 agent 平台，可视为一种完整 harness 实现。
- [Kozuchi Agent (arXiv:2608.15579)](https://arxiv.org/abs/2608.15579) —— 开放权重修复 agent 的 harness 工程经验报告，见 [[arxiv-2608-15579]]。
- [awesome-harness-engineering](https://github.com/Jiaaqiliu/Awesome-Harness-Engineering) —— 工程实践资源清单。
- [Awesome-Agent-Engineering](https://github.com/ggjy/Awesome-Agent-Engineering) —— 综述配套论文清单。

## 待验证问题

- 「Harness engineering」术语的提出者归属（综述引用了 Hashimoto 与 OpenAI）需核对原始文献。
- 六组件与 Meng et al. 的六元组、Li et al. 的七层 ETCLOVG 分类法的对应关系待逐条比对。
- 工业界各系统（Claude Code、Codex、Devin、Manus）的 harness 架构细节多为非公开，公开描述与实现的一致性待验证。

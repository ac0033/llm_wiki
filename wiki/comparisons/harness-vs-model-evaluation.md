---
type: comparison
title: 模型评估与 Harness 评估的解耦
status: draft
topics:
- evaluation
- methodology
- agent-harness
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 3
quality: medium
confidence: medium
evidence_sources:
- https://arxiv.org/abs/2405.15793
- https://arxiv.org/abs/2310.06770
- https://www.tbench.ai/
---
# 模型评估与 Harness 评估的解耦

任何一个 Agent 基准分数，都是"模型 × [[agent-harness]] × 环境"三个因子的联合结果，而排行榜只给你一个数。这一页回答的问题是：如何把这三个因子拆开评，让每个因子各归各的账。

## 为什么必须解耦

- 同一个模型换 Harness，分数可以差出量级。[[swe-agent]] 论文（arXiv:2405.15793）的消融实验表明，光是文件查看器、编辑守卫这些 ACI（Agent-Computer Interface）细节的改变，就能显著改变 [[swe-bench]] 解决率——模型一行没换。
- 反过来，同一个 Harness 换模型，差异同样巨大。于是"系统 A 击败系统 B"这句话本身没有信息量，除非交代两边模型和 Harness 各是什么。
- 还有更隐蔽的第三因子：环境配置。[[swe-bench]] 的依赖安装、[[osworld]] 的虚拟机快照、[[webarena]] 的观察表示（accessibility tree 还是截图），都是环境侧变量，出问题时和"模型不行"在分数上无法区分。

## 解耦的实验设计

核心思路是控制变量，两个方向都要做：

1. **固定 Harness，扫模型。** 用同一个开源 Harness（如 [[openhands]]、[[swe-agent]]）接不同模型跑同一基准。所得排序回答"模型（在该 Harness 下）的 Agent 能力"。注意结论严格说只对该 Harness 成立——模型与 Harness 存在交互效应，A 模型配 A 厂自己的 Harness 可能另有表现。
2. **固定模型，扫 Harness。** 用同一个模型配不同 Harness 跑同一基准。所得排序回答"Harness 工程质量"。[[terminal-bench]] 排行榜天然就是这种"模型 × Harness"组合矩阵，是目前做这类对照最方便的公开资源。

配套纪律：

- **消融单组件。** 想归因到具体组件（[[context-manager]] 的压缩策略、工具集、重试机制），就一次只换一个组件做消融，而不是整体替换。
- **报告接口条件。** 观察空间、动作空间、步数上限、token 预算、环境版本，全部写进报告。缺了这些，分数不可复现也不可比较。
- **控制成本与步数。** Harness 可以通过"给模型更多步数/更多 token"换分数，比较时必须固定预算，否则比的是花钱能力。

## 拆不干净的地方

- **联合优化：** [[claude-code]] 这类厂商自家 Harness 与自家模型联合打磨，"模型能力"里有一部分只有在那个 Harness 里才兑现，拆开了两边都失真。此时更诚实的做法是把"模型+官方 Harness"当作一个整体产品来评，并明确标注。
- **基准与 Harness 共同演化：** [[swe-agent]] 的 ACI 就是围着 [[swe-bench]] 任务磨出来的，Harness 对基准过拟合后，"固定模型扫 Harness"测出的其实是过拟合程度。缓解办法是跨基准验证——在 [[swe-bench]] 上磨的 Harness，再去 [[terminal-bench]]、[[appworld]] 上跑一遍。
- **环境即变量：** [[gaia]] 依赖真实网页，世界本身在变，两次实验之间分数漂移可能来自环境而非任何一方。优先选快照化、可重置的基准（[[appworld]]、[[swe-bench]]、[[terminal-bench]]）做对照实验。

## 实践清单

评模型时：固定一个主流开源 Harness、固定预算、报全配置。评 Harness 时：固定模型（最好两个以上，防模型特异效应）、多基准交叉、做单组件消融。两种报告都应附轨迹样本——最终让结论可信的往往不是那个总分，而是失败轨迹里暴露的东西。

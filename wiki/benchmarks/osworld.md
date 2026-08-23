---
type: benchmark
title: OSWorld
status: draft
topics:
- benchmark
- computer-use
- os-agent
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 3
quality: medium
confidence: medium
canonical_url: https://arxiv.org/abs/2404.07972
evidence_sources:
- https://arxiv.org/abs/2404.07972
- https://os-world.github.io/
- https://github.com/xlang-ai/OSWorld
---
# OSWorld

OSWorld 是 xlang-ai 团队（港大、CMU 等合作）提出的"真实操作系统"基准（论文 arXiv:2404.07972）：Agent 在真实的 Ubuntu/Windows/macOS 虚拟机里操作真实应用（浏览器、Office、终端、文件管理器等）完成开放式计算机任务。它是"computer-use Agent"浪潮的标志性评测。

## 评什么

评的是开放式、多应用的桌面任务完成能力：跨应用组合（如"从网页下载数据、用表格软件处理、把结果发邮件"）、GUI 操作、文件系统操作、故障恢复。任务不要求固定操作路径，只看最终状态。

## 环境

- 真实虚拟机（VMware/VirtualBox 等后端），预装真实应用，环境可快照重置。
- Agent 观察为屏幕截图（可配 accessibility tree），动作为鼠标键盘事件（点击、输入、滚动），与真人操作同构。
- 任务状态从虚拟机里以脚本读取（读文件、查数据库、抓应用状态），执行式判定，不依赖模型裁判。

## 指标

主指标为任务成功率（基于最终状态与中间状态的脚本化断言）。论文公布的人类与模型基线差距悬殊（不引用具体数字），以此论证 computer-use 远未解决。

## 对 Harness 评估的启示

- 动作空间在像素坐标层面，Harness 的职责前所未有地重：视觉 grounding（把"保存按钮"翻译成坐标）、动作重试、屏幕变化等待、错误恢复，全是 [[agent-harness]] 的活，模型只提供"意图"。
- 观察-动作循环延迟高（截图、虚拟机执行），Harness 层面的批处理与动作复合（一次输出一串动作）直接影响效率和成功率，报告时应交代这些策略。
- 虚拟机快照/重置机制说明：评测基建本身需要 Harness 级的工程，评估者和被评者的边界在这里变得模糊。

## 待验证 / 边界

- 任务集规模、支持的操作系统组合随版本更新，以官网/仓库为准。
- 虚拟机环境对硬件资源要求高，复现成本是已知门槛。

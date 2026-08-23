---
type: benchmark
title: Terminal-Bench
status: draft
topics:
- benchmark
- terminal
- cli-agent
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 2
quality: medium
confidence: medium
canonical_url: https://www.tbench.ai/
evidence_sources:
- https://www.tbench.ai/
- https://github.com/laude-institute/terminal-bench
---
# Terminal-Bench

Terminal-Bench 是斯坦福大学与 Laude Institute 合作维护的终端任务基准（官网 tbench.ai，代码在 laude-institute/terminal-bench）：Agent 在一个真实的命令行环境里完成端到端任务——编译代码、配置服务、训练模型、数据处理、系统排障——全部通过 shell 交互完成。它补上了 [[swe-bench]] 没覆盖的那块：不是改仓库代码过测试，而是"在终端里把系统级的活干成"。

## 评什么

评命令行环境下的长程自主任务完成：多步命令执行、环境探索、依赖安装、错误恢复、输出验证。任务领域横跨软件工程、系统管理、安全、机器学习、数据科学等。

## 环境

- 每个任务一个 Docker 环境，附带任务描述（自然语言）和一份测试脚本。
- Agent 通过终端多路复用（tmux 风格）与环境交互：发送命令、读取输出，和人在终端里干活的方式一致。
- 判定纯执行式：跑测试脚本检查结果。环境隔离好、重置便宜，复现门槛低于 [[osworld]]。
- 基准有版本演化（如 2.0 及之后版本），不同版本任务集不同，引用成绩必须带版本号。

## 指标

主指标为任务解决率（resolution rate）。官方同时维护排行榜，常见报道口径是"模型 × Harness"组合的成绩。具体分数不引用。

## 对 Harness 评估的启示

- Terminal-Bench 的官方评测基建允许自带 Harness 参赛，排行榜上常见 [[openhands]]、[[claude-code]]、Codex 等不同 Harness 搭配不同模型的组合——它是目前最适合做"固定模型换 Harness / 固定 Harness 换模型"解耦实验的公开基准之一，直接支撑 [[harness-vs-model-evaluation]] 的方法论。
- 终端输出 noisy 且冗长，[[context-manager]] 策略（输出截断、滚动缓冲）对成绩影响显著，是研究上下文管理的理想试验场。
- 任务涉及真实系统变更，Harness 的安全边界（危险命令防护）在评测里也会暴露。

## 待验证 / 边界

- 任务总数随版本变化（不同来源引用 80、89 等数字），以所用版本的官方说明为准。
- 榜单成绩多为各厂商/团队自报，独立复现程度不一。

---
type: comparison
title: 六大 Agent 系统的 Harness 侧重点对比
status: draft
topics:
- comparison
- agent-harness
- framework
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 6
quality: medium
confidence: medium
evidence_sources:
- https://github.com/All-Hands-AI/OpenHands
- https://github.com/SWE-agent/SWE-agent
- https://github.com/langchain-ai/langgraph
- https://github.com/microsoft/autogen
- https://github.com/FoundationAgents/MetaGPT
- https://docs.anthropic.com/en/docs/claude-code/overview
---
# 六大 Agent 系统的 Harness 侧重点对比

这一页把 [[openhands]]、[[swe-agent]]、[[langgraph]]、[[autogen]]、[[metagpt]]、[[claude-code]] 放在一起，回答一个问题：同样是"让 LLM 干活"，这六个系统各自把设计的重心押在了 [[agent-harness]] 的哪一块。先给结论框架，再展开。

## 一句话定位

| 系统 | 本质 | 设计重心 |
|---|---|---|
| OpenHands | 完整编码 Agent 平台 | 事件流抽象 + 沙箱运行时 |
| SWE-agent | 研究型编码 Agent | ACI（给模型用的接口设计） |
| LangGraph | 编排框架 | 显式控制流 + 状态持久化 |
| AutoGen | 多智能体框架 | 会话协议驱动的协作 |
| MetaGPT | 多智能体框架 | SOP 硬编排 + 结构化产物交接 |
| Claude Code | 商业终端 Agent | 人机在环的工作流体验 |

## 按 Harness 组件看各自的强项

**推理循环：** 前三者差异最大。OpenHands 用事件流（Action/Observation 交替）把循环变成可回放的日志；SWE-agent 刻意保持循环极简，复杂度全部压进接口层；LangGraph 干脆不预设循环，让你用图把循环画出来。AutoGen 用消息流转取代全局循环，MetaGPT 用 SOP 把循环锁死成流水线，Claude Code 的循环未公开，但把"用户随时打断"做成了一等能力。

**上下文管理：** 六个系统给了六种答案，正好覆盖 [[context-manager]] 的主要流派——OpenHands 压缩事件流，SWE-agent 让工具不产出爆炸输出，LangGraph 给状态通道和 reducer，AutoGen 给可裁剪的消息缓冲，MetaGPT 用结构化文档交接从源头减量，Claude Code 用 CLAUDE.md 长期记忆加自动压缩。

**工具与动作空间：** SWE-agent 的 ACI 和 Claude Code 的精选工具集代表"克制而清晰"的路线；OpenHands 的 CodeAct（直接执行代码）代表"少工具、大能力"的路线；三个框架（LangGraph/AutoGen/MetaGPT）把动作空间留给用户或角色定义。

**执行环境：** OpenHands 的 Docker 沙箱运行时最完整；Claude Code 反其道而行，直接跑在用户机器上、靠权限系统做信任边界；三个框架基本不管环境，沙箱是自备件。

**规划与编排：** LangGraph 的显式图、AutoGen 的 GroupChat、MetaGPT 的 SOP 流水线是三种编排哲学的标本（显式 / 涌现 / 硬编码）；OpenHands 和 Claude Code 都用"主 Agent + 临时子代理委派"的轻量路线；SWE-agent 明确不玩多智能体。

**状态与持久化：** LangGraph 的 checkpointer 体系最系统化；OpenHands 的事件流天然支持回放，适合研究；Claude Code 的持久化服务于"人的工作流连续性"；其余三家的持久化能力存在但相对轻。

## 怎么选（按需求而非按热度）

- 要一个开箱即用、能打 [[swe-bench]] 的编码 Agent，或要做 Harness 实验的对照基座：OpenHands、SWE-agent。前者平台化程度高，后者代码薄、适合读懂和改造。
- 要自己搭生产级 Agent、需要断点恢复和人工介入：LangGraph。
- 要研究或搭建多角色协作、会话式分工：AutoGen（注意 v0.4 重写与 AG2 分叉）。要做"流程成熟、产物规范"的软件生成：MetaGPT。
- 要在真实开发工作流里日常使用、在意交互体验与安全确认：Claude Code（闭源，不可做内部研究）。

## 对评估的含义

这张对比表同时是一份"归因指南"：拿不同系统打同一个基准时，分数差异大概率来自上表某一两行的组件差异，而不是整体"先进/落后"。做 [[harness-vs-model-evaluation]] 式实验时，先用这张表定位两边 Harness 在哪个组件上分道扬镳，消融就有了假设。各基准对 Harness 的敏感度分析见 [[swe-bench]]、[[terminal-bench]]、[[appworld]] 等页面。

## 待验证 / 边界

- 三个开源框架迭代都快，组件层结论基于当前架构，具体 API 以各仓库为准；Claude Code 闭源，其行内描述只覆盖官方文档可见行为。
- 本页不比较星标、分数等易过期数字。

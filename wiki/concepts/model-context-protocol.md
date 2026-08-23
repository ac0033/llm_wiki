---
type: concept
title: Model Context Protocol（MCP）
aliases: ["model context protocol", "MCP", "mcp 协议"]
status: draft
topics: [agent, protocol, tools, mcp, integration]
harness_components: [action-interface, context-manager]
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 4
quality: high
confidence: high
canonical_url: https://modelcontextprotocol.io
evidence_sources:
  - https://modelcontextprotocol.io
  - https://www.anthropic.com/news/model-context-protocol
  - https://arxiv.org/abs/2606.20683
  - https://github.com/modelcontextprotocol/servers
---

## 一句话结论

Model Context Protocol（MCP）是 Anthropic 于 2024 年 11 月提出并开源的开放协议，用统一的 client-server 架构标准化「应用如何向 LLM/agent 暴露工具、数据源和上下文资源」，把原本每个工具一套定制集成的碎片化问题变成一次实现、处处复用。

## 关键机制

1. **Client-Server 架构。** MCP server 暴露能力（tools、resources、prompts 三类原语），MCP client（内嵌于 agent/IDE/应用）按协议发现与调用。工具提供方与 agent 开发方解耦。
2. **三类原语。** Tools 是可执行函数（模型可调用）；Resources 是可读数据（文件、数据库记录等上下文）；Prompts 是预置的提示模板。具体原语集随协议版本演进，引用时以官方规范为准。
3. **在 harness 中的位置。** 按 arXiv:2606.20683 的分析，MCP 主要强化了 [[context-manager]] 与 [[action-interface]] 之间的边界：工具的「描述与发现」影响上下文组装，工具的「调用与执行」属于动作接口。它是 [[tool-use]] 的标准化接入层。
4. **生态。** 官方与社区维护了大量现成 server（文件系统、Git、数据库、SaaS 等，见 servers 仓库），主流 agent 框架与 IDE 已广泛支持。

## 适用场景

- 企业集成：内部系统（数据库、工单、文档库）封装为 MCP server 后，任何兼容的 agent 都能接入。
- 多工具 agent：工具数量大时，统一的发现与描述机制降低接入成本。
- 跨工具复用：同一 server 同时服务 IDE 助手、coding agent、聊天应用。

## 局限与失败模式

- **安全面。** MCP server 是可执行代码与数据的入口：恶意 server 可以投毒工具描述（tool poisoning）、窃取上下文中的数据；server 的信任与审核机制是部署前提。具体攻防研究细节待核对。
- **协议版本碎片化。** 协议迭代快，不同 client/server 支持的版本与传输方式（stdio、HTTP 等）可能不一致，互操作需要实际验证。
- **不解决语义问题。** MCP 标准化「怎么接」，不保证模型「接了对的」——工具选择、参数正确性仍是 [[action-interface]] 与模型能力的问题。
- **治理缺口。** 权限、审批、审计不在协议核心职责内，仍需 [[verification-governance]] 在 harness 层补齐。

## 与其他页面的关系

- 抽象面：[[tool-use]]；运行时归属：[[action-interface]]、[[context-manager]]。
- 安全与治理：[[verification-governance]]、[[sandboxed-execution]]（server 进程的隔离）。
- agent 间协议的姊妹概念：A2A（Agent2Agent）面向 agent 与 agent 的互操作，落在 [[multi-agent-orchestration]] 与 [[control-loop]] 一侧。
- 使用 MCP 的系统示例：[[openhands]] 等。

## 来源

- [Model Context Protocol 官方站点与规范](https://modelcontextprotocol.io)
- [Anthropic: Introducing the Model Context Protocol（2024-11）](https://www.anthropic.com/news/model-context-protocol)
- [From Question Answering to Task Completion (arXiv:2606.20683)](https://arxiv.org/abs/2606.20683) —— MCP 在 harness 分解中的定位。
- [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) —— 官方/社区 server 集合。

## 待验证问题

- 协议当前版本的准确原语集与传输方式，引用时需以官方规范当时版本为准。
- MCP 安全研究（tool poisoning、rug pull 式 server 更新等）的原始论文与披露待逐篇核对补充。
- MCP 与 A2A 的职责边界在社区讨论中仍有不同解读，待跟踪权威阐述。

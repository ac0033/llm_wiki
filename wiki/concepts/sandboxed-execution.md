---
type: concept
title: Sandboxed Execution（沙箱化执行）
aliases: ["sandboxed execution", "沙箱执行", "sandbox", "沙箱"]
status: draft
topics: [agent, sandbox, security, isolation, runtime]
harness_components: [verification-governance, action-interface]
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 5
quality: high
confidence: medium
canonical_url: https://arxiv.org/abs/2606.20683
evidence_sources:
  - https://arxiv.org/abs/2606.20683
  - https://gvisor.dev
  - https://firecracker-microvm.github.io
  - https://e2b.dev
  - https://arxiv.org/abs/2407.16741
---

## 一句话结论

Sandboxed Execution 是把 agent 产生的代码与命令放进隔离环境中运行的机制：限制文件系统、网络出站、进程与资源用量——它既是安全机制（挡住失控与恶意动作），也是可复现性原语（每次执行从干净环境开始）。

## 关键机制

Agent 能写文件、跑代码、浏览网页、调 API 之后，隔离就从「可选项」变成「必选项」。在 [[agent-harness]] 中，沙箱主要落在 [[verification-governance]]（作为安全约束），同时与 [[action-interface]] 的执行语义紧密耦合。

1. **隔离层级。** 从弱到强大致是：进程级限制 → 容器（Docker）→ 用户态内核（gVisor）→ 微虚拟机（Firecracker 类 microVM）。隔离越强，开销与启动延迟越大。
2. **Agent 专用沙箱服务。** e2b 等托管服务把「给 agent 一个临时、可编程、带文件系统与网络的执行环境」产品化；[[openhands]] 的 runtime 也采用容器化执行。
3. **策略面。** 沙箱不只是隔离技术，还包括策略：网络白名单、文件系统挂载范围、资源配额、超时。策略的松紧由治理层决定。
4. **审批配合。** 沙箱管「在隔离区内能做什么」，审批门（approval gate）管「什么动作允许影响隔离区外」——两者互补而非替代。

## 适用场景

- Coding agent：运行不可信的生成代码与测试，见 [[openhands]]、[[swe-bench]] 类评测的执行环境。
- 数据分析 agent：执行任意数据处理脚本。
- 浏览器/计算机使用 agent：隔离浏览会话，防止恶意页面影响宿主系统。
- 评测：干净、可重置的环境是 benchmark 可复现的前提（见 [[agent-evaluation]]）。

## 局限与失败模式

- **沙箱逃逸。** 隔离实现自身可能有漏洞；容器级隔离对高价值目标的防护强度有限。逃逸风险的具体量化缺乏公开数据，待验证。
- **环境不一致。** 沙箱环境与真实生产环境的差异导致「沙箱里能跑、上线就挂」；评测沙箱与开发沙箱的差异也会影响分数可比性。
- **开销与延迟。** microVM 级隔离的启动与运行开销会拖慢 agent 循环的每一步，长程任务中累积明显。
- **状态管理复杂化。** 沙箱是临时的，跨步骤的状态要么显式持久化（挂载卷、对接 [[state-artifact-store]]），要么随沙箱销毁——设计不当会丢中间结果。
- **网络策略两难。** 断网最安全但很多任务需要联网；开放出站则打开数据外泄与注入的通道。

## 与其他页面的关系

- 治理框架：[[verification-governance]]（沙箱是其安全机制之一）；执行入口：[[action-interface]]。
- 状态对接：[[state-artifact-store]]（沙箱内外状态的同步与持久化）。
- 攻击面关联：[[observation-interface]] 进入的注入内容，最终靠沙箱 + 权限门兜底。
- 相关系统：[[openhands]] 的容器化 runtime；[[agent-evaluation]] 的评测环境建设。

## 来源

- [From Question Answering to Task Completion (arXiv:2606.20683)](https://arxiv.org/abs/2606.20683) —— 沙箱在 harness 中的定位。
- [gVisor](https://gvisor.dev) —— 用户态内核隔离方案。
- [Firecracker](https://firecracker-microvm.github.io) —— microVM 隔离方案。
- [e2b](https://e2b.dev) —— agent 专用沙箱服务。
- [OpenHands (arXiv:2407.16741)](https://arxiv.org/abs/2407.16741) —— 容器化 agent runtime 的开源实现。

## 待验证问题

- 各沙箱方案（容器 vs gVisor vs microVM）在 agent 工作负载下的启动延迟与运行开销对比，缺乏公开的系统性基准，待验证。
- 浏览器 agent 的专用沙箱方案（如综述清单提到的 ceLLMate 等）细节待逐篇核对。
- 沙箱与审批策略的「松紧-可用性」权衡是否有量化研究，待调研。

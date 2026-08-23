---
type: concept
title: Verification & Governance（验证与治理层）
aliases: ["verification and governance", "验证与治理", "verifier", "governance layer"]
status: draft
topics: [agent, harness, verification, governance, safety]
harness_components: [verification-governance]
ingested: 2026-08-18
last_verified: 2026-08-21
source_count: 6
quality: high
confidence: medium
canonical_url: https://arxiv.org/abs/2606.20683
evidence_sources:
  - https://arxiv.org/abs/2606.20683
  - https://arxiv.org/abs/2310.06770
  - https://arxiv.org/abs/2507.21504
  - https://arxiv.org/abs/2608.15579
  - https://doi.org/10.5281/zenodo.22003465
  - https://github.com/Jiaaqiliu/Awesome-Harness-Engineering
---

## 一句话结论

Verification & Governance 层通过测试、断言、验证器模型、沙箱策略、权限门、回滚、重试、预算控制、安全约束和审计轨迹来检查、约束和修复 agent 的执行——它回答的问题是「这一步做对了没有，以及该不该允许它做」。

## 关键机制

在 [[agent-harness]] 六组件中，这一层是闭环可靠性的最后防线，可拆成「验证（对不对）」和「治理（许不许）」两组机制：

**验证侧：**

1. **程序化验证。** 单元测试、构建、linter、断言——结果确定、成本低的反馈信号。[[swe-bench]]（arXiv:2310.06770）这类 benchmark 本身就以「测试是否通过」作为可验证奖励（verifiable reward）。Kozuchi Agent（[[arxiv-2608-15579]]）把它推进到选择阶段：在拿不到隐藏测试的前提下，把 K=8 个候选运行各自生成的测试交叉应用到彼此补丁上，纯执行式地选出最终补丁（+14 解决实例，相对顺序基线）。
2. **模型验证器（verifier model / critic）。** 用另一个（或同一个）模型评审中间产物，适合没有程序化判据的开放式任务，但引入验证器自身的不可靠性。
3. **修复回路。** 验证失败后的重试、带反馈重试、回滚到检查点（依赖 [[state-artifact-store]]），由 [[control-loop]] 调度。

**治理侧：**

1. **权限门（permission gate / approval）。** 高风险动作（删文件、发网络请求、花钱的 API 调用）执行前需人类或策略批准。
2. **沙箱策略。** 文件系统、网络出站、进程执行、资源用量的隔离约束，见 [[sandboxed-execution]]。
3. **预算控制。** 步数、token、费用、时间的硬上限。
4. **审计轨迹。** 完整可追溯的执行记录，供事后审查与合规。

## 适用场景

- 有可验证结果的任务（代码、数学、数据处理）：程序化验证是性价比最高的可靠性来源。
- 生产环境部署：权限门 + 沙箱 + 审计是合规底线。
- 无人值守长程任务：预算控制与自动回滚决定系统能否安全地「放着跑」。

## 局限与失败模式

- **Reward hacking / 验证器博弈。** Agent 学会通过验证而不是完成任务（例如修改测试本身、硬编码预期输出）；验证信号越弱，博弈空间越大。
- **验证器不可靠。** 模型验证器会漏判和误判；用 LLM-as-judge 做治理决策时，judge 的偏差直接进入系统行为。
- **误拦（false negative）。** 过严的权限门和策略会频繁打断执行，把「自主性」磨没，人类审批成为瓶颈。
- **验证成本。** 每步都跑完整测试套件在大型仓库中不可行，验证粒度与成本需要权衡；最优验证频率缺乏通用结论，待验证。
- **注入与越权。** 恶意观察（网页、文件内容中的 prompt injection）可能诱导 agent 执行越权动作，治理层是主要防线但不是充分防线。这类抵抗能力可以被量化测量：dspy-security-bench（[[doi-org-10-5281-zenodo-22003465]]）包装 AgentDojo 环境，同时报告任务效用与攻击抵抗率，并对测量协议做哈希冻结——但该工具目前只有自述的 Zenodo 记录，有效性待验证。

## 与其他页面的关系

- 所属框架：[[agent-harness]]。
- 验证结果作为反馈进入 [[control-loop]]（决定重试/反思/回滚）和 [[context-manager]]（错误信息进上下文）。
- 治理约束施加在 [[action-interface]] 上；隔离执行依赖 [[sandboxed-execution]]；审计数据存在 [[state-artifact-store]]。
- 与 [[agent-evaluation]] 的关系：评估是离线衡量系统质量，验证是运行时的在线检查，两者共享「什么是正确」的判据问题。
- 与 [[agent-observability]]：审计轨迹与运行轨迹是同一数据的两种用途。

## 来源

- [From Question Answering to Task Completion (arXiv:2606.20683)](https://arxiv.org/abs/2606.20683) —— 组件定义来源。
- [SWE-bench (arXiv:2310.06770)](https://arxiv.org/abs/2310.06770) —— 可验证奖励的 benchmark 范例。
- [Evaluation and Benchmarking of LLM Agents: A Survey (arXiv:2507.21504)](https://arxiv.org/abs/2507.21504) —— 验证与评估方法背景。
- [Kozuchi Agent (arXiv:2608.15579)](https://arxiv.org/abs/2608.15579) —— 跨 agent 测试交叉选择作为执行式验证的实现，见 [[arxiv-2608-15579]]。
- [dspy-security-bench (Zenodo)](https://doi.org/10.5281/zenodo.22003465) —— prompt-injection 抵抗的可复现测量 harness（自述来源，待核实），见 [[doi-org-10-5281-zenodo-22003465]]。
- [awesome-harness-engineering](https://github.com/Jiaaqiliu/Awesome-Harness-Engineering) —— 权限与治理的工程实践清单。

## 待验证问题

- 各系统权限模型（Claude Code 的 permission modes、OpenHands 的确认机制等）的实际拦截效果与误拦率缺乏公开数据，待验证。
- 模型验证器相对程序化验证在开放式任务上的可靠性边界，待系统研究。
- 「value-aware evaluation」（把成本、延迟、安全纳入评估目标）在综述中被列为开放挑战，具体方法学待跟踪。

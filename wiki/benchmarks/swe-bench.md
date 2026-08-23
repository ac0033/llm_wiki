---
type: benchmark
title: SWE-bench
status: draft
topics:
- benchmark
- coding-agent
- software-engineering
ingested: 2026-08-18
last_verified: 2026-08-21
source_count: 4
quality: medium
confidence: medium
canonical_url: https://www.swebench.com/
evidence_sources:
- https://www.swebench.com/
- https://arxiv.org/abs/2310.06770
- https://arxiv.org/abs/2608.15579
- https://github.com/swe-bench/SWE-bench
---
# SWE-bench

SWE-bench 是普林斯顿大学团队提出的软件工程基准（论文页见 [[swe-bench-paper]]，arXiv:2310.06770），任务来自真实 GitHub 开源项目的 issue：给 Agent 一个仓库（检出到 issue 修复前的 commit）和 issue 描述，要求产出补丁，然后用项目自己的测试套件判定修复是否成功。

## 评什么

评估的是"端到端解决真实软件 issue"的能力：理解代码库、定位 bug、写出既修复问题又不破坏现有行为的补丁。它测的不是代码生成片段质量，而是在大型真实仓库里的完整工程闭环。

## 环境

- 每个任务实例对应一个真实 Python 仓库（原版约 12 个流行开源项目）的某个历史 commit，配好可运行的依赖环境（官方提供 Docker 镜像做可复现评估）。
- 判定方式：应用 Agent 的补丁后运行测试，要求"修复测试"（fail-to-pass）从失败变通过，且"回归测试"（pass-to-pass）不失败。纯执行式判定，无模型裁判。
- 衍生版本：SWE-bench Verified（OpenAI 与原作者合作人工筛过的子集）、SWE-bench Lite、多模态版、多语言版（SWE-bench Multilingual 等），选哪个版本直接影响分数可比性。

## 指标

主指标是 **Resolved 率**（解决实例占比），常配报补丁应用成功率等中间指标。不引用具体分数，以官方榜单为准。

## 对 Harness 评估的启示

- 它是 [[agent-harness]] 价值的天然放大器：同一模型换不同 Harness（[[swe-agent]] 的 ACI、[[openhands]] 的 CodeAct），解决率差异可以非常大——这是"Harness 与模型解耦评估"最常被引用的证据，见 [[harness-vs-model-evaluation]]。
- 最新参照点：Kozuchi Agent（[[arxiv-2608-15579]]，ASE '26）用本地托管的 27B 开放权重模型、零微调，在 Verified 官方评测器上解决 374/500（74.80%），其论文把成绩明确归因于 harness 工程（阶段图、动作契约、跨 agent 测试时选择）而非模型；同一 harness 原样迁到 Multi-SWE-bench Java 得 41/128（32.03%），是「harness 跨语言迁移」的少见实测。
- 环境即 Harness 的一部分：依赖安装、仓库检出、测试选择都由 Harness/评测基建决定，"模型不会"和"环境没配好"在分数上无法区分，报告时必须交代环境细节。
- 已知风险：数据污染（任务来自公开 GitHub，可能进训练集）、补丁过拟合测试（过 fail-to-pass 但非真修复）。Verified 子集缓解了前者的一部分噪声，但不消除。

## 待验证 / 边界

- 各衍生版本的实例数、筛选标准随时间更新，引用前核对官网。
- 原版只覆盖 Python 仓库，结论外推到其他语言需谨慎。

---
type: benchmark
title: WebArena
status: draft
topics:
- benchmark
- web-agent
- self-hosted
ingested: 2026-08-18
last_verified: 2026-08-18
source_count: 3
quality: medium
confidence: medium
canonical_url: https://arxiv.org/abs/2307.13854
evidence_sources:
- https://arxiv.org/abs/2307.13854
- https://webarena.dev/
- https://github.com/web-arena-x/webarena
---
# WebArena

WebArena 是 CMU 团队提出的 Web Agent 基准（论文 arXiv:2307.13854）：一套自托管的、功能完整的网站环境，Agent 像真人一样通过浏览器操作这些网站完成任务。它与离线网页快照类基准的区别是"活的环境"——状态真实变化，操作有真实后果。

## 评什么

评 Web 导航与操作任务的功能性正确性：在电商、论坛、代码托管、地图、内容管理等站点上完成"找到某信息""下一笔符合条件的订单""改一个仓库设置"这类任务。考察长程规划、页面理解、跨站点组合操作。

## 环境

- 自托管的真实开源 Web 应用实例（电商 Magento、Reddit 风格论坛、GitLab、地图、Wiki 等），用真实数据灌库，打包为 Docker/AMI 镜像，评测方自己部署。
- Agent 通过浏览器自动化接口（Playwright）操作，观察可以是无障碍树（accessibility tree）文本、截图或两者。
- 后续有 VisualWebArena（视觉版）、WorkArena（企业软件场景）等衍生基准，指标口径不同，不要混用。

## 指标

主指标是任务成功率（functional correctness）：用脚本检查环境最终状态或访问轨迹是否满足任务目标，而非比对操作序列。部分信息型任务用字符串/模型辅助判定答案正确性。不引用具体分数。

## 对 Harness 评估的启示

- 观察表示是 Harness 变量：同一个任务，给 Agent accessibility tree、原始 HTML 还是截图，成功率差别很大。报 WebArena 成绩必须说明观察空间与动作空间，否则分数不可比——这是 [[harness-vs-model-evaluation]] 里"接口条件要写进评估报告"的标准案例。
- 环境自托管意味着评测成本高、复现门槛高：Harness 研究者需要考虑环境重置、并发隔离这些工程问题，它们本身就是 Harness 能力的一部分。
- 网站内容静态快照，不会演化；真实 Web 上的 Agent 还需应对改版与反爬，WebArena 分数存在乐观偏差。

## 待验证 / 边界

- 镜像版本与任务集随时间更新（任务数本页不写死），部署指南以官方仓库为准。
- 部分任务判据依赖精确匹配，存在"做对但判错"的已知噪声。

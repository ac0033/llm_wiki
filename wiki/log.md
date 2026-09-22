# 工作日志

按时间倒序记录知识库的维护动作。weekly_compile 流程会追加条目；手工大改动也应在此登记。

## 2026-08-18

- 初始化仓库基础设施：配置（`config/`）、脚本（`scripts/`）、提示词（`prompts/`）、测试（`tests/`）、registry 与水位线（`data/`）。
- 填充首期 AI Agent / Harness 核心 wiki：1 个总览、1 个方向页、17 个概念页、11 个论文页、6 个系统页、7 个基准页、2 个比较页。
- 统一 frontmatter schema，修复同名 slug 与旧 wikilink；`lint_wiki.py` 达到 0 error / 0 warning。
- 完成 `weekly_compile.ps1 -DryRun`：fetch_candidates、weekly_update、lint、Kimi CLI 可用性检查均通过；未写 registry、review queue 或 digest。
- 最终验收：`pytest` 27 项通过；`lint_wiki.py` 0 error / 0 warning；weekly 去重已覆盖 registry 与现有 wiki 页面标题。

## [2026-08-21] weekly_update | candidates={'dropped': 14, 'review': 6} | queue=weekly-2026-08-21.md | digest=weekly-2026-08-21.md

## [2026-08-21] weekly_update | candidates={'review': 2, 'duplicate_in_batch': 6, 'dropped': 12} | queue=weekly-2026-08-21.md | digest=weekly-2026-08-21.md\r
\r
## [2026-08-21] weekly_compile | selected=2 | updated=7 | lint=0 error/0 warning\r
\r
- 入选并入库：Kozuchi Agent（arXiv:2608.15579 → [[arxiv-2608-15579]]）与 dspy-security-bench（Zenodo 10.5281/zenodo.22003465 → [[doi-org-10-5281-zenodo-22003465]]，标 needs_review）。\r
- 更新页面：[[agent-harness]]、[[verification-governance]]、[[agent-evaluation]]、[[swe-bench]] 增加交叉链接与证据；digest weekly-2026-08-21 补评述；review queue 补推荐理由。\r
- 收尾：`compile_index.py` 重建索引，`lint_wiki.py` 0 error / 0 warning。

## [2026-08-22] manual_ingest | agent-memory 子方向建立 + 6 篇文献入库 | lint=0 error/0 warning

- 新增子方向 [[agent-memory-context]]（`wiki/directions/agent-memory-context.md`）；按用户指示新增 `config/directions/agent-memory.yml`，weekly 评分关键词现覆盖 memory / context 主题。
- 入库并编译 6 篇文献：[[arxiv-2310-08560]]（MemGPT）、[[arxiv-2309-02427]]（CoALA）、[[arxiv-2404-13501]]（记忆机制综述）、[[arxiv-2502-12110]]（A-Mem）、[[arxiv-2507-13334]]（Context Engineering 综述）、[[arxiv-2307-03172]]（Lost in the Middle）。
- 更新交叉链接：[[ai-agent-harness]]、[[agent-memory]]、[[context-engineering]]。
- 流程改动（按用户指示）：`prompts/weekly_compile.md` 增加第 9 步「复核交接」；`README.md` 增加「操作流程」（单篇入库、每周复核）；`AGENTS.md` 工作流 3 补充复核确认约定。
- 清理错配：误入库的 arXiv:2404.02737（hep-th 物理论文）的草稿页与 raw PDF 已删除；registry 中对应记录（`data/registry/ingested.jsonl` 中 source_id 为 2404.02737 的行）需人工删除。

## [2026-08-28] weekly_update | candidates={'review': 4, 'dropped': 16} | queue=weekly-2026-08-28.md | digest=weekly-2026-08-28.md

## [2026-09-04] weekly_update | candidates={'dropped': 17, 'review': 2, 'duplicate_in_batch': 1} | queue=weekly-2026-09-04.md | digest=weekly-2026-09-04.md

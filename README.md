# llm_wiki — AI Agent 文献知识库

这是一个从零搭建的 Markdown / Obsidian 文献知识库，主题是 AI Agent，重点关注 **Agent Harness**（智能体的运行时脚手架：驱动模型循环、管理上下文、调度工具的那一层代码与系统设计）。

## 目录分层

- `raw/` — 原始素材层。抓到的 PDF、网页快照、图片，逐字保存，不做改写，是 wiki 页面所有论断的证据来源。
- `wiki/` — 知识层。Obsidian 可直接打开的 Markdown 页面，按类型分目录：`concepts/`、`papers/`、`systems/`、`benchmarks/`、`comparisons/`、`directions/`、`digests/`、`questions/`。页面之间用 wikilink 互联，例如 `[[agent-harness]]`。
- `config/` + `data/` — 元数据层（schema 层）。`config/` 存来源、评分细则、研究方向等配置；`data/registry/` 存候选与已入库文献的机器可读登记簿（JSONL）；`data/state/` 存抓取水位线（watermark）；`data/review_queue/` 存等待人工复核的条目。

## 常用命令

```bash
# 安装依赖（使用 uv）
uv sync

# 抓取新候选文献（先试跑不写盘）
uv run python scripts/fetch_candidates.py --source arxiv --since 2026-08-01 --limit 20 --dry-run

# 每周评分与分流（dry-run 不写 registry / review queue / digest）
uv run python scripts/weekly_update.py --dry-run --limit 20

# 每周完整流程的 Windows 包装脚本（fetch → update → lint → Kimi 编译）
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/weekly_compile.ps1 -DryRun

# 入库一个来源：arXiv ID / DOI / URL / 本地文件均可
uv run python scripts/ingest_source.py 2501.12345
uv run python scripts/ingest_source.py https://example.com/blog-post

# 重建 wiki 索引
uv run python scripts/compile_index.py

# 全面体检（schema、坏链、重复、孤儿、缺 URL、证据不足、stale）
uv run python scripts/lint_wiki.py

# 跑测试
uv run pytest
```

Windows 下每周自动流程见 `scripts/weekly_compile.ps1`（支持 `-DryRun`）与 `scripts/install_weekly_task.ps1`（只生成注册脚本，不实际注册计划任务）。Semantic Scholar 来源默认关闭，因为未认证请求容易触发 429；如需启用，先设置 `SEMANTIC_SCHOLAR_API_KEY`，再把 `config/sources.yml` 中 `semantic_scholar.enabled` 改为 `true`。

## 操作流程

### 单篇入库（看到一篇好文章想收进来）

一条命令即可，支持 arXiv ID、DOI、URL、本地文件四种输入：

```bash
uv run python scripts/ingest_source.py 2501.12345
uv run python scripts/ingest_source.py https://example.com/blog-post
```

脚本会做三件确定性工作：把原文下载到 `raw/`、在 `wiki/papers/` 生成一个只填好元数据的草稿页、登记到 `data/registry/ingested.jsonl`。**注意此时正文还是空的**，需要第二步：在 Kimi Code 会话里说「按 prompts/ingest_source.md 补全刚入库的页面」，Kimi 会读 `raw/` 里的原文、撰写正文、补交叉链接，最后跑 lint 和索引重建收尾。也可以一次入库多篇，让 Kimi 逐个补全。

### 每周复核（review queue）

每周自动流程跑完后，拿不准的候选会进入复核清单，等你确认：

- 清单位置：`data/review_queue/weekly-<日期>.md`；同期周报末尾的「待复核交接」小节（`wiki/digests/weekly-<日期>.md`）也会汇总同样的内容，在 Obsidian 里看周报即可。
- 清单里每条候选前的复选框：`[x]` 表示 weekly_compile 阶段的 Kimi 已给出推荐/暂缓结论并附了理由，**仍在等你确认**，不是最终决定。
- 确认方式：在 Kimi Code 会话里说「带我过一遍本周待复核清单」。Kimi 会逐条讲解推荐理由，你口头给出决定（入库 / 放弃 / 先放着），由它把结论写回清单并执行入库——不需要你手动编辑清单文件。

## 约定

- 页面 frontmatter 规范见 `AGENTS.md`，所有字段的合法性由 `lint_wiki.py` 强制执行。
- 正文用中文撰写，技术术语保留英文原名；论断必须能回溯到 `raw/` 中的一手来源或页面 frontmatter 里的 URL。
- 不编造事实、数字、引用数、benchmark 分数；不确定的一律标"待验证"。

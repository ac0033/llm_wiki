# ingest_source — 单篇入库撰写提示词

`scripts/ingest_source.py` 已完成确定性工作：把原文落到 `raw/`、在 `wiki/papers/`（或对应子目录）生成 frontmatter 完备的草稿页、登记 `data/registry/ingested.jsonl`。你的任务是阅读 `raw/` 中的原文，把草稿页补全为正式的知识页。

## 步骤

1. 找到刚生成的草稿页（registry 最后一条记录的 `slug` 对应 `wiki/**/<slug>.md`）和它引用的 `raw/` 素材。
2. 通读原文，用中文补全以下部分，技术术语保留英文原名：
   - **摘要**：3-5 句，忠实概括原文的核心主张与方法；
   - **要点**：分条列出关键贡献、方法细节、实验设置与结果；
   - **与本库的关系**：说明它与 [[agent-harness]] 及其他相关页面（如 [[context-manager]]、[[swe-bench]]、[[react]]、[[openhands]]）的关联，用 wikilink 互联；
   - **可质疑之处**：指出原文未解决的问题、实验局限或需要交叉验证的论断，标"待验证"。
3. 把 frontmatter 的 `status` 从 `draft` 改为 `current`，`last_verified` 更新为今天；补全 `topics`、`harness_components`、`quality`、`confidence`，必要时补充 `evidence_sources`。
4. 如果原文值得在已有的概念页（如 `wiki/concepts/` 下的页面）中被引用，在那些页面里加一条 wikilink，避免产生孤儿页。
5. 完成正文后由宿主进行独立语义核验，运行 `uv run python scripts/compile_index.py` 和 `uv run python scripts/lint_wiki.py` 收尾。本次模型不执行 shell，不改索引，不把生成结束写成核验通过。

## 红线

- 一切论断必须来自 `raw/` 原文或 frontmatter 的 `canonical_url` / `evidence_sources` URL；读不到原文内容的部分一律标"待验证"，不得编造；
- 不得改动 frontmatter 的 `ingested`；
- 不得修改 `scripts/`、`config/`、`data/` 下的任何文件；
- 不编造数字、引用数、benchmark 分数。

# AGENTS.md — 仓库协作规范

本仓库是一个 AI Agent（重点：Agent Harness）主题的 Markdown / Obsidian 文献知识库。无论是人还是 LLM agent，在本仓库工作都必须遵守本文件的规范。

## 一、三层结构：raw / wiki / schema

| 层 | 位置 | 内容 | 规则 |
|---|---|---|---|
| 原始层（raw） | `raw/papers/`、`raw/articles/`、`raw/assets/` | 抓取的 PDF、网页正文快照、图片 | 逐字保存，绝不改写；是 wiki 一切论断的证据来源 |
| 知识层（wiki） | `wiki/` 各子目录 | 人工/LLM 撰写的知识页面，Obsidian wikilink 互联 | 每个论断必须可回溯到 raw 或 frontmatter 中的一手来源 URL |
| 元数据层（schema） | `config/`、`data/registry/`、`data/state/` | 来源配置、评分细则、JSONL 登记簿、水位线 | 只由确定性脚本写入；字段即 schema，改字段要同步改 `lint_wiki.py` |

数据流向是单向的：`raw → wiki → index`。`wiki/index.md` 与 `wiki/log.md` 由脚本重建/追加，不手改。

## 二、页面 frontmatter schema

每个 `wiki/**/*.md` 页面必须带 YAML frontmatter：

```yaml
---
type: concept                  # 必填，枚举：overview / direction / concept / paper / system / benchmark / comparison / digest / question
title: Agent Harness           # 必填
aliases: [harness, 执行壳]      # 建议，Obsidian 别名
status: current                # 必填，枚举：seed / draft / compiled / current / needs_review / stale / archived
topics: [agent, harness]       # 必填，可为空列表
harness_components: [context-manager, control-loop]  # 可选，取值见方向页六组件
published: 2026-06             # 可选，论文/系统首次发布日期或年月
ingested: 2026-08-18           # 必填，入库日期
last_verified: 2026-08-18      # 必填，最近一次核实日期，超过 90 天会被 lint 标 stale
source_count: 2                # 必填，整数
quality: high                  # 必填，枚举建议：high / medium / low
confidence: high               # 必填，枚举建议：high / medium / low
canonical_url: https://arxiv.org/abs/2606.20683  # paper / system / benchmark 必填或可换成 evidence_sources
evidence_sources:              # concept / system / benchmark / comparison 建议至少 1 条；概念页默认至少 2 条
  - https://arxiv.org/abs/2606.20683
---
```

- 页面文件名的 kebab-case stem 就是 wikilink slug，例如 `wiki/concepts/agent-harness.md` 对应 `[[agent-harness]]`。
- `concept` 类型页面至少需要 1 条 `evidence_sources` 或 `canonical_url`；如果证据少于 2 条，应标为 `seed`、`draft` 或 `needs_review`。
- 正文用中文，技术术语保留英文原名；不确定的事实标"待验证"，禁止编造数字、引用数、benchmark 分数。

## 三、LLM 与确定性代码的边界

**确定性代码（scripts/ 下的 Python 与 PowerShell）负责：**

- 抓取候选（`fetch_candidates.py`）、水位线管理、去重（rapidfuzz 标题相似度）、按 `config/quality-rubric.yml` 打分；
- 下载与文本抽取（PyMuPDF / trafilatura）、写 registry JSONL、写水位线；
- 重建 `wiki/index.md`（`compile_index.py`）、体检（`lint_wiki.py`）；
- 所有 schema 校验、坏链检测、stale 计算。

**LLM 负责（且只负责）：**

- 读 raw 素材与候选元数据，做相关性判断、撰写/改写 wiki 页面正文、写 digest 的分析性文字；
- 在 `prompts/ingest_source.md`、`prompts/weekly_compile.md` 约束的模板内产出内容。

**禁止 LLM 做的事：** 修改 `scripts/`、`config/`、`data/registry/`、`data/state/` 的既有记录；绕过脚本直接改写 `wiki/index.md`；编造来源或把"待验证"内容写成事实。

## 四、四条工作流

1. **ingest（单篇入库）**：运行 `scripts/ingest_source.py <arxiv-id|DOI|URL|本地文件>` 抓取原文到 `raw/`、生成 wiki 草稿页并登记 registry；随后由 LLM 按 `prompts/ingest_source.md` 完善正文。
2. **query（查询）**：直接用 Obsidian 打开 `wiki/`，从 `wiki/index.md` 或 wikilink 跳转；`wiki/questions/` 存放研究问题页。
3. **weekly（每周更新）**：`scripts/fetch_candidates.py` 拉取候选并写 registry；`scripts/weekly_update.py` 去重评分、生成 `data/review_queue/` 复核清单和 `wiki/digests/` 周报；`scripts/weekly_compile.ps1` 在正式运行时串联 fetch → weekly_update → lint → agent-memory 记忆服务预检 → `kimi -p --output-format stream-json` → compile_index → lint。`scripts/install_weekly_task.ps1` 只生成注册脚本，不直接注册计划任务。weekly_compile 收尾时必须做「复核交接」（见 `prompts/weekly_compile.md` 第 9 步）：在周报和复核清单末尾汇总待复核条目、清单路径与确认方式；人工复核在 Claude Code 交互会话中进行（对 Claude 说「带我过一遍本周待复核清单」），由 Claude 逐条讲解并把确认/否决决定写回复核清单。复核清单中的 `[x]` 表示 LLM 已给出推荐/暂缓建议，不代表人已确认。
4. **lint（体检）**：`scripts/lint_wiki.py` 检查 schema、坏链、重复、孤儿页、缺 URL、概念证据不足、90 天 stale；CI 或每次大批量编辑后必跑。
5. **chat（主动对话）**：仓库根目录的 `chat.ps1` 唤起 Claude Code 交互会话（`.\chat.ps1` 新会话、`-Continue` 续最近一次、`-Pick` 从历史会话中选择）。会话记录由 CLI 自动持久化在 `~/.kimi-code/sessions/` 下按工作目录分组。
6. **service（MCP 接入层）**：`service/` 是供 dsh（deepseek-harness）以 MCP stdio 方式调用的薄层（`uv run python -m service.kb_server`），工具：`kb_query`（只读查询，走 `kimi -p` agentic 检索，专属会话 id 存 `data/state/kb_session.json`）、`kb_ingest`（单篇入库）、`kb_lint`、`kb_reindex`。变更性操作前后自动 git 快照（`service/snapshot.py`，身份用 `git -c` 单次注入）；只读操作不触发快照。service 层不改 scripts/ 既有逻辑，只做编排。

## 五、长期记忆（agent-memory）

- Claude 入口显式加载 config/agent-memory.mcp.json，服务为 http://127.0.0.1:8765/mcp，类型为 http。
- service/memory_config.py 向提示词显式加载 .kimi-code/skills/agent-memory/SKILL.md 原样镜像；保留旧路径兼容，不假装 CLI 自动识别另一家的 skill。
- scope 固定 repo:llm-wiki；旧 Kimi 会话记录不迁移、不继承。
- query 只开放记忆读取工具；ingest/weekly 可提出新记忆及更新工作记忆，但不开放人工复核决定、删除和强制收尾。blocked 时不重试、不替用户 acknowledge；pending_review 必须报告。
- chat.ps1 同样显式带 MCP 配置与 skill，人工复核在此交互处理，必须取得用户逐项决定。
- KB_MEMORY_ENABLED=0 关闭非交互记忆连接；其他 provider 未验证记忆适配时明确使用无记忆模式。连接失败应如实报告并继续知识处理，不将可达性当作真实读取。
- 记忆连接以真实工具调用结果为准；连通不代表写入、人工复核已获端到端验证。

## 六、非交互写入范围（LLM agent 的权限边界）

- **可写**：`wiki/`（除 `index.md` 的自动索引区块外）、`data/review_queue/`、`data/logs/`、`wiki/log.md` 的追加。
- **只读**：`scripts/`、`config/`、`tests/`、`data/registry/`、`data/state/`、`raw/` 既有文件、`pyproject.toml`。
- **需人工确认**：安装新依赖、注册计划任务、删除任何文件。git 变更默认需人工确认，唯一例外是 `service/` 层在变更性操作前后自动执行的快照 commit（snapshot），用于保证可回滚。

## 七、工程约定

### 调用入口（service/agent_runner.py）

- `service/agent_runner.py` 集中分配角色：query、ingest、weekly 筛选与综合、chat 默认 Claude Code / Opus 5；生成后的独立语义核验默认 Codex。
- `kb_server.py`、`weekly_compile.ps1`、`chat.ps1` 使用新入口；`kimi_runner.py` 仅作兼容保留，不是默认调用路径。
- weekly 的来源选择返回 URL，宿主验证来自本批次清单后调用原有入库脚本；模型不能任意执行 shell。索引与 lint 仍由宿主执行。
- 新 Claude 入口显式加载 config/agent-memory.mcp.json（HTTP）与 .kimi-code/skills/agent-memory/SKILL.md 镜像；scope 仍为 repo:llm-wiki。必须以真实工具结果确认连接。KB_MEMORY_ENABLED=0 可显式关闭批次记忆；query 只读，批次不开放人工复核决定与删除工具。旧 Kimi 会话不与新会话混用。
- `KB_<角色>_PROVIDER`、`KB_<角色>_MODEL` 可显式覆盖；Fable 5 仅为有额度时显式选用的替代。失败保留文件待复核，不自动通过。

- 写作回库入口为 `scripts/import_writing.py`：确认保存后导入证据片段、低置信度草稿和待读清单，保留已有笔记。片段不得冒充完整原文，草稿入库日期不得冒充事实核验日期。
- service 的变更快照改为操作完成后仅收录本次新增变更路径，排除操作前已脏的文件；不再执行全仓前置快照。此条更新第四节、第六节中关于前后快照的旧描述。
- 来源抓取分页未完成不推进水位；同日周报按批次保留复核记录。确定性写入入口共用维护锁。

- Python 环境用 uv：`uv sync`、`uv run python ...`、`uv run pytest`。
- 抓取脚本支持 `--dry-run`，凡涉及网络的操作必须先用 dry-run 验证。
- 外部引用一律优先一手来源（arXiv 官方页面、项目官网、官方文档）。

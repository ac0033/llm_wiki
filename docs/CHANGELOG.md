# CHANGELOG

版本号遵循 SemVer；1.0.0 之前接口可能调整。

## 0.2.0 · 2026-09-22 · 模型入口改为 agent_runner

- `service/agent_runner.py` 按角色分配 CLI：查询、原文理解、候选筛选、跨文献综合与交互对话走 Claude Code，生成后由 Codex 做独立语义核验；`KB_<角色>_PROVIDER` / `KB_<角色>_MODEL` 可显式覆盖。`kb_server.py`、`weekly_compile.ps1`、`chat.ps1` 改用新入口，`kimi_runner.py` 仅作兼容保留。
- 记忆服务通过 `config/agent-memory.mcp.json` 显式加载，skill 镜像由 `service/memory_config.py` 注入提示词；`KB_MEMORY_ENABLED=0` 关闭非交互记忆连接。
- 单篇入库从网页元数据（og:title / h1 / title）提取标题，不再把订阅横幅当标题。
- 周更只处理本批次新生成的复核清单；来源选择由宿主核对后再调用入库脚本，模型不执行 shell；索引与 lint 由宿主执行。
- 新增公开卫生测试 `tests/test_public_hygiene.py`。

## 0.1.0 · 2026-09-09

- 抓取、去重评分、复核清单与周报、单篇入库、lint、索引重建；MCP 服务 `kb_query` / `kb_ingest` / `kb_lint` / `kb_reindex`；写作回库脚本。

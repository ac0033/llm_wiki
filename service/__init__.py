"""llm_wiki 知识库的 MCP service 薄层。

不改动 scripts/ 下的既有核心代码，只在其上封装：
- snapshot: 变更性操作前后的 git 快照，保证可回滚；
- kimi_runner: 以子进程方式调用 kimi CLI 完成 LLM 环节；
- kb_server: FastMCP (stdio) server，暴露 kb_query / kb_ingest / kb_lint / kb_reindex。
"""

"""FastMCP (stdio) server：llm_wiki 知识库的 MCP service 薄层。

暴露 4 个工具：

- ``kb_query``：只读查询，把问题包装成声明性 prompt 交给 kimi（经 kimi_runner）；
- ``kb_ingest``：单篇入库，pre-snapshot → ingest_source.py → kimi 完善正文 → post-snapshot；
- ``kb_lint``：运行 lint_wiki.py 体检，只读；
- ``kb_reindex``：运行 compile_index.py 重建 wiki/index.md，随后 post-snapshot。

本层不改动 scripts/ 下任何既有代码，只做编排与快照。运行方式::

    uv run python -m service.kb_server      # 或 uv run python service/kb_server.py
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from service import kimi_runner
from service.snapshot import post_snapshot, pre_snapshot

REPO_ROOT = Path(__file__).resolve().parent.parent

SCRIPT_TIMEOUT_SECONDS = 300  # ingest 涉及网络抓取，给足 5 分钟
QUERY_TIMEOUT_SECONDS = 600  # kb_query 的 kimi 检索循环：典型 1 分钟内，复杂查询留足 10 分钟

mcp = FastMCP("llm-wiki-kb")

QUERY_PROMPT_TEMPLATE = """这是一个针对 llm_wiki 知识库的【只读查询】任务。

工作规则：
- 你只能读取仓库内容来回答问题；唯一允许的写入操作是向 data/logs/ 追加查询日志；
- 禁止修改 wiki/、scripts/、config/、prompts/、raw/ 以及 data/ 下除 data/logs/ 外的任何文件；
- 答案中引用的每个论断都必须标注来源页面路径（wiki/ 下的相对路径，例如 wiki/concepts/agent-harness.md）；
- 如果知识库中没有足够依据回答，明确说明"知识库中未收录相关内容"，不要编造。

用户问题：
{question}
"""

INGEST_PROMPT_TEMPLATE = """这是一个针对 llm_wiki 知识库的【单篇入库】任务。

确定性脚本 scripts/ingest_source.py 已经完成抓取：原文已落到 raw/，wiki 草稿页已生成，registry 已登记。来源标识为：{source}

请严格按照 prompts/ingest_source.md 模板的全部要求（模板全文附在最后），阅读 raw/ 中本次入库的原文，把刚生成的草稿页补全为正式知识页，并按模板第 5 步运行 lint 与 compile_index 收尾。

---- prompts/ingest_source.md 全文 ----
{template}
"""


def _run_script(*args: str) -> subprocess.CompletedProcess[str]:
    """以 ``uv run python scripts/<name> ...`` 方式运行仓库脚本，返回完整结果。"""
    return subprocess.run(
        ["uv", "run", "python", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=SCRIPT_TIMEOUT_SECONDS,
        # stdin 给 DEVNULL：本进程 stdin 是 MCP stdio 管道，子进程意外等待
        # 输入会永久挂起；EOF 让它们直接报错或按默认行为继续。
        stdin=subprocess.DEVNULL,
    )


def _format_proc(proc: subprocess.CompletedProcess[str]) -> str:
    parts = []
    if proc.stdout and proc.stdout.strip():
        parts.append(proc.stdout.strip())
    if proc.stderr and proc.stderr.strip():
        parts.append(f"[stderr]\n{proc.stderr.strip()}")
    return "\n".join(parts) or "（无输出）"


@mcp.tool()
def kb_query(question: str) -> str:
    """只读查询知识库。答案标注 wiki/ 来源页面路径；不写知识库本体，不触发快照。"""
    prompt = QUERY_PROMPT_TEMPLATE.format(question=question)
    return kimi_runner.run_kimi(prompt, timeout=QUERY_TIMEOUT_SECONDS)


@mcp.tool()
def kb_ingest(source: str) -> str:
    """单篇入库：arXiv ID / DOI / URL / 本地文件路径。入库前后自动做 git 快照。"""
    pre_snapshot(REPO_ROOT, "ingest")

    proc = _run_script("scripts/ingest_source.py", source)
    if proc.returncode != 0:
        return (
            f"ingest_source.py 执行失败（exit {proc.returncode}），已中止，未做 post-snapshot"
            f"（操作前的 pre-snapshot 可用于回滚）。\n{_format_proc(proc)}"
        )

    template = (REPO_ROOT / "prompts" / "ingest_source.md").read_text(encoding="utf-8")
    prompt = INGEST_PROMPT_TEMPLATE.format(source=source, template=template)
    try:
        # 写正文是完整 agent 循环（读原文、改页、跑 lint/compile_index），实测超过 5 分钟
        answer = kimi_runner.run_kimi(prompt, timeout=900)
    except kimi_runner.KimiError as exc:
        return (
            f"脚本入库已完成，但 kimi 完善正文失败：{exc}\n"
            "未做 post-snapshot，当前工作区保留了脚本产出的草稿状态。"
        )

    committed = post_snapshot(REPO_ROOT, "ingest", f"{source} 入库并完善正文")
    snapshot_note = "已提交 post-snapshot。" if committed else "无新增变更，post-snapshot 跳过。"
    return f"入库完成，{snapshot_note}\n\n[脚本输出]\n{_format_proc(proc)}\n\n[kimi 回复]\n{answer}"


@mcp.tool()
def kb_lint() -> str:
    """运行 scripts/lint_wiki.py 体检（schema、坏链、stale 等），返回完整输出。只读。"""
    proc = _run_script("scripts/lint_wiki.py")
    status = "通过" if proc.returncode == 0 else f"存在问题（exit {proc.returncode}）"
    return f"lint {status}。\n{_format_proc(proc)}"


@mcp.tool()
def kb_reindex() -> str:
    """运行 scripts/compile_index.py 重建 wiki/index.md，随后 post-snapshot。"""
    proc = _run_script("scripts/compile_index.py")
    if proc.returncode != 0:
        return f"compile_index.py 执行失败（exit {proc.returncode}）。\n{_format_proc(proc)}"
    committed = post_snapshot(REPO_ROOT, "reindex", "重建 wiki/index.md")
    snapshot_note = "已提交 post-snapshot。" if committed else "索引无变化，post-snapshot 跳过。"
    return f"重建索引完成，{snapshot_note}\n{_format_proc(proc)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")

"""kimi CLI 子进程封装：以非交互 prompt 模式调用 kimi，并维护专属会话。

实测确认的 kimi CLI 行为（0.38.0）：

- 调用形式：``kimi -p "<prompt>" --output-format stream-json [--session <id>]``；
- stream-json 输出为逐行 JSON，其中 ``role=="assistant"`` 且不带 tool_calls
  的最后一条消息是最终回答文本；
- ``type=="session.resume_hint"`` 的 meta 行携带 ``session_id``（带
  ``session_`` 前缀），首次运行后据此持久化会话 id；
- 恢复会话用 ``--session <id>``（与 resume_hint 推荐的 ``-r`` 等价，已实测）；
- 会话不存在时 exit code 为 1，stderr 含 ``Session "<id>" not found.``。

子进程执行收敛在 :func:`_run_subprocess` 一个小函数里，测试通过替换它来 mock。
"""

from __future__ import annotations

import json
import socket
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SESSION_FILE = REPO_ROOT / "data" / "state" / "kb_session.json"

MEMORY_SERVICE_HOST = "127.0.0.1"
MEMORY_SERVICE_PORT = 8765
MEMORY_SERVICE_URL = f"http://{MEMORY_SERVICE_HOST}:{MEMORY_SERVICE_PORT}/mcp"

KIMI_TIMEOUT_SECONDS = 300  # 5 分钟

MEMORY_DEGRADED_NOTE = "（注：agent-memory 记忆服务不可达，已降级为无记忆模式执行本次查询。）"


class KimiError(RuntimeError):
    """kimi 子进程调用失败（非会话损坏类错误，或重试后仍失败）。"""


def _run_subprocess(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    """执行子进程的唯一入口，测试里替换这个函数即可 mock kimi。"""
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=KIMI_TIMEOUT_SECONDS,
    )


def memory_service_available(timeout: float = 2.0) -> bool:
    """预检 agent-memory 服务可达性（TCP 探测 127.0.0.1:8765）。"""
    try:
        with socket.create_connection(
            (MEMORY_SERVICE_HOST, MEMORY_SERVICE_PORT), timeout=timeout
        ):
            return True
    except OSError:
        return False


def _load_session_id(session_path: Path) -> str | None:
    try:
        data = json.loads(Path(session_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    session_id = data.get("session_id")
    return session_id if isinstance(session_id, str) and session_id else None


def _save_session_id(session_id: str, session_path: Path) -> None:
    session_path = Path(session_path)
    session_path.parent.mkdir(parents=True, exist_ok=True)
    session_path.write_text(
        json.dumps({"session_id": session_id}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _build_cmd(prompt: str, session_id: str | None) -> list[str]:
    cmd = ["kimi", "-p", prompt, "--output-format", "stream-json"]
    if session_id:
        cmd += ["--session", session_id]
    return cmd


def _session_broken(proc: subprocess.CompletedProcess[str]) -> bool:
    """判断失败是否由会话损坏引起（stderr 提示 session 不存在）。"""
    if proc.returncode == 0:
        return False
    stderr = (proc.stderr or "").lower()
    return "session" in stderr and "not found" in stderr


def parse_stream_json(output: str) -> tuple[str, str | None]:
    """解析 stream-json 输出，返回（最终回答文本, session_id 或 None）。"""
    answer: str = ""
    session_id: str | None = None
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        if event.get("type") == "session.resume_hint" and event.get("session_id"):
            session_id = event["session_id"]
        # 带 tool_calls 的 assistant 消息是中间步骤，最终回答是不带工具调用的最后一条
        if (
            event.get("role") == "assistant"
            and event.get("content")
            and not event.get("tool_calls")
        ):
            answer = event["content"]
    return answer, session_id


def run_kimi(
    prompt: str,
    *,
    session_path: Path = SESSION_FILE,
    repo: Path = REPO_ROOT,
    runner=_run_subprocess,
) -> str:
    """调用 kimi 执行一个 prompt，返回回答文本。

    - 有已保存会话则带 ``--session`` 恢复；会话损坏时自动降级为新会话重试一次；
    - 调用前预检 agent-memory 服务，不可达时照常执行，但在结果末尾注明降级；
    - 每次成功调用后把 stream-json 里的 session_id 持久化到 session_path。
    """
    memory_ok = memory_service_available()

    session_id = _load_session_id(session_path)
    proc = runner(_build_cmd(prompt, session_id), repo)
    if _session_broken(proc):
        # 会话损坏：丢弃旧 id，以新会话重试一次
        session_id = None
        proc = runner(_build_cmd(prompt, None), repo)
    if proc.returncode != 0:
        raise KimiError(
            f"kimi 调用失败（exit {proc.returncode}）：{(proc.stderr or '').strip()}"
        )

    answer, new_session_id = parse_stream_json(proc.stdout or "")
    if new_session_id:
        _save_session_id(new_session_id, session_path)

    if not memory_ok:
        answer = f"{answer}\n\n{MEMORY_DEGRADED_NOTE}" if answer else MEMORY_DEGRADED_NOTE
    return answer

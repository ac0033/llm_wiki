"""test_service_kimi_runner.py — mock 子进程函数，验证会话管理与降级行为。"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from service import kimi_runner  # noqa: E402
from service.kimi_runner import MEMORY_DEGRADED_NOTE, run_kimi  # noqa: E402


def stream_json(answer: str, session_id: str) -> str:
    """构造一份最小的 stream-json 输出：一条 resume_hint + 中间工具消息 + 最终回答。"""
    return "\n".join([
        json.dumps({"type": "session.resume_hint", "session_id": session_id}),
        json.dumps({"role": "assistant", "content": "（中间步骤）",
                    "tool_calls": [{"name": "Read"}]}),
        json.dumps({"role": "assistant", "content": answer}),
    ])


def ok_proc(answer: str, session_id: str) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(
        args=[], returncode=0,
        stdout=stream_json(answer, session_id), stderr="",
    )


@pytest.fixture(autouse=True)
def memory_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    """默认记忆服务可达；个别用例再覆盖为不可达，避免测试真做 TCP 探测。"""
    monkeypatch.setattr(kimi_runner, "memory_service_available", lambda: True)


def test_first_run_without_session_then_persist(tmp_path: Path) -> None:
    calls: list[list[str]] = []

    def fake(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
        calls.append(cmd)
        return ok_proc("答案甲", "session_new")

    session_path = tmp_path / "kb_session.json"
    answer = run_kimi("介绍一下 agent harness", session_path=session_path,
                      repo=tmp_path, runner=fake)

    assert answer == "答案甲"
    # prompt 原样透传为 -p 的参数，且首次运行不带 --session
    cmd = calls[0]
    assert cmd[:3] == ["kimi", "-p", "介绍一下 agent harness"]
    assert "--output-format" in cmd and "stream-json" in cmd
    assert "--session" not in cmd
    # session id 已持久化
    saved = json.loads(session_path.read_text(encoding="utf-8"))
    assert saved["session_id"] == "session_new"


def test_resume_with_saved_session(tmp_path: Path) -> None:
    session_path = tmp_path / "kb_session.json"
    session_path.write_text(json.dumps({"session_id": "session_old"}), encoding="utf-8")
    calls: list[list[str]] = []

    def fake(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
        calls.append(cmd)
        return ok_proc("答案乙", "session_newer")

    answer = run_kimi("续上一个问题", session_path=session_path,
                      repo=tmp_path, runner=fake)

    assert answer == "答案乙"
    cmd = calls[0]
    i = cmd.index("--session")
    assert cmd[i + 1] == "session_old"
    # 服务端返回的新 id 覆盖旧 id
    saved = json.loads(session_path.read_text(encoding="utf-8"))
    assert saved["session_id"] == "session_newer"


def test_broken_session_falls_back_to_new_session(tmp_path: Path) -> None:
    session_path = tmp_path / "kb_session.json"
    session_path.write_text(json.dumps({"session_id": "session_gone"}), encoding="utf-8")
    calls: list[list[str]] = []

    def fake(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
        calls.append(cmd)
        if len(calls) == 1:
            return subprocess.CompletedProcess(
                args=cmd, returncode=1, stdout="",
                stderr='Error: Session "session_gone" not found.',
            )
        return ok_proc("降级后答案", "session_fresh")

    answer = run_kimi("随便问问", session_path=session_path,
                      repo=tmp_path, runner=fake)

    assert answer == "降级后答案"
    assert len(calls) == 2
    assert "--session" in calls[0]        # 第一次带旧会话
    assert "--session" not in calls[1]    # 降级后新建会话重试
    saved = json.loads(session_path.read_text(encoding="utf-8"))
    assert saved["session_id"] == "session_fresh"


def test_memory_service_unreachable_degrades(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(kimi_runner, "memory_service_available", lambda: False)

    def fake(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
        return ok_proc("正常答案", "session_x")

    answer = run_kimi("查询", session_path=tmp_path / "s.json",
                      repo=tmp_path, runner=fake)

    # 查询照常执行，但在结果中注明降级
    assert "正常答案" in answer
    assert MEMORY_DEGRADED_NOTE in answer

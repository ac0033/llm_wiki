"""git 快照助手：在变更性操作前后自动提交，保证知识库可回滚。

身份通过 ``git -c user.name=... -c user.email=...`` 单次注入，
绝不写入仓库的本地 git 配置。这是 AGENTS.md 第六节授权的
唯一自动 git 写操作。
"""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path

SNAPSHOT_AUTHOR_NAME = "kb-service"
SNAPSHOT_AUTHOR_EMAIL = "kb-service@local"


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            # stdin 必须是 DEVNULL：服务进程的 stdin 是 MCP stdio 管道，git 在
            # Windows 上遇到文件占用时会向 stdin 询问 "Should I try again?"，
            # 继承管道会永久挂起；给 EOF 让 git 直接报错返回。
            stdin=subprocess.DEVNULL,
            timeout=120,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"git {' '.join(args)} 超时（120s）") from exc
    if check and result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} 失败（exit {result.returncode}）：{result.stderr.strip()}"
        )
    return result


def dirty_paths(repo: Path) -> set[str]:
    paths = set()
    for args in (("diff", "--name-only", "-z"), ("diff", "--cached", "--name-only", "-z"),
                 ("ls-files", "--others", "--exclude-standard", "-z")):
        paths.update(p for p in _git(repo, *args).stdout.split("\0") if p)
    return paths


def snapshot(repo: Path, message: str, paths=None) -> bool:
    """暂存全部变更并按指定 message 提交；没有待提交变更时返回 False 不报错。"""
    repo = Path(repo)
    selected = sorted(dirty_paths(repo) if paths is None else paths)
    if not selected:
        return False
    for path in selected:
        (repo / path).resolve().relative_to(repo.resolve())
    _git(repo, "add", "--", *selected)
    # diff --cached --quiet：有暂存变更时 exit 1，干净时 exit 0
    status = _git(repo, "diff", "--cached", "--quiet", "--", *selected, check=False).returncode
    if status == 0:
        return False
    if status != 1:
        raise RuntimeError("无法检查快照差异")
    _git(
        repo,
        "-c",
        f"user.name={SNAPSHOT_AUTHOR_NAME}",
        "-c",
        f"user.email={SNAPSHOT_AUTHOR_EMAIL}",
        "commit",
        "--only",
        "-m",
        message,
        "--", *selected,
    )
    return True


def pre_snapshot(repo: Path, op: str) -> bool:
    """变更性操作前的快照，message 形如 ``snapshot: pre-<op> <ISO时间>``。"""
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return snapshot(Path(repo), f"snapshot: pre-{op} {timestamp}")


def post_snapshot(repo: Path, op: str, summary: str, paths=None) -> bool:
    """变更性操作成功后的快照，message 形如 ``<op>: <摘要>``。"""
    return snapshot(Path(repo), f"{op}: {summary}", paths=paths)

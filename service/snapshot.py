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
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} 失败（exit {result.returncode}）：{result.stderr.strip()}"
        )
    return result


def snapshot(repo: Path, message: str) -> bool:
    """暂存全部变更并按指定 message 提交；没有待提交变更时返回 False 不报错。"""
    repo = Path(repo)
    _git(repo, "add", "-A")
    # diff --cached --quiet：有暂存变更时 exit 1，干净时 exit 0
    if _git(repo, "diff", "--cached", "--quiet", check=False).returncode == 0:
        return False
    _git(
        repo,
        "-c",
        f"user.name={SNAPSHOT_AUTHOR_NAME}",
        "-c",
        f"user.email={SNAPSHOT_AUTHOR_EMAIL}",
        "commit",
        "-m",
        message,
    )
    return True


def pre_snapshot(repo: Path, op: str) -> bool:
    """变更性操作前的快照，message 形如 ``snapshot: pre-<op> <ISO时间>``。"""
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return snapshot(Path(repo), f"snapshot: pre-{op} {timestamp}")


def post_snapshot(repo: Path, op: str, summary: str) -> bool:
    """变更性操作成功后的快照，message 形如 ``<op>: <摘要>``。"""
    return snapshot(Path(repo), f"{op}: {summary}")

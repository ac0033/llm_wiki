"""test_service_snapshot.py — 用 tmp_path 真实 git init 验证快照助手的两条路径。"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from service.snapshot import post_snapshot, pre_snapshot, snapshot  # noqa: E402


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True,
        encoding="utf-8", errors="replace", check=True,
    )


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init")
    return repo


def test_snapshot_commits_pending_changes(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    (repo / "a.md").write_text("hello\n", encoding="utf-8")

    assert snapshot(repo, "test commit") is True

    log = git(repo, "log", "-1", "--format=%s|%an|%ae").stdout.strip()
    assert log == "test commit|kb-service|kb-service@local"
    # 身份只通过 -c 单次注入，不写仓库本地配置
    local_name = subprocess.run(
        ["git", "config", "--local", "user.name"],
        cwd=repo, capture_output=True, text=True,
    )
    assert local_name.returncode != 0 or not local_name.stdout.strip()


def test_snapshot_returns_false_when_clean(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    (repo / "a.md").write_text("hello\n", encoding="utf-8")
    assert snapshot(repo, "first") is True

    # 没有任何新变更时不报错、不产生新 commit，返回 False
    assert snapshot(repo, "should not happen") is False
    count = git(repo, "rev-list", "--count", "HEAD").stdout.strip()
    assert count == "1"


def test_pre_and_post_snapshot_message_format(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    (repo / "a.md").write_text("v1\n", encoding="utf-8")
    assert pre_snapshot(repo, "ingest") is True
    msg = git(repo, "log", "-1", "--format=%s").stdout.strip()
    assert msg.startswith("snapshot: pre-ingest ")

    (repo / "a.md").write_text("v2\n", encoding="utf-8")
    assert post_snapshot(repo, "ingest", "demo 入库") is True
    msg = git(repo, "log", "-1", "--format=%s").stdout.strip()
    assert msg == "ingest: demo 入库"

"""test_lint_wiki.py — 用临时 wiki 目录测试 lint_wiki 的各项检查。"""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import lint_wiki  # noqa: E402

FIXED_TODAY = date(2026, 8, 18)


def write_page(
    wiki_dir: Path,
    name: str,
    *,
    title: str | None = None,
    ptype: str = "concept",
    status: str = "current",
    last_verified: str = "2026-08-18",
    canonical_url: str | None = None,
    evidence_sources: list[str] | None = None,
    body: str = "正文。",
) -> Path:
    if evidence_sources is None:
        evidence_sources = ["https://arxiv.org/abs/2501.12345", "https://arxiv.org/abs/2501.54321"]
    lines = [
        "---",
        f'title: "{title or name}"',
        f"type: {ptype}",
        f"status: {status}",
        "topics: [agent]",
        "ingested: 2026-08-18",
        f"last_verified: {last_verified}",
        f"source_count: {len(evidence_sources)}",
        "quality: medium",
        "confidence: high",
    ]
    if canonical_url:
        lines.append(f"canonical_url: {canonical_url}")
    lines.append("evidence_sources:")
    for source in evidence_sources:
        lines.append(f"  - {source}")
    lines.extend(["---", "", body])
    path = wiki_dir / f"{name}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def issues_of(issues, check):
    return [i for i in issues if i.check == check]


def test_clean_wiki_no_errors(tmp_path):
    write_page(tmp_path, "a", body="链接到 [[b]]。")
    write_page(tmp_path, "b", body="链接到 [[a]]。")
    issues = lint_wiki.lint_wiki(tmp_path, today=FIXED_TODAY)
    assert [i for i in issues if i.level == "error"] == []


def test_schema_missing_field(tmp_path):
    path = write_page(tmp_path, "a", body="[[a]]")
    text = path.read_text(encoding="utf-8").replace("last_verified: 2026-08-18\n", "")
    path.write_text(text, encoding="utf-8")
    issues = lint_wiki.lint_wiki(tmp_path, today=FIXED_TODAY)
    assert any("last_verified" in i.message for i in issues_of(issues, "schema"))


def test_schema_bad_type(tmp_path):
    write_page(tmp_path, "a", ptype="essay", body="[[a]]")
    issues = lint_wiki.lint_wiki(tmp_path, today=FIXED_TODAY)
    assert any("type" in i.message for i in issues_of(issues, "schema"))


def test_broken_link(tmp_path):
    write_page(tmp_path, "a", body="指向 [[不存在的页面]] 和 [[a]]。")
    issues = lint_wiki.lint_wiki(tmp_path, today=FIXED_TODAY)
    broken = issues_of(issues, "broken_link")
    assert len(broken) == 1
    assert "不存在的页面" in broken[0].message


def test_duplicate_title(tmp_path):
    write_page(tmp_path, "a", title="同一个标题", body="[[a]]")
    write_page(tmp_path, "b", title="同一个标题", body="[[b]]")
    issues = lint_wiki.lint_wiki(tmp_path, today=FIXED_TODAY)
    assert issues_of(issues, "duplicate")


def test_duplicate_slug_across_directories(tmp_path):
    write_page(tmp_path, "a", body="[[a]]")
    write_page(tmp_path / "papers", "a", body="[[a]]")
    issues = lint_wiki.lint_wiki(tmp_path, today=FIXED_TODAY)
    assert any("slug 重复" in i.message for i in issues_of(issues, "duplicate"))


def test_orphan_page(tmp_path):
    write_page(tmp_path, "a", body="[[a]]")
    write_page(tmp_path, "b", body="没有外链。")
    issues = lint_wiki.lint_wiki(tmp_path, today=FIXED_TODAY)
    orphan = issues_of(issues, "orphan")
    assert len(orphan) == 1
    assert orphan[0].level == "warning"
    assert "b.md" in orphan[0].path


def test_missing_url_for_paper(tmp_path):
    write_page(tmp_path, "p", ptype="paper", evidence_sources=[], body="[[p]]")
    issues = lint_wiki.lint_wiki(tmp_path, today=FIXED_TODAY)
    assert issues_of(issues, "missing_url")


def test_concept_without_sources_is_error(tmp_path):
    write_page(tmp_path, "c", ptype="concept", evidence_sources=[], body="[[c]]")
    issues = lint_wiki.lint_wiki(tmp_path, today=FIXED_TODAY)
    weak = issues_of(issues, "weak_concept")
    assert weak and weak[0].level == "error"


def test_single_source_current_concept_is_warning(tmp_path):
    write_page(
        tmp_path,
        "c",
        ptype="concept",
        evidence_sources=["https://arxiv.org/abs/2501.12345"],
        body="[[c]]",
    )
    issues = lint_wiki.lint_wiki(tmp_path, today=FIXED_TODAY)
    weak = issues_of(issues, "weak_concept")
    assert weak and weak[0].level == "warning"


def test_single_source_seed_concept_is_allowed(tmp_path):
    write_page(
        tmp_path,
        "c",
        ptype="concept",
        status="seed",
        evidence_sources=["https://arxiv.org/abs/2501.12345"],
        body="[[c]]",
    )
    issues = lint_wiki.lint_wiki(tmp_path, today=FIXED_TODAY)
    assert issues_of(issues, "weak_concept") == []


def test_stale_warning(tmp_path):
    write_page(tmp_path, "old", last_verified="2026-01-01", body="[[old]]")
    issues = lint_wiki.lint_wiki(tmp_path, today=FIXED_TODAY)
    stale = issues_of(issues, "stale")
    assert len(stale) == 1
    assert stale[0].level == "warning"


def test_digest_exempt_from_orphan(tmp_path):
    write_page(tmp_path, "weekly-2026-08-18", ptype="digest", body="没有人链接我。")
    issues = lint_wiki.lint_wiki(tmp_path, today=FIXED_TODAY)
    assert issues_of(issues, "orphan") == []

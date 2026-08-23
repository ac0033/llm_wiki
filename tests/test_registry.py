"""test_registry.py — registry JSONL 读写、水位线、去重的单元测试。"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import common  # noqa: E402


def test_jsonl_roundtrip(tmp_path):
    path = tmp_path / "candidates.jsonl"
    common.append_jsonl(path, {"title": "论文甲", "status": "new"})
    common.append_jsonl(path, {"title": "论文乙", "status": "new"})
    records = common.read_jsonl(path)
    assert len(records) == 2
    assert records[0]["title"] == "论文甲"


def test_read_jsonl_missing_file(tmp_path):
    assert common.read_jsonl(tmp_path / "不存在.jsonl") == []


def test_read_jsonl_skips_blank_lines(tmp_path):
    path = tmp_path / "r.jsonl"
    path.write_text('{"a": 1}\n\n{"b": 2}\n', encoding="utf-8")
    assert common.read_jsonl(path) == [{"a": 1}, {"b": 2}]


def test_watermark_roundtrip(tmp_path):
    path = tmp_path / "sync_state.json"
    common.set_watermark("arxiv", "2026-08-18", path)
    state = json.loads(path.read_text(encoding="utf-8"))
    assert state["sources"]["arxiv"]["last_fetched"] == "2026-08-18"
    # 第二个来源不应覆盖第一个
    common.set_watermark("openalex", "2026-08-17", path)
    state = json.loads(path.read_text(encoding="utf-8"))
    assert state["sources"]["arxiv"]["last_fetched"] == "2026-08-18"
    assert state["sources"]["openalex"]["last_fetched"] == "2026-08-17"


def test_is_duplicate_near_identical_title():
    existing = ["Agent Harness: A Runtime for LLM Agents"]
    assert common.is_duplicate("agent harness a runtime for llm agents", existing)
    assert common.is_duplicate("Agent Harness — A Runtime for LLM Agents", existing)


def test_is_duplicate_distinct_title():
    existing = ["Agent Harness: A Runtime for LLM Agents"]
    assert not common.is_duplicate("Attention Is All You Need", existing)


def test_slugify():
    assert common.slugify("Agent Harness!") == "agent-harness"
    assert common.slugify("  Context  Manager  ") == "context-manager"


def test_wiki_page_titles_include_existing_pages(tmp_path):
    (tmp_path / "papers").mkdir()
    (tmp_path / "papers" / "react.md").write_text(
        "---\ntitle: ReAct\ntype: paper\n---\n\n正文\n",
        encoding="utf-8",
    )
    (tmp_path / "index.md").write_text("# index\n", encoding="utf-8")
    assert common.wiki_page_titles(tmp_path) == ["ReAct"]

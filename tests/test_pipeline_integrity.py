"""验证原文和人工笔记不被重复操作覆盖，以及分页未完成时的状态。"""
import hashlib
import json
import sys
from pathlib import Path

import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import common
import ingest_source
import fetch_candidates
import import_writing


@pytest.fixture
def isolated(tmp_path, monkeypatch):
    for name, suffix in [("ROOT", ""), ("RAW_DIR", "raw"), ("WIKI_DIR", "wiki"),
                         ("REGISTRY_DIR", "registry"), ("REVIEW_QUEUE_DIR", "review")]:
        monkeypatch.setattr(common, name, tmp_path / suffix)
    return tmp_path


def test_reingest_preserves_notes_and_raw(isolated):
    src = isolated / "source.txt"
    src.write_text("原始内容", encoding="utf-8")
    first = ingest_source.ingest(str(src))
    first["wiki_path"].write_text("人工完善的笔记", encoding="utf-8")
    second = ingest_source.ingest(str(src))
    assert second["status"] == "already_ingested"
    assert first["wiki_path"].read_text(encoding="utf-8") == "人工完善的笔记"
    assert len(common.load_registry("ingested")) == 1


def test_arxiv_versions_have_separate_paths(isolated):
    a = ingest_source.ingest("2608.12345v1", dry_run=True)
    b = ingest_source.ingest("2608.12345v2", dry_run=True)
    assert a["raw_path"] != b["raw_path"]
    assert a["wiki_path"] != b["wiki_path"]


def test_pagination_collects_more_than_one_page(monkeypatch):
    calls = []
    def fake(cfg, since, size):
        page = cfg.get("_offset", 0)
        calls.append(page)
        cfg["_offset"] = page + 1
        cfg["_more"] = page < 2
        return [{"source": "openalex", "source_id": str(page)}]
    monkeypatch.setitem(fetch_candidates.FETCHERS, "openalex", fake)
    records, complete = fetch_candidates.fetch_pages("openalex", {}, "2026-01-01", 1)
    assert len(records) == 3 and complete
    records, complete = fetch_candidates.fetch_pages("openalex", {"max_pages": 2}, None, 1)
    assert len(records) == 2 and not complete


def test_writing_import_is_idempotent_and_marks_draft(isolated):
    text = "读取到的原文片段"
    material = {"title": "文献", "source_url": "https://example.org/paper", "evidence_text": text,
                "content": "本文引用用途", "sha256": hashlib.sha256(text.encode()).hexdigest()}
    path = isolated / "evidence.json"
    path.write_text(json.dumps({"schema_version": 1, "article_confirmed": True, "article_sha256": "abc",
                               "thread_id": "one", "topic": "主题", "materials": [material]}), encoding="utf-8")
    result = import_writing.import_bundle(path)
    queue = Path(result["queue"])
    queue.write_text(queue.read_text(encoding="utf-8") + "\n用户已阅读", encoding="utf-8")
    import_writing.import_bundle(path)
    assert "用户已阅读" in queue.read_text(encoding="utf-8")
    assert len(common.load_registry("ingested")) == 1
    page = next((common.WIKI_DIR / "papers").glob("*.md"))
    assert "status: draft" in page.read_text(encoding="utf-8")

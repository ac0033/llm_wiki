"""将写作证据包导入待读清单和原文片段；不把模型摘要升级为已核验知识。"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common


def import_bundle(path: Path, dry_run: bool = False) -> dict:
    if dry_run:
        return _import_bundle(path, dry_run=True)
    with common.mutation_lock():
        return _import_bundle(path)


def _import_bundle(path: Path, dry_run: bool = False) -> dict:
    bundle = json.loads(path.read_text(encoding="utf-8"))
    if bundle.get("schema_version") != 1 or not bundle.get("article_confirmed"):
        raise ValueError("只导入已确认保存的 schema_version=1 证据包")
    identity = hashlib.sha256((bundle.get("thread_id", "") + bundle["article_sha256"]).encode()).hexdigest()[:20]
    queue = common.REVIEW_QUEUE_DIR / f"writing-{identity}.md"
    if dry_run:
        return {"queue": str(queue), "count": len(bundle.get("materials", []))}
    queue.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# 写作待读：《{bundle['topic']}》", "", "文章已确认保存；来源笔记仍待阅读和核验。勾选表示你已读，不代表事实全部验证。", ""]
    existing = {r.get("url"): r for r in common.load_registry("ingested")}
    import frontmatter
    for page in common.WIKI_DIR.rglob("*.md"):
        try:
            meta = frontmatter.load(page)
            # 只有单来源资料页才视作该文献已收录，概念页列出的参考文献不算已入库。
            if meta.get("type") == "paper" and meta.get("canonical_url"):
                existing.setdefault(meta["canonical_url"], {"slug": page.stem})
        except Exception:
            continue
    for m in bundle.get("materials", []):
        url, text = m.get("source_url", ""), m.get("evidence_text", "")
        if not url.startswith(("https://", "http://")) or not text:
            continue
        key = hashlib.sha256(url.encode()).hexdigest()[:16]
        digest = hashlib.sha256(text.encode()).hexdigest()
        if m.get("sha256") != digest:
            raise ValueError("原文片段指纹不匹配，拒绝导入")
        raw = common.RAW_DIR / "articles" / f"writing-{key}-{digest[:12]}.txt"
        raw.parent.mkdir(parents=True, exist_ok=True)
        if not raw.exists():
            raw.write_text(text, encoding="utf-8")
        slug = f"writing-{key}"
        wiki = common.WIKI_DIR / "papers" / f"{slug}.md"
        if url not in existing and not wiki.exists():
            meta = {"type": "paper", "title": m.get("title") or url, "status": "draft", "topics": ["writing"],
                    "ingested": common.today(), "last_verified": common.today(), "source_count": 1,
                    "quality": "medium", "confidence": "low", "canonical_url": url, "evidence_sources": [url]}
            import yaml
            wiki.parent.mkdir(parents=True, exist_ok=True)
            wiki.write_text("---\n" + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False) + "---\n\n"
                            + f"# {meta['title']}\n\n待阅读核验。last_verified 仅为登记日期，尚未核验论断。\n\n"
                            + f"原文片段：`{raw.relative_to(common.ROOT).as_posix()}`（可能截断，并非全文快照）。\n\n"
                            + "## 对写作的用途（模型整理，待核验）\n\n" + m.get("content", "") + "\n", encoding="utf-8")
        if url not in existing:
            entry = {"source": "writing", "source_id": url, "url": url, "slug": slug,
                     "title": m.get("title") or url, "ingested_at": common.now_iso()}
            common.append_jsonl(common.registry_path("ingested"), entry)
            existing[url] = entry
        lines.extend([f"- [ ] [{m.get('title') or url}]({url})", f"  - 用途：{m.get('content', '')}",
                      f"  - 原文片段：{raw.relative_to(common.ROOT).as_posix()}"])
    if not queue.exists():
        queue.write_text("\n".join(lines) + "\n", encoding="utf-8")
    from compile_index import build_index
    (common.WIKI_DIR / "index.md").write_text(build_index(common.WIKI_DIR), encoding="utf-8")
    return {"queue": str(queue)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    print(json.dumps(import_bundle(args.bundle, args.dry_run), ensure_ascii=False))

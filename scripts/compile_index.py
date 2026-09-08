"""compile_index.py — 扫描 wiki/**/*.md 的 frontmatter，重建 wiki/index.md。

用法：
    uv run python scripts/compile_index.py [--dry-run]

index.md 的结构：按页面类型分组，组内按 last_verified 降序列出 wikilink。
首页头部与尾部若有人工维护内容，放在 <!-- INDEX:BEGIN --> / <!-- INDEX:END --> 标记之外；
脚本只重建标记之间的部分。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import frontmatter  # noqa: E402

import common  # noqa: E402

INDEX_BEGIN = "<!-- INDEX:BEGIN -->"
INDEX_END = "<!-- INDEX:END -->"

TYPE_ORDER = [
    ("overview", "总览"),
    ("direction", "研究方向"),
    ("concept", "概念"),
    ("system", "系统"),
    ("paper", "论文"),
    ("benchmark", "基准"),
    ("comparison", "对比"),
    ("question", "研究问题"),
    ("digest", "每周文摘"),
]


def scan_pages(wiki_dir: Path) -> list[dict]:
    pages = []
    for md in sorted(wiki_dir.rglob("*.md")):
        if md.name == "index.md" or md.name == "log.md":
            continue
        try:
            post = frontmatter.load(md)
        except Exception:
            continue
        slug = post.get("slug") or md.stem
        pages.append({
            "slug": slug,
            "title": post.get("title", md.stem),
            "type": post.get("type", ""),
            "status": post.get("status", ""),
            "last_verified": str(post.get("last_verified", "")),
            "path": md,
        })
    return pages


def render_index(pages: list[dict]) -> str:
    lines = [INDEX_BEGIN, "", f"共 {len(pages)} 个页面。本区块由 compile_index.py 重建，勿手改。", ""]
    for ptype, label in TYPE_ORDER:
        group = [p for p in pages if p["type"] == ptype]
        if not group:
            continue
        lines.append(f"## {label}（{len(group)}）")
        lines.append("")
        for p in sorted(group, key=lambda x: x["last_verified"], reverse=True):
            suffix = "（草稿）" if p["status"] == "draft" else ""
            lines.append(f"- [[{p['slug']}]] — {p['title']}{suffix}")
        lines.append("")
    untyped = [p for p in pages if p["type"] not in dict(TYPE_ORDER)]
    if untyped:
        lines.append("## 未分类")
        lines.append("")
        for p in untyped:
            lines.append(f"- [[{p['slug']}]] — {p['title']}")
        lines.append("")
    lines.append(INDEX_END)
    return "\n".join(lines)


def build_index(wiki_dir: Path) -> str:
    index_path = wiki_dir / "index.md"
    block = render_index(scan_pages(wiki_dir))
    if index_path.exists():
        text = index_path.read_text(encoding="utf-8")
        if INDEX_BEGIN in text and INDEX_END in text:
            head = text.split(INDEX_BEGIN, 1)[0]
            tail = text.split(INDEX_END, 1)[1]
            return head + block + tail
        return text.rstrip() + "\n\n" + block + "\n"
    return f"# 知识库索引\n\n{block}\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="扫描 frontmatter 重建 wiki/index.md")
    parser.add_argument("--dry-run", action="store_true", help="只打印结果不写文件")
    args = parser.parse_args()

    new_index = build_index(common.WIKI_DIR)
    if args.dry_run:
        print(new_index)
        return 0
    (common.WIKI_DIR / "index.md").write_text(new_index, encoding="utf-8")
    print(f"[done] 已重建 {common.WIKI_DIR / 'index.md'}")
    return 0


if __name__ == "__main__":
    if "--dry-run" in sys.argv:
        raise SystemExit(main())
    with common.mutation_lock():
        raise SystemExit(main())

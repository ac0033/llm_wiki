"""ingest_source.py — 单篇入库：支持 arXiv ID / DOI / URL / 本地文件。

用法：
    uv run python scripts/ingest_source.py 2501.12345
    uv run python scripts/ingest_source.py 10.48550/arXiv.2501.12345
    uv run python scripts/ingest_source.py https://example.com/blog-post
    uv run python scripts/ingest_source.py raw/papers/some.pdf
    uv run python scripts/ingest_source.py --dry-run 2501.12345

行为：
- 下载/读取原文，抽取文本存到 raw/（papers 或 articles 子目录）；
- 在 wiki/ 对应子目录生成 frontmatter 完备的草稿页（正文由 LLM 按 prompts/ingest_source.md 补全）；
- 登记 data/registry/ingested.jsonl；--dry-run 只打印计划动作，不写任何文件。
"""
from __future__ import annotations

import argparse
import re
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import httpx  # noqa: E402
from tenacity import retry, stop_after_attempt, wait_exponential  # noqa: E402

import common  # noqa: E402

ARXIV_ID_RE = re.compile(r"^(\d{4}\.\d{4,5})(v\d+)?$")
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")


def detect_kind(source: str) -> str:
    """识别输入来源类型：arxiv / doi / url / local_file。"""
    if ARXIV_ID_RE.match(source):
        return "arxiv"
    if DOI_RE.match(source):
        return "doi"
    if source.startswith(("http://", "https://")):
        if "arxiv.org/abs/" in source:
            m = ARXIV_ID_RE.match(source.rsplit("/abs/", 1)[-1])
            if m:
                return "arxiv"
        return "url"
    if Path(source).exists():
        return "local_file"
    raise ValueError(f"无法识别来源类型：{source}")


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=20))
def _download(url: str) -> httpx.Response:
    resp = httpx.get(url, timeout=60.0, follow_redirects=True)
    resp.raise_for_status()
    return resp


def extract_pdf_text(pdf_bytes: bytes, max_pages: int = 3) -> str:
    """用 PyMuPDF 抽取前几页文本，用于生成草稿页的元信息。"""
    import fitz  # PyMuPDF

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = []
    for page in doc[:max_pages]:
        text.append(page.get_text())
    doc.close()
    return "\n".join(text)


def extract_html_text(html: str, url: str) -> str:
    """用 trafilatura 抽取网页正文。"""
    import trafilatura

    return trafilatura.extract(html, url=url) or ""


def make_draft_page(slug: str, title: str, page_type: str, source_url: str, date_str: str) -> str:
    return f"""---
type: {page_type}
title: "{title.replace('"', "'")}"
aliases: [{slug}]
status: draft
topics: []
harness_components: []
ingested: {date_str}
last_verified: {date_str}
source_count: 1
quality: medium
confidence: low
canonical_url: {source_url}
evidence_sources:
  - {source_url}
---

# {title}

> 本页为 ingest_source.py 自动生成的草稿，正文待按 prompts/ingest_source.md 补全。

- 一手来源：{source_url}
- 摘要：待补全
- 要点：待补全
- 与本库的关系：待补全（例如与 [[agent-harness]] 的关联）
"""


def ingest(source: str, dry_run: bool = False) -> dict:
    if dry_run:
        return _ingest(source, dry_run=True)
    with common.mutation_lock():
        return _ingest(source)


def _ingest(source: str, dry_run: bool = False) -> dict:
    kind = detect_kind(source)
    date_str = common.today()
    print(f"[detect] 类型={kind}")

    if kind == "arxiv":
        arxiv_id = ARXIV_ID_RE.match(source) or ARXIV_ID_RE.match(source.rsplit("/abs/", 1)[-1])
        arxiv_id = arxiv_id.group(0)  # v1/v2 分开保存，不能用新版覆盖旧快照
        abs_url = f"https://arxiv.org/abs/{arxiv_id}"
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}"
        raw_path = common.RAW_DIR / "papers" / f"arxiv-{arxiv_id}.pdf"
        slug = f"arxiv-{arxiv_id.replace('.', '-')}"
        title = f"arXiv {arxiv_id}"
        page_type = "paper"
        source_url = abs_url
        payload = ("pdf", pdf_url)

    elif kind == "doi":
        doi_url = f"https://doi.org/{source}"
        slug = f"doi-{common.slugify(source)}"
        raw_path = common.RAW_DIR / "articles" / f"{slug}.md"
        title = f"DOI {source}"
        page_type = "paper"
        source_url = doi_url
        payload = ("html", doi_url)

    elif kind == "url":
        slug = common.slugify(source.split("//", 1)[-1])[:48] + "-" + hashlib.sha256(source.encode()).hexdigest()[:12]
        raw_path = common.RAW_DIR / "articles" / f"{slug}.md"
        title = source
        page_type = "paper"
        source_url = source
        payload = ("html", source)

    else:  # local_file
        src = Path(source)
        slug = common.slugify(src.stem)
        suffix = src.suffix.lower()
        subdir = "papers" if suffix == ".pdf" else "articles"
        raw_path = common.RAW_DIR / subdir / f"{slug}{suffix}"
        title = src.stem
        page_type = "paper"
        source_url = f"local://{src.as_posix()}"
        payload = ("local", src)

    wiki_path = common.WIKI_DIR / "papers" / f"{slug}.md"

    plan = {
        "kind": kind,
        "slug": slug,
        "raw_path": raw_path,
        "wiki_path": wiki_path,
        "source_url": source_url,
    }
    if dry_run:
        print(f"[dry-run] 计划动作：raw → {raw_path}；草稿页 → {wiki_path}；登记 ingested.jsonl")
        return plan

    registered = common.load_registry("ingested")
    previous = next((r for r in registered if r.get("url") == source_url), None)
    if previous:
        # 已登记来源不重写用户已经完善的笔记；重试使用同一结果。
        plan["status"] = "already_ingested"
        print(f"[skip] 来源已入库：{previous.get('slug', slug)}")
        return plan

    # 1. 落地 raw 素材
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    if payload[0] == "pdf":
        content = raw_path.read_bytes() if raw_path.exists() else _download(payload[1]).content
        if not raw_path.exists():
            raw_path.write_bytes(content)
        preview = extract_pdf_text(content)
    elif payload[0] == "html":
        if raw_path.exists():
            text = raw_path.read_text(encoding="utf-8")
        else:
            resp = _download(payload[1])
            text = extract_html_text(resp.text, payload[1])
            # 同时保留原始 HTML，抽取文本只是阅读副本。
            html_path = raw_path.with_suffix(".html")
            if not html_path.exists():
                html_path.write_text(resp.text, encoding="utf-8")
            raw_path.write_text(text or resp.text, encoding="utf-8")
        preview = text[:2000]
    else:
        src = Path(payload[1])
        if raw_path.exists() and raw_path.read_bytes() != src.read_bytes():
            raise ValueError("同名原始素材内容不同，请换名称入库，不能覆盖旧快照")
        if not raw_path.exists():
            raw_path.write_bytes(src.read_bytes())
        preview = extract_pdf_text(src.read_bytes()) if src.suffix.lower() == ".pdf" else ""

    # 2. 尝试从预览文本里提取标题（失败则保留占位标题）
    if preview:
        first_line = next((ln.strip() for ln in preview.splitlines() if len(ln.strip()) > 10), None)
        if first_line:
            title = first_line[:120]

    # 3. 生成 wiki 草稿页
    wiki_path.parent.mkdir(parents=True, exist_ok=True)
    if not wiki_path.exists():
        wiki_path.write_text(make_draft_page(slug, title, page_type, source_url, date_str), encoding="utf-8")

    # 4. 登记 registry
    common.append_jsonl(common.registry_path("ingested"), {
        "source": kind,
        "source_id": source,
        "title": title,
        "url": source_url,
        "slug": slug,
        "ingested_at": common.now_iso(),
    })

    print(f"[done] raw → {raw_path}")
    print(f"[done] 草稿页 → {wiki_path}（正文待 LLM 按 prompts/ingest_source.md 补全）")
    print(f"[done] 已登记 data/registry/ingested.jsonl")
    return plan


def main() -> int:
    parser = argparse.ArgumentParser(description="单篇入库：arXiv ID / DOI / URL / 本地文件")
    parser.add_argument("source", help="arXiv ID、DOI、URL 或本地文件路径")
    parser.add_argument("--dry-run", action="store_true", help="只打印计划动作，不写任何文件")
    args = parser.parse_args()
    try:
        ingest(args.source, dry_run=args.dry_run)
    except Exception as exc:
        print(f"[error] 入库失败：{exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

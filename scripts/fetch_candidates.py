"""fetch_candidates.py — 从 arXiv / OpenAlex / Semantic Scholar 抓取候选文献。

用法：
    uv run python scripts/fetch_candidates.py --source arxiv --since 2026-08-01 --limit 20 --dry-run
    uv run python scripts/fetch_candidates.py            # 全部启用的来源，按水位线增量抓取

行为：
- 默认读取 data/state/sync_state.json 中各来源的 watermark（上次抓取时间），只取新内容；
- --since 覆盖 watermark；--limit 限制每个来源的条数；--dry-run 只打印不写 registry、不推进水位线；
- 抓取结果追加到 data/registry/candidates.jsonl，抓取成功后推进 watermark。
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import feedparser  # noqa: E402
import httpx  # noqa: E402
from tenacity import retry, stop_after_attempt, wait_exponential  # noqa: E402

import common  # noqa: E402


def _http_get(url: str, params: dict, headers: dict | None = None) -> httpx.Response:
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=20))
    def _get() -> httpx.Response:
        resp = httpx.get(url, params=params, headers=headers, timeout=30.0, follow_redirects=True)
        resp.raise_for_status()
        return resp

    return _get()


def fetch_arxiv(cfg: dict, since: str | None, limit: int) -> list[dict]:
    """arXiv Atom API，按 submittedDate 降序取最新条目。"""
    query = cfg.get("query", "")
    per_request = min(limit, cfg.get("max_results_per_request", 100))
    resp = _http_get(
        cfg["base_url"],
        {
            "search_query": query,
            "start": 0,
            "max_results": per_request,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        },
    )
    feed = feedparser.parse(resp.text)
    out = []
    for entry in feed.entries:
        published = (entry.get("published") or "")[:10]
        if since and published and published < since:
            continue
        arxiv_id = entry.get("id", "").rsplit("/abs/", 1)[-1]
        out.append({
            "source": "arxiv",
            "source_id": arxiv_id,
            "title": " ".join((entry.get("title") or "").split()),
            "authors": [a.get("name", "") for a in entry.get("authors", [])],
            "abstract": " ".join((entry.get("summary") or "").split()),
            "url": entry.get("id", ""),
            "published": published,
        })
    return out


def fetch_openalex(cfg: dict, since: str | None, limit: int) -> list[dict]:
    """OpenAlex Works API，用 from_publication_date 做增量过滤。"""
    params = {
        "search": cfg.get("query", ""),
        "per-page": min(limit, cfg.get("per_page", 50)),
        "sort": "publication_date:desc",
    }
    if since:
        params["filter"] = f"from_publication_date:{since}"
    if cfg.get("mailto"):
        params["mailto"] = cfg["mailto"]
    data = _http_get(cfg["base_url"], params).json()
    out = []
    for work in data.get("results", []):
        doi = work.get("doi") or ""
        out.append({
            "source": "openalex",
            "source_id": work.get("id", ""),
            "title": work.get("title") or "",
            "authors": [a.get("author", {}).get("display_name", "") for a in work.get("authorships", [])],
            "abstract": _openalex_abstract(work),
            "url": doi or work.get("id", ""),
            "published": work.get("publication_date") or "",
        })
    return out


def _openalex_abstract(work: dict) -> str:
    """OpenAlex 的摘要是倒排索引（inverted index），需要还原成连续文本。"""
    inv = work.get("abstract_inverted_index") or {}
    if not inv:
        return ""
    positions: list[tuple[int, str]] = []
    for word, idxs in inv.items():
        for i in idxs:
            positions.append((i, word))
    return " ".join(w for _, w in sorted(positions))


def fetch_semantic_scholar(cfg: dict, since: str | None, limit: int) -> list[dict]:
    """Semantic Scholar Graph API；该 API 无服务端日期过滤，本地按 since 过滤。

    未认证请求很容易遇到 429。需要启用该来源时，先设置
    SEMANTIC_SCHOLAR_API_KEY，再把 config/sources.yml 中 semantic_scholar.enabled
    改为 true。
    """
    headers = {}
    api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
    if api_key:
        headers["x-api-key"] = api_key
    data = _http_get(
        cfg["base_url"],
        {
            "query": cfg.get("query", ""),
            "limit": min(limit, cfg.get("per_page", 50)),
            "fields": cfg.get("fields", "title,abstract,authors,url,externalIds,publicationDate"),
        },
        headers=headers or None,
    ).json()
    out = []
    for paper in data.get("data", []):
        published = paper.get("publicationDate") or ""
        if since and published and published < since:
            continue
        ext = paper.get("externalIds") or {}
        out.append({
            "source": "semantic_scholar",
            "source_id": paper.get("paperId", ""),
            "title": paper.get("title") or "",
            "authors": [a.get("name", "") for a in paper.get("authors", [])],
            "abstract": paper.get("abstract") or "",
            "url": paper.get("url") or "",
            "published": published,
            "arxiv_id": ext.get("ArXiv"),
            "doi": ext.get("DOI"),
        })
    return out


FETCHERS = {
    "arxiv": fetch_arxiv,
    "openalex": fetch_openalex,
    "semantic_scholar": fetch_semantic_scholar,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="抓取候选文献")
    parser.add_argument("--source", choices=[*FETCHERS.keys(), "all"], default="all")
    parser.add_argument("--since", help="只取该日期（YYYY-MM-DD）之后的条目，覆盖 watermark")
    parser.add_argument("--limit", type=int, default=50, help="每个来源最多抓取条数")
    parser.add_argument("--dry-run", action="store_true", help="只打印结果，不写 registry、不推进 watermark")
    args = parser.parse_args()

    cfg_all = common.load_sources_config()
    sources_cfg = cfg_all.get("sources", {})
    watermark_path = common.ROOT / cfg_all.get("watermark_file", "data/state/sync_state.json")

    names = list(FETCHERS) if args.source == "all" else [args.source]
    total_new = 0
    for name in names:
        cfg = sources_cfg.get(name, {})
        if not cfg.get("enabled", False):
            print(f"[skip] {name} 未启用")
            continue
        since = args.since or common.get_watermark(name)
        print(f"[fetch] {name} since={since or '(首次全量)'} limit={args.limit}")
        try:
            records = FETCHERS[name](cfg, since, args.limit)
        except Exception as exc:  # 网络/解析失败不阻断其他来源
            print(f"[error] {name} 抓取失败：{exc}", file=sys.stderr)
            continue

        for r in records:
            r["fetched_at"] = common.now_iso()
            r["status"] = "new"

        if args.dry_run:
            for r in records:
                print(f"  [dry-run] {r['published']} {r['title'][:80]} <{r['url']}>")
        else:
            for r in records:
                common.append_jsonl(common.registry_path("candidates"), r)
            common.set_watermark(name, datetime.now(timezone.utc).date().isoformat(), watermark_path)
        print(f"[done] {name}: {len(records)} 条")
        total_new += len(records)

    print(f"合计新增候选 {total_new} 条{'（dry-run，未写盘）' if args.dry_run else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

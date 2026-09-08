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
from datetime import datetime, timezone, timedelta
import time
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
    categories = cfg.get("categories", [])
    if categories:
        query = f"({query}) AND (" + " OR ".join(f"cat:{c}" for c in categories) + ")"
    if since:
        query = f"({query}) AND submittedDate:[{since.replace('-', '')}0000 TO 999912312359]"
    per_request = min(limit, cfg.get("max_results_per_request", 100))
    resp = _http_get(
        cfg["base_url"],
        {
            "search_query": query,
            "start": cfg.get("_offset", 0),
            "max_results": per_request,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        },
    )
    feed = feedparser.parse(resp.text)
    if feed.get("bozo") or any("/api/errors" in e.get("id", "") for e in feed.entries):
        raise ValueError("arXiv 返回错误或无法解析的响应")
    cfg["_more"] = len(feed.entries) == per_request
    cfg["_offset"] = cfg.get("_offset", 0) + len(feed.entries)
    if since and any((e.get("published") or "")[:10] < since for e in feed.entries):
        cfg["_more"] = False
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
        "cursor": cfg.get("_cursor", "*"),
        "sort": "publication_date:desc",
    }
    if since:
        params["filter"] = f"from_publication_date:{since}"
    if cfg.get("mailto"):
        params["mailto"] = cfg["mailto"]
    data = _http_get(cfg["base_url"], params).json()
    if "results" not in data or "meta" not in data:
        raise ValueError("OpenAlex 响应缺少结果或分页元数据")
    next_cursor = data["meta"].get("next_cursor")
    cfg["_more"] = bool(data["results"] and next_cursor and next_cursor != cfg.get("_cursor"))
    cfg["_cursor"] = next_cursor
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
            "offset": cfg.get("_offset", 0),
            "fields": cfg.get("fields", "title,abstract,authors,url,externalIds,publicationDate"),
        },
        headers=headers or None,
    ).json()
    if "data" not in data:
        raise ValueError("Semantic Scholar 响应缺少 data")
    cfg["_more"] = data.get("next") is not None
    cfg["_offset"] = data.get("next", 0)
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


def fetch_pages(name: str, cfg: dict, since: str | None, page_size: int) -> tuple[list[dict], bool]:
    """达到页数上限时明确返回未完成，不能推进水位；提高上限可继续覆盖窗口。"""
    if page_size <= 0:
        raise ValueError("limit 必须大于 0")
    paging = dict(cfg)
    records, seen = [], set()
    for page in range(cfg.get("max_pages", 20)):
        if page and name == "arxiv":
            time.sleep(cfg.get("request_interval_seconds", 3))
        batch = FETCHERS[name](paging, since, page_size)
        for r in batch:
            key = (r.get("source"), r.get("source_id"))
            if key not in seen:
                records.append(r)
                seen.add(key)
        if not paging.get("_more"):
            return records, True
    return records, False


def main() -> int:
    parser = argparse.ArgumentParser(description="抓取候选文献")
    parser.add_argument("--source", choices=[*FETCHERS.keys(), "all"], default="all")
    parser.add_argument("--since", help="只取该日期（YYYY-MM-DD）之后的条目，覆盖 watermark")
    parser.add_argument("--limit", type=int, default=50, help="每页条数；自动翻页到完成或配置的 max_pages 上限")
    parser.add_argument("--dry-run", action="store_true", help="只打印结果，不写 registry、不推进 watermark")
    args = parser.parse_args()

    cfg_all = common.load_sources_config()
    sources_cfg = cfg_all.get("sources", {})
    watermark_path = common.ROOT / cfg_all.get("watermark_file", "data/state/sync_state.json")

    names = list(FETCHERS) if args.source == "all" else [args.source]
    total_new = 0
    incomplete = False
    known = {(r.get("source"), r.get("source_id")) for r in common.load_registry("candidates")}
    for name in names:
        cfg = sources_cfg.get(name, {})
        if not cfg.get("enabled", False):
            print(f"[skip] {name} 未启用")
            continue
        since = args.since or common.get_watermark(name, common.load_sync_state(watermark_path))
        if since and not args.since:
            since = (datetime.fromisoformat(since) - timedelta(days=cfg.get("lookback_days", 7))).date().isoformat()
        started_at = datetime.now(timezone.utc).date().isoformat()
        print(f"[fetch] {name} since={since or '(首次全量)'} limit={args.limit}")
        try:
            records, complete = fetch_pages(name, cfg, since, args.limit)
        except Exception as exc:  # 网络/解析失败不阻断其他来源
            print(f"[error] {name} 抓取失败：{exc}", file=sys.stderr)
            incomplete = True
            continue

        if not complete:
            incomplete = True
            print(f"[incomplete] {name} 达到页数上限，已保留结果但不推进水位", file=sys.stderr)
        records = [r for r in records if (r.get("source"), r.get("source_id")) not in known]
        for r in records:
            r["fetched_at"] = common.now_iso()
            r["status"] = "new"

        if args.dry_run:
            for r in records:
                print(f"  [dry-run] {r['published']} {r['title'][:80]} <{r['url']}>")
        else:
            for r in records:
                common.append_jsonl(common.registry_path("candidates"), r)
            if complete:
                common.set_watermark(name, started_at, watermark_path)
        print(f"[done] {name}: {len(records)} 条")
        total_new += len(records)

    print(f"合计新增候选 {total_new} 条{'（dry-run，未写盘）' if args.dry_run else ''}")
    return 1 if incomplete else 0


if __name__ == "__main__":
    if "--dry-run" in sys.argv:
        raise SystemExit(main())
    with common.mutation_lock():
        raise SystemExit(main())

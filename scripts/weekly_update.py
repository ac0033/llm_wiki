"""weekly_update.py — 每周更新：去重、评分、分流、生成 review queue 与 digest。

用法：
    uv run python scripts/weekly_update.py [--date 2026-08-18]
    uv run python scripts/weekly_update.py --dry-run --limit 20

行为：
1. 读取 data/registry/candidates.jsonl 中 status == "new" 的候选；
2. 与 data/registry/ingested.jsonl 及同批候选做标题去重（rapidfuzz 相似度）；
3. 按 config/quality-rubric.yml 与 config/directions/*.yml 的关键词打分；
4. 分流：auto_include → digest 正文 + review queue；review → review queue；dropped → 仅回写状态；
5. 非 dry-run 时生成 data/review_queue/weekly-YYYY-MM-DD.md 与 wiki/digests/weekly-YYYY-MM-DD.md，
   把评分/状态回写 candidates.jsonl，并追加 wiki/log.md。

候选抓取由 scripts/fetch_candidates.py 完成；weekly_compile.ps1 会先调用 fetch_candidates，
再调用本脚本。这样抓取与评分两个确定性步骤可以分别测试和复跑。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import common  # noqa: E402


def dedupe_and_score(candidates: list[dict], ingested: list[dict], rubric: dict, keywords: list[str]) -> list[dict]:
    """原地给候选打 status/score 标记并返回处理后的列表。"""
    known_titles = [r.get("title", "") for r in ingested] + common.wiki_page_titles()
    seen_titles: list[str] = []
    for cand in candidates:
        title = cand.get("title", "")
        if is_dup_of_known(title, known_titles):
            cand["status"] = "duplicate_of_ingested"
            continue
        if common.is_duplicate(title, seen_titles):
            cand["status"] = "duplicate_in_batch"
            continue
        seen_titles.append(title)
        cand["score"] = common.score_candidate(cand, rubric, keywords)
        cand["status"] = common.classify_score(cand["score"], rubric)
    return candidates


def is_dup_of_known(title: str, known_titles: list[str]) -> bool:
    return common.is_duplicate(title, known_titles)


def render_review_queue(date_str: str, items: list[dict]) -> str:
    lines = [
        f"# 复核清单 {date_str}",
        "",
        "以下候选由 fetch_candidates.py + weekly_update.py 自动生成。weekly_compile 阶段的 Kimi Code CLI 可以补推荐理由，但不能改动评分和分流结果。",
        "",
    ]
    auto = [c for c in items if c.get("status") == "auto_include"]
    review = [c for c in items if c.get("status") == "review"]
    for section, group in (("高分候选（>= auto_include 阈值）", auto), ("待复核候选", review)):
        lines.append(f"## {section}")
        lines.append("")
        if not group:
            lines.append("（无）")
        for c in sorted(group, key=lambda x: -x.get("score", 0)):
            lines.append(f"- [ ] **{c.get('title', '')}**（{c.get('source')}，{c.get('published', '日期待验证')}，score={c.get('score')}）")
            lines.append(f"  - {c.get('url', '')}")
            abstract = (c.get("abstract") or "")[:300]
            if abstract:
                lines.append(f"  - 摘要（截断）：{abstract}…")
        lines.append("")
    return "\n".join(lines)


def render_digest(date_str: str, items: list[dict]) -> str:
    auto = sorted([c for c in items if c.get("status") == "auto_include"], key=lambda x: -x.get("score", 0))
    lines = [
        "---",
        "type: digest",
        f"title: 每周候选文摘 {date_str}",
        f"aliases: [weekly-{date_str}]",
        "status: draft",
        "topics: [weekly, digest, agent-harness]",
        f"ingested: {date_str}",
        f"last_verified: {date_str}",
        "source_count: 0",
        "quality: medium",
        "confidence: medium",
        "---",
        "",
        f"# 每周候选文摘 {date_str}",
        "",
        f"本周自动抓取并初筛出 {len(auto)} 条高分候选。分析性评述由 weekly_compile 流程补充。",
        "",
    ]
    for c in auto:
        lines.append(f"## {c.get('title', '')}（score={c.get('score')}）")
        lines.append("")
        lines.append(f"- 来源：{c.get('source')}，发表日期：{c.get('published', '待验证')}")
        lines.append(f"- 链接：{c.get('url', '')}")
        lines.append(f"- 摘要（截断）：{(c.get('abstract') or '')[:300]}…")
        lines.append("- 评述：待补充")
        lines.append("")
    if not auto:
        lines.append("（本周无高分候选）")
    return "\n".join(lines)


def append_log(date_str: str, counts: dict[str, int], queue_path: Path, digest_path: Path) -> None:
    log_path = common.WIKI_DIR / "log.md"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if not log_path.exists():
        log_path.write_text("# 维护日志\n", encoding="utf-8")
    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"\n## [{date_str}] weekly_update | candidates={counts} | queue={queue_path.name} | digest={digest_path.name}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="每周更新：去重、评分、生成 review queue 与 digest")
    parser.add_argument("--date", default=common.today(), help="本次更新的日期标签，默认今天")
    parser.add_argument("--limit", type=int, help="最多处理多少条新候选")
    parser.add_argument("--dry-run", action="store_true", help="只打印分流结果，不回写 registry、不生成文件")
    args = parser.parse_args()

    candidates_path = common.registry_path("candidates")
    candidates = common.load_registry("candidates")
    ingested = common.load_registry("ingested")
    rubric = common.load_rubric()
    keywords = common.direction_keywords()

    new_items = [c for c in candidates if c.get("status") == "new"]
    if args.limit is not None:
        new_items = new_items[: args.limit]
    print(f"待处理新候选 {len(new_items)} 条（registry 共 {len(candidates)} 条）")
    if not new_items:
        print("没有新候选，退出。")
        return 0

    dedupe_and_score(new_items, ingested, rubric, keywords)
    counts: dict[str, int] = {}
    for c in new_items:
        counts[c["status"]] = counts.get(c["status"], 0) + 1

    queue_path = common.REVIEW_QUEUE_DIR / f"weekly-{args.date}.md"
    digest_path = common.WIKI_DIR / "digests" / f"weekly-{args.date}.md"

    if args.dry_run:
        print(f"[dry-run] 分流结果：{counts}")
        print(f"[dry-run] 将生成复核清单：{queue_path}")
        print(f"[dry-run] 将生成每周文摘：{digest_path}")
        return 0

    common.write_jsonl(candidates_path, candidates)
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    queue_path.write_text(render_review_queue(args.date, new_items), encoding="utf-8")
    digest_path.parent.mkdir(parents=True, exist_ok=True)
    digest_path.write_text(render_digest(args.date, new_items), encoding="utf-8")
    append_log(args.date, counts, queue_path, digest_path)

    print(f"分流结果：{counts}")
    print(f"复核清单：{queue_path}")
    print(f"每周文摘：{digest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

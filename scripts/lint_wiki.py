"""lint_wiki.py — wiki 体检。

检查项：
1. schema：frontmatter 必填字段齐全、type/status 取值合法、日期格式合法；
2. 坏链：正文中的 [[wikilink]] 目标在库内无对应页面文件名 slug；
3. 重复：文件名 slug 或 title 重复；
4. 孤儿页：没有任何其他页面链接到它（index.md 与 digest 除外）；
5. 缺 URL：paper / system / benchmark 类型必须有 canonical_url 或 evidence_sources；
6. 概念证据不足：concept 类型没有来源为 error；单来源但状态不是 seed/draft/needs_review 为 warning；
7. stale：last_verified 距今超过 90 天（warning 级）。

用法：
    uv run python scripts/lint_wiki.py [--warnings-as-errors]

error 级问题导致退出码 1；warning 默认不导致失败。
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import frontmatter  # noqa: E402

import common  # noqa: E402

WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass
class Issue:
    level: str  # "error" | "warning"
    check: str
    path: str
    message: str

    def __str__(self) -> str:
        return f"[{self.level}] {self.check}: {self.path}: {self.message}"


def lint_wiki(wiki_dir: Path, today: date | None = None) -> list[Issue]:
    today = today or date.today()
    issues: list[Issue] = []
    pages: list[dict] = []

    md_files = [p for p in sorted(wiki_dir.rglob("*.md")) if p.name not in ("index.md", "log.md")]

    for md in md_files:
        rel = md.relative_to(wiki_dir).as_posix()
        try:
            post = frontmatter.load(md)
        except Exception as exc:
            issues.append(Issue("error", "schema", rel, f"frontmatter 解析失败：{exc}"))
            continue
        meta = dict(post.metadata)
        body = post.content
        slug = str(meta.get("slug") or md.stem)
        pages.append({
            "slug": slug,
            "path": rel,
            "meta": meta,
            "links": set(m.group(1).strip() for m in WIKILINK_RE.finditer(body)),
        })

        # 1. schema
        for field in common.REQUIRED_FRONTMATTER:
            if field not in meta:
                issues.append(Issue("error", "schema", rel, f"缺少必填字段 {field}"))
        ptype = meta.get("type")
        if ptype and ptype not in common.PAGE_TYPES:
            issues.append(Issue("error", "schema", rel, f"非法 type：{ptype}"))
        status = meta.get("status")
        if status and status not in common.STATUS_VALUES:
            issues.append(Issue("error", "schema", rel, f"非法 status：{status}"))
        for field in ("ingested", "last_verified"):
            value = str(meta.get(field, ""))
            if value and not DATE_RE.match(value):
                issues.append(Issue("error", "schema", rel, f"{field} 不是 YYYY-MM-DD：{value}"))
        for field in ("topics", "harness_components", "evidence_sources"):
            if field in meta and not isinstance(meta.get(field), list):
                issues.append(Issue("error", "schema", rel, f"{field} 必须是列表"))

        evidence_sources = meta.get("evidence_sources") or []
        canonical_url = str(meta.get("canonical_url") or "").strip()
        declared_count = meta.get("source_count")
        if declared_count is not None and not isinstance(declared_count, int):
            issues.append(Issue("error", "schema", rel, "source_count 必须是整数"))

        # 5. 缺 URL：paper / system / benchmark 至少要有一手来源
        if ptype in common.URL_REQUIRED_TYPES and not canonical_url and len(evidence_sources) < 1:
            issues.append(Issue("error", "missing_url", rel,
                                f"{ptype} 类型必须提供 canonical_url 或 evidence_sources"))

        # 6. 概念证据：可以先用 seed/draft 标记单来源概念，但不能没有来源
        if ptype == "concept":
            evidence_count = len(evidence_sources) or (1 if canonical_url else 0)
            if evidence_count < 1:
                issues.append(Issue("error", "weak_concept", rel, "concept 类型没有任何来源"))
            elif evidence_count < common.CONCEPT_MIN_SOURCES and status not in ("seed", "draft", "needs_review"):
                issues.append(Issue("warning", "weak_concept", rel,
                                    f"concept 类型来源少于 {common.CONCEPT_MIN_SOURCES} 条，建议标 seed/needs_review 或补充来源"))

        # 7. stale
        last_verified = str(meta.get("last_verified", ""))
        if DATE_RE.match(last_verified):
            try:
                age = (today - date.fromisoformat(last_verified)).days
            except ValueError:
                issues.append(Issue("error", "schema", rel, "last_verified 不是有效日历日期"))
                continue
            if age > common.STALE_DAYS:
                issues.append(Issue("warning", "stale", rel, f"last_verified 已 {age} 天（>{common.STALE_DAYS} 天）"))

    existing_slugs = {p["slug"] for p in pages}

    # 2. 坏链
    for page in pages:
        for target in sorted(page["links"]):
            if target not in existing_slugs:
                issues.append(Issue("error", "broken_link", page["path"], f"链接目标不存在：[[{target}]]"))

    # 3. 重复
    seen_titles: dict[str, str] = {}
    slug_to_paths: dict[str, list[str]] = {}
    for page in pages:
        slug_to_paths.setdefault(page["slug"], []).append(page["path"])
        title = common.normalize_title(str(page["meta"].get("title", "")))
        if title:
            if title in seen_titles:
                issues.append(Issue("error", "duplicate", page["path"],
                                    f"title 与 {seen_titles[title]} 重复：{page['meta'].get('title')}"))
            else:
                seen_titles[title] = page["path"]
    for slug, paths in slug_to_paths.items():
        if len(paths) > 1:
            issues.append(Issue("error", "duplicate", slug, f"slug 重复出现 {len(paths)} 次：{', '.join(paths)}"))

    # 4. 孤儿页：没有任何其他页面链接到它（digest 页豁免——它们是周期产物）
    linked: set[str] = set()
    for page in pages:
        linked |= page["links"]
    for page in pages:
        if page["meta"].get("type") == "digest":
            continue
        if page["slug"] not in linked:
            issues.append(Issue("warning", "orphan", page["path"], "没有任何页面链接到本页"))

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="wiki 体检")
    parser.add_argument("--warnings-as-errors", action="store_true", help="warning 也导致退出码 1")
    args = parser.parse_args()

    issues = lint_wiki(common.WIKI_DIR)
    errors = [i for i in issues if i.level == "error"]
    warnings = [i for i in issues if i.level == "warning"]

    for issue in issues:
        print(issue)
    print(f"\n体检完成：{len(errors)} 个 error，{len(warnings)} 个 warning。")

    if errors or (args.warnings_as_errors and warnings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

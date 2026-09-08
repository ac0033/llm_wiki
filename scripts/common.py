"""公共工具：路径、配置加载、registry 读写、去重、评分。

scripts/ 下所有确定性脚本共享本模块。LLM 不修改本文件。
"""
from __future__ import annotations

import json
import re
import unicodedata
import os
from contextlib import contextmanager
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import frontmatter
import yaml
from rapidfuzz import fuzz

ROOT = Path(__file__).resolve().parents[1]

REGISTRY_DIR = ROOT / "data" / "registry"
STATE_DIR = ROOT / "data" / "state"
REVIEW_QUEUE_DIR = ROOT / "data" / "review_queue"
WIKI_DIR = ROOT / "wiki"
RAW_DIR = ROOT / "raw"
CONFIG_DIR = ROOT / "config"

# wiki 页面类型枚举，与 AGENTS.md 的 schema 约定一致
PAGE_TYPES = [
    "overview",
    "concept",
    "paper",
    "system",
    "benchmark",
    "comparison",
    "digest",
    "direction",
    "question",
]

STATUS_VALUES = ["seed", "draft", "compiled", "current", "needs_review", "stale", "archived"]

REQUIRED_FRONTMATTER = [
    "title",
    "type",
    "status",
    "topics",
    "ingested",
    "last_verified",
    "source_count",
    "quality",
    "confidence",
]

# 需要至少一条一手来源 URL 的类型（canonical_url 或 evidence_sources 任一即可）
URL_REQUIRED_TYPES = ["paper", "system", "benchmark"]

# 概念页默认需要至少两个独立来源；单来源概念必须标为 seed/draft/needs_review
CONCEPT_MIN_SOURCES = 2

STALE_DAYS = 90

# rapidfuzz 标题相似度阈值（0~100），超过视为重复
DUP_TITLE_THRESHOLD = 90


def today() -> str:
    return date.today().isoformat()


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or {}


def load_sources_config() -> dict[str, Any]:
    return load_yaml(CONFIG_DIR / "sources.yml")


def load_rubric() -> dict[str, Any]:
    return load_yaml(CONFIG_DIR / "quality-rubric.yml")


def load_directions() -> list[dict[str, Any]]:
    directions = []
    for p in sorted((CONFIG_DIR / "directions").glob("*.yml")):
        directions.append(load_yaml(p))
    return directions


def direction_keywords() -> list[str]:
    kws: list[str] = []
    for d in load_directions():
        kws.extend(d.get("keywords", []))
    return kws


def wiki_page_titles(wiki_dir: Path | None = None) -> list[str]:
    """返回现有 wiki 页面标题，用于 weekly 去重。

    首期种子页可能先于 registry 存在；只看 ingested.jsonl 会把已覆盖论文再次推荐。
    """
    wiki_dir = wiki_dir or WIKI_DIR
    titles: list[str] = []
    for path in sorted(wiki_dir.rglob("*.md")):
        if path.name in {"index.md", "log.md"}:
            continue
        try:
            title = frontmatter.load(path).get("title")
        except Exception:
            continue
        if title:
            titles.append(str(title))
    return titles


# ---------- registry（JSONL 登记簿） ----------

def registry_path(name: str) -> Path:
    """name 例如 candidates / ingested。"""
    return REGISTRY_DIR / f"{name}.jsonl"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    tmp.replace(path)


@contextmanager
def mutation_lock():
    """确定性维护脚本串行写库；进程崩溃由操作系统释放锁。"""
    path = ROOT / ".maintenance.lock"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as handle:
        handle.seek(0, 2)
        if not handle.tell():
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == "nt":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle, fcntl.LOCK_UN)


def load_registry(name: str) -> list[dict[str, Any]]:
    return read_jsonl(registry_path(name))


# ---------- 水位线（watermark） ----------

def load_sync_state(path: Path | None = None) -> dict[str, Any]:
    path = path or (STATE_DIR / "sync_state.json")
    if not path.exists():
        return {"sources": {}}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_watermark(source: str, state: dict[str, Any] | None = None) -> str | None:
    state = state or load_sync_state()
    return state.get("sources", {}).get(source, {}).get("last_fetched")


def set_watermark(source: str, when: str, path: Path | None = None) -> None:
    path = path or (STATE_DIR / "sync_state.json")
    state = load_sync_state(path)
    state.setdefault("sources", {})[source] = {"last_fetched": when}
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        f.write("\n")
    tmp.replace(path)


# ---------- slug 与去重 ----------

def slugify(text: str) -> str:
    """生成 kebab-case slug，与 wikilink 目标约定一致。"""
    text = unicodedata.normalize("NFKD", text)
    text = text.lower()
    text = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", text)
    return text.strip("-")


def normalize_title(title: str) -> str:
    return re.sub(r"\s+", " ", (title or "").strip().lower())


def is_duplicate(title: str, existing_titles: Iterable[str], threshold: int = DUP_TITLE_THRESHOLD) -> bool:
    """标题相似度超过阈值即视为重复（rapidfuzz token 排序比）"""
    nt = normalize_title(title)
    for other in existing_titles:
        if fuzz.token_sort_ratio(nt, normalize_title(other)) >= threshold:
            return True
    return False


# ---------- 评分 ----------

def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def score_candidate(candidate: dict[str, Any], rubric: dict[str, Any], keywords: list[str],
                    reference_date: date | None = None) -> float:
    """按 quality-rubric.yml 给候选打分，返回 0~100。

    维度：
    - relevance：标题 + 摘要中命中方向关键词的比例（命中关键词数 / 关键词总数，封顶 1）。
    - recency：按半衰期指数衰减，published 越近越高；缺日期按 0.5 处理。
    - source_quality：来源权重，缺省 0.5。
    """
    reference_date = reference_date or date.today()
    weights = rubric.get("weights", {"relevance": 0.5, "recency": 0.2, "source_quality": 0.3})
    source_weights = rubric.get("source_weights", {})
    half_life = rubric.get("recency_half_life_days", 180)

    text = f"{candidate.get('title', '')} {candidate.get('abstract', '')}".lower()
    if keywords:
        hits = sum(1 for kw in keywords if kw.lower() in text)
        relevance = min(1.0, hits / max(1, len(keywords)) * 3)  # 命中约 1/3 关键词即视为高度相关
    else:
        relevance = 0.0

    published = _parse_date(candidate.get("published"))
    if published:
        age_days = max(0, (reference_date - published).days)
        recency = 0.5 ** (age_days / half_life)
    else:
        recency = 0.5

    source_quality = source_weights.get(candidate.get("source", ""), 0.5)

    total = (
        weights.get("relevance", 0) * relevance
        + weights.get("recency", 0) * recency
        + weights.get("source_quality", 0) * source_quality
    ) * 100
    return round(total, 2)


def classify_score(score: float, rubric: dict[str, Any]) -> str:
    """返回分流结果：auto_include / review / dropped。"""
    thresholds = rubric.get("thresholds", {"auto_include": 80, "review": 50})
    if score >= thresholds.get("auto_include", 80):
        return "auto_include"
    if score >= thresholds.get("review", 50):
        return "review"
    return "dropped"

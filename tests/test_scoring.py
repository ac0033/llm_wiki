"""test_scoring.py — 评分与分流逻辑的单元测试。"""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import common  # noqa: E402

RUBRIC = {
    "weights": {"relevance": 0.5, "recency": 0.2, "source_quality": 0.3},
    "source_weights": {"arxiv": 0.8, "openalex": 0.7},
    "thresholds": {"auto_include": 80, "review": 50},
    "recency_half_life_days": 180,
}
KEYWORDS = ["agent harness", "tool use", "context management", "swe-bench"]
TODAY = date(2026, 8, 18)


def score(candidate):
    return common.score_candidate(candidate, RUBRIC, KEYWORDS, reference_date=TODAY)


def test_relevant_recent_paper_scores_higher():
    hot = {"title": "Agent Harness for Tool Use", "abstract": "context management on SWE-bench",
           "source": "arxiv", "published": "2026-08-10"}
    cold = {"title": "An unrelated survey of databases", "abstract": "b-tree index internals",
            "source": "arxiv", "published": "2020-01-01"}
    assert score(hot) > score(cold)


def test_score_bounds():
    cand = {"title": "", "abstract": "", "source": "unknown", "published": ""}
    s = score(cand)
    assert 0 <= s <= 100


def test_recency_decays():
    fresh = {"title": "x", "abstract": "", "source": "arxiv", "published": "2026-08-18"}
    old = {"title": "x", "abstract": "", "source": "arxiv", "published": "2026-02-19"}  # 约一个半衰期
    assert score(fresh) > score(old)


def test_missing_date_gets_neutral_recency():
    no_date = {"title": "x", "abstract": "", "source": "arxiv", "published": ""}
    ancient = {"title": "x", "abstract": "", "source": "arxiv", "published": "2000-01-01"}
    assert score(no_date) > score(ancient)


def test_classify_score():
    assert common.classify_score(85, RUBRIC) == "auto_include"
    assert common.classify_score(80, RUBRIC) == "auto_include"
    assert common.classify_score(60, RUBRIC) == "review"
    assert common.classify_score(50, RUBRIC) == "review"
    assert common.classify_score(10, RUBRIC) == "dropped"


def test_weekly_dedupe_marks_duplicates():
    """weekly_update 的去重逻辑：与已入库重复、批内重复分别打标。"""
    import weekly_update

    candidates = [
        {"title": "Agent Harness Runtime", "status": "new", "source": "arxiv", "published": "2026-08-10"},
        {"title": "Agent Harness Runtime", "status": "new", "source": "openalex", "published": "2026-08-10"},
        {"title": "A brand new paper about tool use in LLM agents", "status": "new",
         "source": "arxiv", "published": "2026-08-15",
         "abstract": "tool use context management agent harness"},
    ]
    ingested = [{"title": "Agent Harness Runtime"}]
    weekly_update.dedupe_and_score(candidates, ingested, RUBRIC, KEYWORDS)
    assert candidates[0]["status"] == "duplicate_of_ingested"
    assert candidates[1]["status"] == "duplicate_of_ingested"  # 第二条也会命中 known_titles
    assert candidates[2]["status"] in ("auto_include", "review", "dropped")
    assert "score" in candidates[2]
